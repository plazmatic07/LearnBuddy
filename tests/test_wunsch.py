"""Tests for recognizing the wish for more questions."""

from __future__ import annotations

import pytest

from custom_components.learnbuddy.wunsch import erkenne_zusatzwunsch


@pytest.mark.parametrize(
    ("nachricht", "anzahl"),
    [
        ("👍", 1),
        (" 👍🏽 ", 1),
        ("👍👍", 1),
        ("noch 10 mehr", 10),
        ("Noch 10 mehr!", 10),
        ("noch 3", 3),
        ("10 mehr bitte", 10),
        ("noch eine", 1),
        ("noch eine Aufgabe bitte", 1),
        ("noch zehn Vokabeln", 10),
        ("mehr", 1),
        ("weiter", 1),
        ("nochmal", 1),
        ("5 more", 5),
        ("one more please", 1),
        ("another question", 1),
        ("noch 500", 500),
    ],
)
def test_wunsch_erkannt(nachricht: str, anzahl: int) -> None:
    assert erkenne_zusatzwunsch(nachricht) == anzahl


@pytest.mark.parametrize(
    "nachricht",
    [
        "",
        "   ",
        "10",
        "dog",
        "bitte",
        "noch 0",
        "noch 3 oder 4",
        "👍 super",
        "ich mag noch mehr Eis",
        "noch eine Aufgabe für mich bitte gleich",
        "der Hund",
    ],
)
def test_kein_wunsch(nachricht: str) -> None:
    assert erkenne_zusatzwunsch(nachricht) is None
