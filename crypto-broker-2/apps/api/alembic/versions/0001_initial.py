"""initial schema"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False, unique=True),
        sa.Column("username", sa.String(255)),
        sa.Column("first_name", sa.String(255)),
        sa.Column("last_name", sa.String(255)),
        sa.Column("kyc_status", sa.Enum("pending","approved","rejected","review", name="kyc_status"), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_index("ix_users_telegram_id", "users", ["telegram_id"])

    op.create_table(
        "companies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("status", sa.Enum("pending","approved","suspended", name="company_status"), nullable=False),
    )

    op.create_table(
        "company_members",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("companies.id"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("role", sa.String(50), nullable=False),
    )

    op.create_table(
        "assets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("symbol", sa.String(30), nullable=False, unique=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("decimals", sa.Integer(), nullable=False),
        sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
    )

    op.create_table(
        "networks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("code", sa.String(50), nullable=False, unique=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
    )

    op.create_table(
        "quotes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("status", sa.Enum("active","accepted","expired","cancelled", name="quote_status"), nullable=False),
        sa.Column("sell_asset", sa.String(30), nullable=False),
        sa.Column("buy_asset", sa.String(30), nullable=False),
        sa.Column("sell_amount", sa.Numeric(36,18), nullable=False),
        sa.Column("buy_amount", sa.Numeric(36,18), nullable=False),
        sa.Column("fee_amount", sa.Numeric(36,18), nullable=False),
        sa.Column("provider", sa.String(50), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("quote_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("quotes.id"), nullable=False),
        sa.Column("status", sa.Enum("created","risk_check","awaiting_funds","executing","settling","completed","failed","blocked","cancelled", name="order_status"), nullable=False),
        sa.Column("sell_asset", sa.String(30), nullable=False),
        sa.Column("buy_asset", sa.String(30), nullable=False),
        sa.Column("sell_amount", sa.Numeric(36,18), nullable=False),
        sa.Column("buy_amount", sa.Numeric(36,18), nullable=False),
        sa.Column("provider", sa.String(50), nullable=False),
    )

    op.create_table(
        "ledger_entries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("order_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("orders.id"), nullable=False),
        sa.Column("account", sa.String(100), nullable=False),
        sa.Column("asset", sa.String(30), nullable=False),
        sa.Column("debit", sa.Numeric(36,18), nullable=False, server_default="0"),
        sa.Column("credit", sa.Numeric(36,18), nullable=False, server_default="0"),
        sa.Column("reference", sa.String(255), nullable=False),
    )

def downgrade():
    op.drop_table("ledger_entries")
    op.drop_table("orders")
    op.drop_table("quotes")
    op.drop_table("networks")
    op.drop_table("assets")
    op.drop_table("company_members")
    op.drop_table("companies")
    op.drop_index("ix_users_telegram_id", table_name="users")
    op.drop_table("users")
    for name in ("order_status","quote_status","company_status","kyc_status"):
        sa.Enum(name=name).drop(op.get_bind(), checkfirst=True)
