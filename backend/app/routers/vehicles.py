"""Vehicles CRUD router."""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session as DBSession
from datetime import datetime

from app.db import get_db
from app.auth import get_current_user
from app.models.vehicle import Vehicle, VehicleCategory, VehicleType
from app.models.user import User
from app.services.plate_utils import normalize_plate

router = APIRouter()


class VehicleOut(BaseModel):
    id: str
    plate: str
    plate_normalized: str
    category: str
    vehicle_type: str
    owner_name: Optional[str]
    owner_phone: Optional[str]
    owner_email: Optional[str]
    subscription_expires: Optional[datetime]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VehicleIn(BaseModel):
    plate: str
    category: str = "visitor"
    vehicle_type: str = "car"
    owner_name: Optional[str] = None
    owner_phone: Optional[str] = None
    owner_email: Optional[str] = None
    subscription_expires: Optional[datetime] = None
    notes: Optional[str] = None


def _to_out(v: Vehicle) -> dict:
    return {**{c.name: getattr(v, c.name) for c in v.__table__.columns}, "id": str(v.id)}


@router.get("", response_model=List[dict])
def list_vehicles(
    category: Optional[str] = None,
    search: Optional[str] = None,
    db: DBSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(Vehicle)
    if category:
        q = q.filter(Vehicle.category == category)
    if search:
        q = q.filter(Vehicle.plate.ilike(f"%{search}%"))
    return [_to_out(v) for v in q.order_by(Vehicle.created_at.desc()).all()]


@router.get("/search")
def search_vehicles(plate: str = Query(...), db: DBSession = Depends(get_db), _: User = Depends(get_current_user)):
    normalized = normalize_plate(plate)
    vehicles = db.query(Vehicle).filter(
        (Vehicle.plate_normalized.ilike(f"%{normalized}%")) | (Vehicle.plate.ilike(f"%{plate}%"))
    ).all()
    return [_to_out(v) for v in vehicles]


@router.get("/{vehicle_id}")
def get_vehicle(vehicle_id: str, db: DBSession = Depends(get_db), _: User = Depends(get_current_user)):
    v = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not v:
        raise HTTPException(404, "Vehicle not found")
    return _to_out(v)


@router.post("", status_code=201)
def create_vehicle(data: VehicleIn, db: DBSession = Depends(get_db), _: User = Depends(get_current_user)):
    normalized = normalize_plate(data.plate)
    existing = db.query(Vehicle).filter(Vehicle.plate_normalized == normalized).first()
    if existing:
        raise HTTPException(409, "Vehicle with this plate already exists")
    v = Vehicle(
        plate=data.plate,
        plate_normalized=normalized,
        category=VehicleCategory(data.category),
        vehicle_type=VehicleType(data.vehicle_type),
        owner_name=data.owner_name,
        owner_phone=data.owner_phone,
        owner_email=data.owner_email,
        subscription_expires=data.subscription_expires,
        notes=data.notes,
    )
    db.add(v)
    db.commit()
    db.refresh(v)
    return _to_out(v)


@router.put("/{vehicle_id}")
def update_vehicle(vehicle_id: str, data: VehicleIn, db: DBSession = Depends(get_db), _: User = Depends(get_current_user)):
    v = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not v:
        raise HTTPException(404, "Vehicle not found")
    for field, val in data.model_dump(exclude_unset=True).items():
        if hasattr(v, field):
            setattr(v, field, val)
    if data.plate:
        v.plate_normalized = normalize_plate(data.plate)
    db.commit()
    db.refresh(v)
    return _to_out(v)


@router.delete("/{vehicle_id}", status_code=204)
def delete_vehicle(vehicle_id: str, db: DBSession = Depends(get_db), _: User = Depends(get_current_user)):
    v = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not v:
        raise HTTPException(404, "Vehicle not found")
    db.delete(v)
    db.commit()


@router.post("/{vehicle_id}/blacklist")
def blacklist_vehicle(vehicle_id: str, db: DBSession = Depends(get_db), _: User = Depends(get_current_user)):
    v = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not v:
        raise HTTPException(404, "Vehicle not found")
    v.category = VehicleCategory.blacklist
    db.commit()
    return {"message": "Vehicle blacklisted"}


@router.post("/{vehicle_id}/whitelist")
def whitelist_vehicle(vehicle_id: str, db: DBSession = Depends(get_db), _: User = Depends(get_current_user)):
    v = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not v:
        raise HTTPException(404, "Vehicle not found")
    v.category = VehicleCategory.visitor
    db.commit()
    return {"message": "Vehicle removed from blacklist"}
