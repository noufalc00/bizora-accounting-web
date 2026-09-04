"""
Reports API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

from database.database import get_db
from database.models import Voucher, LedgerEntry, Account, Party, Product, VoucherType
from core.security import get_current_user

router = APIRouter()


class TrialBalanceItem(BaseModel):
    account_name: str
    account_type: str
    debit_total: float
    credit_total: float
    balance: float
    balance_type: str


class TrialBalanceResponse(BaseModel):
    from_date: str
    to_date: str
    total_debit: float
    total_credit: float
    accounts: List[TrialBalanceItem]


class ProfitLossItem(BaseModel):
    account_name: str
    amount: float
    type: str  # income or expense


class ProfitLossResponse(BaseModel):
    from_date: str
    to_date: str
    total_income: float
    total_expense: float
    net_profit: float
    items: List[ProfitLossItem]


class BalanceSheetItem(BaseModel):
    account_name: str
    amount: float
    type: str  # asset or liability


class BalanceSheetResponse(BaseModel):
    as_on_date: str
    total_assets: float
    total_liabilities: float
    items: List[BalanceSheetItem]


@router.get("/trial-balance", response_model=TrialBalanceResponse)
async def get_trial_balance(
    from_date: str,
    to_date: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Generate Trial Balance report"""
    company_id = int(current_user.get("company_id", 0))
    
    # Get all accounts for company
    accounts = db.query(Account).filter(Account.company_id == company_id).all()
    
    items = []
    total_debit = 0.0
    total_credit = 0.0
    
    for account in accounts:
        # Calculate debit total for this account
        debit_result = db.query(LedgerEntry).filter(
            LedgerEntry.company_id == company_id,
            LedgerEntry.debit_account_id == account.id,
            LedgerEntry.voucher_date >= from_date,
            LedgerEntry.voucher_date <= to_date
        ).all()
        
        debit_total = sum(entry.debit_amount for entry in debit_result)
        
        # Calculate credit total for this account
        credit_result = db.query(LedgerEntry).filter(
            LedgerEntry.company_id == company_id,
            LedgerEntry.credit_account_id == account.id,
            LedgerEntry.voucher_date >= from_date,
            LedgerEntry.voucher_date <= to_date
        ).all()
        
        credit_total = sum(entry.credit_amount for entry in credit_result)
        
        # Add opening balance
        opening_balance = account.opening_balance
        if account.opening_balance_type == "Dr":
            debit_total += opening_balance
        else:
            credit_total += opening_balance
        
        balance = abs(debit_total - credit_total)
        balance_type = "Dr" if debit_total > credit_total else "Cr"
        
        if balance > 0:
            items.append(TrialBalanceItem(
                account_name=account.account_name,
                account_type=account.account_type.value,
                debit_total=debit_total,
                credit_total=credit_total,
                balance=balance,
                balance_type=balance_type
            ))
            
            total_debit += debit_total
            total_credit += credit_total
    
    return TrialBalanceResponse(
        from_date=from_date,
        to_date=to_date,
        total_debit=total_debit,
        total_credit=total_credit,
        accounts=items
    )


