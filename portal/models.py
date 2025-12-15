from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal

class Department(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class BookCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    author = models.CharField(max_length=255, blank=True, db_index=True)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, db_index=True)
    category = models.ForeignKey(BookCategory, on_delete=models.SET_NULL, null=True, blank=True, db_index=True)
    subject = models.CharField(max_length=255, blank=True, db_index=True)
    isbn = models.CharField(max_length=20, unique=True, blank=True, db_index=True)
    edition = models.CharField(max_length=50, blank=True)
    publication_year = models.PositiveIntegerField(null=True, blank=True)
    language = models.CharField(max_length=50, blank=True)
    book_type = models.CharField(max_length=50, blank=True)
    barcode = models.CharField(max_length=50, unique=True, null=True, blank=True)
    publisher = models.CharField(max_length=255, blank=True)
    shelf_no = models.CharField(max_length=50, blank=True)
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
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, db_index=True)
    student_id = models.CharField(max_length=50, blank=True)
    roll_number = models.CharField(max_length=50, blank=True)
    course = models.CharField(max_length=100, blank=True)
    year = models.PositiveIntegerField(null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    is_active_member = models.BooleanField(default=True)
    role = models.CharField(max_length=20, choices=[('student', 'Student'), ('librarian', 'Librarian'), ('admin', 'Admin')], default='student', db_index=True)

    def __str__(self):
        return self.user.get_username()


class Transaction(models.Model):
    STATUS_CHOICES = (
        ('ISSUED', 'Issued'),
        ('RETURNED', 'Returned'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ISSUED', db_index=True)

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portal_transactions', db_index=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, db_index=True)
    issued_on = models.DateTimeField(default=timezone.now, db_index=True)
    due_date = models.DateField(db_index=True)
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

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portal_bookrequests', db_index=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, db_index=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    note = models.TextField(blank=True)

    def __str__(self):
        return f"{self.book.title} request by {self.user.username}"


class NewsItem(models.Model):
    title = models.CharField(max_length=255, db_index=True)
    summary = models.TextField(blank=True)
    image = models.ImageField(upload_to='news/', null=True, blank=True)
    published_on = models.DateField(default=timezone.localdate, db_index=True)

    def __str__(self):
        return self.title


class Eresource(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True)
    url = models.URLField()
    letter = models.CharField(max_length=1)   # A–Z or #

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
