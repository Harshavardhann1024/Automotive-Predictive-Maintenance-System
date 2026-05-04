from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from typing import Optional

from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.core.auth import get_password_hash, verify_password, create_access_token

class AuthService:
    @staticmethod
    async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
        """Authenticate a user with email and password."""
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate) -> UserResponse:
        """Create a new user with hashed password."""
        # Check if user already exists
        result = await db.execute(select(User).where(User.email == user_data.email))
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create new user
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            name=user_data.name,
            email=user_data.email,
            password_hash=hashed_password,
            role=user_data.role
        )

        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)

        return UserResponse.from_orm(db_user)

    @staticmethod
    def create_access_token_for_user(user: User) -> str:
        """Create JWT access token for authenticated user."""
        access_token = create_access_token(
            data={"sub": user.email, "user_id": str(user.id), "role": user.role}
        )
        return access_token