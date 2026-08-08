"""Order model - represents an OTC trade order."""

import enum
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from sqlalchemy import Enum, ForeignKey, Numeric, String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin


class OrderStatus(str, enum.Enum):
    """
    Order status states for the state machine.
    
    State transitions:
    CREATED -> QUOTED -> AWAITING_PAYMENT -> EXECUTING -> SETTLED (terminal)
    Any state -> FAILED (terminal)
    """
    CREATED = "created"
    QUOTED = "quoted"
    AWAITING_PAYMENT = "awaiting_payment"
    EXECUTING = "executing"
    SETTLED = "settled"
    FAILED = "failed"


class Order(TimestampMixin, Base):
    """
    Order model representing an OTC trade.
    
    Non-custodial: We don't store user balances. The order tracks the intent
    to exchange assets, and ledger_entries track the actual movement of funds.
    """
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), 
        index=True,
        nullable=False
    )
    
    # State machine field
    state: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, name="orderstatus"),
        default=OrderStatus.CREATED,
        nullable=False,
        index=True
    )
    
    # Provider that executed the order
    provider: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Asset pair
    asset_in_symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    asset_out_symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    
    # Amounts
    amount_in: Mapped[Decimal] = mapped_column(Numeric(36, 18), nullable=False)
    amount_out: Mapped[Optional[Decimal]] = mapped_column(Numeric(36, 18), nullable=True)
    
    # Fee information
    fee_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(36, 18), nullable=True)
    fee_currency: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # External provider reference
    external_order_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Error handling
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Settlement timestamp
    settled_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True
    )

    def __repr__(self) -> str:
        return f"<Order(id={self.id}, user_id={self.user_id}, state={self.state.value})>"

    def can_transition_to(self, new_state: OrderStatus) -> bool:
        """Check if order can transition to a new state."""
        allowed_transitions = {
            OrderStatus.CREATED: {OrderStatus.QUOTED, OrderStatus.FAILED},
            OrderStatus.QUOTED: {OrderStatus.AWAITING_PAYMENT, OrderStatus.FAILED},
            OrderStatus.AWAITING_PAYMENT: {OrderStatus.EXECUTING, OrderStatus.FAILED},
            OrderStatus.EXECUTING: {OrderStatus.SETTLED, OrderStatus.FAILED},
            OrderStatus.SETTLED: set(),
            OrderStatus.FAILED: set(),
        }
        return new_state in allowed_transitions.get(self.state, set())
