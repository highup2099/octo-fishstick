import enum
from sqlalchemy import Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base, TimestampMixin

class CompanyStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    suspended = "suspended"

class Company(TimestampMixin, Base):
    __tablename__ = "companies"
    name: Mapped[str] = mapped_column(String(255))
    status: Mapped[CompanyStatus] = mapped_column(Enum(CompanyStatus, name="company_status"), default=CompanyStatus.pending)

class CompanyMember(TimestampMixin, Base):
    __tablename__ = "company_members"
    company_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id"), index=True)
    user_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    role: Mapped[str] = mapped_column(String(50), default="viewer")
