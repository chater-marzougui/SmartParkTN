"""SQLAlchemy model for parking sessions (entry-exit pair with billing)."""
import uuid
from sqlalchemy import Column, String, DateTime, Enum, Float, Integer, JSON, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from app.db import Base
import enum


class PaymentStatus(str, enum.Enum):
    pending = "pending"
    paid = "paid"
    disputed = "disputed"
    waived = "waived"


class Session(Base):
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    plate = Column(String(50), nullable=False, index=True)
    vehicle_id = Column(UUID(as_uuid=True), ForeignKey("vehicles.id"), nullable=True)
    entry_event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=True)
    exit_event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=True)
    entry_time = Column(DateTime(timezone=True), nullable=False, index=True)
    exit_time = Column(DateTime(timezone=True))
    duration_minutes = Column(Integer)
    tariff_id = Column(UUID(as_uuid=True), ForeignKey("tariffs.id"), nullable=True)
    tariff_snapshot = Column(JSON)          # snapshot of tariff at billing time
    amount_due = Column(Float)
    payment_status = Column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.pending)
    gate_entry = Column(String(100))
    gate_exit = Column(String(100))
    notes = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
