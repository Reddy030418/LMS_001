# ANU Library Management System (LMS)

A comprehensive Django-based Library Management System for Acharya Nagarjuna University, featuring user authentication, book search/issue/return, role-based dashboards, AI recommendations, analytics, and Dockerized deployment with preloaded data.

## Features
- **Authentication & Roles**: Student, Librarian, Admin logins with profile management.
- **Book Management**: Search, issue/return with fine calculation, requests for unavailable books.
- **Dashboards**: Student (issued books, recommendations), Librarian (low stock, overdues), Admin (KPIs, trends, exports).
- **AI Recommendations**: Layered engine (content-based, collaborative, popularity) for personalized suggestions.
- **E-Resources & News**: Digital links and announcements.
- **Analytics**: Aggregations for issues, fines, monthly trends.
- **Deployment**: Dockerized with PostgreSQL; automatic data seeding (3000+ transactions).

## Quick Start (Local Development)
1. Install Python 3.10+ and virtualenv.
2. `pip install -r requirements.txt`
3. `python manage.py migrate`
4. Run seeding: `python manage.py import_departments`, `import_books`, `import_users`, `generate_transactions --count 3000`, etc.
5. `python manage.py runserver`
6. Access http://127.0.0.1:8000/

**Credentials**:
- Admin: admin / admin123
- Librarian: LIB001 / lib@123
- Student: 2022CSE001 / anu@123

## Dockerized Deployment (One-Command)
1. Install Docker Desktop (https://www.docker.com/products/docker-desktop/).
2. From project root: `docker compose up --build`
3. App runs at http://localhost:8000/ with seeded data.
4. Stop with Ctrl+C; data persists.

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
├── Dockerfile        # Build image
├── docker-compose.yml # Services
└── README.md         # This file
```

## Exam/Viva Notes
- **ER Design**: Normalized (3NF), referential integrity, scalable queries.
- **Flows**: Role-based auth, ORM-driven CRUD, rule-based AI.
- **Deployment**: Portable via Docker; production-ready with Gunicorn/PostgreSQL.

For issues, check logs or contact maintainer.
