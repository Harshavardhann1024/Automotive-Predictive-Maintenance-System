from sqlalchemy import Column, String, Enum, DateTime
from sqlalchemy import Uuid as UUID
from datetime import datetime
import uuid
import enum

from backend.core.database import Base

class UserRole(str, enum.Enum):
    admin = "admin"
    engineer = "engineer"
    viewer = "viewer"

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)