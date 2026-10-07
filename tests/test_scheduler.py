"""Tests for the scheduling logic."""

from __future__ import annotations

from datetime import date, datetime, time, timedelta
from random import Random
from zoneinfo import ZoneInfo

import pytest

from custom_components.learnbuddy.models import (
    Arbeit,
    Ergebnis,
    Kind,
    Statistik,
    Vokabel,
)
from custom_components.learnbuddy.scheduler import (
    abfragen_am_tag,
    antwortfrist,
    aufgaben_der_arbeit,
    faellig_ab,
    naechste_arbeit,
    naechste_box,
    naechster_zeitpunkt,
    verdichtung,
    waehle_arbeit,
    waehle_aufgabe,
    zeitpunkte,
)

BERLIN = ZoneInfo("Europe/Berlin")
# 2026-10-06 is a Tuesday
DIENSTAG = date(2026, 10, 6)
JETZT = datetime(2026, 10, 6, 12, 0, tzinfo=BERLIN)
KIND = Kind(
    id="k1",
    name="Max",
    werktag_von=time(15, 0),
    werktag_bis=time(19, 0),
    wochenende_aktiv=False,
)


def _arbeit(datum: date, **kwargs: object) -> Arbeit:
    werte: dict[str, object] = {
        "abfragen_pro_tag": 2,
        "start_tage_vorher": 7,
        "intensivierung": False,
    }
    werte.update(kwargs)
    return Arbeit(id="a1", fach_id="f1", datum=datum, **werte)  # type: ignore[arg-type]


def _zeit(tag: date, stunde: int, minute: int = 0) -> datetime:
    return datetime.combine(tag, time(stunde, minute), tzinfo=BERLIN)


@pytest.mark.parametrize(
    ("tage_bis", "erwartet"),
    [(8, 0), (7, 2), (4, 2), (1, 2), (0, 0), (-1, 0)],
)
def test_abfragen_am_tag_konstant(tage_bis: int, erwartet: int) -> None:
    arbeit = _arbeit(DIENSTAG + timedelta(days=tage_bis))
    assert abfragen_am_tag(arbeit, DIENSTAG) == erwartet


@pytest.mark.parametrize(
    ("tage_bis", "erwartet"),
    [(8, 0), (7, 3), (4, 4), (1, 6), (0, 0)],
)
def test_abfragen_am_tag_intensivierung(tage_bis: int, erwartet: int) -> None:
    arbeit = _arbeit(
        DIENSTAG + timedelta(days=tage_bis), abfragen_pro_tag=3, intensivierung=True
    )
    assert abfragen_am_tag(arbeit, DIENSTAG) == erwartet


def test_abfragen_am_tag_intensivierung_ein_tag() -> None:
    arbeit = _arbeit(
        DIENSTAG + timedelta(days=1), start_tage_vorher=1, intensivierung=True
    )
    assert abfragen_am_tag(arbeit, DIENSTAG) == 2


def test_zeitpunkte() -> None:
    assert zeitpunkte(KIND, DIENSTAG, 2, BERLIN) == [
        _zeit(DIENSTAG, 16),
        _zeit(DIENSTAG, 18),
    ]
    assert zeitpunkte(KIND, DIENSTAG, 0, BERLIN) == []
    # Saturday without weekend questions
    assert zeitpunkte(KIND, date(2026, 10, 10), 2, BERLIN) == []
    verkehrt = Kind(id="k", name="x", werktag_von=time(19), werktag_bis=time(15))
    assert zeitpunkte(verkehrt, DIENSTAG, 2, BERLIN) == []


def test_naechster_zeitpunkt_heute() -> None:
    arbeit = _arbeit(DIENSTAG + timedelta(days=3))
    assert naechster_zeitpunkt(_zeit(DIENSTAG, 8), KIND, [arbeit]) == _zeit(
        DIENSTAG, 16
    )
    assert naechster_zeitpunkt(_zeit(DIENSTAG, 16), KIND, [arbeit]) == _zeit(
        DIENSTAG, 16
    )
    assert naechster_zeitpunkt(_zeit(DIENSTAG, 16, 1), KIND, [arbeit]) == _zeit(
        DIENSTAG, 18
    )


