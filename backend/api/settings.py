"""
Settings API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from database.database import get_db
from database.models import Setting
from core.security import get_current_user

router = APIRouter()


class SettingCreate(BaseModel):
    setting_key: str
    setting_value: str


class SettingUpdate(BaseModel):
    setting_value: str


class SettingResponse(BaseModel):
    id: int
    company_id: Optional[int]
    setting_key: str
    setting_value: str
    
    class Config:
        from_attributes = True


@router.post("", response_model=SettingResponse)
async def create_setting(
    setting: SettingCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new setting"""
    company_id = int(current_user.get("company_id", 0))
    
    # Check if setting already exists
    existing = db.query(Setting).filter(
        Setting.company_id == company_id,
        Setting.setting_key == setting.setting_key
    ).first()
    
    if existing:
        # Update existing
        existing.setting_value = setting.setting_value
        db.commit()
        db.refresh(existing)
        return existing
    
    # Create new
    db_setting = Setting(
        company_id=company_id,
        **setting.model_dump()
    )
    db.add(db_setting)
    db.commit()
    db.refresh(db_setting)
    
    return db_setting


@router.get("", response_model=List[SettingResponse])
async def list_settings(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List all settings for company"""
    company_id = int(current_user.get("company_id", 0))
    
    settings = db.query(Setting).filter(Setting.company_id == company_id).all()
    return settings


@router.get("/{setting_key}", response_model=SettingResponse)
async def get_setting(
    setting_key: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get setting by key"""
    company_id = int(current_user.get("company_id", 0))
    
    setting = db.query(Setting).filter(
        Setting.company_id == company_id,
        Setting.setting_key == setting_key
    ).first()
    
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    
    return setting


@router.put("/{setting_key}", response_model=SettingResponse)
async def update_setting(
    setting_key: str,
    setting_update: SettingUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update setting"""
    company_id = int(current_user.get("company_id", 0))
    
    setting = db.query(Setting).filter(
        Setting.company_id == company_id,
        Setting.setting_key == setting_key
    ).first()
    
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    
    setting.setting_value = setting_update.setting_value
    db.commit()
    db.refresh(setting)
    
    return setting


@router.delete("/{setting_key}")
async def delete_setting(
    setting_key: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete setting"""
    company_id = int(current_user.get("company_id", 0))
    
    setting = db.query(Setting).filter(
        Setting.company_id == company_id,
        Setting.setting_key == setting_key
    ).first()
    
    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")
    
    db.delete(setting)
    db.commit()
    
    return {"message": "Setting deleted successfully"}
