"""Tests for the pure logic of simulated exams."""

from __future__ import annotations

from collections import Counter
from random import Random

from custom_components.learnbuddy.models import Ergebnis, MatheAufgabe, Vokabel
from custom_components.learnbuddy.simulation import (
    MAX_AUFGABEN,
    punkte_text,
    waehle,
    werte_aus,
)

RICHTUNGEN = ("de>en", "en>de")


def _vokabeln(lektion: str | None, anzahl: int, **felder: object) -> list[Vokabel]:
    return [
        Vokabel(
            fach_id="f",
            frage={"de": f"{lektion}-{i}", "en": f"{lektion}-{i}-en"},
            lektion=lektion,
            **felder,  # type: ignore[arg-type]
        )
        for i in range(anzahl)
    ]


def test_waehle_verteilt_ueber_lektionen() -> None:
    aufgaben = [*_vokabeln("A", 20), *_vokabeln("B", 20), *_vokabeln("C", 2)]
    gewaehlt = waehle(aufgaben, RICHTUNGEN, 9, Random(3))
    assert len(gewaehlt) == 9
    assert len({a.id for a, _ in gewaehlt}) == 9
    je_lektion = Counter(a.lektion for a, _ in gewaehlt)
    # C only has two tasks, the others fill up evenly
    assert je_lektion["C"] == 2
    assert {je_lektion["A"], je_lektion["B"]} == {3, 4}
    assert {richtung for _, richtung in gewaehlt} == set(RICHTUNGEN)


def test_waehle_nur_freigegebene_und_fragbare() -> None:
    aufgaben = [
        *_vokabeln("A", 3),
        *_vokabeln("A", 5, geprueft=False),
        Vokabel(fach_id="f", frage={"de": "nur deutsch", "en": ""}),
    ]
    gewaehlt = waehle(aufgaben, RICHTUNGEN, 10, Random(1))
    assert len(gewaehlt) == 3
    assert all(a.geprueft for a, _ in gewaehlt)
    assert waehle(aufgaben, RICHTUNGEN, 0, Random(1)) == []
    assert waehle([], RICHTUNGEN, 5, Random(1)) == []
    # A math subject has a single direction
    mathe = [MatheAufgabe(fach_id="m", aufgabe="1 + 1", loesung="2")]
    assert waehle(mathe, ("mathe",), 5, Random(1)) == [(mathe[0], "mathe")]


def test_waehle_obergrenze() -> None:
    gewaehlt = waehle(_vokabeln("A", 80), RICHTUNGEN, 99, Random(1))
    assert len(gewaehlt) == MAX_AUFGABEN


def test_waehle_ist_zufaellig() -> None:
    aufgaben = _vokabeln("A", 30)
    reihen = {
        tuple(a.id for a, _ in waehle(aufgaben, RICHTUNGEN, 5, Random(seed)))
        for seed in range(10)
    }
    assert len(reihen) > 5


def test_werte_aus() -> None:
    auswertung = werte_aus(
        [
            Ergebnis.RICHTIG,
            Ergebnis.FAST_RICHTIG,
            Ergebnis.TEILWEISE,
            Ergebnis.FALSCH,
            # Could not be judged: does not count
            Ergebnis.UNBEANTWORTET,
            # Not answered any more
            None,
        ]
    )
    assert (auswertung.punkte, auswertung.moeglich, auswertung.unbewertet) == (
        2.5,
        5,
        1,
    )
    assert auswertung.prozent == 50
    leer = werte_aus([Ergebnis.UNBEANTWORTET])
    assert (leer.punkte, leer.moeglich, leer.prozent) == (0, 0, None)


def test_punkte_text() -> None:
    assert punkte_text(7.0, "de") == "7"
    assert punkte_text(7.5, "de") == "7,5"
    assert punkte_text(7.5, "en") == "7.5"
