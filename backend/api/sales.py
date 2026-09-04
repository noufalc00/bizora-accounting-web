"""
Sales API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from database.database import get_db
from database.models import Voucher, VoucherItem, VoucherType
from core.security import get_current_user

router = APIRouter()


class VoucherItemCreate(BaseModel):
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


class SalesCreate(BaseModel):
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
    payment_mode: str  # cash, credit, bank
    narration: Optional[str] = None
    items: List[VoucherItemCreate]


class SalesResponse(BaseModel):
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


@router.post("", response_model=SalesResponse)
async def create_sales(
    sales: SalesCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new sales voucher"""
    company_id = int(current_user.get("company_id", 0))
    user_id = int(current_user.get("user_id", 0))
    
    db_sales = Voucher(
        company_id=company_id,
        voucher_type=VoucherType.SALES,
        created_by=user_id,
        **sales.model_dump(exclude={"items"})
    )
    db.add(db_sales)
    db.commit()
    db.refresh(db_sales)
    
    # Add items
    for item in sales.items:
        db_item = VoucherItem(
            voucher_id=db_sales.id,
            **item.model_dump()
        )
        db.add(db_item)
    
    db.commit()
    db.refresh(db_sales)
    
    return db_sales


@router.get("", response_model=List[SalesResponse])
async def list_sales(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    party_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List sales vouchers"""
    company_id = int(current_user.get("company_id", 0))
    
    query = db.query(Voucher).filter(
        Voucher.company_id == company_id,
        Voucher.voucher_type == VoucherType.SALES
    )
    
    if from_date:
        query = query.filter(Voucher.voucher_date >= from_date)
    if to_date:
        query = query.filter(Voucher.voucher_date <= to_date)
    if party_id:
        query = query.filter(Voucher.party_id == party_id)
    
    sales = query.order_by(Voucher.voucher_date.desc()).offset(skip).limit(limit).all()
    return sales


@router.get("/{sales_id}", response_model=SalesResponse)
async def get_sales(
    sales_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get sales voucher by ID"""
    sales = db.query(Voucher).filter(
        Voucher.id == sales_id,
        Voucher.voucher_type == VoucherType.SALES
    ).first()
    if not sales:
        raise HTTPException(status_code=404, detail="Sales voucher not found")
    return sales


@router.put("/{sales_id}", response_model=SalesResponse)
async def update_sales(
    sales_id: int,
    sales_update: SalesCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update sales voucher"""
    sales = db.query(Voucher).filter(
        Voucher.id == sales_id,
        Voucher.voucher_type == VoucherType.SALES
    ).first()
    if not sales:
        raise HTTPException(status_code=404, detail="Sales voucher not found")
    
    # Update voucher fields
    for field, value in sales_update.model_dump(exclude={"items"}).items():
        setattr(sales, field, value)
    
    # Delete existing items
    db.query(VoucherItem).filter(VoucherItem.voucher_id == sales_id).delete()
    
    # Add new items
    for item in sales_update.items:
        db_item = VoucherItem(
            voucher_id=sales.id,
            **item.model_dump()
        )
        db.add(db_item)
    
    db.commit()
    db.refresh(sales)
    return sales


@router.delete("/{sales_id}")
async def delete_sales(
    sales_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete sales voucher"""
    sales = db.query(Voucher).filter(
        Voucher.id == sales_id,
        Voucher.voucher_type == VoucherType.SALES
    ).first()
    if not sales:
        raise HTTPException(status_code=404, detail="Sales voucher not found")
    
    # Delete items
    db.query(VoucherItem).filter(VoucherItem.voucher_id == sales_id).delete()
    
    # Delete voucher
    db.delete(sales)
    db.commit()
    return {"message": "Sales voucher deleted successfully"}
