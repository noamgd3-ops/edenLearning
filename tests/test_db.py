import pytest
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

def test_update_progress_correct(db_path):
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

def test_mastered_after_three_correct(db_path):
    init_db(db_path)
    for _ in range(3):
        update_progress("write", correct=True, db_path=db_path)
    p = get_progress("write", db_path)
    assert p["status"] == "mastered"

def test_wrong_resets_consecutive(db_path):
    init_db(db_path)
    update_progress("write", correct=True, db_path=db_path)
    update_progress("write", correct=True, db_path=db_path)
    update_progress("write", correct=False, db_path=db_path)
    p = get_progress("write", db_path)
    assert p["consecutive_correct"] == 0
    assert p["status"] != "mastered"
