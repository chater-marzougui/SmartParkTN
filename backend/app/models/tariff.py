"""SQLAlchemy model for tariff profiles."""
import uuid
from sqlalchemy import Column, String, Float, Boolean, DateTime, JSON, func
from sqlalchemy.dialects.postgresql import UUID
from app.db import Base


class Tariff(Base):
    __tablename__ = "tariffs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    vehicle_types = Column(JSON, nullable=False, default=["car"])   # list[str]
    first_hour_tnd = Column(Float, nullable=False, default=2.0)
    extra_hour_tnd = Column(Float, nullable=False, default=1.0)
    daily_max_tnd = Column(Float, nullable=False, default=20.0)
    night_multiplier = Column(Float, nullable=False, default=1.5)
    night_start = Column(String(5), nullable=False, default="22:00")  # "HH:MM"
    night_end = Column(String(5), nullable=False, default="06:00")
    weekend_multiplier = Column(Float, nullable=False, default=1.2)
    valid_from = Column(DateTime(timezone=True))
    valid_until = Column(DateTime(timezone=True))
    active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