@router.get("/profit-loss", response_model=ProfitLossResponse)
async def get_profit_loss(
    from_date: str,
    to_date: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Generate Profit & Loss report"""
    company_id = int(current_user.get("company_id", 0))
    
    # Get income accounts
    income_accounts = db.query(Account).filter(
        Account.company_id == company_id,
        Account.account_type == "income"
    ).all()
    
    # Get expense accounts
    expense_accounts = db.query(Account).filter(
        Account.company_id == company_id,
        Account.account_type == "expense"
    ).all()
    
    items = []
    total_income = 0.0
    total_expense = 0.0
    
    for account in income_accounts:
        # Calculate income
        credit_result = db.query(LedgerEntry).filter(
            LedgerEntry.company_id == company_id,
            LedgerEntry.credit_account_id == account.id,
            LedgerEntry.voucher_date >= from_date,
            LedgerEntry.voucher_date <= to_date
        ).all()
        
        amount = sum(entry.credit_amount for entry in credit_result)
        if amount > 0:
            items.append(ProfitLossItem(
                account_name=account.account_name,
                amount=amount,
                type="income"
            ))
            total_income += amount
    
    for account in expense_accounts:
        # Calculate expense
        debit_result = db.query(LedgerEntry).filter(
            LedgerEntry.company_id == company_id,
            LedgerEntry.debit_account_id == account.id,
            LedgerEntry.voucher_date >= from_date,
            LedgerEntry.voucher_date <= to_date
        ).all()
        
        amount = sum(entry.debit_amount for entry in debit_result)
        if amount > 0:
            items.append(ProfitLossItem(
                account_name=account.account_name,
                amount=amount,
                type="expense"
            ))
            total_expense += amount
    
    net_profit = total_income - total_expense
    
    return ProfitLossResponse(
        from_date=from_date,
        to_date=to_date,
        total_income=total_income,
        total_expense=total_expense,
        net_profit=net_profit,
        items=items
    )


@router.get("/balance-sheet", response_model=BalanceSheetResponse)
async def get_balance_sheet(
    as_on_date: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Generate Balance Sheet report"""
    company_id = int(current_user.get("company_id", 0))
    
    # Get asset accounts (cash_bank, party, stock)
    asset_accounts = db.query(Account).filter(
        Account.company_id == company_id,
        Account.account_type.in_(["cash_bank", "party", "stock"])
    ).all()
    
    # Get liability accounts (party, tax_liability, capital)
    liability_accounts = db.query(Account).filter(
        Account.company_id == company_id,
        Account.account_type.in_(["party", "tax_liability", "capital"])
    ).all()
    
    items = []
    total_assets = 0.0
    total_liabilities = 0.0
    
    for account in asset_accounts:
        # Calculate asset balance
        debit_result = db.query(LedgerEntry).filter(
            LedgerEntry.company_id == company_id,
            LedgerEntry.debit_account_id == account.id,
            LedgerEntry.voucher_date <= as_on_date
        ).all()
        
        credit_result = db.query(LedgerEntry).filter(
            LedgerEntry.company_id == company_id,
            LedgerEntry.credit_account_id == account.id,
            LedgerEntry.voucher_date <= as_on_date
        ).all()
        
        debit_total = sum(entry.debit_amount for entry in debit_result)
        credit_total = sum(entry.credit_amount for entry in credit_result)
        
        opening_balance = account.opening_balance
        if account.opening_balance_type == "Dr":
            debit_total += opening_balance
        else:
            credit_total += opening_balance
        
        balance = debit_total - credit_total
        if balance > 0:
            items.append(BalanceSheetItem(
                account_name=account.account_name,
                amount=balance,
                type="asset"
            ))
            total_assets += balance
    
    for account in liability_accounts:
        # Calculate liability balance
        debit_result = db.query(LedgerEntry).filter(
            LedgerEntry.company_id == company_id,
            LedgerEntry.debit_account_id == account.id,
            LedgerEntry.voucher_date <= as_on_date
        ).all()
        
        credit_result = db.query(LedgerEntry).filter(
            LedgerEntry.company_id == company_id,
            LedgerEntry.credit_account_id == account.id,
            LedgerEntry.voucher_date <= as_on_date
        ).all()
        
        debit_total = sum(entry.debit_amount for entry in debit_result)
        credit_total = sum(entry.credit_amount for entry in credit_result)
        
        opening_balance = account.opening_balance
        if account.opening_balance_type == "Dr":
            debit_total += opening_balance
        else:
            credit_total += opening_balance
        
        balance = credit_total - debit_total
        if balance > 0:
            items.append(BalanceSheetItem(
                account_name=account.account_name,
                amount=balance,
                type="liability"
            ))
            total_liabilities += balance
    
    return BalanceSheetResponse(
        as_on_date=as_on_date,
        total_assets=total_assets,
        total_liabilities=total_liabilities,
        items=items
    )


@router.get("/day-book")
async def get_day_book(
    from_date: str,
    to_date: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Generate Day Book report"""
    company_id = int(current_user.get("company_id", 0))
    
    vouchers = db.query(Voucher).filter(
        Voucher.company_id == company_id,
        Voucher.voucher_date >= from_date,
        Voucher.voucher_date <= to_date,
        Voucher.voucher_type != VoucherType.QUOTATION
    ).order_by(Voucher.voucher_date).all()
    
    return {
        "from_date": from_date,
        "to_date": to_date,
        "vouchers": [
            {
                "id": v.id,
                "voucher_type": v.voucher_type.value,
                "voucher_no": v.voucher_no,
                "voucher_date": v.date,
                "party_name": v.party_name,
                "net_amount": v.net_amount,
                "payment_mode": v.payment_mode
            }
            for v in vouchers
        ]
    }
