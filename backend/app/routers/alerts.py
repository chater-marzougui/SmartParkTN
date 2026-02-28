"""Alerts router."""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession

from app.db import get_db
from app.auth import get_current_user
from app.models.alert import Alert
from app.models.user import User
from app.services.alert_service import resolve_alert

router = APIRouter()


def _to_out(a: Alert) -> dict:
    return {c.name: getattr(a, c.name) for c in a.__table__.columns} | {"id": str(a.id)}


@router.get("")
def list_alerts(db: DBSession = Depends(get_db), _: User = Depends(get_current_user)):
    return [_to_out(a) for a in db.query(Alert).filter(Alert.resolved == False).order_by(Alert.created_at.desc()).all()]


@router.get("/history")
def alert_history(db: DBSession = Depends(get_db), _: User = Depends(get_current_user)):
    return [_to_out(a) for a in db.query(Alert).filter(Alert.resolved == True).order_by(Alert.created_at.desc()).limit(200).all()]


@router.put("/{alert_id}/resolve")
def resolve(alert_id: str, db: DBSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    a = resolve_alert(db, alert_id, current_user.username)
    if not a:
        raise HTTPException(404, "Alert not found")
    return _to_out(a)
