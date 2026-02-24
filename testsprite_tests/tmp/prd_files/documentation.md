# ANU Library Management System (LMS) - ER Diagram & System Flow Documentation

## PART A: Entity-Relationship (ER) Diagram – Conceptual Documentation

The logical ER structure is expressed in text form below. This can be directly converted into a visual diagram using tools like Lucidchart, Draw.io, or ERDPlus if needed. The design follows normalization principles (3NF) for data integrity and scalability.

### 1. Core Entities and Relationships

#### 1. User (Django Auth User)
- **Purpose**: Authentication and identity management.
- **Type**: System entity (built-in Django model).
- **Primary Key**: `id` (Auto-increment integer).
- **Key Attributes**:
  - `username` (CharField, unique).
  - `email` (EmailField, unique).
  - `password` (CharField, hashed).
  - `is_active` (Boolean).
  - `is_staff` (Boolean, for librarians/admins).
  - `is_superuser` (Boolean, for super admins).
  - `date_joined` (DateTimeField).
  - `last_login` (DateTimeField).
- **Relationships**:
  - One-to-One → Profile (each user has one profile).
  - One-to-Many → Transaction (user issues many books).
  - One-to-Many → BookRequest (user makes many requests).

#### 2. Profile
- **Purpose**: Stores role-specific user details (extends User).
- **Type**: Extension entity.
- **Primary Key**: `id` (Auto-increment integer).
- **Foreign Keys**:
  - `user` → User (OneToOneField).
  - `department` → Department (ForeignKey, optional).
- **Attributes**:
  - `role` (CharField: 'student', 'librarian', 'admin').
  - `roll_number` (CharField, for students).
  - `course` (CharField).
  - `year` (IntegerField).
  - `phone` (CharField).
  - `address` (TextField).
  - `is_active_member` (Boolean).
- **Relationship Meaning**: One User has exactly one Profile; one Department has many Profiles.

#### 3. Department
- **Purpose**: Academic categorization for books and users.
- **Type**: Master entity.
- **Primary Key**: `id` (Auto-increment integer).
- **Attributes**:
  - `name` (CharField, e.g., "Computer Science").
  - `code` (CharField, unique, e.g., "CSE").
  - `description` (TextField).
  - `is_active` (Boolean).
- **Relationships**:
  - One-to-Many → Book (department has many books).
  - One-to-Many → Profile (department has many users).
  - One-to-Many → EResource (department has many e-resources).

#### 4. Book
- **Purpose**: Core library resource (physical/digital books).
- **Type**: Core entity.
- **Primary Key**: `id` (Auto-increment integer).
- **Foreign Keys**:
  - `department` → Department (ForeignKey).
- **Attributes**:
  - `title` (CharField).
  - `author` (CharField).
  - `isbn` (CharField, unique).
  - `publisher` (CharField).
  - `edition` (CharField).
  - `publication_year` (IntegerField).
  - `subject` (CharField, e.g., "Thriller").
  - `category` (CharField).
  - `language` (CharField).
  - `book_type` (CharField, e.g., "Rare", "Thesis").
  - `total_copies` (IntegerField).
  - `available_copies` (IntegerField).
  - `shelf_no` (CharField).
  - `description` (TextField).
  - `is_trending` (Boolean).
  - `created_at` (DateTimeField).
- **Relationships**:
  - One-to-Many → Transaction (book involved in many issues/returns).
  - One-to-Many → BookRequest (book receives many requests).

#### 5. Transaction
- **Purpose**: Tracks book issue/return lifecycle and fines.
- **Type**: Transactional entity.
- **Primary Key**: `id` (Auto-increment integer).
- **Foreign Keys**:
  - `user` → User (ForeignKey).
  - `book` → Book (ForeignKey).
- **Attributes**:
  - `issued_on` (DateField).
  - `due_date` (DateField).
  - `returned_on` (DateField, null for active).
  - `fine_amount` (DecimalField).
  - `status` (CharField: 'ISSUED', 'RETURNED').
- **Relationship Meaning**: Many-to-Many via User-Book (one user many books, one book many users over time).

