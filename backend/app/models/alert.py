"""SQLAlchemy model for system alerts."""
import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Enum, Text, func
from sqlalchemy.dialects.postgresql import UUID
from app.db import Base
import enum


class AlertType(str, enum.Enum):
    BLACKLIST = "BLACKLIST"
    OVERSTAY = "OVERSTAY"
    DUPLICATE_PLATE = "DUPLICATE_PLATE"
    LOW_CONFIDENCE = "LOW_CONFIDENCE"
    FRAUD = "FRAUD"
    REVENUE_ANOMALY = "REVENUE_ANOMALY"
    PLATE_MISMATCH = "PLATE_MISMATCH"


class AlertSeverity(str, enum.Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alert_type = Column(Enum(AlertType), nullable=False, index=True)
    severity = Column(Enum(AlertSeverity), nullable=False)
    plate = Column(String(50), index=True)
    gate_id = Column(String(100))
    message = Column(Text, nullable=False)
    resolved = Column(Boolean, nullable=False, default=False)
    resolved_by = Column(String(200))
    resolved_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
