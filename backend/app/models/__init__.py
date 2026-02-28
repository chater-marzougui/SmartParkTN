"""Re-export all models for Alembic auto-discovery."""
from app.db import Base  # noqa: F401 — shared declarative base
from app.models.vehicle import Vehicle, VehicleCategory, VehicleType
from app.models.event import Event, EventType, DecisionType
from app.models.session import Session, PaymentStatus
from app.models.decision import Decision, DecisionOutcome
from app.models.tariff import Tariff
from app.models.rule import Rule, RuleHistory
from app.models.user import User, UserRole
from app.models.alert import Alert, AlertType, AlertSeverity

__all__ = [
    "Base",
    "Vehicle", "VehicleCategory", "VehicleType",
    "Event", "EventType", "DecisionType",
    "Session", "PaymentStatus",
    "Decision", "DecisionOutcome",
    "Tariff",
    "Rule", "RuleHistory",
    "User", "UserRole",
    "Alert", "AlertType", "AlertSeverity",
]
