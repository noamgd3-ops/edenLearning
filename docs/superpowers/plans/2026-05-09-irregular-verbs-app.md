# Irregular Verbs Learning App — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local Streamlit app that teaches English irregular verbs through 5 typing exercise modes with Hebrew translations and SM-2 spaced repetition.

**Architecture:** Streamlit front-end manages all UI and session state via `st.session_state`. Pure-Python modules handle data, scheduling, and exercise generation. SQLite stores per-word progress persistently.

**Tech Stack:** Python 3.10+, Streamlit, SQLite3 (stdlib), JSON (stdlib)

---

## File Map

| File | Responsibility |
|---|---|
| `app.py` | Streamlit entry point, all UI screens |
| `data/verbs.json` | 70 verbs with Hebrew translations |
| `data/progress.db` | SQLite progress DB (auto-created) |
| `src/db.py` | DB init, read/write progress records |
| `src/scheduler.py` | SM-2 algorithm, pick next words for session |
| `src/exercises.py` | Generate exercise prompts for 5 modes |
| `src/session.py` | Session dataclass, answer checking |
| `tests/test_scheduler.py` | Unit tests for SM-2 logic |
| `tests/test_exercises.py` | Unit tests for exercise generation |
| `tests/test_db.py` | Unit tests for DB operations |

---

## Task 1: Project Setup

**Files:**
- Create: `requirements.txt`
- Create: `src/__init__.py`
- Create: `tests/__init__.py`

- [ ] **Step 1: Install Streamlit**

```bash
pip install streamlit pytest
```

Expected: `Successfully installed streamlit-...`

- [ ] **Step 2: Create requirements.txt**

```
streamlit>=1.32.0
pytest>=8.0.0
```

- [ ] **Step 3: Create package init files**

```bash
mkdir -p src tests data
touch src/__init__.py tests/__init__.py
```

- [ ] **Step 4: Commit**

```bash
git init
git add requirements.txt src/__init__.py tests/__init__.py
git commit -m "chore: project scaffold"
```

---

## Task 2: Verb Data (verbs.json)

**Files:**
- Create: `data/verbs.json`

- [ ] **Step 1: Create verbs.json with all 70 verbs and Hebrew translations**

