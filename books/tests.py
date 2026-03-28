from django.test import TestCase
from .models import Department, Book

class DepartmentModelTest(TestCase):
    def setUp(self):
        self.dept = Department.objects.create(name='Computer Science')

    def test_department_creation(self):
        self.assertEqual(self.dept.name, 'Computer Science')
        self.assertEqual(str(self.dept), 'Computer Science')

class BookModelTest(TestCase):
    def setUp(self):
        self.dept = Department.objects.create(name='Physics')
        self.book = Book.objects.create(
            title='Quantum Mechanics',
            author='John Doe',
            edition='1st',
            publisher='Science Pub',
            isbn='1234567890123',
            department=self.dept,
            subject='Physics',
            rack='A1',
            total_copies=5,
            available_copies=5,
            is_featured=True
        )

    def test_book_creation(self):
        self.assertEqual(self.book.title, 'Quantum Mechanics')
        self.assertEqual(self.book.author, 'John Doe')
        self.assertEqual(self.book.isbn, '1234567890123')
        self.assertEqual(self.book.department.name, 'Physics')
        self.assertEqual(self.book.available_copies, 5)
        self.assertTrue(self.book.is_featured)
        self.assertEqual(str(self.book), 'Quantum Mechanics')
