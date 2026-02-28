"""Analytics router — occupancy, revenue, peak hours etc."""
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import func
from fastapi import APIRouter, Depends

from app.db import get_db
from app.auth import get_current_user
from app.models.session import Session as ParkingSession, PaymentStatus
from app.models.event import Event, DecisionType
from app.models.user import User

router = APIRouter()


@router.get("/occupancy")
def get_occupancy(db: DBSession = Depends(get_db), _: User = Depends(get_current_user)):
    current = db.query(ParkingSession).filter(ParkingSession.exit_time == None).count()
    # Total capacity comes from rules; default 200
    total = 200
    return {"current": current, "total": total, "percentage": round(current / total * 100, 1)}


@router.get("/revenue")
def get_revenue(
    from_date: str = None,
    to_date: str = None,
    db: DBSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(
        func.date(ParkingSession.entry_time).label("date"),
        func.sum(ParkingSession.amount_due).label("amount"),
    ).filter(ParkingSession.payment_status == PaymentStatus.paid)
    if from_date:
        q = q.filter(ParkingSession.entry_time >= from_date)
    if to_date:
        q = q.filter(ParkingSession.entry_time <= to_date)
    rows = q.group_by(func.date(ParkingSession.entry_time)).order_by(func.date(ParkingSession.entry_time)).all()
    return [{"date": str(r.date), "amount": float(r.amount or 0)} for r in rows]


@router.get("/peak-hours")
def get_peak_hours(db: DBSession = Depends(get_db), _: User = Depends(get_current_user)):
    rows = db.query(
        func.extract("dow", Event.timestamp).label("day"),
        func.extract("hour", Event.timestamp).label("hour"),
        func.count().label("count"),
    ).group_by("day", "hour").all()
    return [{"day": int(r.day), "hour": int(r.hour), "count": int(r.count)} for r in rows]


@router.get("/top-vehicles")
def get_top_vehicles(db: DBSession = Depends(get_db), _: User = Depends(get_current_user)):
    rows = db.query(
        Event.plate,
        func.count().label("visits"),
        func.max(Event.timestamp).label("last_seen"),
    ).group_by(Event.plate).order_by(func.count().desc()).limit(10).all()
    return [{"plate": r.plate, "visits": int(r.visits), "last_seen": str(r.last_seen)} for r in rows]


@router.get("/decisions")
def get_decisions(db: DBSession = Depends(get_db), _: User = Depends(get_current_user)):
    from app.models.decision import Decision, DecisionOutcome
    rows = db.query(Decision.outcome, func.count().label("cnt")).group_by(Decision.outcome).all()
    result = {"allow": 0, "deny": 0, "alert": 0}
    for r in rows:
        result[r.outcome.value] = int(r.cnt)
    return result
