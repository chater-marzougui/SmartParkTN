"""SQLAlchemy model for staff users."""
import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Enum, func
from sqlalchemy.dialects.postgresql import UUID
from app.db import Base
import enum


class UserRole(str, enum.Enum):
    superadmin = "superadmin"
    admin = "admin"
    staff = "staff"
    viewer = "viewer"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(200), nullable=False)
    email = Column(String(200), unique=True, nullable=False)
    hashed_password = Column(String(300), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.staff)
    active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
