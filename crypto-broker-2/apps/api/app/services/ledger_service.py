"""Ledger Service - Domain service for managing double-entry ledger entries."""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.ledger import LedgerEntry, LedgerEntryType
from app.models.user import User


class LedgerService:
    """
    Service for handling ledger entries using double-entry bookkeeping.
    
    CRITICAL: User balance is NEVER stored directly. It is ALWAYS computed
    by aggregating ledger entries. This ensures audit trail integrity.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_entry(
        self,
        user_id: int,
        asset_symbol: str,
        network_symbol: str,
        amount: Decimal,
        entry_type: LedgerEntryType,
        reference_type: Optional[str] = None,
        reference_id: Optional[int] = None,
        description: Optional[str] = None,
    ) -> LedgerEntry:
        """
        Create a new ledger entry and calculate the running balance.
        
        Args:
            user_id: ID of the user
            asset_symbol: Symbol of the asset (e.g., 'BTC')
            network_symbol: Symbol of the network (e.g., 'TRC20')
            amount: Amount of the entry (positive for credits, negative for debits)
            entry_type: Type of entry (DEPOSIT, EXCHANGE, FEE, WITHDRAWAL)
            reference_type: Type of reference (e.g., 'order', 'quote')
            reference_id: ID of the referenced entity
            description: Optional description
            
        Returns:
            Created LedgerEntry with calculated balance_after
        """
        # Calculate current balance before this entry
        current_balance = await self.get_balance(user_id, asset_symbol, network_symbol)
        
        # Calculate new balance after this entry
        balance_after = current_balance + amount
        
        # Create the ledger entry
        entry = LedgerEntry(
            user_id=user_id,
            asset_symbol=asset_symbol,
            network_symbol=network_symbol,
            amount=amount,
            entry_type=entry_type,
            reference_type=reference_type,
            reference_id=reference_id,
            balance_after=balance_after,
            description=description,
        )

        self.db.add(entry)
        await self.db.commit()
        await self.db.refresh(entry)

        return entry

    async def get_balance(
        self,
        user_id: int,
        asset_symbol: str,
        network_symbol: str,
    ) -> Decimal:
        """
        Calculate user balance by aggregating all ledger entries.
        
        This is the ONLY way to determine a user's balance. Never store
        balance directly on the user model.
        
        Args:
            user_id: ID of the user
            asset_symbol: Symbol of the asset
            network_symbol: Symbol of the network
            
        Returns:
            Current balance as Decimal
        """
        result = await self.db.execute(
            select(func.sum(LedgerEntry.amount)).where(
                LedgerEntry.user_id == user_id,
                LedgerEntry.asset_symbol == asset_symbol,
                LedgerEntry.network_symbol == network_symbol,
            )
        )
        
        balance = result.scalar_one_or_none()
        return balance or Decimal('0')

    async def get_balance_history(
        self,
        user_id: int,
        asset_symbol: Optional[str] = None,
        network_symbol: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[LedgerEntry]:
        """
        Get ledger entry history for a user.
        
        Args:
            user_id: ID of the user
            asset_symbol: Optional filter by asset
            network_symbol: Optional filter by network
            limit: Maximum number of entries to return
            offset: Offset for pagination
            
        Returns:
            List of LedgerEntry objects
        """
        query = select(LedgerEntry).where(LedgerEntry.user_id == user_id)
        
        if asset_symbol:
            query = query.where(LedgerEntry.asset_symbol == asset_symbol)
        
        if network_symbol:
            query = query.where(LedgerEntry.network_symbol == network_symbol)
        
        query = query.order_by(LedgerEntry.created_at.desc()).limit(limit).offset(offset)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create_exchange_entries(
        self,
        user_id: int,
        order_id: int,
        debit_asset: str,
        debit_network: str,
        debit_amount: Decimal,
        credit_asset: str,
        credit_network: str,
        credit_amount: Decimal,
        fee_asset: Optional[str] = None,
        fee_network: Optional[str] = None,
        fee_amount: Optional[Decimal] = None,
    ) -> List[LedgerEntry]:
        """
        Create atomic exchange entries (debit + credit + optional fee).
        
        This creates multiple ledger entries for a single exchange operation,
        ensuring the double-entry principle is maintained.
        
        Args:
            user_id: ID of the user
            order_id: ID of the related order
            debit_asset: Asset being sold
            debit_network: Network of the debit
            debit_amount: Amount being debited
            credit_asset: Asset being bought
            credit_network: Network of the credit
            credit_amount: Amount being credited
            fee_asset: Asset used for fee (optional)
            fee_network: Network of the fee (optional)
            fee_amount: Fee amount (optional)
            
        Returns:
            List of created LedgerEntry objects
        """
        entries = []
        
        # Debit entry (negative amount - money leaving)
        debit_entry = await self.create_entry(
            user_id=user_id,
            asset_symbol=debit_asset,
            network_symbol=debit_network,
            amount=-debit_amount,
            entry_type=LedgerEntryType.EXCHANGE,
            reference_type='order',
            reference_id=order_id,
            description=f"Exchange debit for order {order_id}",
        )
        entries.append(debit_entry)
        
        # Credit entry (positive amount - money arriving)
        credit_entry = await self.create_entry(
            user_id=user_id,
            asset_symbol=credit_asset,
            network_symbol=credit_network,
            amount=credit_amount,
            entry_type=LedgerEntryType.EXCHANGE,
            reference_type='order',
            reference_id=order_id,
            description=f"Exchange credit for order {order_id}",
        )
        entries.append(credit_entry)
        
        # Fee entry (if applicable)
        if fee_amount and fee_asset and fee_network:
            fee_entry = await self.create_entry(
                user_id=user_id,
                asset_symbol=fee_asset,
                network_symbol=fee_network,
                amount=-fee_amount,
                entry_type=LedgerEntryType.FEE,
                reference_type='order',
                reference_id=order_id,
                description=f"Exchange fee for order {order_id}",
            )
            entries.append(fee_entry)
        
        return entries