```json
[
  {"infinitive": "sit",        "past": "sat",        "category": "→ a",       "hebrew": "לשבת",        "hebrew_past": "ישב"},
  {"infinitive": "ring",       "past": "rang",       "category": "→ a",       "hebrew": "לצלצל",       "hebrew_past": "צלצל"},
  {"infinitive": "sing",       "past": "sang",       "category": "→ a",       "hebrew": "לשיר",        "hebrew_past": "שר"},
  {"infinitive": "swim",       "past": "swam",       "category": "→ a",       "hebrew": "לשחות",       "hebrew_past": "שחה"},
  {"infinitive": "drink",      "past": "drank",      "category": "→ a",       "hebrew": "לשתות",       "hebrew_past": "שתה"},
  {"infinitive": "begin",      "past": "began",      "category": "→ a",       "hebrew": "להתחיל",      "hebrew_past": "התחיל"},
  {"infinitive": "know",       "past": "knew",       "category": "→ ew",      "hebrew": "לדעת",        "hebrew_past": "ידע"},
  {"infinitive": "throw",      "past": "threw",      "category": "→ ew",      "hebrew": "לזרוק",       "hebrew_past": "זרק"},
  {"infinitive": "grow",       "past": "grew",       "category": "→ ew",      "hebrew": "לגדול",       "hebrew_past": "גדל"},
  {"infinitive": "blow",       "past": "blew",       "category": "→ ew",      "hebrew": "לנשוף",       "hebrew_past": "נשף"},
  {"infinitive": "fly",        "past": "flew",       "category": "→ ew",      "hebrew": "לעוף",        "hebrew_past": "עף"},
  {"infinitive": "draw",       "past": "drew",       "category": "→ ew",      "hebrew": "לצייר",       "hebrew_past": "ציור"},
  {"infinitive": "speak",      "past": "spoke",      "category": "long o",    "hebrew": "לדבר",        "hebrew_past": "דיבר"},
  {"infinitive": "break",      "past": "broke",      "category": "long o",    "hebrew": "לשבור",       "hebrew_past": "שבר"},
  {"infinitive": "steal",      "past": "stole",      "category": "long o",    "hebrew": "לגנוב",       "hebrew_past": "גנב"},
  {"infinitive": "write",      "past": "wrote",      "category": "long o",    "hebrew": "לכתוב",       "hebrew_past": "כתב"},
  {"infinitive": "ride",       "past": "rode",       "category": "long o",    "hebrew": "לרכוב",       "hebrew_past": "רכב"},
  {"infinitive": "drive",      "past": "drove",      "category": "long o",    "hebrew": "לנהוג",       "hebrew_past": "נהג"},
  {"infinitive": "choose",     "past": "chose",      "category": "long o",    "hebrew": "לבחור",       "hebrew_past": "בחר"},
  {"infinitive": "wake",       "past": "woke",       "category": "long o",    "hebrew": "להתעורר",     "hebrew_past": "התעורר"},
  {"infinitive": "rise",       "past": "rose",       "category": "long o",    "hebrew": "לעלות",       "hebrew_past": "עלה"},
  {"infinitive": "shine",      "past": "shone",      "category": "long o",    "hebrew": "לזרוח",       "hebrew_past": "זרח"},
  {"infinitive": "think",      "past": "thought",    "category": "→ ought",   "hebrew": "לחשוב",       "hebrew_past": "חשב"},
  {"infinitive": "buy",        "past": "bought",     "category": "→ ought",   "hebrew": "לקנות",       "hebrew_past": "קנה"},
  {"infinitive": "bring",      "past": "brought",    "category": "→ ought",   "hebrew": "להביא",       "hebrew_past": "הביא"},
  {"infinitive": "fight",      "past": "fought",     "category": "→ ought",   "hebrew": "להילחם",      "hebrew_past": "נלחם"},
  {"infinitive": "teach",      "past": "taught",     "category": "→ aught",   "hebrew": "ללמד",        "hebrew_past": "לימד"},
  {"infinitive": "catch",      "past": "caught",     "category": "→ aught",   "hebrew": "לתפוס",       "hebrew_past": "תפס"},
  {"infinitive": "leave",      "past": "left",       "category": "→ t",       "hebrew": "לעזוב",       "hebrew_past": "עזב"},
  {"infinitive": "mean",       "past": "meant",      "category": "→ t",       "hebrew": "להתכוון",     "hebrew_past": "התכוון"},
  {"infinitive": "learn",      "past": "learned",    "category": "→ t",       "hebrew": "ללמוד",       "hebrew_past": "למד"},
  {"infinitive": "sleep",      "past": "slept",      "category": "→ t",       "hebrew": "לישון",       "hebrew_past": "ישן"},
  {"infinitive": "keep",       "past": "kept",       "category": "→ t",       "hebrew": "לשמור",       "hebrew_past": "שמר"},
  {"infinitive": "feel",       "past": "felt",       "category": "→ t",       "hebrew": "להרגיש",      "hebrew_past": "הרגיש"},
  {"infinitive": "sweep",      "past": "swept",      "category": "→ t",       "hebrew": "לטאטא",       "hebrew_past": "טאטא"},
  {"infinitive": "get",        "past": "got",        "category": "short o",   "hebrew": "לקבל",        "hebrew_past": "קיבל"},
  {"infinitive": "forget",     "past": "forgot",     "category": "short o",   "hebrew": "לשכוח",       "hebrew_past": "שכח"},
  {"infinitive": "shoot",      "past": "shot",       "category": "short o",   "hebrew": "לירות",       "hebrew_past": "ירה"},
  {"infinitive": "win",        "past": "won",        "category": "short o",   "hebrew": "לנצח",        "hebrew_past": "ניצח"},
  {"infinitive": "come",       "past": "came",       "category": "o → long o","hebrew": "לבוא",        "hebrew_past": "בא"},
  {"infinitive": "become",     "past": "became",     "category": "o → long o","hebrew": "להפוך",       "hebrew_past": "הפך"},
  {"infinitive": "stand",      "past": "stood",      "category": "a → oo",    "hebrew": "לעמוד",       "hebrew_past": "עמד"},
  {"infinitive": "understand", "past": "understood", "category": "a → oo",    "hebrew": "להבין",       "hebrew_past": "הבין"},
  {"infinitive": "shake",      "past": "shook",      "category": "a → oo",    "hebrew": "לנער",        "hebrew_past": "ניער"},
  {"infinitive": "take",       "past": "took",       "category": "a → oo",    "hebrew": "לקחת",        "hebrew_past": "לקח"},
  {"infinitive": "sell",       "past": "sold",       "category": "ell → old", "hebrew": "למכור",       "hebrew_past": "מכר"},
  {"infinitive": "tell",       "past": "told",       "category": "ell → old", "hebrew": "לספר",        "hebrew_past": "סיפר"},
  {"infinitive": "say",        "past": "said",       "category": "uy → ai",   "hebrew": "לומר",        "hebrew_past": "אמר"},
  {"infinitive": "pay",        "past": "paid",       "category": "uy → ai",   "hebrew": "לשלם",        "hebrew_past": "שילם"},
  {"infinitive": "fall",       "past": "fell",       "category": "short a",   "hebrew": "ליפול",       "hebrew_past": "נפל"},
  {"infinitive": "hold",       "past": "held",       "category": "short a",   "hebrew": "להחזיק",      "hebrew_past": "החזיק"},
  {"infinitive": "feed",       "past": "fed",        "category": "short a",   "hebrew": "להאכיל",      "hebrew_past": "האכיל"},
  {"infinitive": "meet",       "past": "met",        "category": "short a",   "hebrew": "לפגוש",       "hebrew_past": "פגש"},
  {"infinitive": "tear",       "past": "tore",       "category": "ear → ore", "hebrew": "לקרוע",       "hebrew_past": "קרע"},
  {"infinitive": "wear",       "past": "wore",       "category": "ear → ore", "hebrew": "ללבוש",       "hebrew_past": "לבש"},
  {"infinitive": "build",      "past": "built",      "category": "d → t",     "hebrew": "לבנות",       "hebrew_past": "בנה"},
  {"infinitive": "send",       "past": "sent",       "category": "d → t",     "hebrew": "לשלוח",       "hebrew_past": "שלח"},
  {"infinitive": "spend",      "past": "spent",      "category": "d → t",     "hebrew": "לבלות",       "hebrew_past": "בילה"},
  {"infinitive": "lend",       "past": "lent",       "category": "d → t",     "hebrew": "להשאיל",      "hebrew_past": "השאיל"},
  {"infinitive": "shut",       "past": "shut",       "category": "no change", "hebrew": "לסגור",       "hebrew_past": "סגר"},
  {"infinitive": "let",        "past": "let",        "category": "no change", "hebrew": "לאפשר",       "hebrew_past": "אפשר"},
  {"infinitive": "put",        "past": "put",        "category": "no change", "hebrew": "לשים",        "hebrew_past": "שם"},
  {"infinitive": "cut",        "past": "cut",        "category": "no change", "hebrew": "לחתוך",       "hebrew_past": "חתך"},
  {"infinitive": "read",       "past": "read",       "category": "no change", "hebrew": "לקרוא",       "hebrew_past": "קרא"},
  {"infinitive": "cost",       "past": "cost",       "category": "no change", "hebrew": "לעלות כסף",   "hebrew_past": "עלה"},
  {"infinitive": "hit",        "past": "hit",        "category": "no change", "hebrew": "להכות",       "hebrew_past": "הכה"},
  {"infinitive": "hurt",       "past": "hurt",       "category": "no change", "hebrew": "לפצוע",       "hebrew_past": "פצע"},
  {"infinitive": "beat",       "past": "beat",       "category": "no change", "hebrew": "להכות/לנצח",  "hebrew_past": "הכה"},
  {"infinitive": "do",         "past": "did",        "category": "others",    "hebrew": "לעשות",       "hebrew_past": "עשה"},
  {"infinitive": "go",         "past": "went",       "category": "others",    "hebrew": "ללכת",        "hebrew_past": "הלך"},
  {"infinitive": "have",       "past": "had",        "category": "others",    "hebrew": "להיות לי",    "hebrew_past": "היה לי"},
  {"infinitive": "be",         "past": "was",        "category": "others",    "hebrew": "להיות",       "hebrew_past": "היה"},
  {"infinitive": "make",       "past": "made",       "category": "others",    "hebrew": "להכין",       "hebrew_past": "הכין"},
  {"infinitive": "run",        "past": "ran",        "category": "others",    "hebrew": "לרוץ",        "hebrew_past": "רץ"},
  {"infinitive": "see",        "past": "saw",        "category": "others",    "hebrew": "לראות",       "hebrew_past": "ראה"}
]
```

