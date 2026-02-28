"""SQLAlchemy model for vehicles (database identity is the plate number)."""
import uuid
from sqlalchemy import Column, String, DateTime, Enum, Text, func
from sqlalchemy.dialects.postgresql import UUID
from app.db import Base
import enum


class VehicleCategory(str, enum.Enum):
    visitor = "visitor"
    subscriber = "subscriber"
    vip = "vip"
    blacklist = "blacklist"


class VehicleType(str, enum.Enum):
    car = "car"
    truck = "truck"
    motorcycle = "motorcycle"
    bus = "bus"


class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plate = Column(String(50), unique=True, nullable=False, index=True)
    plate_normalized = Column(String(50), unique=True, nullable=False, index=True)
    category = Column(Enum(VehicleCategory), nullable=False, default=VehicleCategory.visitor)
    vehicle_type = Column(Enum(VehicleType), nullable=False, default=VehicleType.car)
    owner_name = Column(String(200))
    owner_phone = Column(String(50))
    owner_email = Column(String(200))
    subscription_expires = Column(DateTime(timezone=True))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
