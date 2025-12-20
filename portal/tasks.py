from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from .models import Transaction, BookRequest
from .utils import calculate_fine

@shared_task
def send_overdue_reminders():
    """Send overdue reminder emails to students with overdue books."""
    today = timezone.localdate()

    overdue_transactions = Transaction.objects.filter(
        returned_on__isnull=True,
        due_date__lt=today
    ).select_related("user", "book")

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

@shared_task
def send_request_approval_email(request_id, approved):
    """Send email notification for book request approval/rejection."""
    try:
        request = BookRequest.objects.select_related('user', 'book').get(id=request_id)
        status = "approved" if approved else "rejected"
        subject = f"Book Request {status.capitalize()} – '{request.book.title}'"
        message = (
            f"Dear {request.user.username},\n\n"
            f"Your request for the book '{request.book.title}' has been {status}.\n\n"
            f"Request Date: {request.requested_on}\n"
            f"Status: {status.capitalize()}\n\n"
            "If approved, you can collect the book from the library.\n\n"
            "— Acharya Nagarjuna University Library"
        )

        if request.user.email:
            send_mail(
                subject,
                message,
                "library@anu.ac.in",
                [request.user.email],
                fail_silently=True
            )
    except BookRequest.DoesNotExist:
        pass