- [ ] **Step 2: Commit**

```bash
git add data/verbs.json
git commit -m "feat: add verb data with Hebrew translations"
```

---

## Task 3: Database Layer (src/db.py)

**Files:**
- Create: `src/db.py`
- Create: `tests/test_db.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_db.py`:

```python
import os, tempfile, pytest
from src.db import init_db, get_progress, update_progress, get_all_progress

@pytest.fixture
def db_path(tmp_path):
    return str(tmp_path / "test.db")

def test_init_creates_table(db_path):
    init_db(db_path)
    progress = get_all_progress(db_path)
    assert isinstance(progress, dict)

def test_new_verb_defaults(db_path):
    init_db(db_path)
    p = get_progress("write", db_path)
    assert p["status"] == "new"
    assert p["times_seen"] == 0
    assert p["ease_factor"] == 2.5

def test_update_progress(db_path):
    init_db(db_path)
    update_progress("write", correct=True, db_path=db_path)
    p = get_progress("write", db_path)
    assert p["times_seen"] == 1
    assert p["times_correct"] == 1

def test_wrong_answer_increments_seen(db_path):
    init_db(db_path)
    update_progress("write", correct=False, db_path=db_path)
    p = get_progress("write", db_path)
    assert p["times_seen"] == 1
    assert p["times_correct"] == 0
```