def test_naechster_zeitpunkt_naechster_tag() -> None:
    arbeit = _arbeit(DIENSTAG + timedelta(days=3))
    morgen = DIENSTAG + timedelta(days=1)
    assert naechster_zeitpunkt(_zeit(DIENSTAG, 18, 30), KIND, [arbeit]) == _zeit(
        morgen, 16
    )


def test_naechster_zeitpunkt_mindestabstand() -> None:
    arbeit = _arbeit(DIENSTAG + timedelta(days=3), abfragen_pro_tag=24)
    # 24 questions in 4 hours: one every 10 minutes starting at 15:05
    ergebnis = naechster_zeitpunkt(
        _zeit(DIENSTAG, 15, 6), KIND, [arbeit], letzte_frage=_zeit(DIENSTAG, 15, 5)
    )
    assert ergebnis == _zeit(DIENSTAG, 15, 15)


def test_naechster_zeitpunkt_fruehestens() -> None:
    arbeit = _arbeit(DIENSTAG + timedelta(days=5))
    uebermorgen = DIENSTAG + timedelta(days=2)
    ergebnis = naechster_zeitpunkt(
        _zeit(DIENSTAG, 8), KIND, [arbeit], fruehestens=_zeit(uebermorgen, 17)
    )
    assert ergebnis == _zeit(uebermorgen, 18)


def test_naechster_zeitpunkt_wochenende_und_fenster() -> None:
    # Exam on Monday: Friday is the last weekday before, weekend is off
    montag = date(2026, 10, 12)
    freitag = date(2026, 10, 9)
    arbeit = _arbeit(montag)
    assert naechster_zeitpunkt(_zeit(freitag, 18, 30), KIND, [arbeit]) is None
    mit_wochenende = Kind(id="k", name="x")
    assert naechster_zeitpunkt(
        _zeit(freitag, 18, 30), mit_wochenende, [arbeit]
    ) == _zeit(date(2026, 10, 10), 12)


def test_naechster_zeitpunkt_ohne_ergebnis() -> None:
    assert naechster_zeitpunkt(_zeit(DIENSTAG, 8), KIND, []) is None
    vorbei = _arbeit(DIENSTAG - timedelta(days=1))
    assert naechster_zeitpunkt(_zeit(DIENSTAG, 8), KIND, [vorbei]) is None
    heute = _arbeit(DIENSTAG)
    assert naechster_zeitpunkt(_zeit(DIENSTAG, 8), KIND, [heute]) is None


def test_naechster_zeitpunkt_spaeter_start() -> None:
    # Exam in 30 days: questions start 7 days before
    arbeit = _arbeit(DIENSTAG + timedelta(days=30))
    assert naechster_zeitpunkt(_zeit(DIENSTAG, 8), KIND, [arbeit]) == _zeit(
        DIENSTAG + timedelta(days=23), 16
    )


def test_naechster_zeitpunkt_mehrere_arbeiten() -> None:
    eins = _arbeit(DIENSTAG + timedelta(days=3))
    zwei = _arbeit(DIENSTAG + timedelta(days=2))
    # 4 questions per day: 15:30, 16:30, 17:30, 18:30
    assert naechster_zeitpunkt(_zeit(DIENSTAG, 8), KIND, [eins, zwei]) == _zeit(
        DIENSTAG, 15, 30
    )


def test_naechster_zeitpunkt_braucht_zeitzone() -> None:
    arbeit = _arbeit(DIENSTAG + timedelta(days=3))
    with pytest.raises(ValueError, match="timezone"):
        naechster_zeitpunkt(datetime(2026, 10, 6, 8), KIND, [arbeit])  # noqa: DTZ001


def test_waehle_arbeit() -> None:
    aktiv = _arbeit(DIENSTAG + timedelta(days=2))
    fern = Arbeit(id="a2", fach_id="f1", datum=DIENSTAG + timedelta(days=60))
    rng = Random(1)
    assert waehle_arbeit([aktiv, fern], DIENSTAG, rng) is aktiv
    assert waehle_arbeit([fern], DIENSTAG, rng) is None
    assert waehle_arbeit([], DIENSTAG, rng) is None


