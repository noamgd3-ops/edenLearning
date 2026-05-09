import pytest
from src.scheduler import pick_session_words

VERBS = [
    {"infinitive": "write", "past": "wrote", "category": "long o", "hebrew": "לכתוב", "hebrew_past": "כתב"},
    {"infinitive": "go",    "past": "went",  "category": "others",  "hebrew": "ללכת",  "hebrew_past": "הלך"},
    {"infinitive": "run",   "past": "ran",   "category": "others",  "hebrew": "לרוץ",  "hebrew_past": "רץ"},
]

def test_returns_list_of_verbs():
    words = pick_session_words(VERBS, {}, session_size=3)
    assert len(words) == 3

def test_due_words_come_first():
    from datetime import date, timedelta
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    progress = {
        "write": {
            "next_review": yesterday, "status": "learning",
            "ease_factor": 2.5, "interval_days": 1.0,
            "times_seen": 2, "times_correct": 1,
            "consecutive_correct": 0, "verb": "write"
        }
    }
    words = pick_session_words(VERBS, progress, session_size=3)
    assert words[0]["infinitive"] == "write"

def test_session_size_respected():
    words = pick_session_words(VERBS, {}, session_size=2)
    assert len(words) == 2

def test_mastered_words_go_last():
    from datetime import date, timedelta
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    progress = {
        "write": {
            "next_review": yesterday, "status": "mastered",
            "ease_factor": 3.0, "interval_days": 30.0,
            "times_seen": 10, "times_correct": 10,
            "consecutive_correct": 5, "verb": "write"
        }
    }
    words = pick_session_words(VERBS, progress, session_size=3)
    infinitives = [w["infinitive"] for w in words]
    assert infinitives.index("write") > 0
