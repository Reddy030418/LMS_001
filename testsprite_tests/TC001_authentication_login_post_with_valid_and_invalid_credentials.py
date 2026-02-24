import requests
from requests.auth import HTTPBasicAuth

BASE_URL = "http://localhost:8000"
LOGIN_PATH = "/accounts/login/"
HEADERS = {"Accept": "application/json"}
TIMEOUT = 30

def test_authentication_login_post_with_valid_and_invalid_credentials():
    # Setup basic authentication for API (from instructions)
    auth = HTTPBasicAuth("anuadmin", "admin123")

    session = requests.Session()
    try:
        # Valid credentials test
        valid_data = {"username": "admin", "password": "adminpass"}
        valid_response = session.post(
            BASE_URL + LOGIN_PATH,
            headers=HEADERS,
            data=valid_data,
            auth=auth,
            timeout=TIMEOUT,
            allow_redirects=False,
        )
        # According to PRD, on successful login POST returns 302 Redirect.
        # But Test Plan says expect HTTP 200 JSON with success=true.
        # To reconcile, we check if 200 json success true else check 302.
        if valid_response.status_code == 200:
            json_resp = valid_response.json()
            assert "success" in json_resp, "Missing 'success' key in valid login response JSON"
            assert json_resp["success"] is True, "Expected success=true for valid credentials"
        elif valid_response.status_code == 302:
            # If redirect (PRD expected), consider success
            # No json body in redirect, so pass
            pass
        else:
            assert False, f"Unexpected status code {valid_response.status_code} for valid login"

        # Invalid credentials test
        invalid_data = {"username": "baduser", "password": "badpass"}
        invalid_response = session.post(
            BASE_URL + LOGIN_PATH,
            headers=HEADERS,
            data=invalid_data,
            auth=auth,
            timeout=TIMEOUT,
            allow_redirects=False,
        )
        # According to test plan expect 401 JSON with success=false
        # But PRD says POST /accounts/login/ invalid credentials returns 200 page with errors (HTML)
        # So check for both cases:
        if invalid_response.status_code == 401:
            try:
                json_resp = invalid_response.json()
                assert "success" in json_resp, "Missing 'success' key in invalid login response JSON"
                assert json_resp["success"] is False, "Expected success=false for invalid credentials"
            except ValueError:
                assert False, "Invalid login response not JSON as expected"
        elif invalid_response.status_code == 200:
            # Likely HTML page with form errors, no JSON or success key false
            # So try to check if content contains error info
            content_type = invalid_response.headers.get("Content-Type", "")
            assert "text/html" in content_type, "Expected HTML content for invalid login with 200 status"
            # Cannot assert JSON success=false per PRD, so consider pass here
        else:
            assert False, f"Unexpected status code {invalid_response.status_code} for invalid login"
    finally:
        session.close()

test_authentication_login_post_with_valid_and_invalid_credentials()