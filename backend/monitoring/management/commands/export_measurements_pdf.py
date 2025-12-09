from pathlib import Path

from django.core.management.base import BaseCommand
from django.utils import timezone
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from monitoring.models import Measurement


class Command(BaseCommand):
    help = "Export measurements to PDF summary"

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            help="Output PDF path",
            default=f"measurements-{timezone.now():%Y%m%d%H%M%S}.pdf",
        )

    def handle(self, *args, **options):
        output_path = Path(options["output"])
        output_path.parent.mkdir(parents=True, exist_ok=True)
        c = canvas.Canvas(str(output_path), pagesize=letter)
        width, height = letter
        y = height - 50
        c.setFont("Helvetica-Bold", 16)
        c.drawString(50, y, "Cold Chain Measurements")
        y -= 30
        c.setFont("Helvetica", 10)
        for measurement in (
            Measurement.objects.select_related("sensor").order_by("-recorded_at")[:500]
        ):
            if y < 80:
                c.showPage()
                y = height - 50
                c.setFont("Helvetica", 10)
            line = (
                f"{measurement.recorded_at:%Y-%m-%d %H:%M} | "
                f"{measurement.sensor.name:<20} | "
                f"T: {measurement.temperature}°C | "
                f"H: {measurement.humidity}% | "
                f"Status: {measurement.status}"
            )
            c.drawString(50, y, line)
            y -= 14
        c.save()
        self.stdout.write(self.style.SUCCESS(f"PDF exported to {output_path}"))

