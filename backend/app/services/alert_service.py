"""Alert service — create and manage system alerts."""
from datetime import datetime, timezone
from sqlalchemy.orm import Session as DBSession

from app.models.alert import Alert, AlertType, AlertSeverity


ALERT_SEVERITY_MAP = {
    AlertType.BLACKLIST:       AlertSeverity.critical,
    AlertType.DUPLICATE_PLATE: AlertSeverity.high,
    AlertType.FRAUD:           AlertSeverity.high,
    AlertType.OVERSTAY:        AlertSeverity.medium,
    AlertType.PLATE_MISMATCH:  AlertSeverity.medium,
    AlertType.LOW_CONFIDENCE:  AlertSeverity.low,
    AlertType.REVENUE_ANOMALY: AlertSeverity.medium,
}


def create_alert(
    db: DBSession,
    alert_type: AlertType,
    message: str,
    plate: str = None,
    gate_id: str = None,
    severity: AlertSeverity = None,
) -> Alert:
    if severity is None:
        severity = ALERT_SEVERITY_MAP.get(alert_type, AlertSeverity.medium)

    alert = Alert(
        alert_type=alert_type,
        severity=severity,
        plate=plate,
        gate_id=gate_id,
        message=message,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def resolve_alert(db: DBSession, alert_id: str, resolved_by: str) -> Alert:
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        return None
    alert.resolved = True
    alert.resolved_by = resolved_by
    alert.resolved_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(alert)
    return alert
