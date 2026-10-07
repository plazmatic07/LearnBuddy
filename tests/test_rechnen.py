"""Tests for the safe arithmetic evaluation."""

from __future__ import annotations

from fractions import Fraction

import pytest

from custom_components.learnbuddy.rechnen import berechne


@pytest.mark.parametrize(
    ("ausdruck", "wert"),
    [
        ("1 + 2", Fraction(3)),
        ("3/4 + 1/8", Fraction(7, 8)),
        ("7 · 8", Fraction(56)),
        ("7 × 8", Fraction(56)),
        ("12 : 4", Fraction(3)),
        ("12 ÷ 4", Fraction(3)),
        ("2,5 * 4", Fraction(10)),
        ("0.1 + 0.2", Fraction(3, 10)),
        ("(2 + 3) * 4", Fraction(20)),
        ("-3 + 5", Fraction(2)),
        ("5 − 8", Fraction(-3)),
        ("2^3", Fraction(8)),
        ("5²", Fraction(25)),
        ("2³ + 1", Fraction(9)),
        ("2 ** -1", Fraction(1, 2)),
        ("½ + ¼", Fraction(3, 4)),
        ("20 % * 50", Fraction(10)),
        ("12,5%", Fraction(1, 8)),
        ("+4", Fraction(4)),
    ],
)
def test_berechne(ausdruck: str, wert: Fraction) -> None:
    assert berechne(ausdruck) == wert


@pytest.mark.parametrize(
    "ausdruck",
    [
        "",
        "   ",
        "1 / 0",
        "0 ** -1",
        "2 ** 0.5",
        "2 ** 11",
        "9 ** 9 ** 9",
        "x + 1",
        "3 = 3",
        "__import__('os')",
        "abs(-1)",
        "1 if 1 else 2",
        "[1, 2]",
        "1 +",
        "(1 + 2",
        "3 // 2",
        "1 < 2",
        "~1",
        "1" + " + 1" * 100,
        "9" * 70,
        "10 ** 10 * 10 ** 10 * 10 ** 10 * 10 ** 10 * 10 ** 10 * 10 ** 10 * 10",
        "(" * 150 + "1" + ")" * 150,
    ],
)
def test_berechne_ungueltig(ausdruck: str) -> None:
    assert berechne(ausdruck) is None
