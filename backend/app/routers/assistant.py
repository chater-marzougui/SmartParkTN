"""AI Assistant router."""
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session as DBSession

from app.db import get_db
from app.auth import get_current_user
from app.models.vehicle import Vehicle
from app.models.decision import Decision
from app.models.user import User
from app.ai.chat_handler import answer_question

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    answer: str
    sources: list
    confidence: float


class ExplainResponse(BaseModel):
    decision: str
    reason: str
    rule_ref: str
    timestamp: str
    facts: dict


@router.post("/chat", response_model=ChatResponse)
async def chat(
    req: ChatRequest,
    db: DBSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    vehicle_context = ""
    decision_context = ""

    # Enrich context with DB data if plate is provided
    if req.context and req.context.get("plate"):
        plate = req.context["plate"]
        vehicle = db.query(Vehicle).filter(Vehicle.plate_normalized == plate).first()
        if vehicle:
            vehicle_context = (
                f"Plate: {vehicle.plate}\n"
                f"Category: {vehicle.category.value}\n"
                f"Type: {vehicle.vehicle_type.value}\n"
                f"Owner: {vehicle.owner_name or 'Unknown'}\n"
                f"Subscription expires: {vehicle.subscription_expires or 'N/A'}"
            )
        # Get last decision for this plate
        last_decision = (
            db.query(Decision)
            .filter(Decision.plate == plate)
            .order_by(Decision.timestamp.desc())
            .first()
        )
        if last_decision:
            decision_context = (
                f"Last decision: {last_decision.outcome.value.upper()}\n"
                f"Reason code: {last_decision.reason_code}\n"
                f"Rule reference: {last_decision.rule_ref or 'N/A'}\n"
                f"Timestamp: {last_decision.timestamp}"
            )

    result = await answer_question(req.message, vehicle_context, decision_context)
    return ChatResponse(**result)


@router.get("/explain/{decision_id}", response_model=ExplainResponse)
def explain_decision(
    decision_id: str,
    db: DBSession = Depends(get_db),
    _: User = Depends(get_current_user),
):
    decision = db.query(Decision).filter(Decision.id == decision_id).first()
    if not decision:
        raise HTTPException(404, "Decision not found")
    return ExplainResponse(
        decision=decision.outcome.value,
        reason=decision.reason_code,
        rule_ref=decision.rule_ref or "",
        timestamp=str(decision.timestamp),
        facts=decision.facts or {},
    )
