"""Tariffs router (admin only)."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session as DBSession

from app.db import get_db
from app.auth import require_roles
from app.models.tariff import Tariff
from app.models.user import User
from app.services.rule_engine import RuleEngine

router = APIRouter()


def _to_out(t: Tariff) -> dict:
    return {c.name: getattr(t, c.name) for c in t.__table__.columns} | {"id": str(t.id)}


class TariffIn(BaseModel):
    name: str
    vehicle_types: List[str] = ["car"]
    first_hour_tnd: float = 2.0
    extra_hour_tnd: float = 1.0
    daily_max_tnd: float = 20.0
    night_multiplier: float = 1.5
    night_start: str = "22:00"
    night_end: str = "06:00"
    weekend_multiplier: float = 1.2
    active: bool = True


@router.get("")
def list_tariffs(db: DBSession = Depends(get_db), _: User = Depends(require_roles("admin", "superadmin", "staff"))):
    return [_to_out(t) for t in db.query(Tariff).all()]


@router.post("", status_code=201)
def create_tariff(data: TariffIn, db: DBSession = Depends(get_db), _: User = Depends(require_roles("admin", "superadmin"))):
    t = Tariff(**data.model_dump())
    db.add(t)
    db.commit()
    db.refresh(t)
    return _to_out(t)


@router.put("/{tariff_id}")
def update_tariff(tariff_id: str, data: TariffIn, db: DBSession = Depends(get_db), _: User = Depends(require_roles("admin", "superadmin"))):
    t = db.query(Tariff).filter(Tariff.id == tariff_id).first()
    if not t:
        raise HTTPException(404, "Tariff not found")
    for k, v in data.model_dump().items():
        setattr(t, k, v)
    db.commit()
    db.refresh(t)
    return _to_out(t)


@router.delete("/{tariff_id}", status_code=204)
def delete_tariff(tariff_id: str, db: DBSession = Depends(get_db), _: User = Depends(require_roles("admin", "superadmin"))):
    t = db.query(Tariff).filter(Tariff.id == tariff_id).first()
    if not t:
        raise HTTPException(404, "Tariff not found")
    db.delete(t)
    db.commit()


@router.get("/simulate")
def simulate_tariff(
    duration: int,
    vehicle_type: str = "car",
    db: DBSession = Depends(get_db),
    _: User = Depends(require_roles("admin", "superadmin", "staff")),
):
    from datetime import datetime, timezone, timedelta
    entry = datetime.now(timezone.utc)
    exit_ = entry + timedelta(minutes=duration)
    engine = RuleEngine(db)
    result = engine.calculate_tariff(vehicle_type, entry, exit_)
    return result
