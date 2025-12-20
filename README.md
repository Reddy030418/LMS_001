# ANU Library Management System (LMS)

A comprehensive Django-based Library Management System for Acharya Nagarjuna University, featuring user authentication, book search/issue/return, role-based dashboards, AI recommendations, analytics, and deployment with preloaded data.

## Features
- **Authentication & Roles**: Student, Librarian, Admin logins with profile management.
- **Book Management**: Search, issue/return with fine calculation, requests for unavailable books.
- **Dashboards**: Student (issued books, recommendations), Librarian (low stock, overdues), Admin (KPIs, trends, exports).
- **AI Recommendations**: Layered engine (content-based, collaborative, popularity) for personalized suggestions.
- **E-Resources & News**: Digital links and announcements.
- **Analytics**: Aggregations for issues, fines, monthly trends.
- **Deployment**: Production-ready with PostgreSQL; automatic data seeding (3000+ transactions).

## Quick Start (Local Development)
1. **Prerequisites**: Install Python 3.10+, virtualenv, and Git.
2. **Clone Repository**: `git clone <repository-url>` && `cd anu-lms`
3. **Create Virtual Environment**: `python -m venv venv` && `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Linux/Mac)
4. **Install Dependencies**: `pip install -r requirements.txt`
5. **Database Setup**: `python manage.py migrate`
6. **Seed Data**:
   - `python manage.py import_departments`
   - `python manage.py import_books`
   - `python manage.py import_users`
   - `python manage.py generate_transactions --count 3000`
   - `python manage.py import_categories`
   - `python manage.py import_eresources`
   - `python manage.py import_news`
7. **Run Server**: `python manage.py runserver`
8. **Access Application**: http://127.0.0.1:8000/

**Default Credentials**:
- **Admin**: admin / admin123
- **Librarian**: LIB001 / lib@123
- **Student**: 2022CSE001 / anu@123

**Environment Variables** (for production):
- `DEBUG=False`
- `SECRET_KEY=<your-secret-key>`
- `DATABASE_URL=postgresql://user:password@localhost:5432/anu_lms`
- `ALLOWED_HOSTS=yourdomain.com`



## Architecture & Documentation
- **ER Diagram & System Flows**: See [docs/documentation.md](docs/documentation.md) for entities (User, Profile, Book, etc.), relationships, and end-to-end flows (auth, search, issue/return, recommendations).
- **Models**: portal/models.py (Book, Transaction, etc.).
- **Views**: portal/views.py (dashboards, search).
- **Recommender**: portal/services/recommender.py (AI logic).
- **Settings**: anu_lms/settings.py (PostgreSQL, static files).

## Project Structure
```
ANU-LMS/
├── anu_lms/          # Django project settings
├── portal/           # Core app (models, views, templates)
├── accounts/         # Auth extensions
├── books/            # Book-related
├── transactions/     # Issue/return
├── dashboard/        # Analytics
├── static/           # CSS/JS
├── templates/        # HTML
├── data/             # CSV seed files
├── docs/             # Documentation
├── management/commands/ # Data import scripts
├── requirements.txt  # Dependencies
└── README.md         # This file
```

## Exam/Viva Notes
- **ER Design**: Normalized (3NF), referential integrity, scalable queries.
- **Flows**: Role-based auth, ORM-driven CRUD, rule-based AI.
- **Deployment**: Portable via Docker; production-ready with Gunicorn/PostgreSQL.

For issues, check logs or contact maintainer.
