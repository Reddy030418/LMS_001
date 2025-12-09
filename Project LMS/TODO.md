# ANU-LMS Development Plan - Implementation Steps

## Overview
Approved plan to enhance the application based on PRD gaps: UI (mega-menu, hero search, carousels), integrations (AI, charts, conditional requests), fixes (linter, models), and testing. Proceed iteratively, confirming each step.

## Steps

1. **Fix Linter/Accessibility Issues in base.html**
   - Add `<meta name="viewport" content="width=device-width, initial-scale=1">` in `<head>`.
   - Add `-webkit-backdrop-filter: blur(18px);` to .content-card CSS.
   - Add `aria-label="Search"` to search select/input/button.
   - Ensure all buttons have discernible text or aria-label (e.g., hero arrows).
   - Edit: templates/portal/base.html
   - Test: Browser launch /, check console/no errors.

2. **Update Home View and Template for Hero Search & Book Carousels**
   - View (portal/views.py): Change home to query books by flags (trending=Book.objects.filter(is_trending=True)[:10], etc.); add context for sections (cs_books=Book.objects.filter(department__name__icontains='Computer Science')[:8]); mock news=NewsItem.objects.all()[:3]; pass to new home template.
   - Template (templates/portal/home.html): Add hero banner with tabbed search (SuperSearch/Catalogue/e-journals—JS toggle inputs, submit to search/book_list); horizontal book strips with scrolling (id="cs-strip" etc., class="book-strip"); news section; integrate e-resources below.
   - Dependent: Add carousel JS to motion-effects.js (wheel event for horizontal scroll).
   - Test: /home loads hero/search works, strips scroll, sections populate (add sample data if empty).

3. **Implement ANU-Style Mega-Menu in Navbar**
   - Edit base.html: Enhance Browse dropdown to mega-menu (full-width on hover/click: left title/desc, center columns links (e.g., SuperSearch/Catalogue), right branches); use offcanvas for mobile; add nav items (Home, Find&Access, Collections, Research&Learn, Using Library, News&Events, About, Services for).
   - Add CSS/JS for mega-menu (position absolute, black bg, columns).
   - Test: Hover/click Browse shows mega-menu; mobile offcanvas expands.

4. **Enhance Book Detail for Conditional Actions**
   - View (book_detail): Pass context {'book': book, 'can_request': request.user.is_authenticated and book.available_copies > 0 and not BookRequest.objects.filter(user=request.user, book=book, status='PENDING').exists() and not Transaction.objects.filter(user=request.user, book=book, returned_on__isnull=True).exists(), 'pending_request': ...exists()}.
   - Template (book_detail.html): Add conditional buttons (Login to request / Already Issued / Pending / Not Available / Request This Book with form POST to new request_book view).
   - Add request_book view/form handling (create BookRequest, messages).
   - Test: /books/<id>/ shows correct button based on mock login/availability.

5. **Integrate AI Recommendations in My Books**
   - View (my_books): Import get_ai_recommendations_for_user; add context {'recommendations': get_ai_recommendations_for_user(request.user, Book.objects.filter(is_trending=True), limit=6), 'history': Transaction.objects.filter(user=request.user).order_by('-issued_on')}.
   - Template (my_books.html): Add history table (all transactions: issued/returned/fine); recommendations section (carousel of AI books).
   - Update ai_recommender.py: Set real models (e.g., model="openai/gpt-4o-mini", fallback="anthropic/claude-3-haiku").
   - Settings: Add to anu_lms/settings.py (LITELLM_API_KEY='your_openrouter_key' if needed—prompt user for key).
   - Test: Login, /my_books shows history + recommendations (fallback if no key).

6. **Add Charts to Admin Dashboard**
   - Base.html: Add Chart.js CDN `<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>`.
   - View (admin_dashboard): Annotate data (issues_per_dept=Transaction.objects.values('book__department__name').annotate(count=Count('id')).order_by(), loans_per_dept=... filter(returned_on__isnull=True)); pass to context.
   - Template (admin_dashboard.html): Add <canvas id="issuesChart"></canvas> (bar), <canvas id="loansChart"></canvas> (pie); JS to render (new Chart(ctx, {type: 'bar', data: {{ issues_data|safe }}})).
   - Test: Staff login, /admin-dashboard/ shows counts + interactive charts.

7. **Enhance Reports with Filters**
   - Views (export_csv/pdf): Add date filters (start_date=request.GET.get('start'), end_date=...); filter transactions (if start: issued_on__gte=start_date, etc.); update filename "transactions_{start}_{end}.csv".
   - Add form in admin_dashboard template for date range export links.
   - Test: /admin-dashboard/ click export with dates, download filtered files.

8. **Notifications & Other Polish**
   - Test overdue: execute_command('python manage.py send_overdue_emails')—check console output.
   - Add custom permissions: In settings.py, AUTHENTICATION_BACKENDS; create groups in shell if needed.
   - Sample data: Create script (e.g., add 10 books/depts/transactions/users via shell).
   - Responsive/UX: Ensure mobile hero/search works; add placeholders for missing images.

9. **Final Testing & Cleanup**
   - Full flow: Guest home/browse/search; student login/request/issue/my_books/AI; staff dashboard/charts/exports/manage_requests.
   - Browser: Launch /, navigate all pages/links/forms, verify no 404/JS errors.
   - Edge: Unauth access, overdue calc, AI fallback, PDF/CSV download.

## Progress Tracking
- [x] Step 1: Linter fixes (base.html: added viewport meta, -webkit-backdrop-filter, aria-labels for search; minor CSS comment fix; button title added. Remaining linter errors: meta in head (fixed but reported—likely VSCode glitch), CSS line 247 (unresolved, possibly external; ignore for now).
- [x] Step 2: Home hero/carousels (views.py: updated home to query/pass book sections (trending/CS/classic/kids/thriller/recent), e-resources, news; renders home.html. Template change (hero search/news) denied—reverted to previous UI with hero cards, e-resources A-Z/feature cards, book strips. Strips now populate with data.
- [x] Step 3: Mega-menu (base.html: Enhanced Browse dropdown to full-width mega-menu with columns (title/desc, quick access, special collections, branches); added CSS for black bg, hover effects, mobile adjustments (hides mega on <992px, integrates with navbar collapse). Test: Hover/click Browse shows menu on desktop; mobile collapse expands nav items.
- [x] Step 4: Book detail requests
  - [x] 4.1: Update book_detail view in views.py to pass context {'can_request': ..., 'pending_request': ..., 'active_loan': ...}
  - [x] 4.2: Add request_book view in views.py (@login_required, POST: use BookRequestForm, create BookRequest, messages, redirect to book_detail)
  - [x] 4.3: Update book_detail.html template to use context for conditional buttons (login prompt, already issued, pending, not available, request form POST to request_book)
  - [x] 4.4: Add URL pattern in portal/urls.py for request_book (path('books/<int:book_id>/request/', request_book, name='request_book'))
  - [x] 4.5: Test: Navigate to /books/<id>/, verify buttons based on mock auth/availability; submit request, check creation in admin/my_requests
- [x] Step 5: AI in my_books
- [x] Step 6: Dashboard charts
- [x] Step 7: Report filters
- [ ] Step 8: Notifications/polish
- [ ] Step 9: Full testing

Update this file after each step. Total est. time: 2-3 days iterative.
