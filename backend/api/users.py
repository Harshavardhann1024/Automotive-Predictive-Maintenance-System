from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.schemas.user import UserCreate, UserResponse
from backend.services.user_service import create_user

router = APIRouter()

@router.post("/", response_model=UserResponse)
async def create_user_route(user: UserCreate, db: AsyncSession = Depends(get_db)):
    return await create_user(db, user)