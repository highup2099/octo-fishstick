from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base, TimestampMixin

class Asset(TimestampMixin, Base):
    __tablename__ = "assets"
    symbol: Mapped[str] = mapped_column(String(30), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    decimals: Mapped[int] = mapped_column(default=8)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)

class Network(TimestampMixin, Base):
    __tablename__ = "networks"
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
