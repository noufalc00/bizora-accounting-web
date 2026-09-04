"""
Products API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from database.database import get_db
from database.models import Product
from core.security import get_current_user

router = APIRouter()


class ProductCreate(BaseModel):
    name: str
    code: Optional[str] = None
    category: Optional[str] = None
    unit: Optional[str] = None
    purchase_price: float = 0.0
    sale_price: float = 0.0
    gst_rate: float = 0.0
    cess_rate: float = 0.0
    hsn_code: Optional[str] = None
    stock_quantity: float = 0.0
    minimum_stock: float = 0.0


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    category: Optional[str] = None
    unit: Optional[str] = None
    purchase_price: Optional[float] = None
    sale_price: Optional[float] = None
    gst_rate: Optional[float] = None
    cess_rate: Optional[float] = None
    hsn_code: Optional[str] = None
    stock_quantity: Optional[float] = None
    minimum_stock: Optional[float] = None
    is_active: Optional[bool] = None


class ProductResponse(BaseModel):
    id: int
    company_id: int
    name: str
    code: Optional[str]
    category: Optional[str]
    unit: Optional[str]
    purchase_price: float
    sale_price: float
    gst_rate: float
    cess_rate: float
    hsn_code: Optional[str]
    stock_quantity: float
    minimum_stock: float
    is_active: bool
    
    class Config:
        from_attributes = True


@router.post("", response_model=ProductResponse)
async def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new product"""
    company_id = int(current_user.get("company_id", 0))
    
    db_product = Product(
        company_id=company_id,
        **product.model_dump()
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    return db_product


@router.get("", response_model=List[ProductResponse])
async def list_products(
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List products"""
    company_id = int(current_user.get("company_id", 0))
    
    query = db.query(Product).filter(Product.company_id == company_id)
    if category:
        query = query.filter(Product.category == category)
    
    products = query.offset(skip).limit(limit).all()
    return products


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get product by ID"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update product"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    for field, value in product_update.model_dump(exclude_unset=True).items():
        setattr(product, field, value)
    
    db.commit()
    db.refresh(product)
    return product


@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete product"""
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    db.delete(product)
    db.commit()
    return {"message": "Product deleted successfully"}
