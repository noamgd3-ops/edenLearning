import sqlite3
from datetime import date, timedelta

DB_PATH = "data/progress.db"

def init_db(db_path=DB_PATH):
    con = sqlite3.connect(db_path)
    con.execute("""
        CREATE TABLE IF NOT EXISTS progress (
            verb TEXT PRIMARY KEY,
            times_seen INTEGER DEFAULT 0,
            times_correct INTEGER DEFAULT 0,
            ease_factor REAL DEFAULT 2.5,
            interval_days REAL DEFAULT 1.0,
            next_review TEXT DEFAULT '2000-01-01',
            consecutive_correct INTEGER DEFAULT 0,
            status TEXT DEFAULT 'new',
            total_response_time REAL DEFAULT 0.0,
            last_response_time REAL DEFAULT 0.0
        )
    """)
    # migrate existing DBs that don't have the new columns
    for col in ("total_response_time REAL DEFAULT 0.0", "last_response_time REAL DEFAULT 0.0"):
        try:
            con.execute(f"ALTER TABLE progress ADD COLUMN {col}")
        except Exception:
            pass
    con.commit()
    con.close()

def _row_to_dict(row):
    keys = ["verb", "times_seen", "times_correct", "ease_factor",
            "interval_days", "next_review", "consecutive_correct", "status",
            "total_response_time", "last_response_time"]
    return dict(zip(keys, row))

def get_progress(verb, db_path=DB_PATH):
    con = sqlite3.connect(db_path)
    row = con.execute("SELECT * FROM progress WHERE verb=?", (verb,)).fetchone()
    con.close()
    if row:
        return _row_to_dict(row)
    return {
        "verb": verb, "times_seen": 0, "times_correct": 0,
        "ease_factor": 2.5, "interval_days": 1.0,
        "next_review": "2000-01-01", "consecutive_correct": 0, "status": "new",
        "total_response_time": 0.0, "last_response_time": 0.0,
    }

def update_progress(verb, correct, response_time=0.0, db_path=DB_PATH):
    p = get_progress(verb, db_path)
    p["times_seen"] += 1
    p["total_response_time"] = p.get("total_response_time", 0.0) + response_time
    p["last_response_time"] = response_time

    if correct:
        p["times_correct"] += 1
        p["consecutive_correct"] += 1
        new_ef = min(p["ease_factor"] + 0.1, 3.0)
        new_interval = p["interval_days"] * new_ef
        p["ease_factor"] = new_ef
        p["interval_days"] = new_interval
        if p["consecutive_correct"] >= 3:
            p["status"] = "mastered"
        else:
            p["status"] = "learning"
    else:
        p["consecutive_correct"] = 0
        p["ease_factor"] = max(1.3, p["ease_factor"] - 0.2)
        p["interval_days"] = 1.0
        p["status"] = "learning" if p["times_seen"] > 1 else "new"

    next_rev = (date.today() + timedelta(days=p["interval_days"])).isoformat()
    p["next_review"] = next_rev

    con = sqlite3.connect(db_path)
    con.execute("""
        INSERT INTO progress VALUES (?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(verb) DO UPDATE SET
            times_seen=excluded.times_seen,
            times_correct=excluded.times_correct,
            ease_factor=excluded.ease_factor,
            interval_days=excluded.interval_days,
            next_review=excluded.next_review,
            consecutive_correct=excluded.consecutive_correct,
            status=excluded.status,
            total_response_time=excluded.total_response_time,
            last_response_time=excluded.last_response_time
    """, (p["verb"], p["times_seen"], p["times_correct"], p["ease_factor"],
          p["interval_days"], p["next_review"], p["consecutive_correct"], p["status"],
          p["total_response_time"], p["last_response_time"]))
    con.commit()
    con.close()

def get_all_progress(db_path=DB_PATH):
    con = sqlite3.connect(db_path)
    rows = con.execute("SELECT * FROM progress").fetchall()
    con.close()
    return {r[0]: _row_to_dict(r) for r in rows}
