"""Tests for the daily log of answers."""

from __future__ import annotations

from datetime import date, timedelta

import pytest

from custom_components.learnbuddy.verlauf import (
    AUFBEWAHRUNG_TAGE,
    MAX_SIMULATIONEN,
    FachTag,
    KindVerlauf,
    SimErgebnis,
    tage_von_bis,
    trefferquote,
    woche,
)

MO = date(2026, 10, 5)
DI = date(2026, 10, 6)
MI = date(2026, 10, 7)


def _beispiel() -> KindVerlauf:
    verlauf = KindVerlauf()
    for _ in range(4):
        verlauf.frage(MO, "en")
    verlauf.ergebnis(MO, "en", "richtig", lektion="Unit 3", aufgabe_id="a")
    verlauf.ergebnis(MO, "en", "fast_richtig", lektion="Unit 3", aufgabe_id="b")
    verlauf.ergebnis(MO, "en", "falsch", lektion="Unit 3", aufgabe_id="c")
    verlauf.ergebnis(MO, "en", "unbeantwortet", lektion="Unit 3", aufgabe_id="d")
    verlauf.frage(DI, "en")
    verlauf.frage(DI, "bio")
    verlauf.ergebnis(DI, "en", "falsch", lektion="Unit 3", aufgabe_id="c")
    verlauf.ergebnis(DI, "bio", "teilweise", lektion="Zelle", aufgabe_id="z")
    return verlauf


def test_buchen_und_summe() -> None:
    verlauf = _beispiel()
    assert verlauf.seit == MO
    assert verlauf.summe(MO, MO) == {
        "gefragt": 4,
        "richtig": 2,
        "teilweise": 0,
        "falsch": 1,
        "unbeantwortet": 1,
        "trefferquote": 67,
        "tage_aktiv": 1,
    }
    assert verlauf.summe(MO, MI) == {
        "gefragt": 6,
        "richtig": 2,
        "teilweise": 1,
        "falsch": 2,
        "unbeantwortet": 1,
        "trefferquote": 50,
        "tage_aktiv": 2,
    }
    # A period without anything
    leer = verlauf.summe(MI, MI)
    assert leer["gefragt"] == 0
    assert leer["trefferquote"] is None
    assert leer["tage_aktiv"] == 0

    eintrag = verlauf.tage[MO]["en"]
    assert eintrag.lektionen == {"Unit 3": [2, 1]}
    assert eintrag.aufgaben_falsch == {"c": 1}
    # Partly right is neither right nor wrong for the lesson
    assert verlauf.tage[DI]["bio"].lektionen == {}

    # Unknown results and missing details change nothing more
    verlauf.ergebnis(MI, "en", "gibtsnicht")
    assert MI not in verlauf.tage
    verlauf.ergebnis(MI, "en", "falsch")
    assert verlauf.tage[MI]["en"].aufgaben_falsch == {}
    assert verlauf.tage[MI]["en"].lektionen == {}


def test_frage_zurueck() -> None:
    verlauf = KindVerlauf()
    verlauf.frage(MO, "en")
    verlauf.frage_zurueck(MO, "en")
    assert verlauf.tage[MO]["en"].gefragt == 0
    # Never below zero, and nothing is created for unknown days
    verlauf.frage_zurueck(MO, "en")
    verlauf.frage_zurueck(DI, "en")
    verlauf.frage_zurueck(MO, "bio")
    assert verlauf.tage[MO]["en"].gefragt == 0
    assert list(verlauf.tage) == [MO]


def test_reihe_mit_glaettung() -> None:
    verlauf = _beispiel()
    reihe = verlauf.reihe(MO - timedelta(days=1), MI)
    assert [e["tag"] for e in reihe] == [
        "2026-10-04",
        "2026-10-05",
        "2026-10-06",
        "2026-10-07",
    ]
    assert [e["gefragt"] for e in reihe] == [0, 4, 2, 0]
    assert [e["unbeantwortet"] for e in reihe] == [0, 1, 0, 0]
    # Smoothed over the last days: Monday 2 of 3, from Tuesday 2 of 4
    assert [e["trefferquote"] for e in reihe] == [None, 67, 50, 50]

    # The window looks back before the period, and it ends after seven days
    spaeter = verlauf.reihe(date(2026, 10, 11), date(2026, 10, 13))
    assert [e["trefferquote"] for e in spaeter] == [50, 0, None]


def test_lernstand() -> None:
    verlauf = KindVerlauf()
    assert verlauf.lernstand_am("en", MI) is None
    verlauf.lernstand(MO, "en", 10, 2)
    verlauf.lernstand(MO, "en", 10, 3)
    verlauf.lernstand(MI, "en", 12, 6)
    verlauf.lernstand(MI, "leer", 0, 0)
    assert verlauf.lernstand_am("en", MO - timedelta(days=1)) is None
    assert verlauf.lernstand_am("en", DI) == 30
    assert verlauf.lernstand_am("en", MI) == 50
    assert verlauf.lernstand_am("leer", MI) is None
    # The last value carries on over days without an entry
    assert verlauf.lernstand_reihe("en", MO - timedelta(days=1), MI) == [
        None,
        30,
        30,
        50,
    ]
    assert verlauf.lernstand_reihe("en", DI, DI) == [30]
    assert verlauf.lernstand_reihe("bio", MO, DI) == [None, None]


