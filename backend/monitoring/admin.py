from django.contrib import admin

from .models import Alert, AlertRule, AuditLog, Measurement, Sensor, Ticket, User ,Channel


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "role", "is_active")
    search_fields = ("username", "email")
    list_filter = ("role", "is_active")


@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ("name", "serial_number", "location", "threshold_min", "threshold_max")
    search_fields = ("name", "serial_number", "location")
    list_filter = ("is_active",)


@admin.register(Measurement)
class MeasurementAdmin(admin.ModelAdmin):
    list_display = ("sensor", "temperature", "humidity", "recorded_at", "status")
    list_filter = ("sensor", "status")
    search_fields = ("sensor__name",)


@admin.register(AlertRule)
class AlertRuleAdmin(admin.ModelAdmin):
    list_display = ("name", "sensor", "min_temp", "max_temp", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ("sensor", "severity", "status", "created_at")
    list_filter = ("severity", "status")
    search_fields = ("sensor__name",)

@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ("name", "channel_type", "target")



@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "priority", "created_at")
    list_filter = ("status", "priority")
    search_fields = ("title",)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("action", "actor", "created_at")
    list_filter = ("action",)
    search_fields = ("action", "actor__username")
