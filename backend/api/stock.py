"""
Stock API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from database.database import get_db
from database.models import StockMovement, Product
from core.security import get_current_user

router = APIRouter()


class StockMovementCreate(BaseModel):
    product_id: int
    movement_type: str  # in, out, adjustment
    quantity: float
    rate: float = 0.0
    reference_type: Optional[str] = None
    reference_no: Optional[str] = None
    movement_date: str
    narration: Optional[str] = None


class StockMovementResponse(BaseModel):
    id: int
    company_id: int
    product_id: int
    movement_type: str
    quantity: float
    rate: float
    reference_type: Optional[str]
    reference_no: Optional[str]
    movement_date: str
    narration: Optional[str]
    
    class Config:
        from_attributes = True


class StockReportItem(BaseModel):
    product_id: int
    product_name: str
    category: Optional[str]
    current_stock: float
    purchase_price: float
    sale_price: float
    stock_value: float


@router.post("/movements", response_model=StockMovementResponse)
async def create_stock_movement(
    movement: StockMovementCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a stock movement"""
    company_id = int(current_user.get("company_id", 0))
    
    # Verify product exists
    product = db.query(Product).filter(Product.id == movement.product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    # Create movement
    db_movement = StockMovement(
        company_id=company_id,
        **movement.model_dump()
    )
    db.add(db_movement)
    
    # Update product stock
    if movement.movement_type == "in":
        product.stock_quantity += movement.quantity
    elif movement.movement_type == "out":
        product.stock_quantity -= movement.quantity
    elif movement.movement_type == "adjustment":
        product.stock_quantity = movement.quantity
    
    db.commit()
    db.refresh(db_movement)
    
    return db_movement


@router.get("/movements", response_model=List[StockMovementResponse])
async def list_stock_movements(
    product_id: Optional[int] = None,
    movement_type: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List stock movements"""
    company_id = int(current_user.get("company_id", 0))
    
    query = db.query(StockMovement).filter(StockMovement.company_id == company_id)
    
    if product_id:
        query = query.filter(StockMovement.product_id == product_id)
    if movement_type:
        query = query.filter(StockMovement.movement_type == movement_type)
    if from_date:
        query = query.filter(StockMovement.movement_date >= from_date)
    if to_date:
        query = query.filter(StockMovement.movement_date <= to_date)
    
    movements = query.order_by(StockMovement.movement_date.desc()).offset(skip).limit(limit).all()
    return movements


@router.get("/report", response_model=List[StockReportItem])
async def get_stock_report(
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Generate stock report"""
    company_id = int(current_user.get("company_id", 0))
    
    query = db.query(Product).filter(Product.company_id == company_id, Product.is_active == True)
    
    if category:
        query = query.filter(Product.category == category)
    
    products = query.all()
    
    items = []
    for product in products:
        stock_value = product.stock_quantity * product.purchase_price
        items.append(StockReportItem(
            product_id=product.id,
            product_name=product.name,
            category=product.category,
            current_stock=product.stock_quantity,
            purchase_price=product.purchase_price,
            sale_price=product.sale_price,
            stock_value=stock_value
        ))
    
    return items


@router.get("/low-stock")
async def get_low_stock(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get products with low stock"""
    company_id = int(current_user.get("company_id", 0))
    
    products = db.query(Product).filter(
        Product.company_id == company_id,
        Product.stock_quantity <= Product.minimum_stock,
        Product.is_active == True
    ).all()
    
    return [
        {
            "product_id": p.id,
            "product_name": p.name,
            "current_stock": p.stock_quantity,
            "minimum_stock": p.minimum_stock
        }
        for p in products
    ]
