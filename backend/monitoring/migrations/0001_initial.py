import uuid

from django.conf import settings
from django.contrib.auth.models import UserManager
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone

import monitoring.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                ("last_login", models.DateTimeField(blank=True, null=True, verbose_name="last login")),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        error_messages={"unique": "A user with that username already exists."},
                        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
                        max_length=150,
                        unique=True,
                        validators=[django.contrib.auth.validators.UnicodeUsernameValidator()],
                        verbose_name="username",
                    ),
                ),
                ("first_name", models.CharField(blank=True, max_length=150, verbose_name="first name")),
                ("last_name", models.CharField(blank=True, max_length=150, verbose_name="last name")),
                ("email", models.EmailField(blank=True, max_length=254, verbose_name="email address")),
                ("is_staff", models.BooleanField(default=False, help_text="Designates whether the user can log into this admin site.", verbose_name="staff status")),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                ("date_joined", models.DateTimeField(default=django.utils.timezone.now, verbose_name="date joined")),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("admin", "Admin"),
                            ("manager", "Manager"),
                            ("technician", "Technician"),
                            ("viewer", "Viewer"),
                        ],
                        default="viewer",
                        max_length=32,
                    ),
                ),
                ("organization", models.CharField(blank=True, max_length=255)),
                ("phone_number", models.CharField(blank=True, max_length=50)),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "verbose_name": "user",
                "verbose_name_plural": "users",
                "abstract": False,
            },
            managers=[
                ("objects", UserManager()),
            ],
        ),
        migrations.CreateModel(
            name="Sensor",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=100)),
                ("serial_number", models.CharField(max_length=100, unique=True)),
                ("location", models.CharField(blank=True, max_length=255)),
                ("description", models.TextField(blank=True)),
                (
                    "token",
                    models.CharField(
                        default=monitoring.models._generate_sensor_token,
                        max_length=64,
                        unique=True,
                    ),
                ),
                ("threshold_min", models.DecimalField(decimal_places=2, default=2.0, max_digits=5)),
                ("threshold_max", models.DecimalField(decimal_places=2, default=8.0, max_digits=5)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="sensors",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="AlertRule",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("name", models.CharField(max_length=120)),
                ("min_temp", models.DecimalField(decimal_places=2, default=2.0, max_digits=5)),
                ("max_temp", models.DecimalField(decimal_places=2, default=8.0, max_digits=5)),
                ("window_minutes", models.PositiveIntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                ("channels", models.JSONField(blank=True, default=list)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="rules",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "sensor",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="alert_rules",
                        to="monitoring.sensor",
                    ),
                ),
            ],
            options={
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="Measurement",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("temperature", models.DecimalField(decimal_places=2, max_digits=5)),
                ("humidity", models.DecimalField(decimal_places=2, max_digits=5)),
                ("recorded_at", models.DateTimeField(default=django.utils.timezone.now)),
                ("received_at", models.DateTimeField(auto_now_add=True)),
                (
                    "status",
                    models.CharField(
                        choices=[("normal", "Normal"), ("warning", "Warning"), ("critical", "Critical")],
                        default="normal",
                        max_length=32,
                    ),
                ),
                ("note", models.CharField(blank=True, max_length=255)),
                ("raw_payload", models.JSONField(blank=True, default=dict)),
                (
                    "sensor",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="measurements", to="monitoring.sensor"),
                ),
            ],
            options={
                "ordering": ["-recorded_at"],
            },
        ),
        migrations.CreateModel(
            name="Alert",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                (
                    "severity",
                    models.CharField(
                        choices=[("info", "Info"), ("warning", "Warning"), ("critical", "Critical")],
                        default="warning",
                        max_length=32,
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("open", "Open"), ("acknowledged", "Acknowledged"), ("resolved", "Resolved")],
                        default="open",
                        max_length=32,
                    ),
                ),
                ("message", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("acknowledged_at", models.DateTimeField(blank=True, null=True)),
                ("resolved_at", models.DateTimeField(blank=True, null=True)),
                (
                    "acknowledged_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="acknowledged_alerts",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "measurement",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="alerts", to="monitoring.measurement"),
                ),
                (
                    "resolved_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="resolved_alerts",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "rule",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="alerts",
                        to="monitoring.alertrule",
                    ),
                ),
                (
                    "sensor",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="alerts", to="monitoring.sensor"),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Ticket",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("title", models.CharField(max_length=200)),
                ("description", models.TextField(blank=True)),
                (
                    "status",
                    models.CharField(
                        choices=[("open", "Open"), ("in_progress", "In Progress"), ("closed", "Closed")],
                        default="open",
                        max_length=32,
                    ),
                ),
                (
                    "priority",
                    models.CharField(
                        choices=[("low", "Low"), ("medium", "Medium"), ("high", "High"), ("critical", "Critical")],
                        default="medium",
                        max_length=32,
                    ),
                ),
                ("closed_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "alert",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tickets",
                        to="monitoring.alert",
                    ),
                ),
                (
                    "assigned_to",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="assigned_tickets",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "opened_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="opened_tickets",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="AuditLog",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("action", models.CharField(max_length=150)),
                ("target_model", models.CharField(blank=True, max_length=150)),
                ("target_id", models.CharField(blank=True, max_length=150)),
                ("payload", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "actor",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="logs",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at"],
            },
        ),
    ]

