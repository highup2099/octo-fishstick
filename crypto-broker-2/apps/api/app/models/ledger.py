from decimal import Decimal
from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base, TimestampMixin

class LedgerEntry(TimestampMixin, Base):
    __tablename__ = "ledger_entries"
    order_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("orders.id"), index=True)
    account: Mapped[str] = mapped_column(String(100), index=True)
    asset: Mapped[str] = mapped_column(String(30), index=True)
    debit: Mapped[Decimal] = mapped_column(Numeric(36, 18), default=0)
    credit: Mapped[Decimal] = mapped_column(Numeric(36, 18), default=0)
    reference: Mapped[str] = mapped_column(String(255))
