import random
from datetime import timedelta, time, datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
from django.db.models import Q, F, Sum
from django.contrib.auth.models import User
from portal.models import Book, Transaction, Profile

FINE_PER_DAY = 2  # Matches LMS fine policy
ISSUE_DAYS = 14


class Command(BaseCommand):
    help = "Generate realistic synthetic book transactions (bulk-optimized for PostgreSQL)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=3000,
            help="Number of transactions to generate (default: 3000)",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=500,
            help="Batch size for bulk_create (default: 500)",
        )
        parser.add_argument(
            "--cleanup",
            action="store_true",
            help="Delete ALL existing transactions before generating",
        )

    def handle(self, *args, **options):
        if options["cleanup"]:
            deleted_count, _ = Transaction.objects.all().delete()
            self.stdout.write(self.style.WARNING("Deleted %d existing transactions." % deleted_count))
            Book.objects.update(available_copies=F('total_copies'))
            self.stdout.write(self.style.WARNING("Reset all book available_copies to total_copies."))

        # Fetch student users
        users = list(User.objects.filter(profile__role="student"))
        if not users:
            self.stdout.write(self.style.ERROR("No student users found. Run import_users first."))
            return

        # Fetch books with bias toward academic subjects
        academic_books = list(Book.objects.filter(
            Q(subject__icontains="Algorithms") |
            Q(subject__icontains="Programming") |
            Q(subject__icontains="Economics") |
            Q(subject__icontains="Law") |
            Q(subject__icontains="Engineering") |
            Q(subject__icontains="Exam") |
            Q(subject__icontains="Academic") |
            Q(subject__icontains="Textbook")
        ))
        all_books = list(Book.objects.all())
        other_books = [b for b in all_books if b not in academic_books]
        other_sample = random.sample(other_books, min(30, len(other_books)))
        books = academic_books + other_sample

        if not books:
            self.stdout.write(self.style.ERROR("No books found. Run import_books first."))
            return

        target_count = options["count"]
        batch_size = options["batch_size"]
        self.stdout.write("Generating %d transactions in batches of %d..." % (target_count, batch_size))

        # Prepare all transactions in memory
        transaction_batch = []
        book_adjustments = {}  # book_id -> net change to available_copies

        for i in range(target_count):
            user = random.choice(users)
            book = random.choice(books)

            # Issue date in last 6 months
            issue_date = timezone.now().date() - timedelta(days=random.randint(1, 180))
            due_date = issue_date + timedelta(days=ISSUE_DAYS)
            issue_datetime = timezone.make_aware(datetime.combine(issue_date, time(0, 0)))

            # Return status: 70% on time, 20% late, 10% active
            roll = random.random()
            if roll < 0.70:
                return_date = issue_date + timedelta(days=random.randint(0, ISSUE_DAYS))
            elif roll < 0.90:
                return_date = due_date + timedelta(days=random.randint(1, 15))
            else:
                return_date = None

            # Fine calculation
            fine = Decimal(0)
            if return_date and return_date > due_date:
                fine = Decimal((return_date - due_date).days * FINE_PER_DAY)

            tx = Transaction(
                user=user,
                book=book,
                issued_on=issue_datetime,
                due_date=due_date,
                returned_on=return_date,
                fine_amount=fine,
            )
            transaction_batch.append(tx)

            # Track available_copies adjustments
            bid = book.id
            if bid not in book_adjustments:
                book_adjustments[bid] = 0
            book_adjustments[bid] -= 1  # issue
            if return_date:
                book_adjustments[bid] += 1  # return

            # Bulk insert when batch is full
            if len(transaction_batch) >= batch_size:
                Transaction.objects.bulk_create(transaction_batch, batch_size=batch_size)
                self.stdout.write("  Inserted %d transactions..." % (i + 1))
                transaction_batch = []

        # Insert remaining
        if transaction_batch:
            Transaction.objects.bulk_create(transaction_batch, batch_size=batch_size)

        # Bulk update book available_copies
        books_to_update = []
        for book in Book.objects.filter(id__in=book_adjustments.keys()):
            adjustment = book_adjustments[book.id]
            book.available_copies = max(0, book.available_copies + adjustment)
            books_to_update.append(book)

        if books_to_update:
            Book.objects.bulk_update(books_to_update, ['available_copies'], batch_size=batch_size)

        # Report stats
        total_transactions = Transaction.objects.count()
        active_issues = Transaction.objects.filter(returned_on__isnull=True).count()
        overdue = Transaction.objects.filter(
            returned_on__isnull=True,
            due_date__lt=timezone.now().date()
        ).count()
        total_fines = Transaction.objects.filter(
            fine_amount__gt=0
        ).aggregate(total=Sum('fine_amount'))['total'] or 0

        self.stdout.write(
            self.style.SUCCESS(
                "\n[OK] Generated %d transactions.\n"
                "  Total in DB:    %d\n"
                "  Active issues:  %d (%.1f%%)\n"
                "  Overdue:        %d\n"
                "  Total fines:    Rs.%s"
                % (
                    target_count,
                    total_transactions,
                    active_issues,
                    active_issues / max(total_transactions, 1) * 100,
                    overdue,
                    total_fines,
                )
            )
        )
