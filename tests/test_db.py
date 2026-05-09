import pytest
from unittest.mock import MagicMock, patch


def _make_db():
    """Return fresh in-memory dict acting as a Supabase table."""
    store = {}

    def upsert_fn(row):
        store[row["verb"]] = dict(row)
        m = MagicMock()
        m.execute.return_value = MagicMock(data=[row])
        return m

    def select_fn(*args):
        m = MagicMock()

        def eq_fn(col, val):
            m2 = MagicMock()
            m2.execute.return_value = MagicMock(data=[store[val]] if val in store else [])
            return m2

        def neq_fn(col, val):
            m2 = MagicMock()
            m2.execute.return_value = MagicMock(data=list(store.values()))
            return m2

        m.eq = eq_fn
        m.neq = neq_fn
        m.execute.return_value = MagicMock(data=list(store.values()))
        return m

    def delete_fn():
        m = MagicMock()

        def neq_fn(col, val):
            store.clear()
            m2 = MagicMock()
            m2.execute.return_value = MagicMock(data=[])
            return m2

        m.neq = neq_fn
        return m

    tbl = MagicMock()
    tbl.select.side_effect = select_fn
    tbl.upsert.side_effect = upsert_fn
    tbl.delete.side_effect = delete_fn

    sb = MagicMock()
    sb.table.return_value = tbl
    return sb


@pytest.fixture(autouse=True)
def mock_supabase(monkeypatch):
    sb = _make_db()
    monkeypatch.setattr("src.db._client", lambda: sb)
    return sb


def test_new_verb_defaults():
    from src.db import get_progress
    p = get_progress("write")
    assert p["status"] == "new"
    assert p["times_seen"] == 0
    assert p["ease_factor"] == 2.5


def test_update_progress_correct():
    from src.db import update_progress, get_progress
    update_progress("write", correct=True)
    p = get_progress("write")
    assert p["times_seen"] == 1
    assert p["times_correct"] == 1


def test_wrong_answer_increments_seen():
    from src.db import update_progress, get_progress
    update_progress("write", correct=False)
    p = get_progress("write")
    assert p["times_seen"] == 1
    assert p["times_correct"] == 0


def test_mastered_after_three_correct():
    from src.db import update_progress, get_progress
    for _ in range(3):
        update_progress("write", correct=True)
    p = get_progress("write")
    assert p["status"] == "mastered"


def test_wrong_resets_consecutive():
    from src.db import update_progress, get_progress
    update_progress("write", correct=True)
    update_progress("write", correct=True)
    update_progress("write", correct=False)
    p = get_progress("write")
    assert p["consecutive_correct"] == 0
    assert p["status"] != "mastered"
