import secrets
import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "admin", "Admin"
        MANAGER = "manager", "Manager"
        TECHNICIAN = "technician", "Technician"
        VIEWER = "viewer", "Viewer"

    role = models.CharField(
        max_length=32, choices=Role.choices, default=Role.VIEWER
    )
    organization = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=50, blank=True)

    def __str__(self) -> str:
        return f"{self.username} ({self.role})"



def _generate_sensor_token() -> str:
    return secrets.token_hex(16)


class Sensor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100, unique=True)
    location = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    token = models.CharField(max_length=64, unique=True, default=_generate_sensor_token)
    threshold_min = models.DecimalField(max_digits=5, decimal_places=2, default=2.0)
    threshold_max = models.DecimalField(max_digits=5, decimal_places=2, default=8.0)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="sensors"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.location or 'n/a'})"


class Measurement(models.Model):
    class Status(models.TextChoices):
        NORMAL = "normal", "Normal"
        WARNING = "warning", "Warning"
        CRITICAL = "critical", "Critical"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sensor = models.ForeignKey(
        Sensor, related_name="measurements", on_delete=models.CASCADE
    )
    temperature = models.DecimalField(max_digits=5, decimal_places=2)
    humidity = models.DecimalField(max_digits=5, decimal_places=2)
    recorded_at = models.DateTimeField(default=timezone.now)
    received_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=32, choices=Status.choices, default=Status.NORMAL
    )
    note = models.CharField(max_length=255, blank=True)
    raw_payload = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-recorded_at"]

    def __str__(self) -> str:
        return f"{self.sensor.name} @ {self.recorded_at:%Y-%m-%d %H:%M}"


class AlertRule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=120)
    sensor = models.ForeignKey(
        Sensor,
        related_name="alert_rules",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    min_temp = models.DecimalField(max_digits=5, decimal_places=2, default=2.0)
    max_temp = models.DecimalField(max_digits=5, decimal_places=2, default=8.0)
    window_minutes = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    channels = models.ManyToManyField("Channel", blank=True)
    created_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="rules"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        scope = self.sensor.name if self.sensor else "global"
        return f"{self.name} ({scope})"


class Alert(models.Model):
    class Severity(models.TextChoices):
        INFO = "info", "Info"
        WARNING = "warning", "Warning"
        CRITICAL = "critical", "Critical"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        ACKNOWLEDGED = "acknowledged", "Acknowledged"
        RESOLVED = "resolved", "Resolved"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sensor = models.ForeignKey(
        Sensor, related_name="alerts", on_delete=models.CASCADE
    )
    rule = models.ForeignKey(
        AlertRule,
        related_name="alerts",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    measurement = models.ForeignKey(
        Measurement, related_name="alerts", on_delete=models.CASCADE
    )
    severity = models.CharField(
        max_length=32, choices=Severity.choices, default=Severity.WARNING
    )
    status = models.CharField(
        max_length=32, choices=Status.choices, default=Status.OPEN
    )
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    acknowledged_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="acknowledged_alerts",
    )
    resolved_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="resolved_alerts",
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.sensor.name} - {self.severity}"

class Channel(models.Model):
    CHANNEL_TYPES = [
        ("email", "Email"),
        ("telegram", "Telegram"),
        ("whatsapp", "WhatsApp"),
        ("webhook", "Webhook"),
    ]

    name = models.CharField(max_length=100)
    channel_type = models.CharField(max_length=20, choices=CHANNEL_TYPES)
    target = models.CharField(max_length=255, help_text="Email, chat ID, phone ID ou URL webhook")

    def __str__(self):
        return f"{self.name} ({self.channel_type})"



class Ticket(models.Model):
    class Status(models.TextChoices):
        OPEN = "open", "Open"
        IN_PROGRESS = "in_progress", "In Progress"
        CLOSED = "closed", "Closed"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    alert = models.ForeignKey(
        Alert, related_name="tickets", on_delete=models.CASCADE, null=True, blank=True
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=32, choices=Status.choices, default=Status.OPEN
    )
    priority = models.CharField(
        max_length=32, choices=Priority.choices, default=Priority.MEDIUM
    )
    opened_by = models.ForeignKey(
        User,
        related_name="opened_tickets",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    assigned_to = models.ForeignKey(
        User,
        related_name="assigned_tickets",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    closed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title


class AuditLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    action = models.CharField(max_length=150)
    actor = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="logs"
    )
    target_model = models.CharField(max_length=150, blank=True)
    target_id = models.CharField(max_length=150, blank=True)
    payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.action} by {self.actor or 'system'}"
