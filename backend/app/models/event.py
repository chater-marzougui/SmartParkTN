"""SQLAlchemy model for parking events (every camera detection)."""
import uuid
from sqlalchemy import Column, String, DateTime, Enum, Float, Text, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from app.db import Base
import enum


class EventType(str, enum.Enum):
    entry = "entry"
    exit = "exit"
    detection = "detection"


class DecisionType(str, enum.Enum):
    allow = "allow"
    deny = "deny"
    alert = "alert"


class Event(Base):
    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plate = Column(String(50), nullable=False, index=True)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=True)
    gate_id = Column(String(100), nullable=False)
    camera_id = Column(String(100))
    event_type = Column(Enum(EventType), nullable=False)
    ocr_confidence = Column(Float)
    raw_plate = Column(String(100))
    decision = Column(Enum(DecisionType))
    rule_applied = Column(String(200))
    image_url = Column(String(500))
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
