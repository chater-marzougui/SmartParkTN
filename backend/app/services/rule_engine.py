"""Rule Engine — reads rules from DB, makes access decisions and calculates billing."""
from datetime import datetime, date, timezone
from typing import Optional

from sqlalchemy.orm import Session as DBSession

from app.models.rule import Rule
from app.models.vehicle import Vehicle, VehicleCategory
from app.models.tariff import Tariff

# Default rule values (used if DB has no entry)
RULE_DEFAULTS = {
    "access.max_stay_hours": 24,
    "access.subscriber_grace_minutes": 60,
    "access.low_confidence_threshold": 0.70,
    "access.blacklist_auto_alert": True,
    "access.visitor_auto_session": True,
    "access.unknown_plate_behavior": "allow",
    "billing.night.start": "22:00",
    "billing.night.end": "06:00",
    "alerts.overstay_hours": 24,
    "alerts.duplicate_window_minutes": 2,
}


class RuleEngine:
    def __init__(self, db: DBSession):
        self.db = db
        self._cache: dict = {}
        self._load_rules()

    def _load_rules(self):
        rules = self.db.query(Rule).all()
        self._cache = {r.key: r.value for r in rules}

    def get(self, key: str, default=None):
        return self._cache.get(key, RULE_DEFAULTS.get(key, default))

    # ── Access Decision ────────────────────────────────────────────────────
    def check_access(self, plate: str, vehicle: Optional[Vehicle] = None) -> dict:
        """Return { decision, reason_code, rule_ref, gate_action, facts }."""
        facts = {"plate": plate}

        if vehicle is None:
            action = self.get("access.unknown_plate_behavior", "allow")
            if action == "deny":
                return {"decision": "deny", "reason_code": "UNKNOWN_PLATE", "rule_ref": "Rule: unknown_plate_behavior", "gate_action": "close", "facts": facts}
            if action == "alert":
                return {"decision": "alert", "reason_code": "UNKNOWN_PLATE_ALERT", "rule_ref": "Rule: unknown_plate_behavior", "gate_action": "open", "facts": facts}
            return {"decision": "allow", "reason_code": "VISITOR", "rule_ref": "Standard tariff", "gate_action": "open", "facts": facts}

        facts["category"] = vehicle.category.value

        if vehicle.category == VehicleCategory.blacklist:
            return {"decision": "deny", "reason_code": "BLACKLIST", "rule_ref": "Article 3.2", "gate_action": "close", "facts": facts}

        if vehicle.category == VehicleCategory.vip:
            return {"decision": "allow", "reason_code": "VIP", "rule_ref": "Article 2.1", "gate_action": "open", "facts": facts}

        if vehicle.category == VehicleCategory.subscriber:
            if vehicle.subscription_expires:
                expire_date = vehicle.subscription_expires.date() if hasattr(vehicle.subscription_expires, "date") else vehicle.subscription_expires
                today = date.today()
                grace_minutes = self.get("access.subscriber_grace_minutes", 60)
                grace_days = grace_minutes / (60 * 24)
                facts["subscription_expires"] = str(expire_date)
                if (today - expire_date).days > grace_days:
                    return {"decision": "deny", "reason_code": "EXPIRED_SUBSCRIPTION", "rule_ref": "Article 4.1", "gate_action": "close", "facts": facts}
            return {"decision": "allow", "reason_code": "SUBSCRIBER", "rule_ref": "Article 2.2", "gate_action": "open", "facts": facts}

        return {"decision": "allow", "reason_code": "VISITOR", "rule_ref": "Standard tariff", "gate_action": "open", "facts": facts}

    # ── Billing Calculation ────────────────────────────────────────────────
    def calculate_tariff(
        self,
        vehicle_type: str,
        entry_time: datetime,
        exit_time: datetime,
        tariff: Optional[Tariff] = None,
    ) -> dict:
        """Calculate billing for a session."""
        if tariff is None:
            tariff = (
                self.db.query(Tariff)
                .filter(Tariff.active == True, Tariff.vehicle_types.contains([vehicle_type]))
                .first()
            )
        if tariff is None:
            # Fallback to any active tariff
            tariff = self.db.query(Tariff).filter(Tariff.active == True).first()
        if tariff is None:
            return {"amount": 0.0, "duration_minutes": 0, "breakdown": "No active tariff found"}

        duration_minutes = max(0, int((exit_time - entry_time).total_seconds() / 60))
        hours = duration_minutes / 60

        if hours <= 1:
            price = tariff.first_hour_tnd
        else:
            price = tariff.first_hour_tnd + (hours - 1) * tariff.extra_hour_tnd

        # Apply daily cap
        price = min(price, tariff.daily_max_tnd)

        # Night multiplier
        if self._spans_night(entry_time, exit_time, tariff.night_start, tariff.night_end):
            price *= tariff.night_multiplier

        # Weekend multiplier  
        if entry_time.weekday() >= 5:  # Sat=5, Sun=6
            price *= tariff.weekend_multiplier

        return {
            "amount": round(price, 3),
            "duration_minutes": duration_minutes,
            "tariff_name": tariff.name,
            "tariff_id": str(tariff.id),
        }

    def _spans_night(self, entry: datetime, exit: datetime, night_start: str, night_end: str) -> bool:
        start_h, start_m = map(int, night_start.split(":"))
        end_h, end_m = map(int, night_end.split(":"))
        entry_h = entry.hour + entry.minute / 60
        # Simple check: entry is within night window
        if start_h > end_h:  # crosses midnight
            return entry_h >= start_h or entry_h < end_h
        return start_h <= entry_h < end_h
