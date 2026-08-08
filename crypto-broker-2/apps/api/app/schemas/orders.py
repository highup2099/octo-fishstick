"""Schemas for Orders API."""
from decimal import Decimal
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models.order import OrderStatus


class OrderCreateRequest(BaseModel):
    """Запрос на создание ордера."""
    quote_id: str = Field(..., description="ID подтвержденной котировки")
    withdrawal_address: str = Field(..., description="Адрес вывода средств", min_length=10, max_length=256)
    withdrawal_network: str = Field(..., description="Сеть вывода", min_length=2, max_length=50)


class OrderResponse(BaseModel):
    """Ответ с данными ордера."""
    id: str
    user_id: str
    status: OrderStatus
    sell_asset: str
    buy_asset: str
    sell_amount: Decimal
    buy_amount: Decimal
    fee_amount: Decimal
    withdrawal_address: Optional[str]
    withdrawal_network: Optional[str]
    provider_order_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
