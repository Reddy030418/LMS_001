import csv
from django.core.management.base import BaseCommand
from portal.models import Book, Department, BookCategory

class Command(BaseCommand):
    help = "Import books from CSV"

    def handle(self, *args, **options):
        with open("data/books.csv", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                try:
                    department = Department.objects.get(code=row["department_code"])
                    category, _ = BookCategory.objects.get_or_create(name=row["category"])

                    book, created = Book.objects.get_or_create(
                        isbn=row["isbn"],
                        defaults={
                            "title": row["title"],
                            "author": row["author"],
                            "publisher": row["publisher"],
                            "edition": row["edition"],
                            "publication_year": int(row["publication_year"]) if row["publication_year"] else None,
                            "department": department,
                            "subject": row["subject"],
                            "category": category,
                            "language": row["language"],
                            "book_type": row["book_type"],
                            "total_copies": int(row["total_copies"]),
                            "available_copies": int(row["available_copies"]),
                            "shelf_no": row["shelf_no"],
                            "description": row["description"],
                        }
                    )

                    if created:
                        self.stdout.write(self.style.SUCCESS(f"Added {book.title}"))
                    else:
                        self.stdout.write(f"Skipped {book.title}")
                except Department.DoesNotExist:
                    self.stderr.write(f"Department not found for code {row.get('department_code')}: {row.get('title')}")
                except Exception as e:
                    self.stderr.write(f"Error importing {row.get('title')}: {e}")
