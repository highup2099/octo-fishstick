from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4
import logging
from fastapi import Depends, HTTPException
from app.schemas.quotes import QuoteCreate
from app.providers.simulated import SimulatedProvider
from app.core.security import get_current_active_user, TokenData

logger = logging.getLogger(__name__)

class QuoteService:
    def __init__(self):
        self.provider = SimulatedProvider()

    async def create(self, payload: QuoteCreate, current_user: TokenData) -> dict:
        """Create a new quote with user association and audit logging."""
        try:
            result = await self.provider.get_quote(payload.sell_asset, payload.buy_asset, payload.sell_amount)
            
            quote_data = {
                "id": str(uuid4()),
                "user_id": str(current_user.user_id),  # Associate quote with user
                "sell_asset": result.sell_asset,
                "buy_asset": result.buy_asset,
                "sell_amount": result.sell_amount,
                "buy_amount": result.buy_amount,
                "fee_amount": result.fee_amount,
                "provider": result.provider,
                "status": "active",
                "expires_at": (datetime.now(timezone.utc) + timedelta(seconds=30)).isoformat(),
            }
            
            # Audit log for quote creation
            logger.info(
                f"Quote created: id={quote_data['id']}, user_id={current_user.user_id}, "
                f"sell={payload.sell_amount} {payload.sell_asset}, buy_asset={payload.buy_asset}"
            )
            
            return quote_data
        except Exception as e:
            logger.error(f"Failed to create quote for user {current_user.user_id}: {str(e)}")
            raise
