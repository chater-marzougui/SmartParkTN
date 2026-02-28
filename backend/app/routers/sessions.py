"""Sessions router."""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession

from app.db import get_db
from app.auth import get_current_user
from app.models.session import Session as ParkingSession
from app.models.user import User
from app.services.session_service import close_session

router = APIRouter()


def _to_out(s: ParkingSession) -> dict:
    return {c.name: getattr(s, c.name) for c in s.__table__.columns} | {"id": str(s.id)}


@router.get("", response_model=List[dict])
def list_sessions(
    plate: Optional[str] = None,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    db: DBSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(ParkingSession)
    if plate:
        q = q.filter(ParkingSession.plate.ilike(f"%{plate}%"))
    return [_to_out(s) for s in q.order_by(ParkingSession.entry_time.desc()).limit(500).all()]


@router.get("/open")
def open_sessions(db: DBSession = Depends(get_db), _: User = Depends(get_current_user)):
    sessions = db.query(ParkingSession).filter(ParkingSession.exit_time == None).all()
    return [_to_out(s) for s in sessions]


@router.get("/{session_id}")
def get_session(session_id: str, db: DBSession = Depends(get_db), _: User = Depends(get_current_user)):
    s = db.query(ParkingSession).filter(ParkingSession.id == session_id).first()
    if not s:
        raise HTTPException(404, "Session not found")
    return _to_out(s)


@router.post("/{session_id}/close")
def manual_close_session(session_id: str, db: DBSession = Depends(get_db), _: User = Depends(get_current_user)):
    s = db.query(ParkingSession).filter(ParkingSession.id == session_id).first()
    if not s:
        raise HTTPException(404, "Session not found")
    if s.exit_time:
        raise HTTPException(400, "Session already closed")
    s = close_session(db, s)
    return _to_out(s)
