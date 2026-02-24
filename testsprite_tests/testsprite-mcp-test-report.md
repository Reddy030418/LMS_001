# TestSprite AI Testing Report (MCP)

---

## 1️⃣ Document Metadata

| Field           | Value                        |
|-----------------|------------------------------|
| **Project Name**| LMS_001                      |
| **Date**        | 2026-02-24                   |
| **Prepared by** | TestSprite AI Team           |
| **Test Type**   | Backend API                  |
| **Server**      | http://localhost:8000        |
| **Total Tests** | 6                            |
| **Passed**      | 1 ✅                         |
| **Failed**      | 5 ❌                         |
| **Pass Rate**   | 16.67%                       |

---

## 2️⃣ Requirement Validation Summary

### 🔐 Authentication

#### TC001 — Login POST with Valid and Invalid Credentials
- **Test Code:** [TC001_authentication_login_post_with_valid_and_invalid_credentials.py](./tmp/TC001_authentication_login_post_with_valid_and_invalid_credentials.py)
- **Status:** ❌ Failed
- **Error:** `AssertionError: Expected 302 redirect on valid login, got 404`
- **Test Visualization:** https://www.testsprite.com/dashboard/mcp/tests/bcd9c927-aebf-4583-93d5-2bb7935b65af/ccca6de5-e5b4-465e-b57d-4a42a6670d34
- **Analysis:** The test attempted to POST to `/accounts/login/`, but this route returns 404. The actual login endpoint in the Django app is mapped under `/login/` (via the `portal` app) rather than under the `/accounts/` prefix. The `accounts` app uses a separate URL namespace. Tests need to use the correct login URL path (`/login/`). This is a URL routing misconfiguration between test expectations and the actual `urls.py` setup.

---

### 📚 Book Management

#### TC002 — Get Book Detail — Valid and Invalid ID
- **Test Code:** [TC002_book_management_get_book_detail_valid_and_invalid_id.py](./tmp/TC002_book_management_get_book_detail_valid_and_invalid_id.py)
- **Status:** ❌ Failed
- **Error:** `AssertionError: No valid book ID found in books list`
- **Test Visualization:** https://www.testsprite.com/dashboard/mcp/tests/bcd9c927-aebf-4583-93d5-2bb7935b65af/352330da-67de-46ae-8b4f-8f37ff9fe15a
- **Analysis:** The test tried to scrape a book ID from the `/books/` page HTML response, but could not find a valid integer book ID in the expected format (e.g., in anchor href attributes like `/books/1/`). This likely means either: (a) the books page requires login and returns a redirect/login page instead, or (b) the HTML structure of the books list does not expose book IDs in a way the scraper can detect. The book list view should return visible book links with IDs for unauthenticated users, or the test needs authentication first.

#### TC003 — POST Request Book — With and Without Authentication
- **Test Code:** [TC003_book_transactions_post_request_book_with_and_without_authentication.py](./tmp/TC003_book_transactions_post_request_book_with_and_without_authentication.py)
- **Status:** ❌ Failed
- **Error:** `AssertionError: Failed to get a valid book_id from books list page: No book ID found on books list page`
- **Test Visualization:** https://www.testsprite.com/dashboard/mcp/tests/bcd9c927-aebf-4583-93d5-2bb7935b65af/15d300f7-d00f-4fde-a2b6-381b83dea989
- **Analysis:** Same root cause as TC002 — the test cannot extract a book ID from the books list page. As a dependency, TC003 relies on successfully discovering a book ID from `/books/`. If the page is login-protected or its HTML doesn't expose IDs, this test also fails. Resolving TC002's root cause will likely fix this test too.

---

### 📊 Dashboard API

#### TC004 — GET Dashboard Statistics — With and Without Authentication
- **Test Code:** [TC004_dashboard_api_get_overall_library_statistics_with_and_without_authentication.py](./tmp/TC004_dashboard_api_get_overall_library_statistics_with_and_without_authentication.py)
- **Status:** ❌ Failed
- **Error:** `requests.exceptions.HTTPError: 404 Client Error: Not Found for url: http://localhost:8000/accounts/login/`
- **Test Visualization:** https://www.testsprite.com/dashboard/mcp/tests/bcd9c927-aebf-4583-93d5-2bb7935b65af/076ac9ec-acc3-4df1-bb72-10773b3e04d7
- **Analysis:** Same URL routing issue as TC001. The test tried to authenticate by POSTing to `/accounts/login/` but this URL path does not exist — the actual login route is `/login/`. Dashboard API endpoints at `/api/dashboard/stats/` require session authentication, so login must succeed first. Fix the login URL in test setup to resolve this.

