"""
Vouchers API endpoints (Cash/Bank receipts, payments, journal entries, etc.)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from database.database import get_db
from database.models import Voucher, VoucherItem, VoucherType
from core.security import get_current_user

router = APIRouter()


class VoucherCreate(BaseModel):
    voucher_type: VoucherType
    voucher_no: str
    voucher_date: str
    party_id: Optional[int] = None
    party_name: Optional[str] = None
    total_amount: float = 0.0
    discount_amount: float = 0.0
    tax_amount: float = 0.0
    cgst_amount: float = 0.0
    sgst_amount: float = 0.0
    igst_amount: float = 0.0
    cess_amount: float = 0.0
    round_off: float = 0.0
    net_amount: float = 0.0
    payment_mode: Optional[str] = None
    narration: Optional[str] = None
    items: Optional[List[dict]] = None


class VoucherResponse(BaseModel):
    id: int
    company_id: int
    voucher_type: str
    voucher_no: str
    voucher_date: str
    party_id: Optional[int]
    party_name: Optional[str]
    total_amount: float
    discount_amount: float
    tax_amount: float
    cgst_amount: float
    sgst_amount: float
    igst_amount: float
    cess_amount: float
    round_off: float
    net_amount: float
    payment_mode: Optional[str]
    narration: Optional[str]
    is_posted: bool
    is_cancelled: bool
    
    class Config:
        from_attributes = True


@router.post("", response_model=VoucherResponse)
async def create_voucher(
    voucher: VoucherCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new voucher"""
    company_id = int(current_user.get("company_id", 0))
    user_id = int(current_user.get("user_id", 0))
    
    db_voucher = Voucher(
        company_id=company_id,
        created_by=user_id,
        **voucher.model_dump(exclude={"items"})
    )
    db.add(db_voucher)
    db.commit()
    db.refresh(db_voucher)
    
    # Add items if provided
    if voucher.items:
        for item in voucher.items:
            db_item = VoucherItem(
                voucher_id=db_voucher.id,
                **item
            )
            db.add(db_item)
        db.commit()
    
    return db_voucher


@router.get("", response_model=List[VoucherResponse])
async def list_vouchers(
    voucher_type: Optional[VoucherType] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List vouchers"""
    company_id = int(current_user.get("company_id", 0))
    
    query = db.query(Voucher).filter(Voucher.company_id == company_id)
    
    if voucher_type:
        query = query.filter(Voucher.voucher_type == voucher_type)
    if from_date:
        query = query.filter(Voucher.voucher_date >= from_date)
    if to_date:
        query = query.filter(Voucher.voucher_date <= to_date)
    
    vouchers = query.order_by(Voucher.voucher_date.desc()).offset(skip).limit(limit).all()
    return vouchers


@router.get("/{voucher_id}", response_model=VoucherResponse)
async def get_voucher(
    voucher_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get voucher by ID"""
    voucher = db.query(Voucher).filter(Voucher.id == voucher_id).first()
    if not voucher:
        raise HTTPException(status_code=404, detail="Voucher not found")
    return voucher


@router.delete("/{voucher_id}")
async def delete_voucher(
    voucher_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete voucher"""
    voucher = db.query(Voucher).filter(Voucher.id == voucher_id).first()
    if not voucher:
        raise HTTPException(status_code=404, detail="Voucher not found")
    
    # Delete items
    db.query(VoucherItem).filter(VoucherItem.voucher_id == voucher_id).delete()
    
    # Delete voucher
    db.delete(voucher)
    db.commit()
    return {"message": "Voucher deleted successfully"}
