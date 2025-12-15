import csv
from datetime import datetime, date
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from portal.models import Transaction, Book

class Command(BaseCommand):
    help = "Import transactions from CSV"

    def handle(self, *args, **options):
        with open("data/transactions.csv", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                try:
                    user = User.objects.get(username=row["username"])
                    book = Book.objects.get(isbn=row["isbn"])

                    # Parse dates
                    issued_on_str = row.get("issued_on")
                    issued_on = datetime.strptime(issued_on_str, "%Y-%m-%d %H:%M:%S") if issued_on_str else datetime.now()

                    due_date_str = row["due_date"]
                    due_date = date.fromisoformat(due_date_str) if due_date_str else date.today()

                    returned_on_str = row.get("returned_on")
                    returned_on = date.fromisoformat(returned_on_str) if returned_on_str else None

                    fine_amount_str = row.get("fine_amount", "0")
                    fine_amount = float(fine_amount_str) if fine_amount_str else 0.0

                    # Check if transaction already exists
                    existing = Transaction.objects.filter(
                        user=user,
                        book=book,
                        issued_on=issued_on
                    ).first()

                    if existing:
                        self.stdout.write(f"Skipped existing transaction for {user.username} - {book.title}")
                        continue

                    transaction = Transaction.objects.create(
                        user=user,
                        book=book,
                        issued_on=issued_on,
                        due_date=due_date,
                        returned_on=returned_on,
                        fine_amount=fine_amount
                    )

                    # If returned, ensure available copies are updated (but since import, assume initial state)
                    if returned_on:
                        # Optionally update available_copies, but skip for import to avoid double-counting
                        pass

                    self.stdout.write(self.style.SUCCESS(f"Added transaction for {user.username} - {book.title}"))

                except User.DoesNotExist:
                    self.stderr.write(f"User not found: {row.get('username')}")
                except Book.DoesNotExist:
                    self.stderr.write(f"Book not found: {row.get('isbn')}")
                except ValueError as e:
                    self.stderr.write(f"Date parsing error for row: {e}")
                except Exception as e:
                    self.stderr.write(f"Error importing transaction {row.get('username')} - {row.get('isbn')}: {e}")
