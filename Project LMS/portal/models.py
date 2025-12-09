from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal

class Department(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True, blank=True)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, blank=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    subject = models.CharField(max_length=255, blank=True)
    isbn = models.CharField(max_length=20, blank=True)
    barcode = models.CharField(max_length=50, unique=True, null=True, blank=True)
    publisher = models.CharField(max_length=255, blank=True)
    rack_number = models.CharField(max_length=50, blank=True)

    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)

    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    description = models.TextField(blank=True)

    # flags for homepage sections
    is_trending = models.BooleanField(default=False)
    is_classic = models.BooleanField(default=False)
    is_romance = models.BooleanField(default=False)
    is_kids = models.BooleanField(default=False)
    is_thriller = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    student_id = models.CharField(max_length=50, blank=True)
    is_active_member = models.BooleanField(default=True)

    def __str__(self):
        return self.user.get_username()


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portal_transactions')
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    issued_on = models.DateTimeField(default=timezone.now)
    due_date = models.DateField()
    returned_on = models.DateField(null=True, blank=True)
    fine_amount = models.DecimalField(max_digits=7, decimal_places=2, default=0)

    def is_overdue(self):
        if self.returned_on:
            return self.returned_on > self.due_date
        return timezone.localdate() > self.due_date

    def __str__(self):
        return f"{self.book.title} → {self.user.username}"


class BookRequest(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portal_bookrequests')
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    note = models.TextField(blank=True)

    def __str__(self):
        return f"{self.book.title} request by {self.user.username}"


class NewsItem(models.Model):
    title = models.CharField(max_length=255)
    summary = models.TextField(blank=True)
    image = models.ImageField(upload_to='news/', null=True, blank=True)
    published_on = models.DateField(default=timezone.localdate)

    def __str__(self):
        return self.title


class Eresource(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    url = models.URLField()
    letter = models.CharField(max_length=1)   # A–Z or #

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