- [ ] **Step 2: Run to verify failure**

```bash
pytest tests/test_db.py -v
```

Expected: `ModuleNotFoundError: No module named 'src.db'`

- [ ] **Step 3: Implement src/db.py**

```python
import sqlite3
from datetime import date

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
            status TEXT DEFAULT 'new'
        )
    """)
    con.commit()
    con.close()

def _row_to_dict(row):
    keys = ["verb","times_seen","times_correct","ease_factor",
            "interval_days","next_review","consecutive_correct","status"]
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
        "next_review": "2000-01-01", "consecutive_correct": 0, "status": "new"
    }

def update_progress(verb, correct, db_path=DB_PATH):
    p = get_progress(verb, db_path)
    p["times_seen"] += 1
    if correct:
        p["times_correct"] += 1
        p["consecutive_correct"] += 1
        new_ef = min(p["ease_factor"] + 0.1, 3.0)
        new_interval = p["interval_days"] * new_ef
        if p["consecutive_correct"] >= 3:
            p["status"] = "mastered"
        elif p["times_seen"] > 0:
            p["status"] = "learning"
        p["ease_factor"] = new_ef
        p["interval_days"] = new_interval
    else:
        p["consecutive_correct"] = 0
        p["ease_factor"] = max(1.3, p["ease_factor"] - 0.2)
        p["interval_days"] = 1.0
        p["status"] = "learning" if p["times_seen"] > 1 else "new"
    today = date.today().isoformat()
    from datetime import timedelta
    next_rev = (date.today() + timedelta(days=p["interval_days"])).isoformat()
    p["next_review"] = next_rev
    con = sqlite3.connect(db_path)
    con.execute("""
        INSERT INTO progress VALUES (?,?,?,?,?,?,?,?)
        ON CONFLICT(verb) DO UPDATE SET
            times_seen=excluded.times_seen,
            times_correct=excluded.times_correct,
            ease_factor=excluded.ease_factor,
            interval_days=excluded.interval_days,
            next_review=excluded.next_review,
            consecutive_correct=excluded.consecutive_correct,
            status=excluded.status
    """, (p["verb"], p["times_seen"], p["times_correct"], p["ease_factor"],
          p["interval_days"], p["next_review"], p["consecutive_correct"], p["status"]))
    con.commit()
    con.close()

def get_all_progress(db_path=DB_PATH):
    con = sqlite3.connect(db_path)
    rows = con.execute("SELECT * FROM progress").fetchall()
    con.close()
    return {r[0]: _row_to_dict(r) for r in rows}
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_db.py -v
```

