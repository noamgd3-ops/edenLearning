# Irregular Verbs Learning App — Design Spec
*Date: 2026-05-09*

## Overview

A locally-run desktop learning app (Streamlit) that helps the user master English irregular verbs through interactive typing exercises. The app covers 70 verbs sourced from a classroom chart, with Hebrew translations baked in, spaced repetition progress tracking, and multiple fun exercise styles.

---

## Stack

| Layer | Choice | Reason |
|---|---|---|
| UI | Streamlit | Modern look, pure Python, runs with one command |
| Data | JSON file | Static verb data with Hebrew translations |
| Progress | SQLite (via `sqlite3`) | Lightweight, local, persistent across sessions |
| Spaced repetition | SM-2 algorithm | Simple, well-proven, implemented in ~20 lines |

Run with: `streamlit run app.py`

---

## Data

### `data/verbs.json`

Each entry:
```json
{
  "infinitive": "write",
  "past": "wrote",
  "category": "long o",
  "hebrew_infinitive": "לכתוב",
  "hebrew_past": "כתב"
}
```

70 entries total, translations embedded directly (no API).

### `data/progress.db` (SQLite)

Table: `progress`

| Column | Type | Description |
|---|---|---|
| verb | TEXT PK | Infinitive form |
| times_seen | INTEGER | Total exercise attempts |
| times_correct | INTEGER | Correct attempts |
| ease_factor | REAL | SM-2 ease factor (starts at 2.5) |
| interval_days | REAL | Days until next review |
| next_review | DATE | When to show it again |
| status | TEXT | `new` / `learning` / `mastered` |

---

## Exercise Modes

Five modes rotate randomly, weighted by what's most needed per word:

| # | Mode | Prompt | Answer |
|---|---|---|---|
| 1 | Hebrew → Infinitive | "How do you spell: לכתוב?" | `write` |
| 2 | Infinitive → Past | "Past tense of: write?" | `wrote` |
| 3 | Past → Infinitive | "Base form of: wrote?" | `write` |
| 4 | Scrambled letters | "Unscramble: **t-o-r-w-e**" | `wrote` |
| 5 | Fill in the blank | "Yesterday I ___ a letter. (write)" | `wrote` |

All modes use a **text input box**. Answer is checked case-insensitively and trimmed.

---

## UX Flow

```
[Home screen]
  → Show session stats (words due today, mastered total, current streak)
  → [Start Practice] button

[Exercise screen]
  → Show exercise prompt (one of 5 modes)
  → User types answer + presses Enter
  → Immediate feedback:
      ✅ Correct  → green flash, show Hebrew meaning, next word
      ❌ Wrong    → red shake, show correct answer + Hebrew, next word
  → Progress bar showing session completion

[Session Summary screen]
  → Words practiced, correct %, streak, newly mastered words
  → [Practice Again] / [Home] buttons
```

---

## Progress & Spaced Repetition

Uses a simplified **SM-2** algorithm:

- **Correct answer:** increase interval (next review further away), increase ease factor slightly
- **Wrong answer:** reset interval to 1 day, decrease ease factor
- Words are promoted: `new → learning → mastered` after 3 consecutive correct reviews

Session size: **20 exercises** per session (mix of due words + new words).

---

## Streak & Gamification

- **Streak counter:** increments each day the user completes at least one session
- **Session score:** shown as X/20 with percentage
- **Mastery badge:** words that reach `mastered` status get a ⭐ on the home screen word list
- **Category progress:** show % mastered per verb category (→ a, long o, etc.)

---

## File Structure

```
edenLearniung/
├── app.py                  # Streamlit entry point
├── data/
│   ├── verbs.json          # 70 verbs with Hebrew translations
│   └── progress.db         # SQLite progress (auto-created)
├── src/
│   ├── db.py               # DB init and queries
│   ├── exercises.py        # Exercise generation logic (5 modes)
│   ├── scheduler.py        # SM-2 spaced repetition logic
│   └── session.py          # Session state management
├── irregular_verbs.csv     # Original source data
└── docs/
    └── superpowers/specs/
        └── 2026-05-09-irregular-verbs-learning-app-design.md
```

---

## Out of Scope

- Audio pronunciation
- Multiplayer / leaderboard
- Cloud sync
- Mobile support
