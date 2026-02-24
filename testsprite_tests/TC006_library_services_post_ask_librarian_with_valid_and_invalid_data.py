import requests

BASE_URL = "http://localhost:8000"


def test_tc006_post_ask_librarian_valid_invalid():
    url = f"{BASE_URL}/ask-librarian/"
    
    # Valid data
    valid_payload = {
        "name": "Test User",
        "email": "testuser@example.com",
        "message": "I need help."
    }
    try:
        resp = requests.post(url, data=valid_payload, timeout=30)
        # According to PRD endpoint, success responds with HTTP 302 redirect
        assert resp.status_code == 302, f"Expected 302 for valid request, got {resp.status_code}"
    except Exception as e:
        raise AssertionError(f"Exception during valid post ask-librarian: {e}")

    # Invalid test cases
    invalid_cases = [
        ({"name": "", "email": "testuser@example.com", "message": "I need help."}, "name empty"),
        ({"name": "Test User", "email": "", "message": "I need help."}, "email empty"),
        ({"name": "Test User", "email": "not-an-email", "message": "I need help."}, "email invalid"),
        ({"name": "Test User", "email": "testuser@example.com", "message": ""}, "message empty"),
    ]

    for payload, case_desc in invalid_cases:
        try:
            r = requests.post(url, data=payload, timeout=30)
            # Expect HTTP 200 status code with form containing errors
            assert r.status_code == 200, f"Expected 200 for invalid case '{case_desc}', got {r.status_code}"
        except Exception as ex:
            raise AssertionError(f"Exception during invalid case '{case_desc}': {ex}")


test_tc006_post_ask_librarian_valid_invalid()
