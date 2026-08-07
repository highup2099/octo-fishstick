import enum
from decimal import Decimal
from sqlalchemy import Enum, ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base, TimestampMixin

class OrderStatus(str, enum.Enum):
    created = "created"
    risk_check = "risk_check"
    awaiting_funds = "awaiting_funds"
    executing = "executing"
    settling = "settling"
    completed = "completed"
    failed = "failed"
    blocked = "blocked"
    cancelled = "cancelled"

class Order(TimestampMixin, Base):
    __tablename__ = "orders"
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    quote_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("quotes.id"), index=True)
    status: Mapped[OrderStatus] = mapped_column(Enum(OrderStatus, name="order_status"), default=OrderStatus.created, index=True)
    sell_asset: Mapped[str] = mapped_column(String(30))
    buy_asset: Mapped[str] = mapped_column(String(30))
    sell_amount: Mapped[Decimal] = mapped_column(Numeric(36, 18))
    buy_amount: Mapped[Decimal] = mapped_column(Numeric(36, 18))
    provider: Mapped[str] = mapped_column(String(50))