#### 6. BookRequest
- **Purpose**: Handles user requests for unavailable books.
- **Type**: Transactional entity.
- **Primary Key**: `id` (Auto-increment integer).
- **Foreign Keys**:
  - `user` → User (ForeignKey).
  - `book` → Book (ForeignKey).
- **Attributes**:
  - `status` (CharField: 'PENDING', 'APPROVED', 'REJECTED').
  - `created_at` (DateTimeField).
  - `processed_at` (DateTimeField, null).
- **Relationship Meaning**: One User many requests; one Book many requests.

#### 7. NewsItem
- **Purpose**: Library announcements and events.
- **Type**: Informational entity.
- **Primary Key**: `id` (Auto-increment integer).
- **Attributes**:
  - `title` (CharField).
  - `content` (TextField).
  - `published_on` (DateField).
  - `is_active` (Boolean).
- **Relationships**: None (standalone).

#### 8. EResource
- **Purpose**: Digital resources (e-journals, databases).
- **Type**: Resource entity.
- **Primary Key**: `id` (Auto-increment integer).
- **Foreign Keys**:
  - `department` → Department (ForeignKey, optional).
- **Attributes**:
  - `name` (CharField).
  - `link` (URLField).
  - `letter` (CharField, for indexing).
  - `resource_type` (CharField, e.g., "Journal").
  - `description` (TextField).
- **Relationships**: One Department many EResources.

### 2. ER Relationship Summary (Text Notation)
- User ──1:1── Profile
- User ──1:N── Transaction
- User ──1:N── BookRequest
- Department ──1:N── Book
- Department ──1:N── Profile
- Department ──1:N── EResource
- Book ──1:N── Transaction
- Book ──1:N── BookRequest
- NewsItem (standalone)
- EResource ──N:1── Department

This structure ensures referential integrity (ForeignKeys with on_delete=CASCADE/SET_NULL), normalization (no redundancy), and scalability (ORM queries optimized with select_related/prefetch_related).

## PART B: System Flow Documentation (End-to-End)

### 3. User Authentication Flow
1. User accesses /login/ (views.login_view).
2. Submits username/password; AuthenticationForm validates.
3. If valid, login(request, user); load Profile for role.
4. Redirect to role-based dashboard (student_dashboard if 'student', admin_dashboard if superuser).
5. On logout (/logout/), clear session, redirect to home.
- **Error Handling**: Invalid creds → messages.error; next= param for post-login redirect.
- **Security**: CSRF protection, password hashing.

### 4. Book Search & Discovery Flow
1. User submits query to /search/ (views.search_view) or /books/ (views.book_list).
2. Query filters Book.objects with Q(title__icontains=query | author | subject).
3. Paginator(12 per page); render templates/books/book_list.html with results.
4. Advanced search (/search/advanced/): Filters by title, author, department, category, availability.
5. AJAX suggestions (/api/search-suggestions/): Top 5 title/author matches.
- **Discovery**: Home page shows trending, department-specific books; recommendations in dashboard.

### 5. Book Issue Flow
1. Authenticated student requests issue (/issue-book/, views.issue_book).
2. IssueForm validates (available_copies > 0, user role='student', borrow limit < MAX_BORROW=5).
3. Create Transaction (issued_on=now, due_date=now+14 days, status='ISSUED').
4. Decrement book.available_copies; save.
5. Messages.success; redirect to my_books.
- **Checks**: No active loan/request for same book.

### 6. Book Return & Fine Flow
1. User/librarian accesses /return-book/<tx_id>/ (views.return_book).
2. On POST, set returned_on=now; calculate fine if overdue (utils.calculate_fine).
3. Update transaction.fine_amount, status='RETURNED'.
4. Increment book.available_copies; save.
5. Messages.success; redirect to my_books or admin_dashboard.
- **Fine Logic**: Daily rate on overdue days; aggregated in dashboards.

