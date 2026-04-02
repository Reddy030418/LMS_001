# ANU LMS - Library Management System TODO

## Project Overview

- **Name**: Acharya Nagarjuna University Library Management System (ANU LMS)
- **Framework**: Django 4.2.7
- **Database**: SQLite (development) / PostgreSQL (production)
- **Key Features**:
  - User authentication (Students, Librarians, Admins)
  - Book catalog with search and advanced filtering
  - Book issue/return with due dates and fines
  - Personalized recommendations
  - Dashboard for users and admins
  - E-resources and news management
  - Email notifications for overdues and approvals
- **Current Status**: Core functionality implemented with recent enhancements in recommendations and async email notifications.

## Completed Tasks

### Core Functionality

- [x] User registration and authentication with role-based access (Student, Librarian, Admin)
- [x] Book catalog management (CRUD operations for books)
- [x] Book search functionality (title, author, subject, advanced search)
- [x] Book issue and return system with due dates
- [x] Fine calculation for overdue books
- [x] Dashboard views for students, librarians, and admins
- [x] Basic recommendations system

### Performance & Optimization

- [x] Database indexing on key fields
- [x] Query optimization with select_related
- [x] Caching implementation (LocMemCache, per-user recommendation cache)
- [x] Pagination (12 items per page)
- [x] Gunicorn configuration for production
- [x] Logging setup

### Security & Configuration

- [x] Environment variable configuration for secrets
- [x] Rate limiting on search endpoints
- [x] DEBUG=False for production
- [x] Security headers and settings
- [x] Database connection pooling

### Testing

- [x] Unit tests for models, views, and forms
- [x] Integration tests for key workflows
- [x] API endpoint testing

### Documentation

- [x] README.md with setup instructions
- [x] API documentation
- [x] Contribution guidelines

### Recent Enhancements

- [x] Improved recommendations with department popularity and cache invalidation
- [x] Async email notifications using Celery (overdue reminders, request approvals)
- [x] User Profile Management (profile details, picture, password)
- [x] Responsive Design (mobile-friendly, adaptive layouts)
- [x] User Experience (loading indicators, error messages, dark mode)

## Pending Tasks (Prioritized Roadmap)

### 🥇 Priority 1: High-Impact Showpiece Features & Core Completion

- [x] **AI "Librarian" Chatbot (RAG)**
  - [x] Implement real-time AI assistant using OpenAI/Claude APIs.
  - [x] Provide contextual book recommendations based on natural language queries.
- [ ] **Manual Testing**
  - Verify all user roles functionality, mobile responsiveness, and cross-browser compatibility.
- [x] **Book Reservations**
  - [x] Implement reservation queue for unavailable books
  - [x] Notification system for when reserved books become available
  - [x] Reservation expiry and cancellation
- [x] **Advanced Search & Filtering**
  - [x] Add filters for publication year, language, book type; faceted search and sorting.

### 🥈 Priority 2: Engagement, Real-Time Interactivity, and Security

- [x] **Live WebSockets Notifications**
  - [x] Use Django Channels for instant browser notifications on approvals/returns.
- [x] **Gamification & Student Engagement**
  - [x] Implement Reading Streaks & Badges (e.g., "Research Scholar", "Night Owl").
  - [x] Create Departmental Leaderboards and Peer Reviews/Reading Lists.
- [x] **Authentication & Security**
  - [x] Two-factor authentication (2FA), password reset, failure lockout.
  - [x] HTTPS implementation (SSL, HSTS, secure cookies).
  - [x] GDPR compliance and audit logging.

### 🥉 Priority 3: Professional Architecture (Senior Level) & Enterprise Integrations

- [x] **Full Dockerization**
  - [x] Create `docker-compose.yml` for isolated containers (web app, Celery worker, Redis, PostGIS/PostgreSQL).
- [x] **Aggressive Caching Strategy**
  - [x] Implement Redis caching for the book catalog and dashboard statistics.
- [x] **Continuous Integration (CI/CD)**
  - [x] GitHub Actions for automated testing, code quality checks, and deployments.
- [x] **Single Sign-On (SSO)**
  - [x] Integrate OAuth2 (Google Workspace/Microsoft Entra ID) for instant `.edu` logins.
- [x] **Automated Penalty Payments**
  - [x] Integrate Stripe/Razorpay APIs for overdue fines.
- [x] **Analytics Dashboard**
  - [x] User activity trends, book popularity, and department-wise usage statistics.

### 🔄 Priority 4: Smart Automation & Extended Functionality

- [x] **Automated Reminders (Celery)**
  - [x] Use Celery + Redis to send daily email warnings for upcoming due dates (3 days before, 1 day before).
- [x] **Inter-Library Loan System (ILL)**
  - [x] Form workflow for students to request books outside the local inventory; manage approval pipelines.
- [x] **In-Browser E-Reader**
  - [x] Integrate open-source EPUB/PDF reader (ePub.js/PDF.js).
- [x] **Calendar Integration**
  - [x] Export return deadlines or study room slots to Google/Apple Calendar.
- [x] **E-Resources Management**
  - [x] Upload/manage digital resources, permissions, and external platform integration.

### 🛠️ Priority 5: DevOps, Testing & Maintenance (Backlog)

- [ ] **Performance & Automated Testing**
  - Load testing (Locust), Selenium End-to-End coverage (80%+), API testing expansion.
- [ ] **Monitoring & Observability**
  - Django Silk (query profiling), Prometheus/Grafana, Error tracking.
- [ ] **Backup & Recovery**
  - Automated backups, restoration testing, disaster recovery plan.
- [ ] **Code Quality & Documentation**
  - Refactoring, type hints, dependency management/cleanup.
  - Comprehensive API docs (Swagger/OpenAPI), user manuals, video tutorials.
- [ ] **Accessibility**
  - WCAG compliance, screen reader support, keyboard navigation.

## Technical Debt

- [ ] Refactor views.py for better separation of concerns
- [ ] Implement proper error handling across all views
- [ ] Standardize API response formats
- [ ] Add comprehensive input validation

## Future Considerations

- [ ] Mobile app development (React Native/Flutter)
- [ ] Integration with university systems (SIS, LDAP)
- [ ] Multi-language support (i18n)
- [ ] Offline functionality for critical features