---

### 🏛️ Departmental and E-Resources

#### TC005 — GET Department Books — Valid and Invalid Department
- **Test Code:** [TC005_departmental_browse_get_department_books_valid_and_invalid_department.py](./tmp/TC005_departmental_browse_get_department_books_valid_and_invalid_department.py)
- **Status:** ✅ Passed
- **Test Visualization:** https://www.testsprite.com/dashboard/mcp/tests/bcd9c927-aebf-4583-93d5-2bb7935b65af/6e0085a4-7c96-4b71-a472-3ea93d82daef
- **Analysis:** Department browsing works correctly. The `/departments/` list and `/departments/<id>/books/` detail endpoints return proper HTML responses. Invalid department IDs return 404 as expected. No authentication issues because these are publicly accessible endpoints.

---

### 📞 Library Services

#### TC006 — POST Ask Librarian — Valid and Invalid Data
- **Test Code:** [TC006_library_services_post_ask_librarian_with_valid_and_invalid_data.py](./tmp/TC006_library_services_post_ask_librarian_with_valid_and_invalid_data.py)
- **Status:** ❌ Failed
- **Error:** `AssertionError: Expected 302 redirect for valid data, got 403`
- **Test Visualization:** https://www.testsprite.com/dashboard/mcp/tests/bcd9c927-aebf-4583-93d5-2bb7935b65af/ad9a3ac7-ba26-4206-94c3-8fdb50f72b3e
- **Analysis:** The POST to `/ask-librarian/` returned HTTP 403 Forbidden, which is Django's CSRF protection rejecting the request. The test did not include a valid CSRF token in the POST body. Django requires either `{% csrf_token %}` in forms or the `X-CSRFToken` header for all state-changing requests. The test must first fetch the page to obtain a CSRF token cookie and include it in the POST request.

---

## 3️⃣ Coverage & Matching Metrics

| Requirement              | Total Tests | ✅ Passed | ❌ Failed |
|--------------------------|-------------|-----------|-----------|
| Authentication           | 1           | 0         | 1         |
| Book Management          | 2           | 0         | 2         |
| Book Transactions        | 1           | 0         | 1         |
| Dashboard API            | 1           | 0         | 1         |
| Departmental & E-Resources| 1          | 1         | 0         |
| Library Services         | 1           | 0         | 1         |
| **Total**                | **6**       | **1**     | **5**     |

**Overall Pass Rate: 16.67%**

---

## 4️⃣ Key Gaps / Risks

### 🔴 Critical Issues

1. **Incorrect Login URL in Tests (Affects TC001, TC004)**
   - **Risk:** High — Multiple tests depend on authentication
   - **Root Cause:** Tests use `/accounts/login/` but the actual login route is `/login/` (registered under the `portal` app URL config)
   - **Fix:** Update test login URL to `http://localhost:8000/login/`

2. **CSRF Protection Blocking POST Requests (Affects TC006)**
   - **Risk:** High — All POST form submissions fail without CSRF tokens
   - **Root Cause:** Django's CSRF middleware rejects requests without valid CSRF tokens
   - **Fix:** Tests must perform a GET request first to obtain the CSRF cookie, then include `csrfmiddlewaretoken` in the POST body

3. **Book IDs Not Extractable from List Page (Affects TC002, TC003)**
   - **Risk:** High — Book transaction tests cannot proceed without a valid book ID
   - **Root Cause:** Either the books list page requires login (redirecting unauthenticated users) or book IDs are not in the HTML in an easily parseable link format
   - **Fix:** Ensure authentication precedes book browsing, and verify that `/books/` HTML contains anchor tags with href patterns like `/books/<id>/`

### 🟡 Moderate Risks

4. **Session-Based Authentication Coupling**
   - Tests that need authentication must manage session cookies carefully across requests
   - Consider using Django test fixtures or creating API token authentication for easier test setup

5. **Missing Test Coverage for Core Librarian Workflows**
   - Issue Book (`/issue-book/`) and Return Book (`/return-book/<id>/`) endpoints are not covered
   - These are high-risk workflows (inventory management) that need dedicated test cases

6. **No Negative/Edge Case Coverage for API Endpoints**
   - API endpoints (`/api/monthly-trends/`, `/api/most-issued-books/`, etc.) are not tested
   - Malformed inputs and boundary conditions not validated

### 🟢 What's Working

- **Departmental browsing** is fully functional and publicly accessible
- **404 handling** for invalid department IDs works correctly
- **Server startup and routing** for public pages is stable

---

*Report generated by TestSprite MCP on 2026-02-24*
