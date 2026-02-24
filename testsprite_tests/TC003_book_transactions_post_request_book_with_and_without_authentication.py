import requests
import re

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_book_transactions_post_request_book_with_and_without_auth():
    # Step 1: GET /books/ (public), regex r'href=["\']/books/(\d+)/' for book_id
    try:
        response = requests.get(f"{BASE_URL}/books/", timeout=TIMEOUT)
        assert response.status_code == 200, f"Expected 200 OK from /books/, got {response.status_code}"
        book_ids = re.findall(r'href=["\']/books/(\d+)/', response.text)
        assert book_ids, "No book_id found in /books/ page"
        book_id = book_ids[0]
    except Exception as e:
        raise AssertionError(f"Failed at GET /books/: {e}")

    # Step 2: POST /accounts/login/ with {'Accept':'application/json'} header, data username='admin' password='adminpass',
    # expect 200, assert json()['success']==True
    session_auth = requests.Session()
    login_url = f"{BASE_URL}/accounts/login/"
    login_data = {'username': 'admin', 'password': 'adminpass'}
    login_headers = {'Accept': 'application/json'}
    try:
        login_resp = session_auth.post(login_url, data=login_data, headers=login_headers, timeout=TIMEOUT)
        # According to PRD, successful login returns 302 redirect, but test case expects 200 with json success true.
        # So we verify status_code == 200 and json success True.
        assert login_resp.status_code == 200, f"Expected 200 OK from login post, got {login_resp.status_code}"
        json_resp = login_resp.json()
        assert 'success' in json_resp, "'success' key not in login response JSON"
        assert json_resp['success'] is True, f"Login success expected True, got {json_resp['success']}"
    except Exception as e:
        raise AssertionError(f"Failed at POST /accounts/login/: {e}")

    # Step 3: POST /request-book/<book_id>/ with same session cookies, expect 200 or 302
    request_book_url = f"{BASE_URL}/request-book/{book_id}/"
    try:
        post_req_resp = session_auth.post(request_book_url, timeout=TIMEOUT)
        assert post_req_resp.status_code in (200, 302), f"Expected 200 or 302 from POST /request-book/{book_id}/, got {post_req_resp.status_code}"
    except Exception as e:
        raise AssertionError(f"Failed at authenticated POST /request-book/{book_id}/: {e}")

    # Step 4: new session POST /request-book/<book_id>/ expect 302 or 401 (unauthenticated)
    session_no_auth = requests.Session()
    try:
        post_req_no_auth_resp = session_no_auth.post(request_book_url, timeout=TIMEOUT, allow_redirects=False)
        # Accept 302 redirect or 401 Unauthorized response
        assert post_req_no_auth_resp.status_code in (302, 401), f"Expected 302 or 401 from unauthenticated POST /request-book/{book_id}/, got {post_req_no_auth_resp.status_code}"
    except Exception as e:
        raise AssertionError(f"Failed at unauthenticated POST /request-book/{book_id}/: {e}")

test_book_transactions_post_request_book_with_and_without_auth()