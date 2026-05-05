from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models.vehicle import Vehicle

async def create_vehicle(db: AsyncSession, vehicle_data):
    vehicle = Vehicle(**vehicle_data.model_dump())

    db.add(vehicle)
    await db.commit()
    await db.refresh(vehicle)

    return vehicle

async def get_vehicles(db: AsyncSession):
    result = await db.execute(select(Vehicle))
    return result.scalars().all()

async def get_vehicle_by_id(db: AsyncSession, vehicle_id: str):
    result = await db.execute(select(Vehicle).where(Vehicle.id == vehicle_id))
    return result.scalar_one_or_none()