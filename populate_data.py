import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'anu_lms.settings')
django.setup()

from portal.models import Department, Book, Eresource, NewsItem, Profile, Transaction, BookRequest
from django.contrib.auth.models import User
from datetime import date, timedelta
import random

# Step 1: Create Departments
departments_data = [
    {'name': 'Computer Science & Engineering', 'code': 'CSE'},
    {'name': 'Electronics & Communication Engineering', 'code': 'ECE'},
    {'name': 'Mechanical Engineering', 'code': 'ME'},
    {'name': 'Civil Engineering', 'code': 'CE'},
    {'name': 'Law', 'code': 'LAW'},
    {'name': 'History', 'code': 'HIS'},
    {'name': 'Geography', 'code': 'GEO'},
    {'name': 'Economics', 'code': 'ECO'},
    {'name': 'English Literature', 'code': 'ENG'},
    {'name': 'Mathematics', 'code': 'MAT'},
    {'name': 'Physics', 'code': 'PHY'},
    {'name': 'Chemistry', 'code': 'CHE'},
    {'name': 'Biology', 'code': 'BIO'},
    {'name': 'Psychology', 'code': 'PSY'},
    {'name': 'Sociology', 'code': 'SOC'},
    {'name': 'Philosophy', 'code': 'PHI'},
    {'name': 'Art', 'code': 'ART'},
    {'name': 'Music', 'code': 'MUS'},
    {'name': 'Business Administration', 'code': 'BUS'},
    {'name': 'Education', 'code': 'EDU'},
    {'name': 'Medicine', 'code': 'MED'},
    {'name': 'Political Science', 'code': 'POL'},
    {'name': 'Environmental Science', 'code': 'ENV'},
]

for data in departments_data:
    Department.objects.get_or_create(name=data['name'], defaults={'code': data['code']})

# Step 2: Create Sample Books with Expanded Fields
book_categories = ['Academic Textbook', 'Programming & Technology', 'Novel – Fiction', 'Novel – Non-Fiction', 'Law & Constitution', 'History', 'Geography', 'Competitive Exams', 'Reference', 'General Knowledge']

