from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session as DBSession
from pydantic import BaseModel

from app.db import get_db
from app.models.user import User
from app.auth import verify_password, create_access_token, get_current_user

router = APIRouter()


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: str
    username: str
    full_name: str
    email: str
    role: str

    class Config:
        from_attributes = True


@router.post("/login", response_model=LoginResponse)
def login(form: OAuth2PasswordRequestForm = Depends(), db: DBSession = Depends(get_db)):
    user = db.query(User).filter(User.username == form.username, User.active == True).first()
    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token({"sub": user.username})
    return LoginResponse(access_token=token)


@router.post("/logout")
def logout():
    # JWT is stateless; client should discard the token
    return {"message": "Logged out"}


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return UserOut(
        id=str(current_user.id),
        username=current_user.username,
        full_name=current_user.full_name,
        email=current_user.email,
        role=current_user.role.value,
    )
