"""Session service — create, manage, and close parking sessions."""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session as DBSession

from app.models.session import Session as ParkingSession, PaymentStatus
from app.models.vehicle import Vehicle
from app.services.rule_engine import RuleEngine


def open_session(
    db: DBSession,
    plate: str,
    entry_time: datetime,
    gate_entry: str,
    vehicle: Optional[Vehicle] = None,
    entry_event_id: Optional[str] = None,
) -> ParkingSession:
    """Create an open session for a vehicle entering."""
    session = ParkingSession(
        plate=plate,
        vehicle_id=vehicle.id if vehicle else None,
        entry_time=entry_time,
        gate_entry=gate_entry,
        entry_event_id=entry_event_id,
        payment_status=PaymentStatus.pending,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def close_session(
    db: DBSession,
    session: ParkingSession,
    exit_time: Optional[datetime] = None,
    gate_exit: Optional[str] = None,
    exit_event_id: Optional[str] = None,
) -> ParkingSession:
    """Close a session, calculate duration and billing."""
    exit_time = exit_time or datetime.now(timezone.utc)
    rule_engine = RuleEngine(db)

    vehicle_type = "car"
    if session.vehicle_id:
        vehicle = db.query(Vehicle).filter(Vehicle.id == session.vehicle_id).first()
        if vehicle:
            vehicle_type = vehicle.vehicle_type.value

    billing = rule_engine.calculate_tariff(
        vehicle_type=vehicle_type,
        entry_time=session.entry_time,
        exit_time=exit_time,
    )

    session.exit_time = exit_time
    session.gate_exit = gate_exit
    session.exit_event_id = exit_event_id
    session.duration_minutes = billing["duration_minutes"]
    session.amount_due = billing["amount"]
    session.tariff_snapshot = billing

    db.commit()
    db.refresh(session)
    return session


def get_open_session(db: DBSession, plate: str) -> Optional[ParkingSession]:
    """Find the most recent open session for a plate."""
    return (
        db.query(ParkingSession)
        .filter(ParkingSession.plate == plate, ParkingSession.exit_time == None)
        .order_by(ParkingSession.entry_time.desc())
        .first()
    )
