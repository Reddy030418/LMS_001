import requests
import re

def test_book_management_get_book_detail_valid_and_invalid_id():
    base_url = "http://localhost:8000"
    timeout = 30

    # Step 1: GET /books/ to get book list HTML and extract a valid book_id
    try:
        resp = requests.get(f"{base_url}/books/", timeout=timeout)
        assert resp.status_code == 200, f"Expected 200 from /books/, got {resp.status_code}"
        html = resp.text
        book_ids = re.findall(r'href=["\']/books/(\d+)/', html)
        assert book_ids, "No book IDs found in /books/ page"
        valid_id = book_ids[0]

        # Step 2: GET /books/<valid_id>/ expect 200 with HTML content
        resp_detail = requests.get(f"{base_url}/books/{valid_id}/", timeout=timeout)
        assert resp_detail.status_code == 200, f"Expected 200 from /books/{valid_id}/, got {resp_detail.status_code}"
        assert resp_detail.text, f"Empty content for /books/{valid_id}/"

        # Step 3: GET /books/999999999/ expect 404 Not Found
        resp_invalid = requests.get(f"{base_url}/books/999999999/", timeout=timeout)
        assert resp_invalid.status_code == 404, f"Expected 404 from /books/999999999/, got {resp_invalid.status_code}"

    except requests.RequestException as e:
        assert False, f"HTTP request failed: {e}"

test_book_management_get_book_detail_valid_and_invalid_id()