"""Vision events router — called by the camera/vision pipeline."""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session as DBSession
from typing import Optional
import base64, os, uuid

from app.db import get_db
from app.config import settings
from app.models.vehicle import Vehicle
from app.models.event import Event, EventType
from app.models.decision import Decision, DecisionOutcome
from app.models.alert import AlertType
from app.services.rule_engine import RuleEngine
from app.services.session_service import open_session, close_session, get_open_session
from app.services.alert_service import create_alert
from app.services.plate_utils import normalize_plate

router = APIRouter()


class PlateEventIn(BaseModel):
    plate: str
    raw_plate: Optional[str] = None
    confidence: float = 1.0
    camera_id: Optional[str] = None
    gate_id: str
    vehicle_type: str = "car"
    image_base64: Optional[str] = None
    event_type: str = "entry"    # "entry" | "exit"


class PlateEventOut(BaseModel):
    decision: str
    reason: str
    gate_action: str
    session_id: Optional[str] = None
    event_id: str


def _save_snapshot(image_base64: str) -> Optional[str]:
    """Save base64-encoded image to disk, return URL path."""
    try:
        data = base64.b64decode(image_base64)
        filename = f"{uuid.uuid4()}.jpg"
        path = os.path.join(settings.SNAPSHOT_DIR, filename)
        os.makedirs(settings.SNAPSHOT_DIR, exist_ok=True)
        with open(path, "wb") as f:
            f.write(data)
        return f"/snapshots/{filename}"
    except Exception:
        return None


@router.post("/plate-event", response_model=PlateEventOut)
def plate_event(
    payload: PlateEventIn,
    background_tasks: BackgroundTasks,
    db: DBSession = Depends(get_db),
):
    plate_normalized = normalize_plate(payload.plate)
    now = datetime.now(timezone.utc)

    # Low-confidence flag
    if payload.confidence < settings.get("access.low_confidence_threshold", 0.70) if hasattr(settings, "get") else payload.confidence < 0.70:
        background_tasks.add_task(
            create_alert, db, AlertType.LOW_CONFIDENCE,
            f"Low OCR confidence {payload.confidence:.0%} on plate {payload.plate}",
            plate=payload.plate, gate_id=payload.gate_id,
        )

    # Look up vehicle
    vehicle = db.query(Vehicle).filter(Vehicle.plate_normalized == plate_normalized).first()

    # Run rule engine
    rule_engine = RuleEngine(db)
    result = rule_engine.check_access(plate_normalized, vehicle)

    # Save snapshot
    image_url = None
    if payload.image_base64:
        image_url = _save_snapshot(payload.image_base64)

    # Create event record
    event = Event(
        plate=plate_normalized,
        vehicle_id=vehicle.id if vehicle else None,
        gate_id=payload.gate_id,
        camera_id=payload.camera_id,
        event_type=EventType(payload.event_type),
        ocr_confidence=payload.confidence,
        raw_plate=payload.raw_plate or payload.plate,
        decision=result["decision"],
        rule_applied=result.get("rule_ref"),
        image_url=image_url,
        timestamp=now,
    )
    db.add(event)
    db.flush()

    # Create decision record
    decision = Decision(
        event_id=event.id,
        plate=plate_normalized,
        outcome=DecisionOutcome(result["decision"]),
        reason_code=result["reason_code"],
        rule_ref=result.get("rule_ref"),
        rule_snapshot=result,
        facts=result.get("facts", {}),
        gate_action=result["gate_action"],
        timestamp=now,
    )
    db.add(decision)

    # Session management
    session_id = None
    if result["decision"] == "allow":
        if payload.event_type == "entry":
            auto_session = rule_engine.get("access.visitor_auto_session", True)
            if auto_session:
                parking_session = open_session(
                    db, plate_normalized, now, payload.gate_id,
                    vehicle=vehicle, entry_event_id=str(event.id)
                )
                session_id = str(parking_session.id)
        elif payload.event_type == "exit":
            open_s = get_open_session(db, plate_normalized)
            if open_s:
                open_s = close_session(db, open_s, now, payload.gate_id, exit_event_id=str(event.id))
                session_id = str(open_s.id)

    # Blacklist alert
    if result["reason_code"] == "BLACKLIST":
        background_tasks.add_task(
            create_alert, db, AlertType.BLACKLIST,
            f"Blacklisted vehicle {plate_normalized} detected at gate {payload.gate_id}",
            plate=plate_normalized, gate_id=payload.gate_id,
        )

    db.commit()

    return PlateEventOut(
        decision=result["decision"],
        reason=result["reason_code"],
        gate_action=result["gate_action"],
        session_id=session_id,
        event_id=str(event.id),
    )
