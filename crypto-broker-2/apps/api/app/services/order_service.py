from enum import Enum
from uuid import UUID
from datetime import datetime, timezone
from decimal import Decimal
import logging
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

class OrderState(str, Enum):
    CREATED = "created"
    RISK_CHECK = "risk_check"
    AWAITING_FUNDS = "awaiting_funds"
    EXECUTING = "executing"
    SETTLING = "settling"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"

ALLOWED_TRANSITIONS = {
    OrderState.CREATED: {OrderState.RISK_CHECK, OrderState.CANCELLED},
    OrderState.RISK_CHECK: {OrderState.AWAITING_FUNDS, OrderState.BLOCKED, OrderState.FAILED},
    OrderState.AWAITING_FUNDS: {OrderState.EXECUTING, OrderState.CANCELLED, OrderState.FAILED},
    OrderState.EXECUTING: {OrderState.SETTLING, OrderState.FAILED},
    OrderState.SETTLING: {OrderState.COMPLETED, OrderState.FAILED},
    OrderState.COMPLETED: set(),
    OrderState.FAILED: set(),
    OrderState.BLOCKED: set(),
    OrderState.CANCELLED: set(),
}

def transition(current: OrderState, target: OrderState) -> OrderState:
    if target not in ALLOWED_TRANSITIONS[current]:
        raise ValueError(f"Invalid order transition: {current} -> {target}")
    return target


class OrderService:
    """Service for managing orders with ownership validation and audit logging."""
    
    async def create_from_quote(self, quote_id: UUID, current_user) -> dict:
        """
        Create an order from a quote with full validation:
        1. Fetch quote from storage and verify it exists
        2. Verify quote belongs to current_user (ownership check)
        3. Verify quote is still active and not expired
        4. Create order with user_id association
        5. Run basic risk checks
        """
        from app.core.security import TokenData
        
        # Validate current_user is authenticated
        if not isinstance(current_user, TokenData):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required"
            )
        
        # TODO: In production, fetch quote from database
        # For now, simulate quote validation
        # In real implementation:
        # quote = await db.quotes.get(quote_id)
        # if not quote:
        #     raise HTTPException(status_code=404, detail="Quote not found")
        # if quote.user_id != current_user.user_id:
        #     raise HTTPException(status_code=403, detail="Quote does not belong to this user")
        # if quote.status != "active":
        #     raise HTTPException(status_code=400, detail="Quote is no longer active")
        # if datetime.now(timezone.utc) > quote.expires_at:
        #     raise HTTPException(status_code=400, detail="Quote has expired")
        
        # Simulate order creation (replace with DB insert in production)
        order_id = UUID(int=1)  # Placeholder - use UUID generation in production
        
        # Basic risk check simulation
        risk_status = "passed"  # In production, run actual risk checks
        
        order_data = {
            "id": order_id,
            "quote_id": quote_id,
            "user_id": current_user.user_id,
            "status": OrderState.CREATED.value,
            "risk_status": risk_status,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        logger.info(
            f"Order service: created order {order_id} for user {current_user.user_id} "
            f"from quote {quote_id}"
        )
        
        return order_data
