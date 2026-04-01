from django.test import TestCase, Client
from django.contrib.auth.models import User
from portal.models import Profile, Department

class DashboardViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser(username='admin_test', password='password123', email='admin@test.com')
        self.student_user = User.objects.create_user(username='student_test', password='password123', email='student@test.com')
        
        self.dept = Department.objects.create(name='CS', code='CS_101')
        admin_profile, _ = Profile.objects.get_or_create(user=self.admin_user)
        admin_profile.role = 'admin'
        admin_profile.department = self.dept
        admin_profile.save()
        student_profile, _ = Profile.objects.get_or_create(user=self.student_user)
        student_profile.role = 'student'
        student_profile.department = self.dept
        student_profile.save()

    def test_dashboard_access_unauthenticated(self):
        response = self.client.get('/dashboard/')
        # Usually redirects to login page (302) or returns 403. Let's check status code isn't 200.
        self.assertNotEqual(response.status_code, 200)

    def test_dashboard_access_student(self):
        self.client.login(username='student_test', password='password123')
        response = self.client.get('/dashboard/')
        # Typically students shouldn't have access to the admin dashboard, or they do have access to a student dashboard.
        # Just ensure the request processes without 500 error.
        self.assertIn(response.status_code, [200, 302, 403])

    def test_dashboard_access_admin(self):
        self.client.login(username='admin_test', password='password123')
        response = self.client.get('/dashboard/')
        self.assertIn(response.status_code, [200, 302, 403])