### 7. Dashboard Analytics Flow
1. Role check: student_dashboard (issued books, fines, history, recommendations).
2. Aggregations: Sum(fine_amount), Count(transactions), annotate for KPIs.
3. Admin dashboard: Total books/users/issues/overdues/fines; monthly trends (TruncMonth).
4. API endpoints (/api/dashboard-stats/, etc.) for JSON data to charts (e.g., dept_issues_api).
5. Render templates/portal/*_dashboard.html with context.
- **Performance**: select_related('book'), prefetch_related for efficiency.

### 8. AI Recommendation Flow
1. In student_dashboard/my_books/book_detail, call services/recommender.get_recommendations(user, limit=6).
2. Layers: Content-based (filter department/subject/category, exclude borrowed); Collaborative (co-borrowed via common users); Popularity (annotate Count('transaction')).
3. Weighted scores (0.4 content, 0.4 collab, 0.2 pop); rank and return Book.objects.filter(id__in=ranked_ids).
4. Cold start: Fallback to dept popular or global top.
5. Render as grid in templates (title, author, cover, link to book_detail).
- **Similar Books**: In book_detail, filter same dept/category/subject, exclude self.

### 9. Email Notification Flow
1. Console backend for dev (EMAIL_BACKEND='console.EmailBackend').
2. Triggers: Overdue check (cron/scheduler, not implemented); on return (fine notification).
3. Use django.core.mail.send_mail for production (Gmail SMTP config in settings).
4. Log status in Transaction or separate model.
- **Extension**: Celery for async emails.

## PART C: Key Exam & Viva Talking Points
- **Design Principles**: Normalized relational DB (3NF, no redundancy); referential integrity via ForeignKeys; scalable with indexes on frequent queries (e.g., title__icontains).
- **Data Flow**: ORM (Django models) for CRUD; views handle business logic (role checks, validations); templates for UI; APIs for dynamic data.
- **Security**: Role-based access (@login_required, user_passes_test); CSRF/XSS protection; hashed passwords.
- **Features**: Real-time fine calc, AI recommendations (explainable, rule-based), analytics (aggregations for KPIs), Docker for deployment.
- **Scalability**: PostgreSQL for production; efficient queries (annotate/Count); ready for caching (Redis) or async tasks (Celery).
- **Testing/Deployment**: Seeded data (3000 transactions); Dockerized (one-command up); manual tests for flows.

## PART D: Performance Optimization & Scaling

### 10. Database Indexing Strategy
- **Indexed Fields**: Book (title, author, isbn, department, category, subject), Transaction (user, book, status, issued_on, due_date), Profile (role, department), BookRequest (user, book, status, created_at), NewsItem (title, published_on), Eresource (name).
- **Purpose**: Speeds up searches (icontains on title/author/subject), filters (department/category), and sorts (issued_on, due_date).
- **Migration**: Run `python manage.py makemigrations && python manage.py migrate` to apply indexes.

### 11. Query Optimization Techniques
- **select_related**: Used in my_books, student_dashboard, admin_dashboard for Book and User relations to avoid N+1 queries.
- **prefetch_related**: Applied in admin_dashboard for department-wise stats.
- **only()**: In search views, select only necessary fields (title, author) to reduce data transfer.
- **Aggregates**: Efficient Count/Sum in dashboards instead of looping.
- **Pagination**: Paginator(20) in book_list/search to limit results per page.

### 12. Caching Implementation
- **Backend**: LocMemCache (simple, no external deps; for production, switch to Redis).
- **Cached Data**:
  - Dashboard stats: 300s timeout (total_books, active_issues, etc.).
  - Recommendations: Per user, 3600s (personalized book suggestions).
- **Usage**: cache.get/set in views/recommender; cache_page decorator for static pages.

### 13. Deployment Scaling
- **Gunicorn Workers**: --workers 3 (handles concurrent requests; increase based on CPU cores).
- **Docker**: PostgreSQL for production (better concurrency than SQLite); volumes for data persistence.
- **Monitoring**: Use Django debug toolbar for query counts; EXPLAIN ANALYZE for slow queries.

### 14. Viva Preparation Points
- Indexes reduce query time from O(n) to O(log n) for searches.
- Caching avoids recomputation; hit ratios >80% expected.
- ORM optimizations prevent N+1; select_related joins tables in one query.
- Scaling: Workers parallelize requests; DB connection pooling in production.

This documentation covers the complete system architecture. For visuals, use the text ER in Draw.io.
