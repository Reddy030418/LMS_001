from django.db import models

class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    edition = models.CharField(max_length=50, blank=True)
    publisher = models.CharField(max_length=200, blank=True)
    isbn = models.CharField(max_length=13, unique=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100, blank=True)
    rack = models.CharField(max_length=50, blank=True)
    total_copies = models.PositiveIntegerField(default=1)
    available_copies = models.PositiveIntegerField(default=1)
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    is_featured = models.BooleanField(default=False)

    def __str__(self):
        return self.title
