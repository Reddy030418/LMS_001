# TODO: Performance Tuning & Optimization for ANU LMS

## Information Gathered
- Current models (portal/models.py): Book (title, author, isbn, department, category, subject), Transaction (user, book, status, due_date, issued_on), Profile (role, department). No explicit db_index=True on frequent fields.
- Views (portal/views.py): Queries in book_list, search_view (no select_related), my_books/student_dashboard (basic filters, no prefetch), admin_dashboard (aggregates good but can cache), recommender.py (multiple queries, no caching).
- Pagination: Used in book_list/search (Paginator(12)), but ensure consistent.
- Caching: Not implemented; use Django's LocMemCache for simplicity (no Redis dep).
- Docker: Gunicorn single worker; update to 3 workers.
- DB: PostgreSQL in Docker; indexes via model db_index (requires migration).
- Bottlenecks: Search (icontains), dashboards (aggregates), recommendations (nested queries).

## Plan
- [ ] Update models.py: Add db_index=True to Book (title, author, isbn, category, department), Transaction (user, book, status, due_date, issued_on), Profile (role, department).
- [ ] Create and run migration for indexes: python manage.py makemigrations && python manage.py migrate.
- [ ] Optimize views.py: Add select_related('book', 'user') in my_books, student_dashboard, history; prefetch_related in admin_dashboard; use .only('title', 'author') in searches; aggregate where possible.
- [ ] Add caching: Configure LocMemCache in settings.py; cache dashboard stats (300s timeout) and recommendations (per user, 3600s).
- [ ] Optimize recommender.py: Use select_related; cache results with user_id key.
- [ ] Ensure pagination: Confirm Paginator(20) in book_list/search; add to department_list if missing.
- [ ] Update docker-compose.yml: Gunicorn with --workers 3.
- [ ] Update docs/documentation.md: Add optimization section (indexes, ORM, caching, viva points).
- [ ] Local test: Runserver, check query performance (e.g., via Django debug toolbar if added, or manual timing); verify no N+1.

## Dependent Files to be edited
- portal/models.py (add db_index).
- anu_lms/settings.py (CACHES config).
- portal/views.py (optimize queries).
- portal/services/recommender.py (caching, select_related).
- docker-compose.yml (Gunicorn workers).
- docs/documentation.md (add section).
- Migrations: New migration file after models change.

## Followup steps
- [ ] Run local tests: python manage.py runserver; access dashboards/searches, check for faster loads (manual or with timeit).
- [ ] Docker test: Once Docker installed, up --build, verify under load (e.g., multiple tabs).
- [ ] Viva prep: Document query EXPLAIN examples (optional, via psql).
- [ ] Mark complete; system now optimized for scale (5k+ books, 20k transactions).