books_data = [
    {'title': 'Introduction to Algorithms', 'author': 'Thomas H. Cormen', 'isbn': '978-0262033848', 'publisher': 'MIT Press', 'department': Department.objects.get(code='CSE'), 'subject': 'Algorithms', 'description': 'Comprehensive guide to algorithms.', 'total_copies': 5, 'available_copies': 3, 'rack_number': 'A1-01', 'is_trending': True},
    {'title': 'Clean Code', 'author': 'Robert C. Martin', 'isbn': '978-0132350884', 'publisher': 'Prentice Hall', 'department': Department.objects.get(code='CSE'), 'subject': 'Software Engineering', 'description': 'Best practices for writing clean code.', 'total_copies': 4, 'available_copies': 2, 'rack_number': 'A1-02', 'is_trending': True},
    {'title': 'Pride and Prejudice', 'author': 'Jane Austen', 'isbn': '978-0141439518', 'publisher': 'Penguin Classics', 'department': Department.objects.get(code='ENG'), 'subject': 'Literature', 'description': 'Classic romance novel.', 'total_copies': 10, 'available_copies': 8, 'rack_number': 'B2-01', 'is_classic': True},
    {'title': 'To Kill a Mockingbird', 'author': 'Harper Lee', 'isbn': '978-0061120084', 'publisher': 'HarperCollins', 'department': Department.objects.get(code='ENG'), 'subject': 'Literature', 'description': 'Story of racial injustice.', 'total_copies': 7, 'available_copies': 5, 'rack_number': 'B2-02', 'is_classic': True},
    {'title': 'The Da Vinci Code', 'author': 'Dan Brown', 'isbn': '978-0307474278', 'publisher': 'Doubleday', 'department': Department.objects.get(code='ENG'), 'subject': 'Thriller', 'description': 'Mystery thriller novel.', 'total_copies': 6, 'available_copies': 4, 'rack_number': 'B2-03', 'is_thriller': True},
    {'title': 'The Little Prince', 'author': 'Antoine de Saint-Exupéry', 'isbn': '978-0156012195', 'publisher': 'Harcourt', 'department': Department.objects.get(code='ENG'), 'subject': 'Children\'s Literature', 'description': 'Philosophical children\'s book.', 'total_copies': 12, 'available_copies': 10, 'rack_number': 'B2-04', 'is_kids': True},
    {'title': 'Calculus', 'author': 'James Stewart', 'isbn': '978-0538497817', 'publisher': 'Cengage Learning', 'department': Department.objects.get(code='MAT'), 'subject': 'Calculus', 'description': 'Comprehensive calculus textbook.', 'total_copies': 8, 'available_copies': 6, 'rack_number': 'C3-01'},
    {'title': 'Quantum Mechanics', 'author': 'David J. Griffiths', 'isbn': '978-1107189638', 'publisher': 'Cambridge University Press', 'department': Department.objects.get(code='PHY'), 'subject': 'Quantum Physics', 'description': 'Introduction to quantum mechanics.', 'total_copies': 5, 'available_copies': 3, 'rack_number': 'D4-01'},
    {'title': 'Design Patterns', 'author': 'Erich Gamma', 'isbn': '978-0201633610', 'publisher': 'Addison-Wesley', 'department': Department.objects.get(code='CSE'), 'subject': 'Software Design', 'description': 'Gang of Four design patterns.', 'total_copies': 6, 'available_copies': 4, 'rack_number': 'A1-03', 'is_trending': True},
    {'title': '1984', 'author': 'George Orwell', 'isbn': '978-0451524935', 'publisher': 'Signet Classics', 'department': Department.objects.get(code='ENG'), 'subject': 'Dystopian Fiction', 'description': 'Dystopian novel about totalitarianism.', 'total_copies': 9, 'available_copies': 7, 'rack_number': 'B2-05', 'is_classic': True},
    {'title': 'Linear Algebra', 'author': 'Gilbert Strang', 'isbn': '978-0980232714', 'publisher': 'Wellesley-Cambridge Press', 'department': Department.objects.get(code='MAT'), 'subject': 'Linear Algebra', 'description': 'Introduction to linear algebra.', 'total_copies': 7, 'available_copies': 5, 'rack_number': 'C3-02'},
    {'title': 'The History of Rome', 'author': 'Theodor Mommsen', 'isbn': '978-0486200802', 'publisher': 'Dover Publications', 'department': Department.objects.get(code='HIS'), 'subject': 'Ancient History', 'description': 'Comprehensive history of Rome.', 'total_copies': 4, 'available_copies': 2, 'rack_number': 'E5-01'},
    {'title': 'Electromagnetism', 'author': 'David J. Griffiths', 'isbn': '978-1108420419', 'publisher': 'Cambridge University Press', 'department': Department.objects.get(code='PHY'), 'subject': 'Electromagnetism', 'description': 'Introduction to electromagnetism.', 'total_copies': 6, 'available_copies': 4, 'rack_number': 'D4-02'},
    {'title': 'Indian Polity', 'author': 'M. Laxmikanth', 'isbn': '978-9352604178', 'publisher': 'McGraw Hill', 'department': Department.objects.get(code='LAW'), 'subject': 'Constitutional Law', 'description': 'Guide to Indian polity for competitive exams.', 'total_copies': 15, 'available_copies': 12, 'rack_number': 'F6-01'},
    {'title': 'The Discovery of India', 'author': 'Jawaharlal Nehru', 'isbn': '978-0143031031', 'publisher': 'Oxford University Press', 'department': Department.objects.get(code='HIS'), 'subject': 'Indian History', 'description': 'Nehru\'s reflections on India.', 'total_copies': 8, 'available_copies': 6, 'rack_number': 'E5-02'},
    {'title': 'Harry Potter and the Philosopher\'s Stone', 'author': 'J.K. Rowling', 'isbn': '978-0747532699', 'publisher': 'Bloomsbury', 'department': Department.objects.get(code='ENG'), 'subject': 'Fantasy', 'description': 'First book in the Harry Potter series.', 'total_copies': 20, 'available_copies': 18, 'rack_number': 'B2-06'},
]

