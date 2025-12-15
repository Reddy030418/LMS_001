import csv
from django.core.management.base import BaseCommand
from portal.models import BookCategory

class Command(BaseCommand):
    help = "Import book categories from CSV"

    def handle(self, *args, **options):
        with open("data/book_categories.csv", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                category, created = BookCategory.objects.get_or_create(
                    name=row["name"],
                    defaults={
                        "description": row.get("description", "")
                    }
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f"Added {category.name}"))
                else:
                    self.stdout.write(f"Skipped {category.name}")