def test_naechste_arbeit() -> None:
    alt = _arbeit(DIENSTAG - timedelta(days=1))
    bald = _arbeit(DIENSTAG + timedelta(days=2))
    spaeter = _arbeit(DIENSTAG + timedelta(days=9))
    heute = _arbeit(DIENSTAG)
    assert naechste_arbeit([alt, spaeter, bald], DIENSTAG) is bald
    assert naechste_arbeit([alt, heute, bald], DIENSTAG) is heute
    assert naechste_arbeit([alt], DIENSTAG) is None


def _vokabel(de: str, en: str, **kwargs: object) -> Vokabel:
    return Vokabel(fach_id="f1", frage={"de": de, "en": en}, **kwargs)  # type: ignore[arg-type]


def test_aufgaben_der_arbeit() -> None:
    unit1 = _vokabel("Hund", "dog", lektion="Unit 1")
    unit3 = _vokabel("Katze", "cat", lektion="Unit 3")
    ohne = _vokabel("Maus", "mouse")
    alle = [unit1, unit3, ohne]
    arbeit = _arbeit(DIENSTAG, lektionen=("Unit 3",))
    assert aufgaben_der_arbeit(arbeit, alle) == [unit3]
    assert aufgaben_der_arbeit(arbeit, alle, {ohne.id}) == [unit3, ohne]
    # Without any selection all tasks of the subject count
    assert aufgaben_der_arbeit(_arbeit(DIENSTAG), alle) == alle
    # An explicit selection alone limits the exam to these tasks
    assert aufgaben_der_arbeit(_arbeit(DIENSTAG), alle, {unit1.id}) == [unit1]


@pytest.mark.parametrize(
    ("box", "ergebnis", "erwartet"),
    [
        (1, Ergebnis.RICHTIG, 2),
        (4, Ergebnis.FAST_RICHTIG, 5),
        (5, Ergebnis.RICHTIG, 5),
        (4, Ergebnis.FALSCH, 1),
        (3, Ergebnis.UNBEANTWORTET, 3),
        (3, Ergebnis.TEILWEISE, 3),
        (0, Ergebnis.RICHTIG, 2),
        (9, Ergebnis.UNBEANTWORTET, 5),
    ],
)
def test_naechste_box(box: int, ergebnis: Ergebnis, erwartet: int) -> None:
    assert naechste_box(box, ergebnis) == erwartet


@pytest.mark.parametrize(
    ("tage_bis", "erwartet"),
    [(30, 1.0), (8, 1.0), (7, 6 / 7), (2, 1 / 7), (1, 0.0), (0, 0.0), (-3, 0.0)],
)
def test_verdichtung(tage_bis: int, erwartet: float) -> None:
    arbeit = _arbeit(DIENSTAG + timedelta(days=tage_bis))
    assert verdichtung(arbeit, DIENSTAG) == pytest.approx(erwartet)
    assert verdichtung(None, DIENSTAG) == 1.0


def test_faellig_ab() -> None:
    assert faellig_ab(Statistik()) is None
    assert faellig_ab(Statistik(box=1, zuletzt_gefragt=JETZT)) == JETZT
    assert faellig_ab(Statistik(box=3, zuletzt_gefragt=JETZT)) == JETZT + timedelta(
        days=2
    )
    assert faellig_ab(Statistik(box=5, zuletzt_gefragt=JETZT), 0.5) == (
        JETZT + timedelta(days=3.5)
    )
    assert faellig_ab(Statistik(box=5, zuletzt_gefragt=JETZT), 0.0) == JETZT
    # Out of range boxes are clamped
    assert faellig_ab(Statistik(box=9, zuletzt_gefragt=JETZT)) == JETZT + timedelta(
        days=7
    )


def _gefragt(aufgabe: Vokabel, box: int, vor: timedelta, key: str = "de>en") -> None:
    stat = aufgabe.statistik_fuer(key)
    stat.box = box
    stat.zuletzt_gefragt = JETZT - vor


