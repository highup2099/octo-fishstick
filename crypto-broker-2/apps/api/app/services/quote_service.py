from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import uuid4
from app.providers.simulated import SimulatedProvider

class QuoteService:
    def __init__(self):
        self.provider = SimulatedProvider()

    async def create(self, sell_asset: str, buy_asset: str, sell_amount: Decimal) -> dict:
        result = await self.provider.get_quote(sell_asset, buy_asset, sell_amount)
        return {
            "id": str(uuid4()),
            "sell_asset": result.sell_asset,
            "buy_asset": result.buy_asset,
            "sell_amount": result.sell_amount,
            "buy_amount": result.buy_amount,
            "fee_amount": result.fee_amount,
            "provider": result.provider,
            "status": "active",
            "expires_at": (datetime.now(timezone.utc) + timedelta(seconds=30)).isoformat(),
        }
