import os
import django
import csv
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'anu_lms.settings')
django.setup()

from portal.models import Department, BookCategory, Book, Profile, Transaction, NewsItem, Eresource

def validate_data():
    # Check unique ISBN
    isbns = set()
    with open('data/books.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['isbn'] in isbns:
                raise ValidationError(f"Duplicate ISBN: {row['isbn']}")
            isbns.add(row['isbn'])
            if int(row['available_copies']) > int(row['total_copies']):
                raise ValidationError(f"Available copies exceed total for ISBN {row['isbn']}")

    # Check department codes exist
    dept_codes = {dept.code for dept in Department.objects.all()}
    with open('data/books.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['department_code'] not in dept_codes:
                raise ValidationError(f"Invalid department code: {row['department_code']}")

    # Check unique usernames
    usernames = set()
    with open('data/users.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['username'] in usernames:
                raise ValidationError(f"Duplicate username: {row['username']}")
            usernames.add(row['username'])

def import_departments():
    with open('data/departments.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            Department.objects.get_or_create(
                code=row['code'],
                defaults={
                    'name': row['name'],
                    'description': row['description'],
                    'is_active': row['is_active'].lower() == 'true'
                }
            )

def import_book_categories():
    with open('data/book_categories.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            BookCategory.objects.get_or_create(
                name=row['name'],
                defaults={'description': row['description']}
            )

def import_books():
    with open('data/books.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            dept = Department.objects.get(code=row['department_code'])
            category = BookCategory.objects.get(name=row['category'])
            Book.objects.get_or_create(
                isbn=row['isbn'],
                defaults={
                    'title': row['title'],
                    'author': row['author'],
                    'publisher': row['publisher'],
                    'edition': row['edition'],
                    'publication_year': int(row['publication_year']),
                    'department': dept,
                    'subject': row['subject'],
                    'category': category,
                    'language': row['language'],
                    'book_type': row['book_type'],
                    'total_copies': int(row['total_copies']),
                    'available_copies': int(row['available_copies']),
                    'shelf_no': row['shelf_no'],
                    'description': row['description']
                }
            )

def import_users():
    with open('data/users.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            user, created = User.objects.get_or_create(
                username=row['username'],
                defaults={
                    'first_name': row['first_name'],
                    'last_name': row['last_name'],
                    'email': row['email'],
                    'password': make_password(row['password']),
                    'is_active': row['is_active'].lower() == 'true',
                    'is_staff': row['role'] in ['librarian', 'admin'],
                    'is_superuser': row['role'] == 'admin'
                }
            )
            if created:
                dept = Department.objects.get(code=row['department_code']) if row['department_code'] else None
                Profile.objects.create(
                    user=user,
                    role=row['role'],
                    department=dept,
                    roll_number=row.get('roll_number', ''),
                    course=row.get('course', ''),
                    year=int(row.get('year', 0)) if row.get('year') else None,
                    phone=row.get('phone', '')
                )

def import_staff():
    with open('data/staff.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            User.objects.get_or_create(
                username=row['username'],
                defaults={
                    'email': row['email'],
                    'password': make_password(row['password']),
                    'is_staff': row['is_staff'].lower() == 'true',
                    'is_superuser': row['is_superuser'].lower() == 'true'
                }
            )

def import_transactions():
    with open('data/transactions.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            user = User.objects.get(username=row['username'])
            book = Book.objects.get(isbn=row['isbn'])
            Transaction.objects.get_or_create(
                user=user,
                book=book,
                issue_date=datetime.strptime(row['issue_date'], '%Y-%m-%d').date(),
                defaults={
                    'due_date': datetime.strptime(row['due_date'], '%Y-%m-%d').date(),
                    'return_date': datetime.strptime(row['return_date'], '%Y-%m-%d').date() if row['return_date'] else None,
                    'fine_amount': float(row['fine_amount']),
                    'status': row['status']
                }
            )

def import_news():
    with open('data/news.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            NewsItem.objects.get_or_create(
                title=row['title'],
                defaults={
                    'content': row['content'],
                    'published_on': datetime.strptime(row['publish_date'], '%Y-%m-%d').date()
                }
            )

def import_eresources():
    with open('data/eresources.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            dept = Department.objects.get(code=row['department_code']) if row['department_code'] else None
            Eresource.objects.get_or_create(
                name=row['title'],
                defaults={
                    'link': row['link'],
                    'department': dept,
                    'resource_type': row['resource_type'],
                    'description': row['description']
                }
            )

if __name__ == '__main__':
    try:
        validate_data()
        import_departments()
        import_book_categories()
        import_books()
        import_users()
        import_staff()
        import_transactions()
        import_news()
        import_eresources()
        print("Data import completed successfully!")
    except Exception as e:
        print(f"Error during import: {e}")
