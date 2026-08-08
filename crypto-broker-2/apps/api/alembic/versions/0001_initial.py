"""Initial migration - create all tables

Revision ID: 0001_initial
Revises: 
Create Date: 2025-01-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create networks table first (referenced by assets)
    op.create_table(
        'networks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('symbol')
    )

    # Create assets table
    op.create_table(
        'assets',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('symbol', sa.String(length=20), nullable=False),
        sa.Column('decimals', sa.Integer(), nullable=False, default=8),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('symbol')
    )

    # Create asset_networks junction table
    op.create_table(
        'asset_networks',
        sa.Column('asset_id', sa.Integer(), nullable=False),
        sa.Column('network_id', sa.Integer(), nullable=False),
        sa.Column('contract_address', sa.String(length=42), nullable=True),
        sa.Column('is_primary', sa.Boolean(), nullable=False, default=False),
        sa.PrimaryKeyConstraint('asset_id', 'network_id'),
        sa.ForeignKeyConstraint(['asset_id'], ['assets.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['network_id'], ['networks.id'], ondelete='CASCADE')
    )

    # Create companies table
    op.create_table(
        'companies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('legal_name', sa.String(length=255), nullable=True),
        sa.Column('tax_id', sa.String(length=50), nullable=True),
        sa.Column('kyc_status', sa.Enum('PENDING', 'APPROVED', 'REJECTED', name='kycstatus'), nullable=False, default='PENDING'),
        sa.Column('risk_tier', sa.Enum('LOW', 'MEDIUM', 'HIGH', name='risktier'), nullable=False, default='LOW'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('telegram_id', sa.BigInteger(), nullable=True),
        sa.Column('username', sa.String(length=100), nullable=True),
        sa.Column('first_name', sa.String(length=100), nullable=True),
        sa.Column('last_name', sa.String(length=100), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('company_id', sa.Integer(), nullable=True),
        sa.Column('kyc_status', sa.Enum('PENDING', 'APPROVED', 'REJECTED', name='kycstatus'), nullable=False, default='PENDING'),
        sa.Column('risk_tier', sa.Enum('LOW', 'MEDIUM', 'HIGH', name='risktier'), nullable=False, default='LOW'),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('telegram_id'),
        sa.UniqueConstraint('email'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='SET NULL')
    )

    # Create company_members table
    op.create_table(
        'company_members',
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.Enum('OWNER', 'ADMIN', 'MEMBER', name='companyrole'), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('company_id', 'user_id'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )

    # Create orders table
    op.create_table(
        'orders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('state', sa.Enum('CREATED', 'QUOTED', 'AWAITING_PAYMENT', 'EXECUTING', 'SETTLED', 'FAILED', name='orderstatus'), nullable=False, default='CREATED'),
        sa.Column('provider', sa.String(length=50), nullable=True),
        sa.Column('asset_in_symbol', sa.String(length=20), nullable=False),
        sa.Column('asset_out_symbol', sa.String(length=20), nullable=False),
        sa.Column('amount_in', sa.Numeric(precision=36, scale=18), nullable=False),
        sa.Column('amount_out', sa.Numeric(precision=36, scale=18), nullable=True),
        sa.Column('fee_amount', sa.Numeric(precision=36, scale=18), nullable=True),
        sa.Column('fee_currency', sa.String(length=20), nullable=True),
        sa.Column('external_order_id', sa.String(length=255), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('settled_at', sa.TIMESTAMP(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )

    # Create ledger_entries table
    op.create_table(
        'ledger_entries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('asset_symbol', sa.String(length=20), nullable=False),
        sa.Column('network_symbol', sa.String(length=20), nullable=False),
        sa.Column('amount', sa.Numeric(precision=36, scale=18), nullable=False),
        sa.Column('entry_type', sa.Enum('DEPOSIT', 'EXCHANGE', 'FEE', 'WITHDRAWAL', name='ledgerentrytype'), nullable=False),
        sa.Column('reference_type', sa.String(length=50), nullable=True),
        sa.Column('reference_id', sa.Integer(), nullable=True),
        sa.Column('balance_after', sa.Numeric(precision=36, scale=18), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE')
    )

    # Create indexes
    op.create_index('ix_orders_user_id', 'orders', ['user_id'])
    op.create_index('ix_orders_state', 'orders', ['state'])
    op.create_index('ix_orders_created_at', 'orders', ['created_at'])
    
    op.create_index('ix_ledger_entries_user_id', 'ledger_entries', ['user_id'])
    op.create_index('ix_ledger_entries_reference', 'ledger_entries', ['reference_type', 'reference_id'])
    op.create_index('ix_ledger_entries_created_at', 'ledger_entries', ['created_at'])
    
    op.create_index('ix_users_telegram_id', 'users', ['telegram_id'])
    op.create_index('ix_users_company_id', 'users', ['company_id'])


def downgrade() -> None:
    op.drop_index('ix_users_company_id', table_name='users')
    op.drop_index('ix_users_telegram_id', table_name='users')
    
    op.drop_index('ix_ledger_entries_created_at', table_name='ledger_entries')
    op.drop_index('ix_ledger_entries_reference', table_name='ledger_entries')
    op.drop_index('ix_ledger_entries_user_id', table_name='ledger_entries')
    
    op.drop_index('ix_orders_created_at', table_name='orders')
    op.drop_index('ix_orders_state', table_name='orders')
    op.drop_index('ix_orders_user_id', table_name='orders')
    
    op.drop_table('ledger_entries')
    op.drop_table('orders')
    op.drop_table('company_members')
    op.drop_table('users')
    op.drop_table('companies')
    op.drop_table('asset_networks')
    op.drop_table('assets')
    op.drop_table('networks')
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
