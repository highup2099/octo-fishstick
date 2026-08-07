from decimal import Decimal
from pydantic import BaseModel, Field

class QuoteCreate(BaseModel):
    sell_asset: str = Field(min_length=2, max_length=30)
    buy_asset: str = Field(min_length=2, max_length=30)
    sell_amount: Decimal = Field(gt=0)

class QuoteResponse(BaseModel):
    id: str
    sell_asset: str
    buy_asset: str
    sell_amount: Decimal
    buy_amount: Decimal
    fee_amount: Decimal
    provider: str
    status: str
    expires_at: str