Expected: 4 tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/db.py tests/test_db.py
git commit -m "feat: add SQLite progress tracking layer"
```

---

## Task 4: Scheduler (src/scheduler.py)

**Files:**
- Create: `src/scheduler.py`
- Create: `tests/test_scheduler.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_scheduler.py`:

```python
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

def test_due_words_prioritized():
    from datetime import date, timedelta
    yesterday = (date.today() - timedelta(days=1)).isoformat()
    progress = {
        "write": {"next_review": yesterday, "status": "learning",
                  "ease_factor": 2.5, "interval_days": 1.0,
                  "times_seen": 2, "times_correct": 1,
                  "consecutive_correct": 0, "verb": "write"}
    }
    words = pick_session_words(VERBS, progress, session_size=3)
    assert words[0]["infinitive"] == "write"

def test_session_size_respected():
    words = pick_session_words(VERBS, {}, session_size=2)
    assert len(words) == 2
```

- [ ] **Step 2: Run to verify failure**

```bash
pytest tests/test_scheduler.py -v
```

Expected: `ModuleNotFoundError: No module named 'src.scheduler'`

- [ ] **Step 3: Implement src/scheduler.py**

```python
import random
from datetime import date

def pick_session_words(verbs, progress, session_size=20):
    today = date.today().isoformat()
    due, new, later = [], [], []
    for v in verbs:
        p = progress.get(v["infinitive"])
        if p is None:
            new.append(v)
        elif p["next_review"] <= today and p["status"] != "mastered":
            due.append(v)
        elif p["status"] == "mastered":
            later.append(v)
        else:
            new.append(v)
    random.shuffle(new)
    random.shuffle(later)
    pool = due + new + later
    return pool[:session_size]
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_scheduler.py -v
```

Expected: 3 tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/scheduler.py tests/test_scheduler.py
git commit -m "feat: add SM-2 session word scheduler"
```

---

## Task 5: Exercise Generator (src/exercises.py)

**Files:**
- Create: `src/exercises.py`
- Create: `tests/test_exercises.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_exercises.py`:

```python
import pytest
from src.exercises import generate_exercise, check_answer

VERB = {"infinitive": "write", "past": "wrote", "category": "long o",
        "hebrew": "לכתוב", "hebrew_past": "כתב"}

def test_generate_returns_dict():
    ex = generate_exercise(VERB, mode="heb_to_inf")
    assert "prompt" in ex
    assert "answer" in ex
    assert "mode" in ex

def test_heb_to_inf_answer():
    ex = generate_exercise(VERB, mode="heb_to_inf")
    assert ex["answer"] == "write"

def test_inf_to_past_answer():
    ex = generate_exercise(VERB, mode="inf_to_past")
    assert ex["answer"] == "wrote"

def test_past_to_inf_answer():
    ex = generate_exercise(VERB, mode="past_to_inf")
    assert ex["answer"] == "write"

def test_scramble_answer():
    ex = generate_exercise(VERB, mode="scramble")
    assert ex["answer"] == "wrote"
    assert sorted(ex["scrambled"]) == sorted("wrote")

def test_fill_blank_answer():
    ex = generate_exercise(VERB, mode="fill_blank")
    assert ex["answer"] == "wrote"

def test_check_answer_case_insensitive():
    assert check_answer("Wrote", "wrote") is True

def test_check_answer_strips_whitespace():
    assert check_answer("  wrote  ", "wrote") is True

def test_check_answer_wrong():
    assert check_answer("writed", "wrote") is False
```