def test_waehle_aufgabe_neue_zuerst() -> None:
    alt = _vokabel("Hund", "dog")
    for richtung_key in ("de>en", "en>de"):
        _gefragt(alt, 1, timedelta(days=3), richtung_key)
    neu = _vokabel("Katze", "cat")
    for seed in range(5):
        auswahl = waehle_aufgabe(
            [alt, neu], ["de>en", "en>de"], Random(seed), jetzt=JETZT
        )
        assert auswahl is not None
        assert auswahl[0] is neu


def test_waehle_aufgabe_faellige_nach_box() -> None:
    box1 = _vokabel("Hund", "dog")
    _gefragt(box1, 1, timedelta(minutes=5))
    box3_faellig = _vokabel("Katze", "cat")
    _gefragt(box3_faellig, 3, timedelta(days=3))
    box2_nicht_faellig = _vokabel("Maus", "mouse")
    _gefragt(box2_nicht_faellig, 2, timedelta(hours=1))
    alle = [box2_nicht_faellig, box3_faellig, box1]
    # Lowest due box first
    assert waehle_aufgabe(alle, ["de>en"], Random(0), jetzt=JETZT) == (box1, "de>en")
    # A due task in a higher box beats a task in a lower box that is not due
    assert waehle_aufgabe(
        [box2_nicht_faellig, box3_faellig], ["de>en"], Random(0), jetzt=JETZT
    ) == (box3_faellig, "de>en")


def test_waehle_aufgabe_nichts_faellig() -> None:
    box2 = _vokabel("Hund", "dog")
    _gefragt(box2, 2, timedelta(hours=1))
    box4 = _vokabel("Katze", "cat")
    _gefragt(box4, 4, timedelta(days=1))
    box2_aelter = _vokabel("Maus", "mouse")
    _gefragt(box2_aelter, 2, timedelta(hours=5))
    assert waehle_aufgabe(
        [box2, box4, box2_aelter], ["de>en"], Random(0), jetzt=JETZT
    ) == (box2_aelter, "de>en")


def test_waehle_aufgabe_verdichtung() -> None:
    box5 = _vokabel("Hund", "dog")
    _gefragt(box5, 5, timedelta(days=2))
    box2 = _vokabel("Katze", "cat")
    _gefragt(box2, 2, timedelta(hours=2))
    # Normally neither is due and the lower box wins
    assert waehle_aufgabe([box5, box2], ["de>en"], Random(0), jetzt=JETZT) == (
        box2,
        "de>en",
    )
    # Right before the exam the intervals shrink: only box 5 (2 days old) is due
    assert waehle_aufgabe(
        [box5, box2], ["de>en"], Random(0), jetzt=JETZT, faktor=0.2
    ) == (box5, "de>en")


def test_waehle_aufgabe_vermeidet_wiederholung() -> None:
    eins = _vokabel("Hund", "dog")
    zwei = _vokabel("Katze", "cat")
    _gefragt(zwei, 4, timedelta(minutes=1))
    assert waehle_aufgabe(
        [eins, zwei], ["de>en"], Random(0), jetzt=JETZT, vermeide=eins.id
    ) == (zwei, "de>en")
    # The only task is asked again
    assert waehle_aufgabe(
        [eins], ["de>en"], Random(0), jetzt=JETZT, vermeide=eins.id
    ) == (eins, "de>en")


def test_waehle_aufgabe_filter() -> None:
    ungeprueft = _vokabel("Hund", "dog", geprueft=False)
    unvollstaendig = _vokabel("Katze", "")
    assert (
        waehle_aufgabe([ungeprueft, unvollstaendig], ["de>en"], Random(0), jetzt=JETZT)
        is None
    )
    assert waehle_aufgabe([], ["de>en"], Random(0), jetzt=JETZT) is None
    assert waehle_aufgabe([_vokabel("a", "b")], [], Random(0), jetzt=JETZT) is None


def test_antwortfrist() -> None:
    ohne = _arbeit(DIENSTAG)
    kurz = _arbeit(DIENSTAG, antwortfrist_minuten=10)
    lang = _arbeit(DIENSTAG, antwortfrist_minuten=120)
    assert antwortfrist([], 60) == 60
    assert antwortfrist([ohne], 60) == 60
    assert antwortfrist([ohne, lang], 60) == 120
    assert antwortfrist([lang, kurz, ohne], 60) == 10
