from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.schemas.auth import UserCreate, UserLogin, AuthResponse, UserResponse
from src.services.auth_service import AuthService
from src.models.user import User
from src.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    return await service.register(user_in)

@router.post("/login", response_model=AuthResponse)
async def login(user_in: UserLogin, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    return await service.login(user_in)

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
