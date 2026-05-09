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

def test_inf_to_hebrew_answer():
    ex = generate_exercise(VERB, mode="inf_to_hebrew")
    assert ex["answer"] == "לכתוב"

def test_past_to_hebrew_answer():
    ex = generate_exercise(VERB, mode="past_to_hebrew")
    assert ex["answer"] == "כתב"

def test_fill_blank_answer():
    ex = generate_exercise(VERB, mode="fill_blank")
    assert ex["answer"] == "wrote"

def test_check_answer_case_insensitive():
    assert check_answer("Wrote", "wrote") is True

def test_check_answer_strips_whitespace():
    assert check_answer("  wrote  ", "wrote") is True

def test_check_answer_wrong():
    assert check_answer("writed", "wrote") is False
