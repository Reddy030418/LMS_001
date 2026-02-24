import requests

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_dashboard_api_get_overall_library_statistics_with_and_without_authentication():
    login_url = f"{BASE_URL}/accounts/login/"
    stats_url = f"{BASE_URL}/api/dashboard/stats/"

    session_auth = requests.Session()
    session_unauth = requests.Session()

    # Step 1: POST /accounts/login/ with Accept=application/json and valid credentials
    login_headers = {
        "Accept": "application/json"
    }
    login_data = {
        "username": "admin",
        "password": "adminpass"
    }
    try:
        login_resp = session_auth.post(login_url, headers=login_headers, data=login_data, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Login POST request failed: {str(e)}"
    assert login_resp.status_code == 200, f"Login expected status 200, got {login_resp.status_code}"
    try:
        login_json = login_resp.json()
    except ValueError:
        assert False, "Login response is not valid JSON"
    assert "success" in login_json, "'success' key missing in login JSON response"
    assert login_json["success"] is True, f"Login JSON success expected True, got {login_json['success']}"

    # Step 2: GET /api/dashboard/stats/ with authenticated session
    try:
        stats_resp_auth = session_auth.get(stats_url, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Authenticated GET /api/dashboard/stats/ failed: {str(e)}"
    assert stats_resp_auth.status_code == 200, f"Authenticated stats expected status 200, got {stats_resp_auth.status_code}"
    try:
        stats_json = stats_resp_auth.json()
    except ValueError:
        assert False, "Authenticated stats response is not valid JSON"
    expected_keys = {"total_books", "issued_books", "overdue_books", "students"}
    missing_keys = expected_keys - stats_json.keys()
    assert not missing_keys, f"Authenticated stats JSON missing keys: {missing_keys}"

    # Step 3: New unauthenticated session GET /api/dashboard/stats/
    try:
        stats_resp_unauth = session_unauth.get(stats_url, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Unauthenticated GET /api/dashboard/stats/ failed: {str(e)}"
    # Expect 401 with JSON response, not a redirect 302
    assert stats_resp_unauth.status_code == 401, f"Unauthenticated stats expected status 401, got {stats_resp_unauth.status_code}"
    try:
        unauth_json = stats_resp_unauth.json()
    except ValueError:
        assert False, "Unauthenticated stats response is not valid JSON"


test_dashboard_api_get_overall_library_statistics_with_and_without_authentication()