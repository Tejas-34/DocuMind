from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from src.models.user import User
from src.schemas.auth import UserCreate, UserLogin, AuthResponse, UserResponse
from src.core.security import get_password_hash, verify_password, create_access_token

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, user_in: UserCreate) -> AuthResponse:
        email = user_in.email.strip().lower()
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        existing_user = result.scalars().first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this email already exists."
            )

        user = User(
            email=email,
            hashed_password=get_password_hash(user_in.password),
            is_active=True
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        token = create_access_token(subject=str(user.id))
        return AuthResponse(
            access_token=token,
            token_type="bearer",
            user=UserResponse.model_validate(user)
        )

    async def login(self, user_in: UserLogin) -> AuthResponse:
        email = user_in.email.strip().lower()
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        user = result.scalars().first()
        if not user or not verify_password(user_in.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password."
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive user account."
            )

        token = create_access_token(subject=str(user.id))
        return AuthResponse(
            access_token=token,
            token_type="bearer",
            user=UserResponse.model_validate(user)
        )

    async def get_user_by_id(self, user_id) -> User:
        stmt = select(User).where(User.id == user_id)
        result = await self.db.execute(stmt)
        user = result.scalars().first()
        return user
