"""
Accounts/Ledger API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from database.database import get_db
from database.models import Account, AccountType
from core.security import get_current_user

router = APIRouter()


class AccountCreate(BaseModel):
    account_name: str
    account_code: Optional[str] = None
    account_type: AccountType
    group_name: Optional[str] = None
    opening_balance: float = 0.0
    opening_balance_type: str = "Dr"
    is_system: bool = False


class AccountUpdate(BaseModel):
    account_name: Optional[str] = None
    account_code: Optional[str] = None
    group_name: Optional[str] = None
    opening_balance: Optional[float] = None
    opening_balance_type: Optional[str] = None


class AccountResponse(BaseModel):
    id: int
    company_id: int
    account_name: str
    account_code: Optional[str]
    account_type: str
    group_name: Optional[str]
    opening_balance: float
    opening_balance_type: str
    is_system: bool
    
    class Config:
        from_attributes = True


@router.post("", response_model=AccountResponse)
async def create_account(
    account: AccountCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new ledger account"""
    company_id = int(current_user.get("company_id", 0))
    
    db_account = Account(
        company_id=company_id,
        **account.model_dump()
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    
    return db_account


@router.get("", response_model=List[AccountResponse])
async def list_accounts(
    account_type: Optional[AccountType] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List ledger accounts"""
    company_id = int(current_user.get("company_id", 0))
    
    query = db.query(Account).filter(Account.company_id == company_id)
    if account_type:
        query = query.filter(Account.account_type == account_type)
    
    accounts = query.offset(skip).limit(limit).all()
    return accounts


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get account by ID"""
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@router.put("/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: int,
    account_update: AccountUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update account"""
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    for field, value in account_update.model_dump(exclude_unset=True).items():
        setattr(account, field, value)
    
    db.commit()
    db.refresh(account)
    return account


@router.delete("/{account_id}")
async def delete_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete account"""
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    
    if account.is_system:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete system accounts"
        )
    
    db.delete(account)
    db.commit()
    return {"message": "Account deleted successfully"}
