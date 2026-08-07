from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol

@dataclass(frozen=True)
class ProviderQuote:
    provider: str
    sell_asset: str
    buy_asset: str
    sell_amount: Decimal
    buy_amount: Decimal
    fee_amount: Decimal

class LiquidityProvider(Protocol):
    async def get_quote(self, sell_asset: str, buy_asset: str, sell_amount: Decimal) -> ProviderQuote: ...
    async def execute(self, order_id: str) -> str: ...
