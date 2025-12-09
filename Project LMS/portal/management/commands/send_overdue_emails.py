from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from portal.models import Transaction
from portal.utils import calculate_fine

class Command(BaseCommand):
    help = "Send overdue reminder emails to students"

    def handle(self, *args, **kwargs):
        today = timezone.localdate()

        overdue_transactions = Transaction.objects.filter(
            returned_on__isnull=True,
            due_date__lt=today
        ).select_related("user", "book")

        if not overdue_transactions:
            self.stdout.write(self.style.SUCCESS("No overdue books today."))
            return

        for tx in overdue_transactions:
            fine = calculate_fine(tx.due_date, today)

            subject = f"Overdue Book Reminder – '{tx.book.title}'"
            message = (
                f"Dear {tx.user.username},\n\n"
                f"The book '{tx.book.title}' issued to you was due on {tx.due_date}.\n"
                f"Today's date: {today}\n"
                f"Days overdue: {(today - tx.due_date).days}\n"
                f"Current estimated fine: ₹{fine}\n\n"
                "Please return the book as soon as possible.\n\n"
                "— Acharya Nagarjuna University Library"
            )

            if tx.user.email:
                send_mail(
                    subject,
                    message,
                    "library@anu.ac.in",
                    [tx.user.email],
                    fail_silently=True
                )

            self.stdout.write(
                self.style.WARNING(f"Email sent to {tx.user.email} about '{tx.book.title}'")
            )

        self.stdout.write(self.style.SUCCESS("Overdue reminder task finished."))
