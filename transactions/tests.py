from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from books.models import Department as BooksDepartment, Book
from .models import Transaction, BookRequest

class TransactionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.dept = BooksDepartment.objects.create(name='Mathematics')
        self.book = Book.objects.create(
            title='Algebra Basics',
            author='Math Guru',
            isbn='9876543210123',
            department=self.dept,
            total_copies=3,
            available_copies=3
        )

    def test_transaction_creation(self):
        due = timezone.now() + timedelta(days=7)
        transaction = Transaction.objects.create(
            user=self.user,
            book=self.book,
            due_date=due,
            is_returned=False
        )
        self.assertEqual(transaction.user.username, 'testuser')
        self.assertEqual(transaction.book.title, 'Algebra Basics')
        self.assertFalse(transaction.is_returned)
        self.assertEqual(transaction.fine_amount, 0.00)

    def test_calculate_fine_not_overdue(self):
        now = timezone.now()
        transaction = Transaction.objects.create(
            user=self.user,
            book=self.book,
            due_date=now + timedelta(days=2)
        )
        transaction.return_date = now + timedelta(days=1)
        transaction.save()
        
        fine = transaction.calculate_fine()
        self.assertEqual(fine, 0.00)

    def test_calculate_fine_overdue(self):
        now = timezone.now()
        transaction = Transaction.objects.create(
            user=self.user,
            book=self.book,
            due_date=now - timedelta(days=5) # Due 5 days ago
        )
        transaction.return_date = now
        transaction.save()
        
        fine = transaction.calculate_fine()
        # 5 days overdue * 2.0 = 10.0
        self.assertEqual(fine, 10.00)

class BookRequestModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser2', password='password123')
        self.dept = BooksDepartment.objects.create(name='Science')
        self.book = Book.objects.create(
            title='Science Basics',
            author='Science Guru',
            isbn='9996543210123',
            department=self.dept,
        )

    def test_book_request_creation(self):
        req = BookRequest.objects.create(
            user=self.user,
            book=self.book,
            status='pending',
            note='Needed for assignment'
        )
        self.assertEqual(req.status, 'pending')
        self.assertEqual(req.user.username, 'testuser2')
        self.assertEqual(req.book.title, 'Science Basics')
        self.assertIn('Science Basics', str(req))
