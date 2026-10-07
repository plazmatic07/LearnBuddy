"""Tests for the local evaluation of math answers."""

from __future__ import annotations

from fractions import Fraction

import pytest

from custom_components.learnbuddy.mathe import bewerte_mathe, zerlege
from custom_components.learnbuddy.models import Ergebnis


@pytest.mark.parametrize(
    ("text", "erwartet"),
    [
        ("56", (Fraction(56), "", None)),
        (" 0,5 ", (Fraction(1, 2), "", 1)),
        ("0.25", (Fraction(1, 4), "", 2)),
        ("1/2", (Fraction(1, 2), "", None)),
        ("½", (Fraction(1, 2), "", None)),
        ("1 1/2", (Fraction(3, 2), "", None)),
        ("1½", (Fraction(3, 2), "", None)),
        ("-1 1/2", (Fraction(-3, 2), "", None)),
        ("−3", (Fraction(-3), "", None)),
        ("1.000", (Fraction(1000), "", None)),
        ("1.234,5", (Fraction(2469, 2), "", 1)),
        ("3 m", (Fraction(3), "m", None)),
        ("3m", (Fraction(3), "m", None)),
        ("3 Meter", (Fraction(3), "m", None)),
        ("12,50 €", (Fraction(25, 2), "€", 2)),
        ("12,50 Euro", (Fraction(25, 2), "€", 2)),
        ("50 %", (Fraction(50), "%", None)),
        ("x = 3", (Fraction(3), "", None)),
        ("= 7.", (Fraction(7), "", None)),
        ("4 cm2", (Fraction(4), "cm²", None)),
    ],
)
def test_zerlege(text: str, erwartet: tuple[Fraction, str, int | None]) -> None:
    assert zerlege(text) == erwartet


@pytest.mark.parametrize("text", ["", "drei", "x", "1/0", "1 1/0", "1.2.3"])
def test_zerlege_keine_zahl(text: str) -> None:
    assert zerlege(text) is None


@pytest.mark.parametrize(
    ("antwort", "loesung", "alternativen", "ergebnis"),
    [
        ("56", "56", [], Ergebnis.RICHTIG),
        ("0,5", "1/2", [], Ergebnis.RICHTIG),
        ("½", "0,5", [], Ergebnis.RICHTIG),
        ("2/4", "1/2", [], Ergebnis.RICHTIG),
        ("1,50", "1 1/2", [], Ergebnis.RICHTIG),
        ("x=3", "3", [], Ergebnis.RICHTIG),
        ("3 Meter", "3 m", [], Ergebnis.RICHTIG),
        ("3", "3 m", [], Ergebnis.FAST_RICHTIG),
        ("3 cm", "3 m", [], Ergebnis.FALSCH),
        ("300 cm", "3 m", ["300 cm"], Ergebnis.RICHTIG),
        ("3 m", "3", [], Ergebnis.RICHTIG),
        ("57", "56", [], Ergebnis.FALSCH),
        ("", "56", [], Ergebnis.FALSCH),
        ("  ", "56", [], Ergebnis.FALSCH),
        # Rounded decimals of a periodic fraction
        ("0,33", "1/3", [], Ergebnis.RICHTIG),
        ("0,667", "2/3", [], Ergebnis.RICHTIG),
        ("0,3", "1/3", [], Ergebnis.FALSCH),
        ("0,34", "1/3", [], Ergebnis.FALSCH),
        ("0,49", "1/2", [], Ergebnis.FALSCH),
        # Texts are compared without case and spaces
        ("Ja", "ja", [], Ergebnis.RICHTIG),
        ("x = 3 oder x = −3", "x=3 oder x=-3", [], Ergebnis.RICHTIG),
        # Not decidable locally
        ("drei", "3", [], None),
        ("gerade", "ungerade", [], None),
        ("4", "x = 3 oder x = -3", ["3 und -3"], None),
        ("4", "vier", ["5"], None),
        ("4", "vier", ["4"], Ergebnis.RICHTIG),
    ],
)
def test_bewerte_mathe(
    antwort: str, loesung: str, alternativen: list[str], ergebnis: Ergebnis | None
) -> None:
    assert bewerte_mathe(antwort, loesung, alternativen) is ergebnis
