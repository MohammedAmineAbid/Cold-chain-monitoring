from django.contrib.auth import get_user_model
from rest_framework import serializers

from . import models


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = get_user_model()
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "role",
            "organization",
            "phone_number",
            "password",
            "is_active",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = super().create(validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class SensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Sensor
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at", "created_by"]


class MeasurementSerializer(serializers.ModelSerializer):
    sensor = serializers.PrimaryKeyRelatedField(queryset=models.Sensor.objects.all())

    class Meta:
        model = models.Measurement
        fields = "__all__"
        read_only_fields = ["id", "received_at", "status"]


class MeasurementIngestSerializer(serializers.Serializer):
    sensor_token = serializers.CharField()
    temperature = serializers.FloatField()
    humidity = serializers.FloatField()
    recorded_at = serializers.DateTimeField(required=False)


class AlertRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AlertRule
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at", "created_by"]


class AlertSerializer(serializers.ModelSerializer):
    sensor = SensorSerializer(read_only=True)
    measurement = MeasurementSerializer(read_only=True)

    class Meta:
        model = models.Alert
        fields = "__all__"
        read_only_fields = [
            "id",
            "created_at",
            "acknowledged_at",
            "resolved_at",
            "acknowledged_by",
            "resolved_by",
        ]


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Ticket
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at", "closed_at"]


class AuditLogSerializer(serializers.ModelSerializer):
    actor = UserSerializer(read_only=True)

    class Meta:
        model = models.AuditLog
        fields = "__all__"
        read_only_fields = ["id", "created_at"]

