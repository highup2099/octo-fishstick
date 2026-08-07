import enum
from sqlalchemy import BigInteger, Enum, String
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base, TimestampMixin

class KYCStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    review = "review"

class User(TimestampMixin, Base):
    __tablename__ = "users"
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(255))
    first_name: Mapped[str | None] = mapped_column(String(255))
    last_name: Mapped[str | None] = mapped_column(String(255))
    kyc_status: Mapped[KYCStatus] = mapped_column(Enum(KYCStatus, name="kyc_status"), default=KYCStatus.pending)
    is_active: Mapped[bool] = mapped_column(default=True)
