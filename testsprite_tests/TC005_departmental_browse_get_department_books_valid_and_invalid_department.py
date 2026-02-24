import requests
import re

BASE_URL = "http://localhost:8000"
TIMEOUT = 30

def test_departmental_browse_get_department_books_valid_and_invalid_department():
    headers = {
        "Authorization": "Basic YW51YWRtaW46YWRtaW4xMjM="  # base64 for "anuadmin:admin123"
    }

    # Step 1: GET /departments/ expect 200
    url_departments = f"{BASE_URL}/departments/"
    try:
        response = requests.get(url_departments, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Request to {url_departments} failed: {e}"
    assert response.status_code == 200, f"Expected 200 from {url_departments}, got {response.status_code}"
    html = response.text

    # Use regex to find department ids from href
    dept_ids = re.findall(r'href=["\']/departments/(\d+)/books/', html)
    assert isinstance(dept_ids, list), "dept_ids should be a list"
    assert len(dept_ids) > 0, "No department ids found in departments page"

    # Use first dept_id for valid test
    valid_dept_id = dept_ids[0]

    # Step 2: GET /departments/<dept_id>/books/ expect 200 no auth needed
    url_valid_dept_books = f"{BASE_URL}/departments/{valid_dept_id}/books/"
    try:
        response_valid = requests.get(url_valid_dept_books, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Request to {url_valid_dept_books} failed: {e}"
    assert response_valid.status_code == 200, f"Expected 200 from {url_valid_dept_books}, got {response_valid.status_code}"

    # Step 3: GET /departments/999999999/books/ expect 404 no auth needed
    url_invalid_dept_books = f"{BASE_URL}/departments/999999999/books/"
    try:
        response_invalid = requests.get(url_invalid_dept_books, timeout=TIMEOUT)
    except requests.RequestException as e:
        assert False, f"Request to {url_invalid_dept_books} failed: {e}"
    assert response_invalid.status_code == 404, f"Expected 404 from {url_invalid_dept_books}, got {response_invalid.status_code}"

test_departmental_browse_get_department_books_valid_and_invalid_department()