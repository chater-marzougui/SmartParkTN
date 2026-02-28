"""Rules CRUD router (admin only)."""
from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session as DBSession

from app.db import get_db
from app.auth import require_roles
from app.models.rule import Rule, RuleHistory
from app.models.user import User

router = APIRouter()


class RuleOut(BaseModel):
    key: str
    value: Any
    description: str = ""
    updated_at: str = ""


class RuleUpdateIn(BaseModel):
    value: Any


@router.get("", response_model=List[dict])
def list_rules(db: DBSession = Depends(get_db), _: User = Depends(require_roles("admin", "superadmin"))):
    return [{"key": r.key, "value": r.value, "description": r.description, "updated_at": str(r.updated_at)} for r in db.query(Rule).all()]


@router.put("/{key}")
def update_rule(
    key: str,
    data: RuleUpdateIn,
    db: DBSession = Depends(get_db),
    current_user: User = Depends(require_roles("admin", "superadmin")),
):
    rule = db.query(Rule).filter(Rule.key == key).first()
    old_value = rule.value if rule else None
    if rule:
        rule.value = data.value
        rule.updated_by = current_user.username
    else:
        rule = Rule(key=key, value=data.value, updated_by=current_user.username)
        db.add(rule)

    # History
    history = RuleHistory(rule_key=key, old_value=old_value, new_value=data.value, changed_by=current_user.username)
    db.add(history)
    db.commit()
    return {"key": key, "value": rule.value}


@router.get("/{key}/history")
def rule_history(key: str, db: DBSession = Depends(get_db), _: User = Depends(require_roles("admin", "superadmin"))):
    return db.query(RuleHistory).filter(RuleHistory.rule_key == key).order_by(RuleHistory.changed_at.desc()).all()
