"""Tests for recognizing the wish for more questions."""

from __future__ import annotations

import pytest

from custom_components.learnbuddy.wunsch import (
    Uebungswunsch,
    WunschFach,
    erkenne_anzahl,
    erkenne_uebungswunsch,
    erkenne_zusatzwunsch,
)


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


# ----------------------------------------------------------------------
# The wish to practise a subject or a lesson
# ----------------------------------------------------------------------


_FAECHER = [
    WunschFach("en", "Englisch", vokabeln=True, lektionen=("Unit 1", "Unit 2")),
    WunschFach("ma", "Mathematik", lektionen=("Brüche", "Unit 2")),
    WunschFach("bio", "Biologie", lektionen=("Die Zelle", "3")),
]


@pytest.mark.parametrize(
    ("nachricht", "wunsch"),
    [
        ("Ich würde gerne Mathe üben", Uebungswunsch("ma")),
        ("ich möchte Mathematik üben!", Uebungswunsch("ma")),
        (
            "Frag mich die Vokabeln aus der Unit 1 ab",
            Uebungswunsch("en", "Unit 1"),
        ),
        ("frag mich 5 Vokabeln ab", Uebungswunsch("en", None, 5)),
        ("gib mir zehn Aufgaben in Bio", Uebungswunsch("bio", None, 10)),
        ("noch 3 Mathe", Uebungswunsch("ma", None, 3)),
        ("ich will eine Runde Englisch üben", Uebungswunsch("en")),
        ("Brüche üben", Uebungswunsch("ma", "Brüche")),
        ("ich will die zelle lernen", Uebungswunsch("bio", "Die Zelle")),
        ("Englisch Unit 2 üben, 4 Stück", Uebungswunsch("en", "Unit 2", 4)),
        ("Bio Kapitel 3 abfragen", Uebungswunsch("bio", "3")),
        ("I want to practice Englisch", Uebungswunsch("en")),
        ("quiz me on 5 words", Uebungswunsch("en", None, 5)),
        # Not assignable
        ("ich will üben", Uebungswunsch()),
        ("Unit 2 üben", Uebungswunsch()),
        ("ich will 7 Aufgaben üben", Uebungswunsch(anzahl=7)),
        ("ich möchte das mit den Tieren lernen", Uebungswunsch()),
        ("5 oder 6 Mathe üben", Uebungswunsch("ma")),
    ],
)
def test_uebungswunsch(nachricht: str, wunsch: Uebungswunsch) -> None:
    assert erkenne_uebungswunsch(nachricht, _FAECHER) == wunsch


@pytest.mark.parametrize(
    "nachricht",
    [
        "",
        "Mathe",
        "Englisch",
        "Unit 1",
        "der Hund",
        "3",
        "ich weiß es nicht",
        "x " * 16,
    ],
)
def test_kein_uebungswunsch(nachricht: str) -> None:
    assert erkenne_uebungswunsch(nachricht, _FAECHER) is None


def test_vokabeln_mit_mehreren_vokabelfaechern() -> None:
    faecher = [
        WunschFach("en", "Englisch", vokabeln=True),
        WunschFach("fr", "Französisch", vokabeln=True),
    ]
    assert erkenne_uebungswunsch("Vokabeln üben", faecher) == Uebungswunsch()
    assert erkenne_uebungswunsch("Französisch Vokabeln üben", faecher) == (
        Uebungswunsch("fr")
    )


def test_fachname_mit_vokabeln() -> None:
    faecher = [
        WunschFach("en", "Englisch Vokabeln", vokabeln=True),
        WunschFach("la", "Latein Vokabeln", vokabeln=True),
    ]
    assert erkenne_uebungswunsch("Latein üben", faecher) == Uebungswunsch("la")
    assert not erkenne_uebungswunsch("Vokabeln üben", faecher).eindeutig


def test_kurzform() -> None:
    assert erkenne_uebungswunsch("bio üben", _FAECHER) == Uebungswunsch("bio")
    # Two letters are no short form
    assert erkenne_uebungswunsch("ma üben", _FAECHER) == Uebungswunsch()


@pytest.mark.parametrize(
    ("nachricht", "anzahl"),
    [("5", 5), ("zehn", 10), ("10 Stück bitte", 10), ("drei bitte", 3)],
)
def test_anzahl(nachricht: str, anzahl: int | None) -> None:
    assert erkenne_anzahl(nachricht) == anzahl


@pytest.mark.parametrize("nachricht", ["", "keine Ahnung", "0", "3 oder 4", "eine"])
def test_keine_anzahl(nachricht: str) -> None:
    assert erkenne_anzahl(nachricht) is None
