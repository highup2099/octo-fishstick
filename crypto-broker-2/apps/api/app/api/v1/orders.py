"""API Router for Orders endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.schemas.orders import OrderCreateRequest, OrderResponse
from app.services.order_service import OrderService
from app.providers.simulated import SimulatedProvider

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    request: OrderCreateRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new order from an existing quote.
    
    - **quote_id**: ID of the accepted quote
    - **withdrawal_address**: Crypto address for receiving funds
    - **withdrawal_network**: Network for withdrawal (e.g., TRC20, ERC20)
    """
    try:
        # Initialize services
        provider = SimulatedProvider()
        order_service = OrderService(db=db, provider=provider)
        
        # TODO: Get user_id from authentication middleware (for now use placeholder)
        user_id = 1
        
        # TODO: Fetch quote and validate it's not expired
        # For MVP, we'll create order with basic data
        # In production, you'd fetch the quote and use its data
        
        order = await order_service.create_order(
            user_id=user_id,
            quote_id=int(request.quote_id),
            asset_in_symbol="USDT",  # TODO: Get from quote
            asset_out_symbol="BTC",  # TODO: Get from quote
            amount_in=1000,  # TODO: Get from quote
            amount_out=0.015,  # TODO: Get from quote
            fee_amount=15,  # TODO: Get from quote
            fee_currency="USDT",
        )
        
        # Transition to QUOTED state
        from app.models.order import OrderStatus
        order = await order_service.transition_state(order, OrderStatus.QUOTED)
        
        return OrderResponse(
            id=str(order.id),
            user_id=str(order.user_id),
            status=order.state,
            sell_asset=order.asset_in_symbol,
            buy_asset=order.asset_out_symbol,
            sell_amount=order.amount_in,
            buy_amount=order.amount_out,
            fee_amount=order.fee_amount,
            withdrawal_address=request.withdrawal_address,
            withdrawal_network=request.withdrawal_network,
            provider_order_id=order.external_order_id,
            created_at=order.created_at,
            updated_at=order.updated_at,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create order: {str(e)}",
        )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get an order by ID."""
    try:
        service = OrderService(db=db)
        order = await service.get_order(int(order_id))
        
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found",
            )
        
        return OrderResponse(
            id=str(order.id),
            user_id=str(order.user_id),
            status=order.state,
            sell_asset=order.asset_in_symbol,
            buy_asset=order.asset_out_symbol,
            sell_amount=order.amount_in,
            buy_amount=order.amount_out,
            fee_amount=order.fee_amount,
            withdrawal_address=None,  # TODO: Store in order model
            withdrawal_network=None,
            provider_order_id=order.external_order_id,
            created_at=order.created_at,
            updated_at=order.updated_at,
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid order ID format",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get order: {str(e)}",
        )
