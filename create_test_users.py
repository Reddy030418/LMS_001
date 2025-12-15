import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'anu_lms.settings')
django.setup()

from django.contrib.auth.models import User
from portal.models import Profile
from django.utils import timezone

# Function to ensure user and profile
def ensure_user(username, password, is_superuser=False, is_staff=False, role='student'):
    user, created = User.objects.get_or_create(username=username, defaults={
        'is_superuser': is_superuser,
        'is_staff': is_staff,
    })
    if not created:
        user.set_password(password)
        user.is_superuser = is_superuser
        user.is_staff = is_staff
        user.save()
    profile, profile_created = Profile.objects.get_or_create(
        user=user,
        defaults={'role': role}
    )
    if not profile_created:
        profile.role = role
        profile.save()
    print(f"User ensured: username='{username}', password='{password}', role='{role}'")

# Ensure admin (superuser)
ensure_user('admin', 'adminpass', is_superuser=True, is_staff=True, role='librarian')

# Ensure librarian (staff)
ensure_user('librarian', 'libpass', is_staff=True, role='librarian')

# Ensure student
ensure_user('student', 'studpass', role='student')
