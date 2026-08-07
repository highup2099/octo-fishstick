from uuid import UUID
from datetime import datetime, timezone
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.schemas.orders import OrderCreate, OrderResponse
from app.core.security import get_current_active_user, TokenData
from app.services.order_service import OrderService, OrderState
from app.services.quote_service import QuoteService

logger = logging.getLogger(__name__)

router = APIRouter()
order_service = OrderService()
quote_service = QuoteService()
# Create a local limiter instance for this module
limiter = Limiter(key_func=get_remote_address)

@router.post("", response_model=OrderResponse)
@limiter.limit("10/minute")  # Rate limit: 10 orders per minute per IP
async def create_order(
    payload: OrderCreate,
    current_user: TokenData = Depends(get_current_active_user)
):
    """
    Create a new order from a quote.
    Requires authentication and validates quote ownership.
    """
    # Audit log for order creation attempt
    logger.info(
        f"Order creation requested: quote_id={payload.quote_id}, "
        f"user_id={current_user.user_id}, timestamp={datetime.now(timezone.utc).isoformat()}"
    )
    
    # Fetch quote and verify ownership
    try:
        order_data = await order_service.create_from_quote(
            quote_id=payload.quote_id,
            current_user=current_user
        )
        
        # Audit log for successful order creation
        logger.info(
            f"Order created successfully: order_id={order_data['id']}, "
            f"quote_id={payload.quote_id}, user_id={current_user.user_id}, "
            f"status={order_data['status']}, timestamp={datetime.now(timezone.utc).isoformat()}"
        )
        
        return order_data
    except HTTPException as e:
        # Audit log for failed order creation
        logger.warning(
            f"Order creation failed: quote_id={payload.quote_id}, "
            f"user_id={current_user.user_id}, reason={e.detail}, "
            f"timestamp={datetime.now(timezone.utc).isoformat()}"
        )
        raise
    except Exception as e:
        # Audit log for unexpected error
        logger.error(
            f"Order creation error: quote_id={payload.quote_id}, "
            f"user_id={current_user.user_id}, error={str(e)}, "
            f"timestamp={datetime.now(timezone.utc).isoformat()}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create order"
        )
