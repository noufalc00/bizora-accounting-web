"""
Authentication API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import timedelta

from database.database import get_db
from database.models import User, Company, UserRole
from core.security import verify_password, get_password_hash, create_access_token
from core.config import settings

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str
    company_id: int = None


class RegisterRequest(BaseModel):
    username: str
    password: str
    company_id: int
    role: UserRole = UserRole.ADMIN


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    company_id: int
    username: str
    role: str


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return JWT token"""
    user = db.query(User).filter(User.username == request.username).first()
    
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # If company_id provided, verify user belongs to company
    company_id = request.company_id or user.company_id
    if company_id and user.company_id != company_id:
        # Check if user is admin (can access any company)
        if user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not have access to this company"
            )
    
    access_token = create_access_token(
        data={"sub": str(user.id), "company_id": str(company_id)}
    )
    
    return TokenResponse(
        access_token=access_token,
        user_id=user.id,
        company_id=company_id,
        username=user.username,
        role=user.role.value
    )


@router.post("/register")
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == request.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Verify company exists
    company = db.query(Company).filter(Company.id == request.company_id).first()
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Create user
    user = User(
        username=request.username,
        password_hash=get_password_hash(request.password),
        company_id=request.company_id,
        role=request.role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {"message": "User created successfully", "user_id": user.id}


@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get current user information"""
    user = db.query(User).filter(User.id == int(current_user["user_id"])).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user.id,
        "username": user.username,
        "role": user.role.value,
        "company_id": user.company_id,
        "is_active": user.is_active
    }
