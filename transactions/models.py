from django.db import models
from django.contrib.auth.models import User
from books.models import Book

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    issue_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    return_date = models.DateTimeField(null=True, blank=True)
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_returned = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"

    def calculate_fine(self):
        from django.utils import timezone
        if self.return_date and self.return_date > self.due_date:
            days_overdue = (self.return_date.date() - self.due_date.date()).days
            fine_per_day = 2.00  # As per PRD, configurable later
            self.fine_amount = max(0, days_overdue * fine_per_day)
            self.save()
        return self.fine_amount

class BookRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    note = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.book.title} ({self.status})"
