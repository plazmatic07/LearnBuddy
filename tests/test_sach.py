"""Tests for the pure logic of knowledge questions."""

from __future__ import annotations

from random import Random

import pytest

from custom_components.learnbuddy.models import Ergebnis
from custom_components.learnbuddy.sach import (
    bewerte_auswahl,
    formatiere,
    gewaehlt,
    gleiche_antwort,
    mische,
    normalisiere,
)

OPTIONEN = ["Chlorophyll", "Wasser", "Zellwand"]


def test_mische() -> None:
    optionen = mische("richtig", ["f1", "f2", "f3", "f4"], Random(1))
    # At most four options, the correct one is always among them
    assert sorted(optionen) == ["f1", "f2", "f3", "richtig"]
    reihenfolgen = {
        tuple(mische("richtig", ["f1", "f2"], Random(seed))) for seed in range(20)
    }
    assert len(reihenfolgen) > 1


def test_formatiere() -> None:
    assert formatiere(OPTIONEN) == "A) Chlorophyll\nB) Wasser\nC) Zellwand"


@pytest.mark.parametrize(
    ("eingabe", "erwartet"),
    [
        ("a", "Chlorophyll"),
        ("B", "Wasser"),
        (" c) ", "Zellwand"),
        ("(b)", "Wasser"),
        ("b.", "Wasser"),
        ("Antwort C", "Zellwand"),
        ("antwort: a", "Chlorophyll"),
        ("wasser", "Wasser"),
        ("  Zellwand! ", "Zellwand"),
        # No fourth option
        ("d", None),
        ("e", None),
        ("", None),
        ("keine Ahnung", None),
        # A sentence is not a letter
        ("a und b", None),
    ],
)
def test_gewaehlt(eingabe: str, erwartet: str | None) -> None:
    assert gewaehlt(eingabe, OPTIONEN) == erwartet


def test_bewerte_auswahl() -> None:
    assert bewerte_auswahl("a", OPTIONEN, "Chlorophyll") is Ergebnis.RICHTIG
    assert bewerte_auswahl("chlorophyll", OPTIONEN, "Chlorophyll") is Ergebnis.RICHTIG
    assert bewerte_auswahl("b", OPTIONEN, "Chlorophyll") is Ergebnis.FALSCH
    assert bewerte_auswahl("weiß nicht", OPTIONEN, "Chlorophyll") is Ergebnis.FALSCH


def test_gleiche_antwort() -> None:
    assert normalisiere("  In den  Chloroplasten. ") == "in den chloroplasten"
    assert gleiche_antwort("in den chloroplasten", "In den Chloroplasten.")
    assert not gleiche_antwort("in den Zellen", "In den Chloroplasten.")
    assert not gleiche_antwort("…", "In den Chloroplasten.")
