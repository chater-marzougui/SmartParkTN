"""SQLAlchemy model for access decisions (explainable AI audit trail)."""
import uuid
from sqlalchemy import Column, String, DateTime, Enum, JSON, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from app.db import Base
import enum


class DecisionOutcome(str, enum.Enum):
    allow = "allow"
    deny = "deny"
    alert = "alert"


class Decision(Base):
    __tablename__ = "decisions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=True)
    plate = Column(String(50), nullable=False, index=True)
    outcome = Column(Enum(DecisionOutcome), nullable=False)
    reason_code = Column(String(100), nullable=False)   # e.g. BLACKLIST, VIP, EXPIRED_SUBSCRIPTION
    rule_ref = Column(String(200))                       # e.g. "Article 3.2"
    rule_snapshot = Column(JSON)                         # the exact rule value at decision time
    facts = Column(JSON)                                 # vehicle category, subscription expiry, etc.
    gate_action = Column(String(50))                     # "open" | "close" | "alert"
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
