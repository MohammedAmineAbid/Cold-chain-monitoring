import csv
from pathlib import Path

from django.core.management.base import BaseCommand
from django.utils import timezone

from monitoring.models import Measurement


class Command(BaseCommand):
    help = "Export measurements to CSV"

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            help="Output file path",
            default=f"measurements-{timezone.now():%Y%m%d%H%M%S}.csv",
        )

    def handle(self, *args, **options):
        output_path = Path(options["output"])
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fields = [
            "id",
            "sensor_id",
            "sensor_name",
            "temperature",
            "humidity",
            "recorded_at",
            "status",
        ]
        with output_path.open("w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fields)
            writer.writeheader()
            for measurement in Measurement.objects.select_related("sensor"):
                writer.writerow(
                    {
                        "id": measurement.id,
                        "sensor_id": measurement.sensor_id,
                        "sensor_name": measurement.sensor.name,
                        "temperature": measurement.temperature,
                        "humidity": measurement.humidity,
                        "recorded_at": measurement.recorded_at.isoformat(),
                        "status": measurement.status,
                    }
                )
        self.stdout.write(self.style.SUCCESS(f"CSV exported to {output_path}"))

