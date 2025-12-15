import csv
from django.core.management.base import BaseCommand
from portal.models import Department

class Command(BaseCommand):
    help = "Import departments from CSV"

    def handle(self, *args, **options):
        with open("data/departments.csv", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                dept, created = Department.objects.get_or_create(
                    code=row["code"],
                    defaults={
                        "name": row["name"],
                        "description": row.get("description", ""),
                        "is_active": row["is_active"].lower() == "true"
                    }
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f"Added {dept.name}"))
                else:
                    self.stdout.write(f"Skipped {dept.name}")
