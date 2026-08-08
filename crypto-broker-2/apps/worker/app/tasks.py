"""Celery tasks for CryptoBroker order processing."""
import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy import select

from .celery_app import celery_app
from app.models.order import Order, OrderStatus
from app.models.ledger import LedgerEntry, LedgerEntryType
from app.providers.simulated import SimulatedProvider

logger = logging.getLogger(__name__)


# Database session factory (configured at worker startup)
_db_session_factory: Optional[async_sessionmaker[AsyncSession]] = None


def init_db_session(engine):
    """Initialize database session factory for worker."""
    global _db_session_factory
    _db_session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    logger.info("Worker database session initialized")


@celery_app.task(name="app.tasks.execute_order", bind=True, max_retries=3)
def execute_order(self, order_id: int):
    """
    Execute an order through the liquidity provider.
    
    This task is called when order transitions to EXECUTING state.
    It routes the order to the appropriate provider (OKX/Bybit/Simulated)
    and handles the execution result.
    """
    if not _db_session_factory:
        logger.error("Database session not initialized in worker")
        return {"error": "Database not initialized"}
    
    try:
        import asyncio
        
        async def _execute():
            async with _db_session_factory() as db:
                # Fetch order
                result = await db.execute(
                    select(Order).where(Order.id == order_id)
                )
                order = result.scalar_one_or_none()
                
                if not order:
                    logger.error(f"Order {order_id} not found")
                    return {"error": f"Order {order_id} not found"}
                
                if order.state != OrderStatus.EXECUTING:
                    logger.warning(
                        f"Order {order_id} is not in EXECUTING state: {order.state}"
                    )
                    return {"skipped": f"Invalid state: {order.state}"}
                
                logger.info(f"Executing order {order_id}...")
                
                # Initialize provider (in production, use factory based on config)
                provider = SimulatedProvider()
                
                # Execute through provider
                external_order_id = await provider.execute(str(order.id))
                
                # Update order with external ID
                order.external_order_id = external_order_id
                order.updated_at = datetime.now(timezone.utc)
                
                # Transition to SETTLING state
                order.state = OrderStatus.SETTLING
                
                await db.commit()
                await db.refresh(order)
                
                logger.info(
                    f"Order {order_id} executed successfully. "
                    f"External ID: {external_order_id}"
                )
                
                # Schedule settlement task
                settle_order.delay(order_id)
                
                return {
                    "order_id": order_id,
                    "external_order_id": external_order_id,
                    "status": "executing",
                }
        
        return asyncio.run(_execute())
        
    except Exception as exc:
        logger.exception(f"Error executing order {order_id}: {exc}")
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@celery_app.task(name="app.tasks.settle_order", bind=True, max_retries=3)
def settle_order(self, order_id: int):
    """
    Settle an order after successful execution.
    
    This task:
    1. Confirms the external order completion
    2. Creates ledger entries for the transaction
    3. Transitions order to SETTLED state
    """
    if not _db_session_factory:
        logger.error("Database session not initialized in worker")
        return {"error": "Database not initialized"}
    
    try:
        import asyncio
        
        async def _settle():
            async with _db_session_factory() as db:
                # Fetch order
                result = await db.execute(
                    select(Order).where(Order.id == order_id)
                )
                order = result.scalar_one_or_none()
                
                if not order:
                    logger.error(f"Order {order_id} not found")
                    return {"error": f"Order {order_id} not found"}
                
                if order.state != OrderStatus.SETTLING:
                    logger.warning(
                        f"Order {order_id} is not in SETTLING state: {order.state}"
                    )
                    return {"skipped": f"Invalid state: {order.state}"}
                
                logger.info(f"Settling order {order_id}...")
                
                # In production, verify external order status via provider API
                # For MVP, we assume success
                
                # Create ledger entries (double-entry bookkeeping)
                # Debit: User receives buy_asset
                debit_entry = LedgerEntry(
                    user_id=order.user_id,
                    asset=order.asset_out_symbol,
                    network="BTC",  # TODO: Get from order
                    amount=order.amount_out,
                    entry_type=LedgerEntryType.CREDIT,
                    reference_id=f"order_{order_id}",
                    description=f"Order {order_id} settlement - received {order.asset_out_symbol}",
                )
                
                # Credit: System fee
                credit_entry = LedgerEntry(
                    user_id=order.user_id,
                    asset=order.fee_currency or "USDT",
                    network="TRC20",  # TODO: Get from order
                    amount=-order.fee_amount,  # Negative for debit (fee deduction)
                    entry_type=LedgerEntryType.DEBIT,
                    reference_id=f"order_{order_id}_fee",
                    description=f"Order {order_id} fee",
                )
                
                db.add(debit_entry)
                db.add(credit_entry)
                
                # Transition to SETTLED
                order.state = OrderStatus.SETTLED
                order.settled_at = datetime.now(timezone.utc)
                order.updated_at = datetime.now(timezone.utc)
                
                await db.commit()
                await db.refresh(order)
                
                logger.info(f"Order {order_id} settled successfully")
                
                return {
                    "order_id": order_id,
                    "status": "settled",
                    "settled_at": order.settled_at.isoformat(),
                }
        
        return asyncio.run(_settle())
        
    except Exception as exc:
        logger.exception(f"Error settling order {order_id}: {exc}")
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@celery_app.task(name="app.tasks.fail_order", bind=True)
def fail_order(self, order_id: int, error_message: str):
    """
    Mark an order as failed.
    
    Called when execution fails or timeout occurs.
    """
    if not _db_session_factory:
        logger.error("Database session not initialized in worker")
        return {"error": "Database not initialized"}
    
    try:
        import asyncio
        
        async def _fail():
            async with _db_session_factory() as db:
                result = await db.execute(
                    select(Order).where(Order.id == order_id)
                )
                order = result.scalar_one_or_none()
                
                if not order:
                    logger.error(f"Order {order_id} not found")
                    return {"error": f"Order {order_id} not found"}
                
                # Don't fail terminal states
                if order.state in (OrderStatus.SETTLED, OrderStatus.FAILED):
                    logger.warning(f"Order {order_id} already in terminal state: {order.state}")
                    return {"skipped": f"Terminal state: {order.state}"}
                
                logger.warning(f"Failing order {order_id}: {error_message}")
                
                order.state = OrderStatus.FAILED
                order.error_message = error_message
                order.updated_at = datetime.now(timezone.utc)
                
                await db.commit()
                await db.refresh(order)
                
                return {
                    "order_id": order_id,
                    "status": "failed",
                    "error": error_message,
                }
        
        return asyncio.run(_fail())
        
    except Exception as exc:
        logger.exception(f"Error failing order {order_id}: {exc}")
        return {"error": str(exc)}


@celery_app.task(name="app.tasks.health_check")
def health_check():
    """Basic health check task."""
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}