for data in books_data:
    Book.objects.get_or_create(title=data['title'], defaults=data)

# Step 3: Create Sample Users and Profiles
users_data = [
    {'username': 'librarian1', 'email': 'librarian@anu.ac.in', 'password': 'password123', 'is_staff': True, 'role': 'librarian', 'department': Department.objects.get(code='CSE'), 'roll_number': None, 'course': None, 'year': None},
    {'username': 'student1', 'email': 'student1@anu.ac.in', 'password': 'password123', 'is_staff': False, 'role': 'student', 'department': Department.objects.get(code='CSE'), 'roll_number': '2021CSE045', 'course': 'BTech', 'year': 3},
    {'username': 'student2', 'email': 'student2@anu.ac.in', 'password': 'password123', 'is_staff': False, 'role': 'student', 'department': Department.objects.get(code='LAW'), 'roll_number': '2022LAW012', 'course': 'LLB', 'year': 2},
    {'username': 'student3', 'email': 'student3@anu.ac.in', 'password': 'password123', 'is_staff': False, 'role': 'student', 'department': Department.objects.get(code='ENG'), 'roll_number': '2020ENG078', 'course': 'BA', 'year': 4},
]

for data in users_data:
    user, created = User.objects.get_or_create(username=data['username'], defaults={'email': data['email'], 'is_staff': data['is_staff']})
    if created:
        user.set_password(data['password'])
        user.save()
    Profile.objects.get_or_create(user=user, defaults={'role': data['role'], 'department': data['department'], 'roll_number': data['roll_number'], 'course': data['course'], 'year': data['year']})

# Create superuser
User.objects.create_superuser(username='anuadmin', email='admin@anu.ac.in', password='admin123')

# Step 4: Create Sample Transactions
students = User.objects.filter(profile__role='student')
books = Book.objects.all()
for i in range(5):
    user = random.choice(students)
    book = random.choice(books)
    if book.available_copies > 0:
        Transaction.objects.get_or_create(user=user, book=book, defaults={'issued_on': date.today() - timedelta(days=random.randint(1, 30)), 'due_date': date.today() + timedelta(days=14)})
        book.available_copies -= 1
        book.save()

# Step 5: Create Sample Book Requests
for i in range(3):
    user = random.choice(students)
    book = random.choice(books)
    BookRequest.objects.get_or_create(user=user, book=book, defaults={'status': 'Pending'})

# Step 6: Create Sample E-Resources
eresources_data = [
    {'name': 'JSTOR', 'description': 'Digital library for academic journals', 'url': 'https://www.jstor.org', 'letter': 'J'},
    {'name': 'PubMed', 'description': 'Medical literature database', 'url': 'https://pubmed.ncbi.nlm.nih.gov', 'letter': 'P'},
    {'name': 'IEEE Xplore', 'description': 'Engineering and technology resources', 'url': 'https://ieeexplore.ieee.org', 'letter': 'I'},
    {'name': 'Google Scholar', 'description': 'Scholarly literature search', 'url': 'https://scholar.google.com', 'letter': 'G'},
]

for data in eresources_data:
    Eresource.objects.get_or_create(name=data['name'], defaults=data)

# Step 7: Create Sample News
news_data = [
    {'title': 'New Library Hours Starting Next Week', 'summary': 'Library will extend hours for exam period.', 'published_on': date.today()},
    {'title': 'AI Book Recommendation Feature Launched', 'summary': 'Use our new AI to get personalized book suggestions.', 'published_on': date.today() - timedelta(days=3)},
    {'title': 'New Arrivals: Latest Engineering Textbooks', 'summary': 'Check out the new books in CSE and ECE departments.', 'published_on': date.today() - timedelta(days=7)},
]

for data in news_data:
    NewsItem.objects.get_or_create(title=data['title'], defaults=data)

print("Comprehensive sample data populated successfully!")
