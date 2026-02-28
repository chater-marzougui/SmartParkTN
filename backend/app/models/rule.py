"""SQLAlchemy model for dynamic config rules (zero-hardcode engine)."""
import uuid
from sqlalchemy import Column, String, DateTime, JSON, func
from sqlalchemy.dialects.postgresql import UUID
from app.db import Base


class Rule(Base):
    __tablename__ = "rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key = Column(String(200), unique=True, nullable=False, index=True)
    value = Column(JSON, nullable=False)
    description = Column(String(500))
    updated_by = Column(String(200))
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class RuleHistory(Base):
    """Audit log for every rule change."""
    __tablename__ = "rule_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rule_key = Column(String(200), nullable=False, index=True)
    old_value = Column(JSON)
    new_value = Column(JSON)
    changed_by = Column(String(200))
    changed_at = Column(DateTime(timezone=True), server_default=func.now())
