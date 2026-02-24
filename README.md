# ANU Library Management System (LMS)

A comprehensive Django-based Library Management System for Acharya Nagarjuna University, featuring user authentication, book search/issue/return, role-based dashboards, AI recommendations, PostgreSQL full-text search, analytics, and deployment with preloaded data.

## Features
- **Authentication & Roles**: Student, Librarian, Admin logins with profile management.
- **Book Management**: Search, issue/return with fine calculation, requests for unavailable books.
- **PostgreSQL Full-Text Search**: Powered by `SearchVector`, `SearchQuery`, and `SearchRank` with `icontains` fallback.
- **Dashboards**: Student (issued books, recommendations), Librarian (low stock, overdues), Admin (KPIs, trends, exports).
- **AI Recommendations**: Layered engine (content-based, collaborative, popularity) for personalized suggestions.
- **E-Resources & News**: Digital links and announcements.
- **Analytics**: Aggregations for issues, fines, monthly trends.
- **Deployment**: Production-ready with PostgreSQL; automatic data seeding (3000+ transactions via `bulk_create`).

## Quick Start (Local Development)

### Prerequisites
- Python 3.10+
- PostgreSQL 14+ (installed and running)
- Git

### Setup

```bash
# 1. Clone repository
git clone <repository-url> && cd LMS_001

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create PostgreSQL database
# Open psql as superuser and run:
#   CREATE ROLE lms WITH LOGIN PASSWORD 'postgres' CREATEDB;
#   CREATE DATABASE anu_lms OWNER lms;

# 5. Run migrations
python manage.py migrate

# 6. Seed ALL data (single command)
python manage.py seed_all

# 7. Run server
python manage.py runserver
```

Open http://127.0.0.1:8000/

### Default Credentials

| Role       | Username     | Password    |
|------------|-------------|-------------|
| **Admin**  | `admin`     | `admin@123` |
| **Librarian** | `LIB001` | `lib@123`   |
| **Student** | `2022CSE001` | `anu@123` |

### Environment Variables

Copy `.env.example` to `.env` and configure:

```env
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# PostgreSQL Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=anu_lms
DB_USER=lms
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# Redis (for Celery & Cache)
REDIS_URL=redis://localhost:6379/0
```

## Data Seeding Commands

| Command | Description |
|---------|-------------|
| `python manage.py seed_all` | **Run all imports in one command** (recommended) |
| `python manage.py import_departments` | Load 18 departments from CSV |
| `python manage.py import_categories` | Load 12 book categories from CSV |
| `python manage.py import_books` | Load 95+ books from CSV |
| `python manage.py import_users` | Load 48 users & profiles from CSV |
| `python manage.py import_eresources` | Load e-resources from CSV |
| `python manage.py import_news` | Load 15 news items from CSV |
| `python manage.py generate_transactions --count 3000` | Generate 3000 synthetic transactions (bulk-optimized) |

## Architecture & Documentation
- **PRD**: See [docs/PRD.md](docs/PRD.md) for full product requirements.
- **ER Diagram & System Flows**: See [docs/documentation.md](docs/documentation.md) for entities, relationships, and end-to-end flows.
- **Models**: `portal/models.py` (Book, Transaction, Profile, Department, etc.)
- **Views**: `portal/views.py` (dashboards, search with PostgreSQL FTS)
- **Recommender**: `portal/services/recommender.py` (AI recommendation engine)
- **Settings**: `anu_lms/settings.py` (PostgreSQL, connection pooling, caching)

## Project Structure
```
LMS_001/
├── anu_lms/                      # Django project settings
│   ├── settings.py               # PostgreSQL config, caching, security
│   ├── urls.py                   # Root URL configuration
│   └── wsgi.py                   # WSGI entry point
├── portal/                       # Core app
│   ├── models.py                 # Data models (Book, Transaction, etc.)
│   ├── views.py                  # View functions with PostgreSQL FTS
│   ├── forms.py                  # Django forms
│   ├── signals.py                # Post-save signals
│   ├── utils.py                  # Fine calculation utilities
│   ├── services/
│   │   └── recommender.py        # AI recommendation engine
│   └── management/commands/      # Data seeding commands
│       ├── seed_all.py           # Master seeding orchestrator
│       ├── import_departments.py
│       ├── import_categories.py
│       ├── import_books.py
│       ├── import_users.py       # User + Profile import
│       ├── import_eresources.py
│       ├── import_news.py
│       ├── import_transactions.py
│       └── generate_transactions.py  # Bulk-optimized synthetic data
├── accounts/                     # Auth extensions (UserProfile)
├── books/                        # Book-related models
├── transactions/                 # Issue/return models
├── dashboard/                    # Analytics app
├── static/                       # CSS, JS, images
├── templates/                    # Django HTML templates
├── data/                         # CSV seed files
│   ├── departments.csv
│   ├── book_categories.csv
│   ├── books.csv
│   ├── users.csv
│   ├── eresources.csv
│   └── news.csv
├── docs/                         # Documentation
│   ├── PRD.md                    # Product Requirements Document
│   └── documentation.md         # ER diagrams & system flows
├── .env.example                  # Environment variable template
├── requirements.txt              # Python dependencies
├── import_data.py                # Standalone data import script
└── README.md                     # This file
```

## Technology Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.10+, Django 4.2.7 |
| **Database** | PostgreSQL 14+ (via `psycopg2-binary 2.9.7`) |
| **Search** | PostgreSQL Full-Text Search (`SearchVector`, `SearchQuery`, `SearchRank`) |
| **Task Queue** | Celery 5.3.4 + Redis 5.0.1 + django-celery-beat 2.5.0 |
| **PDF Generation** | ReportLab 4.0.7 |
| **Image Processing** | Pillow 10.1.0 |
| **Rate Limiting** | django-ratelimit 4.1.0 |
| **WSGI Server** | Gunicorn 21.2.0 |
| **Frontend** | HTML5, CSS3, JavaScript, Django Templates, Bootstrap 5.3 |
| **Caching** | Django LocMemCache (dev), Redis (production) |

## Production Deployment Checklist

- [ ] Set `DEBUG=False` and configure `SECRET_KEY` via env var
- [ ] Set `ALLOWED_HOSTS` to your domain
- [ ] Enable SSL/HTTPS (`SECURE_SSL_REDIRECT=True`)
- [ ] Configure Redis for Celery and caching
- [ ] Switch email backend from console to SMTP
- [ ] Run `python manage.py collectstatic`
- [ ] Deploy with Gunicorn (`gunicorn anu_lms.wsgi --workers 3`)
- [ ] Set up PostgreSQL backups (`pg_dump`)
- [ ] Configure monitoring (Sentry, Prometheus/Grafana)
- [ ] Add comprehensive test coverage

## Exam/Viva Notes
- **Database**: PostgreSQL with full-text search, connection pooling (`CONN_MAX_AGE=600`), `BigAutoField` primary keys.
- **ER Design**: Normalized (3NF), referential integrity, indexed foreign keys.
- **Search**: `SearchVector`/`SearchQuery`/`SearchRank` with weighted fields (title=A, author=B, subject=C).
- **Data Seeding**: Bulk-optimized with `bulk_create`/`bulk_update` for 10x speed improvement.
- **Flows**: Role-based auth, ORM-driven CRUD, rule-based AI recommendations.
- **Deployment**: Production-ready with Gunicorn/PostgreSQL; environment-variable driven configuration.

For issues, check logs or contact maintainer.
