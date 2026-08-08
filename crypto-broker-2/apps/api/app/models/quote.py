"""Quote model - represents a price quote for an OTC trade."""

import enum
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin


class QuoteStatus(str, enum.Enum):
    """Status of a quote."""
    ACTIVE = "active"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class Quote(TimestampMixin, Base):
    """
    Quote model representing a price quote for an OTC trade.
    
    Quotes are time-limited (typically 30 seconds) and can be converted
    to orders when accepted by the user.
    """
    __tablename__ = "quotes"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    
    # Quote status
    status: Mapped[QuoteStatus] = mapped_column(
        Enum(QuoteStatus, name="quotestatus"),
        default=QuoteStatus.ACTIVE,
        index=True,
        nullable=False
    )
    
    # Asset pair
    sell_asset: Mapped[str] = mapped_column(String(20), nullable=False)
    buy_asset: Mapped[str] = mapped_column(String(20), nullable=False)
    
    # Amounts
    sell_amount: Mapped[Decimal] = mapped_column(Numeric(36, 18), nullable=False)
    buy_amount: Mapped[Decimal] = mapped_column(Numeric(36, 18), nullable=False)
    
    # Fee information
    fee_amount: Mapped[Decimal] = mapped_column(Numeric(36, 18), nullable=False)
    fee_currency: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Provider that generated this quote
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    
    # Exchange rate (buy_amount / sell_amount)
    rate: Mapped[Decimal] = mapped_column(Numeric(36, 18), nullable=False)
    
    # Expiration timestamp
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    def __repr__(self) -> str:
        return (
            f"<Quote(id={self.id}, sell={self.sell_amount} {self.sell_asset}, "
            f"buy={self.buy_amount} {self.buy_asset}, status={self.status.value})>"
        )

    def is_expired(self) -> bool:
        """Check if the quote has expired."""
        return datetime.now(timezone.utc) > self.expires_at

    def can_accept(self) -> bool:
        """Check if the quote can be accepted."""
        return self.status == QuoteStatus.ACTIVE and not self.is_expired()
