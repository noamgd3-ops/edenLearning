from datetime import date, timedelta

from supabase import create_client

_SUPABASE_URL = "https://qdgofyprngpuzlcudmvf.supabase.co"
_SUPABASE_KEY = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
    ".eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InFkZ29meXBybmdwdXpsY3VkbXZmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njg1NzQwMTAsImV4cCI6MjA4NDE1MDAxMH0"
    ".ZMa7kxzuaoNWOW5Ml2sFX-ztKRSyJxNraE4d7vm4zVw"
)

def _client():
    return create_client(_SUPABASE_URL, _SUPABASE_KEY)

def init_db(db_path=None):
    pass  # Table already exists in Supabase

def _default_row(verb):
    return {
        "verb": verb,
        "times_seen": 0,
        "times_correct": 0,
        "ease_factor": 2.5,
        "interval_days": 1.0,
        "next_review": "2000-01-01",
        "consecutive_correct": 0,
        "status": "new",
        "total_response_time": 0.0,
        "last_response_time": 0.0,
        "last_wrong_answer": "",
    }

def get_progress(verb, db_path=None):
    sb = _client()
    res = sb.table("progress").select("*").eq("verb", verb).execute()
    if res.data:
        return res.data[0]
    return _default_row(verb)

def update_progress(verb, correct, response_time=0.0, wrong_answer="", db_path=None):
    p = get_progress(verb)
    p["times_seen"] += 1
    p["total_response_time"] = p.get("total_response_time", 0.0) + response_time
    p["last_response_time"] = response_time
    if not correct and wrong_answer:
        p["last_wrong_answer"] = wrong_answer

    if correct:
        p["times_correct"] += 1
        p["consecutive_correct"] += 1
        new_ef = min(p["ease_factor"] + 0.1, 3.0)
        p["ease_factor"] = new_ef
        p["interval_days"] = p["interval_days"] * new_ef
        p["status"] = "mastered" if p["consecutive_correct"] >= 3 else "learning"
    else:
        p["consecutive_correct"] = 0
        p["ease_factor"] = max(1.3, p["ease_factor"] - 0.2)
        p["interval_days"] = 1.0
        p["status"] = "learning" if p["times_seen"] > 1 else "new"

    p["next_review"] = (date.today() + timedelta(days=p["interval_days"])).isoformat()

    sb = _client()
    sb.table("progress").upsert(p).execute()

def get_all_progress(db_path=None):
    sb = _client()
    res = sb.table("progress").select("*").execute()
    return {r["verb"]: r for r in res.data}

def reset_all_progress(db_path=None):
    sb = _client()
    sb.table("progress").delete().neq("verb", "").execute()
