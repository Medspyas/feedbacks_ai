import pytest
from app.utils import clean_text, is_valid_content


def test_clean_text_empty_or_none():

    assert clean_text("") == ""
    assert clean_text(None) == ""


def test_clean_text_html_and_escaping():
    assert clean_text("<p>Hello & welcome</p>") == "Hello &amp; welcome"


def test_clean_text_spaces():
    assert clean_text("    Mot1    Mot2    ") == "Mot1 Mot2"


def test_clean_text_overflow():
    long_text = "a" * 2008
    cleaned = clean_text(long_text)
    assert len(cleaned) == 2000


def test_is_valid_content_cases():
    assert is_valid_content("Bonjour") is True
    assert is_valid_content("123") is True

    assert is_valid_content(None) is False
    assert is_valid_content("") is False
    assert is_valid_content("ab") is False
    assert is_valid_content("a" * 20) is False
