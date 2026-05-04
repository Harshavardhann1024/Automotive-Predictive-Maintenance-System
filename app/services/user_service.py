from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User, UserRole
from passlib.context import CryptContext
from fastapi import HTTPException

# ✅ Use stable hashing (no bcrypt issues)
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")

# ✅ Proper function
def hash_password(password: str):
    return pwd_context.hash(password)

async def create_user(db: AsyncSession, user_data):
    result = await db.execute(select(User).where(User.email == user_data.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        role=user_data.role  # ✅ since we switched to String
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user