import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import time, datetime
from decimal import Decimal
from django.db.models import Q
from django.contrib.auth.models import User
from portal.models import Book, Transaction, Profile

FINE_PER_DAY = 2  # Adjust to match LMS fine policy
ISSUE_DAYS = 14

class Command(BaseCommand):
    help = "Generate realistic synthetic book transactions for testing dashboards, fines, and overdue logic."

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=3000,
            help="Number of transactions to generate (default: 3000)",
        )
        parser.add_argument(
            "--cleanup",
            action="store_true",
            help="Delete existing synthetic transactions before generating (if tagged)",
        )

    def handle(self, *args, **options):
        if options["cleanup"]:
            # Optional: Delete previous synthetic transactions (e.g., if tagged with a field)
            # For now, assume no tag; user can manually clear if needed
            self.stdout.write(self.style.WARNING("Cleanup flag set but no tagged transactions to delete. Skipping."))

        # Fetch student users (prefer students)
        users = list(User.objects.filter(profile__role="student"))
        if not users:
            self.stdout.write(self.style.ERROR("No student users found. Run import_users first."))
            return

        # Fetch books (bias toward academic/programming/exam)
        academic_books = Book.objects.filter(
            Q(subject__icontains="Algorithms") |
            Q(subject__icontains="Programming") |
            Q(subject__icontains="Economics") |
            Q(subject__icontains="Law") |
            Q(subject__icontains="Engineering") |
            Q(subject__icontains="Exam") |
            Q(subject__icontains="Academic") |
            Q(subject__icontains="Textbook")
        )
        all_books = list(Book.objects.all())
        # Bias: 70% academic, 30% others
        num_academic = int(0.7 * len(all_books))
        academic_list = list(academic_books)[:num_academic]
        other_list = random.sample([b for b in all_books if b not in academic_list], min(30, len(all_books) - len(academic_list)))
        books = academic_list + other_list

        if not books:
            self.stdout.write(self.style.ERROR("No books found. Run import_books first."))
            return

        created = 0
        target_count = options["count"]

        self.stdout.write(f"Generating up to {target_count} transactions...")

        while created < target_count and users and books:
            user = random.choice(users)
            book = random.choice(books)

            # Generate dates: issue in last 6 months (180 days)
            issue_date = timezone.now().date() - timedelta(days=random.randint(1, 180))
            due_date = issue_date + timedelta(days=ISSUE_DAYS)
            issue_datetime = timezone.make_aware(datetime.combine(issue_date, time(0, 0)))

            # Roll for return status
            status_roll = random.random()
            if status_roll < 0.7:  # 70% returned on time
                return_date = issue_date + timedelta(days=random.randint(0, ISSUE_DAYS))  # 0 to allow same day return
            elif status_roll < 0.9:  # 20% late
                late_days = random.randint(1, 15)
                return_date = due_date + timedelta(days=late_days)
            else:  # 10% active (not returned)
                return_date = None

            # Calculate fine if late
            fine = 0
            if return_date and return_date > due_date:
                fine = (return_date - due_date).days * FINE_PER_DAY

            # Create transaction (adjust field names to match model: issued_on, returned_on, fine_amount)
            Transaction.objects.create(
                user=user,
                book=book,
                issued_on=issue_datetime,
                due_date=due_date,
                returned_on=return_date,
                fine_amount=Decimal(fine),
            )

            # Adjust available_copies: -1 for issue, +1 if returned (net 0 for closed, -1 for active)
            book.available_copies -= 1
            if return_date:
                book.available_copies += 1
            # Ensure non-negative
            if book.available_copies < 0:
                book.available_copies = 0
            book.save()

            created += 1

            if created % 500 == 0:
                self.stdout.write(f"Generated {created} transactions...")

        # Report stats
        total_transactions = Transaction.objects.count()
        overdue = Transaction.objects.filter(returned_on__isnull=True, due_date__lt=timezone.now().date()).count()
        active_issues = Transaction.objects.filter(returned_on__isnull=True).count()
        total_fines = sum(t.fine_amount for t in Transaction.objects.all() if t.fine_amount)

        self.stdout.write(
            self.style.SUCCESS(
                f"Generated {created} transactions. "
                f"Total: {total_transactions}, "
                f"Active issues: {active_issues} ({active_issues/total_transactions*100:.1f}%), "
                f"Overdue: {overdue}, "
                f"Total fines: ₹{total_fines}"
            )
        )
