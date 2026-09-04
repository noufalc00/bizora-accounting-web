"""
Purchases API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from database.database import get_db
from database.models import Voucher, VoucherItem, VoucherType
from core.security import get_current_user

router = APIRouter()


class PurchaseItemCreate(BaseModel):
    product_id: Optional[int] = None
    product_name: str
    quantity: float
    unit: Optional[str] = None
    rate: float
    amount: float
    discount_percent: float = 0.0
    discount_amount: float = 0.0
    gst_rate: float = 0.0
    cess_rate: float = 0.0
    cgst_amount: float = 0.0
    sgst_amount: float = 0.0
    igst_amount: float = 0.0
    cess_amount: float = 0.0
    net_amount: float


class PurchaseCreate(BaseModel):
    voucher_no: str
    voucher_date: str
    party_id: Optional[int] = None
    party_name: str
    total_amount: float
    discount_amount: float = 0.0
    tax_amount: float = 0.0
    cgst_amount: float = 0.0
    sgst_amount: float = 0.0
    igst_amount: float = 0.0
    cess_amount: float = 0.0
    round_off: float = 0.0
    net_amount: float
    payment_mode: str
    narration: Optional[str] = None
    items: List[PurchaseItemCreate]


class PurchaseResponse(BaseModel):
    id: int
    company_id: int
    voucher_type: str
    voucher_no: str
    voucher_date: str
    party_id: Optional[int]
    party_name: str
    total_amount: float
    discount_amount: float
    tax_amount: float
    cgst_amount: float
    sgst_amount: float
    igst_amount: float
    cess_amount: float
    round_off: float
    net_amount: float
    payment_mode: str
    narration: Optional[str]
    is_posted: bool
    is_cancelled: bool
    
    class Config:
        from_attributes = True


@router.post("", response_model=PurchaseResponse)
async def create_purchase(
    purchase: PurchaseCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new purchase voucher"""
    company_id = int(current_user.get("company_id", 0))
    user_id = int(current_user.get("user_id", 0))
    
    db_purchase = Voucher(
        company_id=company_id,
        voucher_type=VoucherType.PURCHASE,
        created_by=user_id,
        **purchase.model_dump(exclude={"items"})
    )
    db.add(db_purchase)
    db.commit()
    db.refresh(db_purchase)
    
    # Add items
    for item in purchase.items:
        db_item = VoucherItem(
            voucher_id=db_purchase.id,
            **item.model_dump()
        )
        db.add(db_item)
    
    db.commit()
    db.refresh(db_purchase)
    
    return db_purchase


@router.get("", response_model=List[PurchaseResponse])
async def list_purchases(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    party_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List purchase vouchers"""
    company_id = int(current_user.get("company_id", 0))
    
    query = db.query(Voucher).filter(
        Voucher.company_id == company_id,
        Voucher.voucher_type == VoucherType.PURCHASE
    )
    
    if from_date:
        query = query.filter(Voucher.voucher_date >= from_date)
    if to_date:
        query = query.filter(Voucher.voucher_date <= to_date)
    if party_id:
        query = query.filter(Voucher.party_id == party_id)
    
    purchases = query.order_by(Voucher.voucher_date.desc()).offset(skip).limit(limit).all()
    return purchases


@router.get("/{purchase_id}", response_model=PurchaseResponse)
async def get_purchase(
    purchase_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get purchase voucher by ID"""
    purchase = db.query(Voucher).filter(
        Voucher.id == purchase_id,
        Voucher.voucher_type == VoucherType.PURCHASE
    ).first()
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase voucher not found")
    return purchase


@router.put("/{purchase_id}", response_model=PurchaseResponse)
async def update_purchase(
    purchase_id: int,
    purchase_update: PurchaseCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update purchase voucher"""
    purchase = db.query(Voucher).filter(
        Voucher.id == purchase_id,
        Voucher.voucher_type == VoucherType.PURCHASE
    ).first()
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase voucher not found")
    
    # Update voucher fields
    for field, value in purchase_update.model_dump(exclude={"items"}).items():
        setattr(purchase, field, value)
    
    # Delete existing items
    db.query(VoucherItem).filter(VoucherItem.voucher_id == purchase_id).delete()
    
    # Add new items
    for item in purchase_update.items:
        db_item = VoucherItem(
            voucher_id=purchase.id,
            **item.model_dump()
        )
        db.add(db_item)
    
    db.commit()
    db.refresh(purchase)
    return purchase


@router.delete("/{purchase_id}")
async def delete_purchase(
    purchase_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete purchase voucher"""
    purchase = db.query(Voucher).filter(
        Voucher.id == purchase_id,
        Voucher.voucher_type == VoucherType.PURCHASE
    ).first()
    if not purchase:
        raise HTTPException(status_code=404, detail="Purchase voucher not found")
    
    # Delete items
    db.query(VoucherItem).filter(VoucherItem.voucher_id == purchase_id).delete()
    
    # Delete voucher
    db.delete(purchase)
    db.commit()
    return {"message": "Purchase voucher deleted successfully"}
