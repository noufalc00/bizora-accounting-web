"""
Parties (Debtors/Creditors) API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from database.database import get_db
from database.models import Party
from core.security import get_current_user

router = APIRouter()


class PartyCreate(BaseModel):
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    gstin: Optional[str] = None
    party_type: str  # debtor, creditor
    opening_balance: float = 0.0
    credit_limit: float = 0.0


class PartyUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    gstin: Optional[str] = None
    party_type: Optional[str] = None
    opening_balance: Optional[float] = None
    credit_limit: Optional[float] = None
    is_active: Optional[bool] = None


class PartyResponse(BaseModel):
    id: int
    company_id: int
    name: str
    phone: Optional[str]
    email: Optional[str]
    address: Optional[str]
    gstin: Optional[str]
    party_type: str
    opening_balance: float
    credit_limit: float
    is_active: bool
    
    class Config:
        from_attributes = True


@router.post("", response_model=PartyResponse)
async def create_party(
    party: PartyCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new party"""
    company_id = int(current_user.get("company_id", 0))
    
    db_party = Party(
        company_id=company_id,
        **party.model_dump()
    )
    db.add(db_party)
    db.commit()
    db.refresh(db_party)
    
    return db_party


@router.get("", response_model=List[PartyResponse])
async def list_parties(
    party_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List parties"""
    company_id = int(current_user.get("company_id", 0))
    
    query = db.query(Party).filter(Party.company_id == company_id)
    if party_type:
        query = query.filter(Party.party_type == party_type)
    
    parties = query.offset(skip).limit(limit).all()
    return parties


@router.get("/{party_id}", response_model=PartyResponse)
async def get_party(
    party_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get party by ID"""
    party = db.query(Party).filter(Party.id == party_id).first()
    if not party:
        raise HTTPException(status_code=404, detail="Party not found")
    return party


@router.put("/{party_id}", response_model=PartyResponse)
async def update_party(
    party_id: int,
    party_update: PartyUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update party"""
    party = db.query(Party).filter(Party.id == party_id).first()
    if not party:
        raise HTTPException(status_code=404, detail="Party not found")
    
    for field, value in party_update.model_dump(exclude_unset=True).items():
        setattr(party, field, value)
    
    db.commit()
    db.refresh(party)
    return party


@router.delete("/{party_id}")
async def delete_party(
    party_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete party"""
    party = db.query(Party).filter(Party.id == party_id).first()
    if not party:
        raise HTTPException(status_code=404, detail="Party not found")
    
    db.delete(party)
    db.commit()
    return {"message": "Party deleted successfully"}