- [ ] **Step 2: Run to verify failure**

```bash
pytest tests/test_exercises.py -v
```

Expected: `ModuleNotFoundError: No module named 'src.exercises'`

- [ ] **Step 3: Implement src/exercises.py**

```python
import random

MODES = ["heb_to_inf", "inf_to_past", "past_to_inf", "scramble", "fill_blank"]

FILL_TEMPLATES = [
    "Yesterday I ___ [hint].",
    "Last week she ___ [hint].",
    "They ___ [hint] last year.",
    "He ___ [hint] this morning.",
    "We ___ [hint] together.",
]

def generate_exercise(verb, mode=None):
    if mode is None:
        mode = random.choice(MODES)
    inf = verb["infinitive"]
    past = verb["past"]
    heb = verb["hebrew"]
    heb_past = verb["hebrew_past"]

    if mode == "heb_to_inf":
        return {
            "mode": mode,
            "prompt": f"🇮🇱  {heb}  →  Spell the English base form:",
            "answer": inf,
            "hint": f"Category: {verb['category']}",
        }
    elif mode == "inf_to_past":
        return {
            "mode": mode,
            "prompt": f"Past tense of:  **{inf}**",
            "answer": past,
            "hint": f"Hebrew past: {heb_past}",
        }
    elif mode == "past_to_inf":
        return {
            "mode": mode,
            "prompt": f"Base form of:  **{past}**",
            "answer": inf,
            "hint": f"Hebrew: {heb}",
        }
    elif mode == "scramble":
        letters = list(past)
        random.shuffle(letters)
        while letters == list(past) and len(past) > 1:
            random.shuffle(letters)
        scrambled = " - ".join(letters)
        return {
            "mode": mode,
            "prompt": f"Unscramble the past tense of **{inf}**:\n\n### {scrambled}",
            "answer": past,
            "scrambled": "".join(letters),
            "hint": f"Hebrew past: {heb_past}",
        }
    elif mode == "fill_blank":
        template = random.choice(FILL_TEMPLATES).replace("[hint]", f"({inf})")
        return {
            "mode": mode,
            "prompt": f"Fill in the blank (past tense):\n\n_{template}_",
            "answer": past,
            "hint": f"Hebrew past: {heb_past}",
        }

def check_answer(user_input, correct_answer):
    return user_input.strip().lower() == correct_answer.strip().lower()
```

- [ ] **Step 4: Run tests**

```bash
pytest tests/test_exercises.py -v
```

Expected: 9 tests pass.

- [ ] **Step 5: Commit**

```bash
git add src/exercises.py tests/test_exercises.py
git commit -m "feat: add 5-mode exercise generator"
```

---

## Task 6: Main Streamlit App (app.py)

**Files:**
- Create: `app.py`

- [ ] **Step 1: Create app.py**

