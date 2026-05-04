from sqlalchemy import Column, String, ForeignKey, DateTime
from sqlalchemy import Uuid as UUID
from datetime import datetime
import uuid

from app.core.database import Base

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    model = Column(String)
    registration_number = Column(String, unique=True)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)