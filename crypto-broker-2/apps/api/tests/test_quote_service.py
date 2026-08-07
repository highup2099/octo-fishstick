from decimal import Decimal
import pytest
from app.services.quote_service import QuoteService

@pytest.mark.asyncio
async def test_simulated_quote():
    q = await QuoteService().create("USDT", "USDC", Decimal("1000"))
    assert q["provider"] == "simulated"
    assert q["fee_amount"] == Decimal("5.00000000")
    assert q["buy_amount"] == Decimal("994.00500000")
