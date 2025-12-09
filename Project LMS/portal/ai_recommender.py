# portal/ai_recommender.py

import time
from typing import Iterable, List
import litellm
from litellm import APIError
from .models import Book

MAX_RETRIES = 3
BACKOFF_BASE = 2  # seconds

def _call_llm_with_retry(messages, model: str, fallback_model: str | None = None):
    """
    Low-level helper: call litellm with retry + optional failover.
    Raises APIError only if it's NOT an 'overloaded' case or all retries fail.
    """
    delay = BACKOFF_BASE

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return litellm.completion(model=model, messages=messages)
        except APIError as e:
            msg = str(e).lower()

            # Overloaded: retry/backoff, maybe fail over later
            if "overloaded" in msg or "rate limit" in msg:
                if attempt < MAX_RETRIES:
                    print(f"[AI] Channel overloaded (attempt {attempt}). Retrying in {delay}s...")
                    time.sleep(delay)
                    delay *= 2
                    continue
                else:
                    # Try backup model once if provided
                    if fallback_model:
                        print("[AI] Primary overloaded, trying fallback model...")
                        return litellm.completion(model=fallback_model, messages=messages)
                    # No fallback, give up silently to caller
                    raise
            # Any other APIError: re-raise
            raise


def get_ai_recommendations_for_user(user, fallback_qs: Iterable[Book], limit: int = 6) -> List[Book]:
    """
    High-level function used by views.
    It MUST NEVER crash the view. On any error, it just returns fallback_qs[:limit].
    """
    # If user is anonymous or has no history, just fallback
    if user.is_anonymous:
        return list(fallback_qs[:limit])

    try:
        # Simple example prompt – tweak as you like
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a library recommendation engine for Acharya Nagarjuna University. "
                    "Given a student's department and their borrowing history, suggest relevant "
                    "books from the library catalogue. Return only book titles as a comma-separated list."
                ),
            },
            {
                "role": "user",
                "content": f"Student department: {getattr(getattr(user, 'profile', None), 'department', 'Unknown')}. "
                           f"Suggest {limit} books."
            },
        ]

        resp = _call_llm_with_retry(
            messages=messages,
            model="openrouter/openai/gpt-4o-mini",        # your main model
            fallback_model="openrouter/anthropic/claude-3-haiku" # optional backup
        )
        text = resp["choices"][0]["message"]["content"]

        # naive parsing: split by comma and trim
        titles = [t.strip() for t in text.split(",") if t.strip()]

        # match titles from DB
        qs = Book.objects.filter(title__in=titles)
        if qs.exists():
            return list(qs[:limit])

    except Exception as e:
        # VERY important: swallow all errors here, print for logs but never crash
        print(f"[AI] Recommendation error: {e}")

    # Fallback
    return list(fallback_qs[:limit])
