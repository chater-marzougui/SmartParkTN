"""Events audit log router."""
from typing import Optional, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DBSession

from app.db import get_db
from app.auth import get_current_user
from app.models.event import Event
from app.models.user import User

router = APIRouter()


def _to_out(e: Event) -> dict:
    return {c.name: getattr(e, c.name) for c in e.__table__.columns} | {"id": str(e.id)}


@router.get("", response_model=List[dict])
def list_events(
    plate: Optional[str] = None,
    gate_id: Optional[str] = None,
    limit: int = 200,
    db: DBSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(Event)
    if plate:
        q = q.filter(Event.plate.ilike(f"%{plate}%"))
    if gate_id:
        q = q.filter(Event.gate_id == gate_id)
    return [_to_out(e) for e in q.order_by(Event.timestamp.desc()).limit(limit).all()]


@router.get("/{event_id}")
def get_event(event_id: str, db: DBSession = Depends(get_db), _: User = Depends(get_current_user)):
    e = db.query(Event).filter(Event.id == event_id).first()
    if not e:
        from fastapi import HTTPException
        raise HTTPException(404, "Event not found")
    return _to_out(e)