def test_schwachstellen() -> None:
    verlauf = _beispiel()
    # Unit 3: 2 right, 2 wrong over both days
    assert verlauf.schwache_lektionen(MO, MI) == [
        {
            "fach_id": "en",
            "lektion": "Unit 3",
            "richtig": 2,
            "falsch": 2,
            "fehlerquote": 50,
        }
    ]
    # Too few answers on Tuesday alone
    assert verlauf.schwache_lektionen(DI, DI) == []
    # Lessons without a wrong answer are no weak spot
    for _ in range(3):
        verlauf.ergebnis(MI, "bio", "richtig", lektion="Zelle", aufgabe_id="z")
    for _ in range(3):
        verlauf.ergebnis(MI, "bio", "falsch", lektion="Blatt", aufgabe_id="y")
    lektionen = verlauf.schwache_lektionen(MO, MI)
    assert [(e["lektion"], e["fehlerquote"]) for e in lektionen] == [
        ("Blatt", 100),
        ("Unit 3", 50),
    ]
    assert len(verlauf.schwache_lektionen(MO, MI, anzahl=1)) == 1

    assert verlauf.schwierige_aufgaben(MO, MI) == [
        ("bio", "y", 3),
        ("en", "c", 2),
    ]
    assert verlauf.schwierige_aufgaben(MO, MO) == [("en", "c", 1)]


def test_simulationen() -> None:
    verlauf = KindVerlauf()
    erste = SimErgebnis(MO, "arbeit1", "en", 7.5, 10)
    zweite = SimErgebnis(MI, "arbeit1", "en", 3, 4, vollstaendig=False)
    verlauf.simulation(zweite)
    verlauf.simulation(erste)
    assert verlauf.seit == MO
    assert erste.prozent == 75
    assert SimErgebnis(MO, "a", "en", 0, 0).prozent is None
    assert verlauf.simulationen_im(MO, MI) == [zweite, erste]
    assert verlauf.simulationen_im(DI, MI) == [zweite]
    for nummer in range(MAX_SIMULATIONEN + 5):
        verlauf.simulation(SimErgebnis(MI, f"a{nummer}", "en", 1, 1))
    assert len(verlauf.simulationen) == MAX_SIMULATIONEN
    assert verlauf.simulationen[-1].arbeit_id == f"a{MAX_SIMULATIONEN + 4}"


def test_bereinige() -> None:
    verlauf = _beispiel()
    verlauf.simulation(SimErgebnis(MO, "a", "en", 1, 1))
    verlauf.simulation(SimErgebnis(MO, "b", "weg", 1, 1))
    alt = MI - timedelta(days=AUFBEWAHRUNG_TAGE + 1)
    grenze = MI - timedelta(days=AUFBEWAHRUNG_TAGE)
    verlauf.frage(alt, "en")
    verlauf.frage(grenze, "en")
    assert not KindVerlauf().bereinige({"en"}, MI)

    assert verlauf.bereinige({"en"}, MI)
    assert sorted(verlauf.tage) == [grenze, MO, DI]
    # Biology is gone, and with it the only entry of that day's subject
    assert list(verlauf.tage[DI]) == ["en"]
    assert [s.arbeit_id for s in verlauf.simulationen] == ["a"]
    assert not verlauf.bereinige({"en"}, MI)

    # A day whose only subject is gone disappears
    verlauf.frage(MI, "bio")
    assert verlauf.bereinige({"en"}, MI)
    assert MI not in verlauf.tage


def test_speichern_und_laden() -> None:
    verlauf = _beispiel()
    verlauf.lernstand(MO, "en", 10, 3)
    verlauf.simulation(SimErgebnis(MO, "arbeit1", "en", 7.5, 10, vollstaendig=False))
    daten = verlauf.to_dict()
    assert list(daten["tage"]) == ["2026-10-05", "2026-10-06"]
    assert daten["seit"] == "2026-10-05"
    assert KindVerlauf.from_dict(daten).to_dict() == daten
    geladen = KindVerlauf.from_dict(daten)
    assert geladen.tage[MO]["en"] == verlauf.tage[MO]["en"]
    assert geladen.simulationen == verlauf.simulationen

    # Empty and incomplete data
    leer = KindVerlauf.from_dict({})
    assert leer.to_dict() == {"tage": {}, "simulationen": [], "seit": None}
    assert FachTag.from_dict({}) == FachTag()


@pytest.mark.parametrize(
    ("richtig", "falsch", "quote"), [(0, 0, None), (1, 0, 100), (1, 2, 33), (0, 3, 0)]
)
def test_trefferquote(richtig: int, falsch: int, quote: int | None) -> None:
    assert trefferquote(richtig, falsch) == quote


def test_wochen_und_tage() -> None:
    assert woche(MI) == (MO, date(2026, 10, 11))
    assert woche(MO) == (MO, date(2026, 10, 11))
    assert woche(date(2026, 10, 11)) == (MO, date(2026, 10, 11))
    assert woche(MI, -1) == (date(2026, 9, 28), date(2026, 10, 4))
    assert woche(MI, 1)[0] == date(2026, 10, 12)
    assert tage_von_bis(MO, MI) == [MO, DI, MI]
    assert tage_von_bis(MI, MO) == []
