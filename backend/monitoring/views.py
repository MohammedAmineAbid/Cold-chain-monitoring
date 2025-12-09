from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Alert, AlertRule, AuditLog, Measurement, Sensor, Ticket
from .permissions import IsAdminOrReadOnly
from .serializers import (
    AlertRuleSerializer,
    AlertSerializer,
    AuditLogSerializer,
    MeasurementIngestSerializer,
    MeasurementSerializer,
    SensorSerializer,
    TicketSerializer,
    UserSerializer,
)
from .services import record_audit, store_measurement

User = get_user_model()


class SensorViewSet(viewsets.ModelViewSet):
    queryset = Sensor.objects.all()
    serializer_class = SensorSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ["is_active", "location"]
    search_fields = ["name", "serial_number", "location"]
    ordering_fields = ["name", "created_at"]

    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user)
        record_audit(action="sensor.created", actor=self.request.user, target=instance)

    def perform_update(self, serializer):
        instance = serializer.save()
        record_audit(action="sensor.updated", actor=self.request.user, target=instance)

    def perform_destroy(self, instance):
        record_audit(action="sensor.deleted", actor=self.request.user, target=instance)
        super().perform_destroy(instance)


class MeasurementViewSet(viewsets.ModelViewSet):
    queryset = Measurement.objects.select_related("sensor")
    serializer_class = MeasurementSerializer
    filterset_fields = ["sensor", "status"]
    search_fields = ["sensor__name"]
    ordering_fields = ["recorded_at"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = store_measurement(
            sensor=serializer.validated_data["sensor"],
            temperature=float(serializer.validated_data["temperature"]),
            humidity=float(serializer.validated_data["humidity"]),
            recorded_at=serializer.validated_data.get("recorded_at") or timezone.now(),
            actor=request.user,
            raw_payload=serializer.validated_data,
        )
        output = self.get_serializer(result.measurement)
        headers = self.get_success_headers(output.data)
        return Response(output.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_update(self, serializer):
        instance = serializer.save()
        record_audit(action="measurement.updated", actor=self.request.user, target=instance)

    def perform_destroy(self, instance):
        record_audit(action="measurement.deleted", actor=self.request.user, target=instance)
        super().perform_destroy(instance)


class MeasurementIngestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = MeasurementIngestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            sensor = Sensor.objects.get(token=serializer.validated_data["sensor_token"])
        except Sensor.DoesNotExist:
            return Response(
                {"detail": "Unknown sensor token"}, status=status.HTTP_400_BAD_REQUEST
            )

        result = store_measurement(
            sensor=sensor,
            temperature=serializer.validated_data["temperature"],
            humidity=serializer.validated_data["humidity"],
            recorded_at=serializer.validated_data.get("recorded_at") or timezone.now(),
            actor=None,
            raw_payload=serializer.validated_data,
        )
        return Response(
            {
                "measurement_id": result.measurement.id,
                "alerts": [str(alert.id) for alert in result.alerts],
            },
            status=status.HTTP_201_CREATED,
        )


class AlertRuleViewSet(viewsets.ModelViewSet):
    queryset = AlertRule.objects.select_related("sensor")
    serializer_class = AlertRuleSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ["sensor", "is_active"]
    search_fields = ["name"]

    def perform_create(self, serializer):
        instance = serializer.save(created_by=self.request.user)
        record_audit(action="alert_rule.created", actor=self.request.user, target=instance)

    def perform_update(self, serializer):
        instance = serializer.save()
        record_audit(action="alert_rule.updated", actor=self.request.user, target=instance)

    def perform_destroy(self, instance):
        record_audit(action="alert_rule.deleted", actor=self.request.user, target=instance)
        super().perform_destroy(instance)


class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.select_related("sensor", "measurement", "rule")
    serializer_class = AlertSerializer
    filterset_fields = ["status", "severity", "sensor"]
    search_fields = ["sensor__name", "message"]

    def perform_update(self, serializer):
        alert = serializer.save()
        record_audit(action="alert.updated", actor=self.request.user, target=alert)

    def perform_destroy(self, instance):
        record_audit(action="alert.deleted", actor=self.request.user, target=instance)
        super().perform_destroy(instance)

    @action(detail=True, methods=["post"])
    def acknowledge(self, request, pk=None):
        alert = self.get_object()
        alert.status = Alert.Status.ACKNOWLEDGED
        alert.acknowledged_at = timezone.now()
        alert.acknowledged_by = request.user
        alert.save()
        record_audit(action="alert.acknowledged", actor=request.user, target=alert)
        return Response(self.get_serializer(alert).data)

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        alert = self.get_object()
        alert.status = Alert.Status.RESOLVED
        alert.resolved_at = timezone.now()
        alert.resolved_by = request.user
        alert.save()
        record_audit(action="alert.resolved", actor=request.user, target=alert)
        return Response(self.get_serializer(alert).data)


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.select_related("alert", "opened_by", "assigned_to")
    serializer_class = TicketSerializer
    filterset_fields = ["status", "priority"]
    search_fields = ["title", "description"]

    def perform_create(self, serializer):
        instance = serializer.save(opened_by=self.request.user)
        record_audit(action="ticket.created", actor=self.request.user, target=instance)

    def perform_update(self, serializer):
        instance = serializer.save()
        if instance.status == Ticket.Status.CLOSED and not instance.closed_at:
            instance.closed_at = timezone.now()
            instance.save(update_fields=["closed_at"])
        record_audit(action="ticket.updated", actor=self.request.user, target=instance)

    def perform_destroy(self, instance):
        record_audit(action="ticket.deleted", actor=self.request.user, target=instance)
        super().perform_destroy(instance)


class AuditLogViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = AuditLog.objects.select_related("actor")
    serializer_class = AuditLogSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ["action", "actor"]
    search_fields = ["action", "target_model"]


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ["role", "is_active"]
    search_fields = ["username", "email"]

    def perform_create(self, serializer):
        user = serializer.save()
        record_audit(action="user.created", actor=self.request.user, target=user)

    def perform_update(self, serializer):
        user = serializer.save()
        record_audit(action="user.updated", actor=self.request.user, target=user)

    def perform_destroy(self, instance):
        record_audit(action="user.deleted", actor=self.request.user, target=instance)
        super().perform_destroy(instance)
