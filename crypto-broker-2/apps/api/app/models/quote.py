import enum
from datetime import datetime
from decimal import Decimal
from sqlalchemy import DateTime, Enum, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base, TimestampMixin

class QuoteStatus(str, enum.Enum):
    active = "active"
    accepted = "accepted"
    expired = "expired"
    cancelled = "cancelled"

class Quote(TimestampMixin, Base):
    __tablename__ = "quotes"
    status: Mapped[QuoteStatus] = mapped_column(Enum(QuoteStatus, name="quote_status"), default=QuoteStatus.active, index=True)
    sell_asset: Mapped[str] = mapped_column(String(30))
    buy_asset: Mapped[str] = mapped_column(String(30))
    sell_amount: Mapped[Decimal] = mapped_column(Numeric(36, 18))
    buy_amount: Mapped[Decimal] = mapped_column(Numeric(36, 18))
    fee_amount: Mapped[Decimal] = mapped_column(Numeric(36, 18))
    provider: Mapped[str] = mapped_column(String(50))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
