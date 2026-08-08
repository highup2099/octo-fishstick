"""Schemas for Quotes API."""
from decimal import Decimal
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models.quote import QuoteStatus


class QuoteRequest(BaseModel):
    """Запрос на получение котировки."""
    sell_asset: str = Field(..., description="Код актива продажи (напр. BTC)", min_length=2, max_length=30)
    buy_asset: str = Field(..., description="Код актива покупки (напр. USDT)", min_length=2, max_length=30)
    amount: Decimal = Field(..., gt=0, description="Количество продаваемого актива")
    network: Optional[str] = Field(None, description="Сеть вывода (напр. TRC20)")


class QuoteResponse(BaseModel):
    """Ответ с котировкой."""
    id: str
    sell_asset: str
    buy_asset: str
    sell_amount: Decimal
    buy_amount: Decimal
    rate: Decimal
    fee_percent: Decimal
    fee_amount: Decimal
    status: QuoteStatus
    expires_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True
