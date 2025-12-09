from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AlertRuleViewSet,
    AlertViewSet,
    AuditLogViewSet,
    MeasurementIngestView,
    MeasurementViewSet,
    SensorViewSet,
    TicketViewSet,
    UserViewSet,
)

router = DefaultRouter()
router.register("sensors", SensorViewSet, basename="sensor")
router.register("measurements", MeasurementViewSet, basename="measurement")
router.register("alert-rules", AlertRuleViewSet, basename="alert-rule")
router.register("alerts", AlertViewSet, basename="alert")
router.register("tickets", TicketViewSet, basename="ticket")
router.register("audit-logs", AuditLogViewSet, basename="audit-log")
router.register("users", UserViewSet, basename="user")

urlpatterns = [
    path("ingest/", MeasurementIngestView.as_view(), name="measurement-ingest"),
    path("", include(router.urls)),
]

