from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from .models import Alert, AlertRule, AuditLog, Measurement, Sensor, Ticket
from .notifications import (
    send_email_notification,
    send_telegram_notification,
    send_whatsapp_notification,
)


@dataclass
class MeasurementResult:
    measurement: Measurement
    alerts: list[Alert]


def record_audit(
    *, action: str, actor=None, target=None, payload: Optional[dict] = None
) -> AuditLog:
    target_model = target.__class__.__name__ if target else ""
    target_id = str(getattr(target, "id", "")) if target else ""
    return AuditLog.objects.create(
        action=action,
        actor=actor,
        target_model=target_model,
        target_id=target_id,
        payload=payload or {},
    )


def _determine_status(sensor: Sensor, temperature: float) -> str:
    if sensor.threshold_min <= temperature <= sensor.threshold_max:
        return Measurement.Status.NORMAL
    delta = min(
        abs(float(temperature) - float(sensor.threshold_min)),
        abs(float(temperature) - float(sensor.threshold_max)),
    )
    if delta <= 1.5:
        return Measurement.Status.WARNING
    return Measurement.Status.CRITICAL


def _matching_rules(sensor: Sensor) -> Iterable[AlertRule]:
    return AlertRule.objects.filter(is_active=True).filter(
        Q(sensor__isnull=True) | Q(sensor=sensor)
    )


def _should_trigger(rule: AlertRule, temperature: float) -> bool:
    return temperature < float(rule.min_temp) or temperature > float(rule.max_temp)


def _notify_channels(alert: Alert, channels: list[str]) -> None:
    subject = f"[Cold Chain] {alert.severity.title()} for {alert.sensor.name}"
    body = (
        f"Sensor: {alert.sensor.name}\n"
        f"Location: {alert.sensor.location}\n"
        f"Temperature: {alert.measurement.temperature}°C\n"
        f"Recorded at: {alert.measurement.recorded_at:%Y-%m-%d %H:%M:%S}\n"
        f"Status: {alert.status}\n"
        f"Message: {alert.message}"
    )
    if "email" in channels:
        recipients = list(
            get_user_model()
            .objects.filter(is_active=True)
            .exclude(email="")
            .values_list("email", flat=True)
        )
        send_email_notification(subject, body, recipients)
    if "telegram" in channels:
        send_telegram_notification(body)
    if "whatsapp" in channels:
        send_whatsapp_notification(body)


def _create_alert(*, measurement: Measurement, rule: Optional[AlertRule]) -> Alert:
    severity = (
        Alert.Severity.CRITICAL
        if measurement.status == Measurement.Status.CRITICAL
        else Alert.Severity.WARNING
    )
    message = (
        f"Temperature {measurement.temperature}°C outside "
        f"{float(rule.min_temp) if rule else measurement.sensor.threshold_min}"
        f"-"
        f"{float(rule.max_temp) if rule else measurement.sensor.threshold_max}°C"
    )
    alert = Alert.objects.create(
        sensor=measurement.sensor,
        rule=rule,
        measurement=measurement,
        severity=severity,
        message=message,
    )
    channels = rule.channels if rule and rule.channels else ["email", "telegram"]
    _notify_channels(alert, channels)
    record_audit(
        action="alert.created",
        actor=None,
        target=alert,
        payload={"message": message},
    )
    return alert


def _ensure_ticket(alert: Alert) -> Ticket:
    ticket, created = Ticket.objects.get_or_create(
        alert=alert,
        defaults={
            "title": f"{alert.sensor.name} temperature incident",
            "description": alert.message,
            "opened_by": None,
            "priority": Ticket.Priority.CRITICAL
            if alert.severity == Alert.Severity.CRITICAL
            else Ticket.Priority.HIGH,
        },
    )
    if created:
        record_audit(
            action="ticket.autocreated",
            actor=None,
            target=ticket,
            payload={"alert": str(alert.id)},
        )
    return ticket


def store_measurement(
    *,
    sensor: Sensor,
    temperature: float,
    humidity: float,
    recorded_at,
    actor=None,
    raw_payload: Optional[dict] = None,
) -> MeasurementResult:
    recorded_at = recorded_at or timezone.now()

    with transaction.atomic():
        measurement = Measurement.objects.create(
            sensor=sensor,
            temperature=temperature,
            humidity=humidity,
            recorded_at=recorded_at,
            status=_determine_status(sensor, temperature),
            raw_payload=raw_payload or {},
        )
        record_audit(
            action="measurement.created",
            actor=actor,
            target=measurement,
            payload={"sensor": str(sensor.id), "temperature": temperature},
        )

        alerts: list[Alert] = []
        for rule in _matching_rules(sensor):
            if _should_trigger(rule, float(temperature)):
                alert = _create_alert(measurement=measurement, rule=rule)
                alerts.append(alert)
                _ensure_ticket(alert)

        if not alerts and measurement.status != Measurement.Status.NORMAL:
            alert = _create_alert(measurement=measurement, rule=None)
            alerts.append(alert)
            _ensure_ticket(alert)

        return MeasurementResult(measurement=measurement, alerts=alerts)

