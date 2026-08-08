"""Order Service - Domain service for managing order lifecycle with state machine."""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, Type
from enum import Enum

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.order import Order, OrderStatus
from app.models.ledger import LedgerEntry, LedgerEntryType
from app.providers.base import LiquidityProvider


class OrderService:
    """
    Service for handling order lifecycle management.
    
    Implements strict state machine pattern for order status transitions.
    """

    # Define allowed state transitions
    ALLOWED_TRANSITIONS = {
        OrderStatus.CREATED: {OrderStatus.QUOTED, OrderStatus.FAILED},
        OrderStatus.QUOTED: {OrderStatus.AWAITING_PAYMENT, OrderStatus.FAILED},
        OrderStatus.AWAITING_PAYMENT: {OrderStatus.EXECUTING, OrderStatus.FAILED},
        OrderStatus.EXECUTING: {OrderStatus.SETTLED, OrderStatus.FAILED},
        OrderStatus.SETTLED: set(),  # Terminal state
        OrderStatus.FAILED: set(),   # Terminal state
    }

    def __init__(self, db: AsyncSession, provider: Optional[LiquidityProvider] = None):
        self.db = db
        self.provider = provider

    async def create_order(
        self,
        user_id: int,
        quote_id: int,
        asset_in_symbol: str,
        asset_out_symbol: str,
        amount_in: Decimal,
        amount_out: Decimal,
        fee_amount: Decimal,
        fee_currency: str,
    ) -> Order:
        """Create a new order from a quote."""
        order = Order(
            user_id=user_id,
            state=OrderStatus.CREATED,
            asset_in_symbol=asset_in_symbol,
            asset_out_symbol=asset_out_symbol,
            amount_in=amount_in,
            amount_out=amount_out,
            fee_amount=fee_amount,
            fee_currency=fee_currency,
        )

        self.db.add(order)
        await self.db.commit()
        await self.db.refresh(order)

        return order

    async def get_order(self, order_id: int) -> Optional[Order]:
        """Get an order by ID."""
        result = await self.db.execute(
            select(Order).where(Order.id == order_id)
        )
        return result.scalar_one_or_none()

    async def transition_state(self, order: Order, new_state: OrderStatus) -> Order:
        """
        Transition an order to a new state using the state machine.
        
        Args:
            order: The order to transition
            new_state: The target state
            
        Returns:
            Updated order object
            
        Raises:
            ValueError: If the transition is not allowed
        """
        current_state = order.state
        
        # Check if transition is allowed
        if new_state not in self.ALLOWED_TRANSITIONS.get(current_state, set()):
            raise ValueError(
                f"Invalid order state transition: {current_state.value} -> {new_state.value}"
            )

        # Update state
        order.state = new_state
        order.updated_at = datetime.now(timezone.utc)
        
        # Set settled_at if reaching terminal SETTLED state
        if new_state == OrderStatus.SETTLED:
            order.settled_at = datetime.now(timezone.utc)

        await self.db.commit()
        await self.db.refresh(order)

        return order

    async def execute_order(self, order: Order) -> str:
        """
        Execute an order through the liquidity provider.
        
        Args:
            order: The order to execute
            
        Returns:
            External order ID from the provider
            
        Raises:
            ValueError: If order is not in EXECUTING state
        """
        if order.state != OrderStatus.EXECUTING:
            raise ValueError(f"Cannot execute order in state: {order.state.value}")

        if not self.provider:
            raise RuntimeError("No liquidity provider configured")

        # Execute through provider
        external_order_id = await self.provider.execute(str(order.id))
        
        order.external_order_id = external_order_id
        order.updated_at = datetime.now(timezone.utc)
        
        await self.db.commit()
        await self.db.refresh(order)

        return external_order_id

    async def fail_order(self, order: Order, error_message: str) -> Order:
        """Mark an order as failed with an error message."""
        order.state = OrderStatus.FAILED
        order.error_message = error_message
        order.updated_at = datetime.now(timezone.utc)
        
        await self.db.commit()
        await self.db.refresh(order)

        return order
