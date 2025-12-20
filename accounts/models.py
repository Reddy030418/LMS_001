from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('librarian', 'Librarian'),
        ('admin', 'Admin'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    student_id = models.CharField(max_length=50, blank=True)
    roll_number = models.CharField(max_length=50, blank=True)
    course = models.CharField(max_length=100, blank=True)
    year = models.PositiveIntegerField(null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    is_active_member = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"
