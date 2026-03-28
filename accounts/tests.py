from django.test import TestCase
from django.contrib.auth.models import User
from .models import UserProfile

class UserProfileModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='teststudent', password='password123')
        self.librarian_user = User.objects.create_user(username='testlibrarian', password='password123')
        
    def test_user_profile_creation_student(self):
        # The signals might automatically create a UserProfile. Let's check if it exists.
        profile, created = UserProfile.objects.get_or_create(user=self.user)
        profile.role = 'student'
        profile.student_id = 'STU001'
        profile.roll_number = 'RN001'
        profile.course = 'Computer Science'
        profile.year = 2
        profile.phone = '1234567890'
        profile.save()

        self.assertEqual(profile.user.username, 'teststudent')
        self.assertEqual(profile.role, 'student')
        self.assertEqual(profile.student_id, 'STU001')
        self.assertTrue(profile.is_active_member)
        self.assertEqual(str(profile), 'teststudent - student')

    def test_user_profile_creation_librarian(self):
        profile, created = UserProfile.objects.get_or_create(user=self.librarian_user)
        profile.role = 'librarian'
        profile.save()
        
        self.assertEqual(profile.role, 'librarian')
        self.assertEqual(str(profile), 'testlibrarian - librarian')
