from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database import get_db
from backend.schemas.vehicle import VehicleCreate, VehicleResponse
from backend.services.vehicle_service import create_vehicle, get_vehicles, get_vehicle_by_id

router = APIRouter()

@router.get("/", response_model=list[VehicleResponse])
async def list_vehicles(db: AsyncSession = Depends(get_db)):
    return await get_vehicles(db)

@router.get("/{vehicle_id}", response_model=VehicleResponse)
async def get_vehicle(vehicle_id: str, db: AsyncSession = Depends(get_db)):
    return await get_vehicle_by_id(db, vehicle_id)

@router.post("/", response_model=VehicleResponse)
async def create_vehicle_route(vehicle: VehicleCreate, db: AsyncSession = Depends(get_db)):
    return await create_vehicle(db, vehicle)