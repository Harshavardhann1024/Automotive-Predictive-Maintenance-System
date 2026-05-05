from pydantic import BaseModel
from uuid import UUID

class VehicleCreate(BaseModel):
    name: str
    model: str
    registration_number: str
    owner_id: UUID

class VehicleResponse(BaseModel):
    id: UUID
    name: str
    model: str
    registration_number: str
    owner_id: UUID

    class Config:
        from_attributes = True