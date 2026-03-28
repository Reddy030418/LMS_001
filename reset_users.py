import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'anu_lms.settings')
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile
from django.db import transaction

@transaction.atomic
def reset_users():
    print("Deleting all existing users...")
    User.objects.all().delete()
    print("Existing users deleted.")

    # Details
    admin_creds = ('admin', 'admin@123')
    librarians_creds = [('librarian1', 'lib@123'), ('librarian2', 'lib@123')]
    students_creds = [
        ('student1', 'stu@123', 'CS101'),
        ('student2', 'stu@123', 'CS102'),
        ('student3', 'stu@123', 'ME201'),
        ('student4', 'stu@123', 'EE301'),
        ('student5', 'stu@123', 'EC401'),
    ]

    print("Creating admin...")
    admin = User.objects.create_superuser(username=admin_creds[0], email='admin@anu.edu', password=admin_creds[1])
    # profile for admin
    prof, _ = UserProfile.objects.get_or_create(user=admin)
    prof.role = 'admin'
    prof.save()

    print("Creating librarians...")
    for username, password in librarians_creds:
        user = User.objects.create_user(username=username, email=f'{username}@anu.edu', password=password)
        user.is_staff = True
        user.save()
        prof, _ = UserProfile.objects.get_or_create(user=user)
        prof.role = 'librarian'
        prof.save()

    print("Creating students...")
    for idx, (username, password, sid) in enumerate(students_creds):
        user = User.objects.create_user(username=username, email=f'{username}@anu.edu', password=password)
        prof, _ = UserProfile.objects.get_or_create(user=user)
        prof.role = 'student'
        prof.student_id = sid
        prof.save()

    print("All accounts created successfully!")

if __name__ == "__main__":
    reset_users()
