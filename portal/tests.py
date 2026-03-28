from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .models import Department, BookCategory, Book, Profile, Transaction, BookRequest, NewsItem, Eresource

class PortalModelsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='portaluser', password='password123')
        self.dept = Department.objects.create(name='Computer Science', code='CS', description='CS Dept')
        self.category = BookCategory.objects.create(name='Fiction', description='Fiction Books')
        self.book = Book.objects.create(
            title='The Great Gatsby',
            author='F. Scott Fitzgerald',
            department=self.dept,
            category=self.category,
            isbn='1111111111111',
            total_copies=10,
            available_copies=10,
            is_trending=True
        )

    def test_department_creation(self):
        self.assertEqual(self.dept.name, 'Computer Science')
        self.assertEqual(self.dept.code, 'CS')
        self.assertTrue(self.dept.is_active)
        self.assertEqual(str(self.dept), 'Computer Science')

    def test_book_category_creation(self):
        self.assertEqual(self.category.name, 'Fiction')
        self.assertEqual(str(self.category), 'Fiction')

    def test_book_creation(self):
        self.assertEqual(self.book.title, 'The Great Gatsby')
        self.assertEqual(self.book.department, self.dept)
        self.assertEqual(self.book.category, self.category)
        self.assertTrue(self.book.is_trending)
        self.assertEqual(self.book.total_copies, 10)
        self.assertEqual(str(self.book), 'The Great Gatsby')

    def test_profile_creation(self):
        profile = Profile.objects.create(
            user=self.user,
            department=self.dept,
            student_id='PSTU001',
            role='student'
        )
        self.assertEqual(profile.user.username, 'portaluser')
        self.assertEqual(profile.role, 'student')
        self.assertEqual(str(profile), 'portaluser')

    def test_transaction_creation(self):
        now = timezone.now()
        due = now.date() + timedelta(days=7)
        transaction = Transaction.objects.create(
            user=self.user,
            book=self.book,
            due_date=due,
            status='ISSUED'
        )
        self.assertEqual(transaction.status, 'ISSUED')
        self.assertEqual(transaction.user.username, 'portaluser')
        self.assertFalse(transaction.is_overdue())

    def test_transaction_overdue(self):
        now = timezone.now()
        due = now.date() - timedelta(days=2)
        transaction = Transaction.objects.create(
            user=self.user,
            book=self.book,
            due_date=due,
            status='ISSUED'
        )
        self.assertTrue(transaction.is_overdue())
        
    def test_transaction_returned_overdue(self):
        now = timezone.now()
        due = now.date() - timedelta(days=5)
        ret = now.date() - timedelta(days=1)
        transaction = Transaction.objects.create(
            user=self.user,
            book=self.book,
            due_date=due,
            returned_on=ret,
            status='RETURNED'
        )
        self.assertTrue(transaction.is_overdue())

    def test_book_request_creation(self):
        req = BookRequest.objects.create(
            user=self.user,
            book=self.book,
            status='PENDING',
        )
        self.assertEqual(req.status, 'PENDING')
        self.assertIn('The Great Gatsby', str(req))

    def test_news_item_creation(self):
        news = NewsItem.objects.create(
            title='Library Update',
            summary='New books added',
        )
        self.assertEqual(news.title, 'Library Update')

    def test_eresource_creation(self):
        resource = Eresource.objects.create(
            name='IEEE Xplore',
            url='https://ieeexplore.ieee.org',
            letter='I'
        )
        self.assertEqual(resource.name, 'IEEE Xplore')
        self.assertEqual(resource.letter, 'I')


class PortalViewsTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_index_view_loads(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_search_view_loads_and_filters(self):
        # Create a book specific for search
        from .models import Book, Department
        dept = Department.objects.create(name='Test Dept')
        Book.objects.create(title='Unique Searchable Title', author='Author X', department=dept)
        
        response = self.client.get('/search/?q=Searchable')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Unique Searchable Title')

    def test_advanced_search_filters_correctly(self):
        from .models import Book, Department
        dept = Department.objects.create(name='Physics')
        Book.objects.create(title='Quantum Mechanics', author='Scientist A', department=dept, available_copies=2)
        Book.objects.create(title='Classical Mechanics', author='Scientist B', department=dept, available_copies=0)

        # Advanced search for available books
        response = self.client.get('/advanced-search/?title=Mechanics&availability=available')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Quantum Mechanics')
        self.assertNotContains(response, 'Classical Mechanics')  # shouldn't show zero avialable copies if queried as available

    def test_ask_librarian_post_valid_data(self):
        # Valid POST request
        response = self.client.post('/ask-librarian/', {
            'name': 'Student Name',
            'email': 'student@example.com',
            'message': 'Where is the CS lab?'
        })
        # Expect successful redirect
        self.assertEqual(response.status_code, 302)

    def test_ask_librarian_post_invalid_data(self):
        # Missing message
        response = self.client.post('/ask-librarian/', {
            'name': 'Student Name',
            'email': 'invalid'
        })
        self.assertEqual(response.status_code, 200) # Form re-renders with errors
        self.assertContains(response, 'Please enter a valid email address.')
        self.assertContains(response, 'Message is required.')

    def test_book_request_endpoint_auth_required(self):
        # Unauthenticated users shouldn't be able to request
        response = self.client.post('/request-book/1/')
        self.assertEqual(response.status_code, 401)
