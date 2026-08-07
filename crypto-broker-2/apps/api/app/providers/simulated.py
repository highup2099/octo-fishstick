from decimal import Decimal
from .base import ProviderQuote

class SimulatedProvider:
    name = "simulated"

    async def get_quote(self, sell_asset: str, buy_asset: str, sell_amount: Decimal) -> ProviderQuote:
        rate = Decimal("1")
        fee = (sell_amount * Decimal("0.005")).quantize(Decimal("0.00000001"))
        if {sell_asset.upper(), buy_asset.upper()} == {"USDT", "USDC"}:
            rate = Decimal("0.999")
        buy_amount = ((sell_amount - fee) * rate).quantize(Decimal("0.00000001"))
        return ProviderQuote(
            provider=self.name,
            sell_asset=sell_asset.upper(),
            buy_asset=buy_asset.upper(),
            sell_amount=sell_amount,
            buy_amount=buy_amount,
            fee_amount=fee,
        )

    async def execute(self, order_id: str) -> str:
        return f"sim-exec-{order_id}"