```python
import json, random
from pathlib import Path
import streamlit as st
from src.db import init_db, get_all_progress, update_progress
from src.scheduler import pick_session_words
from src.exercises import generate_exercise, check_answer, MODES

DB_PATH = "data/progress.db"
VERBS_PATH = "data/verbs.json"
SESSION_SIZE = 20

# ── bootstrap ──────────────────────────────────────────────────────────────
Path("data").mkdir(exist_ok=True)
init_db(DB_PATH)
verbs = json.loads(Path(VERBS_PATH).read_text(encoding="utf-8"))

st.set_page_config(page_title="Irregular Verbs", page_icon="📚", layout="centered")

# ── session state defaults ─────────────────────────────────────────────────
def reset_session():
    progress = get_all_progress(DB_PATH)
    session_words = pick_session_words(verbs, progress, SESSION_SIZE)
    st.session_state.update({
        "screen": "home",
        "session_words": session_words,
        "session_index": 0,
        "session_correct": 0,
        "session_results": [],   # list of {verb, correct, exercise}
        "current_ex": None,
        "submitted": False,
        "last_correct": None,
        "show_hint": False,
    })

if "screen" not in st.session_state:
    reset_session()

# ── CSS helpers ────────────────────────────────────────────────────────────
st.markdown("""
<style>
.big-prompt { font-size: 1.4rem; font-weight: 600; margin-bottom: 0.5rem; direction: ltr; }
.hebrew { font-size: 1.8rem; direction: rtl; text-align: right; }
.correct-box { background:#d4edda; border-radius:8px; padding:12px; color:#155724; font-size:1.1rem; }
.wrong-box   { background:#f8d7da; border-radius:8px; padding:12px; color:#721c24; font-size:1.1rem; }
.stat-box    { background:#e9ecef; border-radius:8px; padding:10px; text-align:center; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════
# HOME SCREEN
# ══════════════════════════════════════════════════════════════════════════
def show_home():
    st.title("📚 Irregular Verbs Trainer")
    progress = get_all_progress(DB_PATH)
    total = len(verbs)
    mastered = sum(1 for p in progress.values() if p["status"] == "mastered")
    learning = sum(1 for p in progress.values() if p["status"] == "learning")
    new_count = total - mastered - learning

    col1, col2, col3 = st.columns(3)
    col1.markdown(f'<div class="stat-box">⭐ Mastered<br><b>{mastered}/{total}</b></div>', unsafe_allow_html=True)
    col2.markdown(f'<div class="stat-box">📖 Learning<br><b>{learning}</b></div>', unsafe_allow_html=True)
    col3.markdown(f'<div class="stat-box">🆕 New<br><b>{new_count}</b></div>', unsafe_allow_html=True)

    st.write("")
    due_words = st.session_state.session_words
    st.info(f"Today's session: **{len(due_words)} words** ready to practice.")

    if st.button("▶  Start Practice", type="primary", use_container_width=True):
        st.session_state.screen = "exercise"
        st.session_state.session_index = 0
        st.session_state.session_correct = 0
        st.session_state.session_results = []
        st.session_state.submitted = False
        st.session_state.current_ex = None
        st.rerun()

    st.divider()
    st.subheader("All Verbs")
    verb_lookup = {p["verb"]: p for p in progress.values()}
    rows = []
    for v in verbs:
        p = verb_lookup.get(v["infinitive"], {})
        status = p.get("status", "new")
        icon = "⭐" if status == "mastered" else ("📖" if status == "learning" else "🆕")
        rows.append({
            "": icon,
            "Base form": v["infinitive"],
            "Past": v["past"],
            "Hebrew": v["hebrew"],
            "Category": v["category"],
        })
    st.dataframe(rows, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════════════════════════════════════
# EXERCISE SCREEN
# ══════════════════════════════════════════════════════════════════════════
def show_exercise():
    words = st.session_state.session_words
    idx = st.session_state.session_index

    if idx >= len(words):
        st.session_state.screen = "summary"
        st.rerun()
        return

    verb = words[idx]
    progress_pct = idx / len(words)
    st.progress(progress_pct, text=f"Question {idx+1} of {len(words)}")

    if st.session_state.current_ex is None:
        st.session_state.current_ex = generate_exercise(verb)
        st.session_state.submitted = False
        st.session_state.show_hint = False

    ex = st.session_state.current_ex

    mode_labels = {
        "heb_to_inf":  "🇮🇱 Hebrew → English",
        "inf_to_past":  "⏪ Base → Past",
        "past_to_inf":  "⏩ Past → Base",
        "scramble":     "🔀 Unscramble",
        "fill_blank":   "✏️ Fill the Blank",
    }
    st.caption(mode_labels.get(ex["mode"], ex["mode"]))
    st.markdown(f'<div class="big-prompt">{ex["prompt"]}</div>', unsafe_allow_html=True)

    if not st.session_state.submitted:
        user_input = st.text_input("Your answer:", key=f"input_{idx}", label_visibility="collapsed")
        col_a, col_b = st.columns([3, 1])
        with col_a:
            submit = st.button("Submit ✓", type="primary", use_container_width=True)
        with col_b:
            if st.button("Hint 💡", use_container_width=True):
                st.session_state.show_hint = True
                st.rerun()

        if st.session_state.show_hint:
            st.info(f"💡 {ex.get('hint', '')}")

        if submit and user_input.strip():
            correct = check_answer(user_input, ex["answer"])
            st.session_state.last_correct = correct
            st.session_state.submitted = True
            update_progress(verb["infinitive"], correct=correct, db_path=DB_PATH)
            if correct:
                st.session_state.session_correct += 1
            st.session_state.session_results.append({
                "verb": verb["infinitive"],
                "past": verb["past"],
                "hebrew": verb["hebrew"],
                "correct": correct,
                "user_answer": user_input.strip(),
                "mode": ex["mode"],
            })
            st.rerun()
    else:
        correct = st.session_state.last_correct
        if correct:
            st.markdown(f'<div class="correct-box">✅ Correct! <b>{ex["answer"]}</b> &nbsp;&nbsp; 🇮🇱 {verb["hebrew"]} → {verb["hebrew_past"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="wrong-box">❌ The answer is: <b>{ex["answer"]}</b> &nbsp;&nbsp; 🇮🇱 {verb["hebrew"]} → {verb["hebrew_past"]}</div>', unsafe_allow_html=True)

        st.write("")
        if st.button("Next →", type="primary", use_container_width=True):
            st.session_state.session_index += 1
            st.session_state.current_ex = None
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════
# SUMMARY SCREEN
# ══════════════════════════════════════════════════════════════════════════
def show_summary():
    results = st.session_state.session_results
    total = len(results)
    correct = sum(1 for r in results if r["correct"])
    pct = int(correct / total * 100) if total else 0

    st.title("🎉 Session Complete!")
    col1, col2 = st.columns(2)
    col1.metric("Score", f"{correct}/{total}")
    col2.metric("Accuracy", f"{pct}%")

    if pct == 100:
        st.success("Perfect score! 🏆")
    elif pct >= 70:
        st.info("Great job! Keep it up 💪")
    else:
        st.warning("Keep practicing — you'll get there! 📖")

    st.divider()
    st.subheader("Review")
    for r in results:
        icon = "✅" if r["correct"] else "❌"
        label = f"{icon} **{r['verb']}** → {r['past']}  |  {r['hebrew']}"
        if not r["correct"]:
            label += f"  _(you wrote: {r['user_answer']})_"
        st.markdown(label)

    st.write("")
    if st.button("🔄 Practice Again", type="primary", use_container_width=True):
        reset_session()
        st.rerun()
    if st.button("🏠 Home", use_container_width=True):
        reset_session()
        st.session_state.screen = "home"
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════
# ROUTER
# ══════════════════════════════════════════════════════════════════════════
screen = st.session_state.get("screen", "home")
if screen == "home":
    show_home()
elif screen == "exercise":
    show_exercise()
elif screen == "summary":
    show_summary()
```

- [ ] **Step 2: Run the app**

```bash
streamlit run app.py
```

Expected: Browser opens at `http://localhost:8501` showing the home screen with verb list and "Start Practice" button.

- [ ] **Step 3: Smoke-test the golden path**
  - Click "Start Practice"
  - Answer 3 questions (try correct + wrong answers)
  - Verify feedback boxes appear with Hebrew
  - Complete session → verify summary screen
  - Click "Practice Again" → verify session resets

- [ ] **Step 4: Commit**

```bash
git add app.py
git commit -m "feat: complete Streamlit learning app"
```

---

## Task 7: Run Full Test Suite

- [ ] **Step 1: Run all tests**

```bash
pytest tests/ -v
```

Expected: All tests green. Count: 16 tests.

- [ ] **Step 2: Final commit**

```bash
git add .
git commit -m "chore: verify all tests pass"
```

---

## Done

Run with: `streamlit run app.py`
