"""Ledger Entry model - double-entry bookkeeping for audit trail."""

import enum
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import Enum, ForeignKey, Numeric, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin


class LedgerEntryType(str, enum.Enum):
    """Types of ledger entries for double-entry bookkeeping."""
    DEPOSIT = "deposit"
    EXCHANGE = "exchange"
    FEE = "fee"
    WITHDRAWAL = "withdrawal"


class LedgerEntry(TimestampMixin, Base):
    """
    Ledger entry model for tracking all fund movements.
    
    CRITICAL: This is the source of truth for user balances.
    User balance is ALWAYS computed by aggregating these entries.
    Never store balance directly on user model.
    
    Positive amounts represent credits (money in).
    Negative amounts represent debits (money out).
    """
    __tablename__ = "ledger_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False
    )
    
    # Asset and network identification
    asset_symbol: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    network_symbol: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    
    # Amount (positive for credit, negative for debit)
    amount: Mapped[Decimal] = mapped_column(Numeric(36, 18), nullable=False)
    
    # Entry type
    entry_type: Mapped[LedgerEntryType] = mapped_column(
        Enum(LedgerEntryType, name="ledgerentrytype"),
        nullable=False,
        index=True
    )
    
    # Reference to related entity (order, quote, etc.)
    reference_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, index=True)
    reference_id: Mapped[Optional[int]] = mapped_column(nullable=True, index=True)
    
    # Running balance after this entry (for quick lookup without aggregation)
    balance_after: Mapped[Decimal] = mapped_column(Numeric(36, 18), nullable=False)
    
    # Description for audit purposes
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return (
            f"<LedgerEntry(id={self.id}, user_id={self.user_id}, "
            f"asset={self.asset_symbol}, amount={self.amount}, type={self.entry_type.value})>"
        )
