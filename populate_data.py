import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'anu_lms.settings')
django.setup()

from portal.models import Department, Book, Eresource, NewsItem
from django.contrib.auth.models import User
from datetime import date, timedelta

# Create departments
departments = ['Computer Science', 'Literature', 'Mathematics', 'Physics']
for name in departments:
    Department.objects.get_or_create(name=name, code=name[:3].upper())

# Create sample books
books_data = [
    {'title': 'Introduction to Algorithms', 'author': 'Thomas H. Cormen', 'department': Department.objects.get(name='Computer Science'), 'is_trending': True, 'total_copies': 5, 'available_copies': 3},
    {'title': 'Clean Code', 'author': 'Robert C. Martin', 'department': Department.objects.get(name='Computer Science'), 'is_trending': True, 'total_copies': 4, 'available_copies': 2},
    {'title': 'Pride and Prejudice', 'author': 'Jane Austen', 'department': Department.objects.get(name='Literature'), 'is_classic': True, 'total_copies': 10, 'available_copies': 8},
    {'title': 'To Kill a Mockingbird', 'author': 'Harper Lee', 'department': Department.objects.get(name='Literature'), 'is_classic': True, 'total_copies': 7, 'available_copies': 5},
    {'title': 'The Da Vinci Code', 'author': 'Dan Brown', 'department': Department.objects.get(name='Literature'), 'is_thriller': True, 'total_copies': 6, 'available_copies': 4},
    {'title': 'The Little Prince', 'author': 'Antoine de Saint-Exupéry', 'department': Department.objects.get(name='Literature'), 'is_kids': True, 'total_copies': 12, 'available_copies': 10},
    {'title': 'Calculus', 'author': 'James Stewart', 'department': Department.objects.get(name='Mathematics'), 'total_copies': 8, 'available_copies': 6},
    {'title': 'Quantum Mechanics', 'author': 'David J. Griffiths', 'department': Department.objects.get(name='Physics'), 'total_copies': 5, 'available_copies': 3},
]

for data in books_data:
    Book.objects.get_or_create(title=data['title'], defaults=data)

# Create sample e-resources
eresources_data = [
    {'name': 'JSTOR', 'description': 'Digital library for academic journals', 'url': 'https://www.jstor.org', 'letter': 'J'},
    {'name': 'PubMed', 'description': 'Medical literature database', 'url': 'https://pubmed.ncbi.nlm.nih.gov', 'letter': 'P'},
    {'name': 'IEEE Xplore', 'description': 'Engineering and technology resources', 'url': 'https://ieeexplore.ieee.org', 'letter': 'I'},
    {'name': 'Google Scholar', 'description': 'Scholarly literature search', 'url': 'https://scholar.google.com', 'letter': 'G'},
]

for data in eresources_data:
    Eresource.objects.get_or_create(name=data['name'], defaults=data)

# Create sample news
news_data = [
    {'title': 'New Library Hours Starting Next Week', 'summary': 'Library will extend hours for exam period.', 'published_on': date.today()},
    {'title': 'AI Book Recommendation Feature Launched', 'summary': 'Use our new AI to get personalized book suggestions.', 'published_on': date.today() - timedelta(days=3)},
]

for data in news_data:
    NewsItem.objects.get_or_create(title=data['title'], defaults=data)

print("Sample data populated successfully!")
