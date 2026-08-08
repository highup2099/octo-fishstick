"""API Router for Quotes endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from decimal import Decimal

from app.db import get_db
from app.schemas.quotes import QuoteRequest, QuoteResponse
from app.services.quote_service import QuoteService
from app.providers.simulated import SimulatedProvider

router = APIRouter(prefix="/quotes", tags=["quotes"])


@router.post("", response_model=QuoteResponse, status_code=status.HTTP_201_CREATED)
async def create_quote(
    request: QuoteRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Generate a new quote for exchanging assets.
    
    - **sell_asset**: Asset to sell (e.g., USDT)
    - **buy_asset**: Asset to buy (e.g., BTC)
    - **amount**: Amount of sell_asset to exchange
    - **network**: Optional network for withdrawal
    """
    try:
        # Create service with simulated provider for MVP
        provider = SimulatedProvider()
        service = QuoteService(db=db, provider=provider)
        
        # TODO: Get user_id from authentication middleware (for now use placeholder)
        user_id = 1
        
        quote = await service.create_quote(
            user_id=user_id,
            sell_asset=request.sell_asset,
            buy_asset=request.buy_asset,
            sell_amount=request.amount,
        )
        
        return QuoteResponse(
            id=str(quote.id),
            sell_asset=quote.sell_asset,
            buy_asset=quote.buy_asset,
            sell_amount=quote.sell_amount,
            buy_amount=quote.buy_amount,
            rate=quote.rate,
            fee_percent=Decimal("1.5"),  # Default fee percent
            fee_amount=quote.fee_amount,
            status=quote.status,
            expires_at=quote.expires_at,
            created_at=quote.created_at,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create quote: {str(e)}",
        )


@router.get("/{quote_id}", response_model=QuoteResponse)
async def get_quote(
    quote_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a quote by ID."""
    try:
        service = QuoteService(db=db)
        quote = await service.get_quote(int(quote_id))
        
        if not quote:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Quote not found",
            )
        
        return QuoteResponse(
            id=str(quote.id),
            sell_asset=quote.sell_asset,
            buy_asset=quote.buy_asset,
            sell_amount=quote.sell_amount,
            buy_amount=quote.buy_amount,
            rate=quote.rate,
            fee_percent=Decimal("1.5"),
            fee_amount=quote.fee_amount,
            status=quote.status,
            expires_at=quote.expires_at,
            created_at=quote.created_at,
        )
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid quote ID format",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get quote: {str(e)}",
        )
