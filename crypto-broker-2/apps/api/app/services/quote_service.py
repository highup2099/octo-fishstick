"""Quote Service - Domain service for creating and managing quotes."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.providers.base import LiquidityProvider
from app.providers.simulated import SimulatedProvider
from app.models.quote import Quote


class QuoteService:
    """Service for handling quote generation and management."""

    def __init__(self, db: AsyncSession, provider: Optional[LiquidityProvider] = None):
        self.db = db
        self.provider = provider or SimulatedProvider()

    async def create_quote(
        self,
        user_id: int,
        sell_asset: str,
        buy_asset: str,
        sell_amount: Decimal,
    ) -> Quote:
        """
        Create a new quote for the given assets and amount.
        
        Args:
            user_id: ID of the user requesting the quote
            sell_asset: Symbol of the asset to sell (e.g., 'USDT')
            buy_asset: Symbol of the asset to buy (e.g., 'BTC')
            sell_amount: Amount of sell_asset to exchange
            
        Returns:
            Quote object with the calculated rates and amounts
        """
        # Get quote from provider
        provider_quote = await self.provider.get_quote(
            sell_asset=sell_asset,
            buy_asset=buy_asset,
            sell_amount=sell_amount,
        )

        # Create quote record in database
        expires_at = datetime.now(timezone.utc) + timedelta(seconds=30)
        
        quote = Quote(
            user_id=user_id,
            sell_asset=sell_asset,
            buy_asset=buy_asset,
            sell_amount=provider_quote.sell_amount,
            buy_amount=provider_quote.buy_amount,
            fee_amount=provider_quote.fee_amount,
            fee_currency=provider_quote.fee_currency,
            provider=provider_quote.provider,
            rate=provider_quote.rate,
            expires_at=expires_at,
        )

        self.db.add(quote)
        await self.db.commit()
        await self.db.refresh(quote)

        return quote

    async def get_quote(self, quote_id: int) -> Optional[Quote]:
        """Get a quote by ID."""
        from sqlalchemy import select
        
        result = await self.db.execute(
            select(Quote).where(Quote.id == quote_id)
        )
        return result.scalar_one_or_none()

    async def is_quote_valid(self, quote: Quote) -> bool:
        """Check if a quote is still valid (not expired and active)."""
        now = datetime.now(timezone.utc)
        return quote.status == "active" and quote.expires_at > now
