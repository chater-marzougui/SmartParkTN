"""Admin router — user management (superadmin only)."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session as DBSession
from typing import Optional

from app.db import get_db
from app.auth import require_roles, hash_password
from app.models.user import User, UserRole

router = APIRouter()


class UserCreate(BaseModel):
    username: str
    full_name: str
    email: EmailStr
    password: str
    role: str = "staff"


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    active: Optional[bool] = None


def _to_out(u: User) -> dict:
    return {c.name: str(getattr(u, c.name)) if c.name == "id" else getattr(u, c.name) for c in u.__table__.columns if c.name != "hashed_password"}


@router.get("/users")
def list_users(db: DBSession = Depends(get_db), _=Depends(require_roles("superadmin", "admin"))):
    return [_to_out(u) for u in db.query(User).all()]


@router.post("/users", status_code=201)
def create_user(data: UserCreate, db: DBSession = Depends(get_db), _=Depends(require_roles("superadmin"))):
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(409, "Username already exists")
    u = User(
        username=data.username,
        full_name=data.full_name,
        email=data.email,
        hashed_password=hash_password(data.password),
        role=UserRole(data.role),
        active=True,
    )
    db.add(u)
    db.commit()
    db.refresh(u)
    return _to_out(u)


@router.put("/users/{user_id}")
def update_user(user_id: str, data: UserUpdate, db: DBSession = Depends(get_db), _=Depends(require_roles("superadmin"))):
    u = db.query(User).filter(User.id == user_id).first()
    if not u:
        raise HTTPException(404, "User not found")
    for k, v in data.model_dump(exclude_unset=True).items():
        if k == "role" and v:
            v = UserRole(v)
        if v is not None or k == "active":
            setattr(u, k, v)
    db.commit()
    db.refresh(u)
    return _to_out(u)
