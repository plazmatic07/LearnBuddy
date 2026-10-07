"""Tests for exam dates read from a calendar."""

from __future__ import annotations

from datetime import UTC, date, datetime
from typing import Any
from zoneinfo import ZoneInfo

import pytest

from custom_components.learnbuddy.kalender import (
    Termin,
    erkenne_art,
    lies_termin,
    lies_termine,
    passendes_fach,
)

BERLIN = ZoneInfo("Europe/Berlin")


@pytest.mark.parametrize(
    ("texte", "art"),
    [
        (("E", "KA E"), "arbeit"),
        (("Klassenarbeit Mathe",), "arbeit"),
        (("M", "HÜ M"), "hue"),
        (("Vokabeltest", "Test Unit 3"), "hue"),
        (("hue englisch",), "hue"),
        # Both named: the exam wins
        (("KA", "Test"), "arbeit"),
        # Nothing recognisable, and "kaputt" is not "KA"
        (("Bio", "kaputt"), "arbeit"),
        (("", ""), "arbeit"),
    ],
)
def test_erkenne_art(texte: tuple[str, ...], art: str) -> None:
    assert erkenne_art(*texte) == art


def test_lies_termin_mit_uhrzeit() -> None:
    termin = lies_termin(
        {
            "start": "2026-11-03T08:50:00+01:00",
            "end": "2026-11-03T09:35:00+01:00",
            "summary": "E",
            "description": "KA E",
            "uid": "abc",
        },
        BERLIN,
    )
    assert termin == Termin(
        uid="abc", datum=date(2026, 11, 3), art="arbeit", text="KA E", kuerzel="E"
    )
    assert termin.to_dict() == {
        "uid": "abc",
        "datum": "2026-11-03",
        "art": "arbeit",
        "text": "KA E",
    }


@pytest.mark.parametrize(
    ("start", "tag"),
    [
        ("2026-11-03", date(2026, 11, 3)),
        # Late in UTC is already the next day in Berlin
        ("2026-11-03T23:30:00+00:00", date(2026, 11, 4)),
        ("2026-11-03 08:00:00", date(2026, 11, 3)),
        (date(2026, 11, 3), date(2026, 11, 3)),
        (datetime(2026, 11, 3, 23, 30, tzinfo=UTC), date(2026, 11, 4)),
        (datetime(2026, 11, 3, 8, 0), date(2026, 11, 3)),  # noqa: DTZ001
    ],
)
def test_datum(start: Any, tag: date) -> None:
    termin = lies_termin({"start": start, "summary": "HÜ M"}, BERLIN)
    assert termin is not None
    assert termin.datum == tag
    # Without an ID the day and the text identify the event
    assert termin.uid == f"{tag.isoformat()}|HÜ M"
    assert termin.text == "HÜ M"
    assert termin.art == "hue"


@pytest.mark.parametrize(
    "roh",
    [
        {"summary": "E"},
        {"start": None, "summary": "E"},
        {"start": "morgen", "summary": "E"},
        {"start": "2026-13-40T99:00:00", "summary": "E"},
        {"start": 5, "summary": "E"},
        {"start": "2026-11-03"},
        {"start": "2026-11-03", "summary": "  ", "description": None},
    ],
)
def test_unbrauchbar(roh: dict[str, Any]) -> None:
    assert lies_termin(roh, BERLIN) is None


def test_lies_termine() -> None:
    rohe = [
        {"start": "2026-11-10", "summary": "M", "description": "HÜ M", "uid": "2"},
        {"start": "2026-10-01", "summary": "D", "description": "KA D", "uid": "0"},
        {"start": "2026-11-03", "summary": "E", "description": "KA E", "uid": "1"},
        # Delivered twice
        {"start": "2026-11-03", "summary": "E", "description": "KA E", "uid": "1"},
        {"start": "kaputt", "summary": "X"},
        # Today still counts
        {"start": "2026-10-07", "summary": "F", "description": "Test F", "uid": "3"},
    ]
    termine = lies_termine(rohe, BERLIN, date(2026, 10, 7))
    assert [t.uid for t in termine] == ["3", "1", "2"]


@pytest.mark.parametrize(
    ("kuerzel", "text", "fach"),
    [
        ("E", "KA E", "en"),
        ("e", "ka e", "en"),
        ("Bio", "KA Bio", "bio"),
        # Two subjects start with M
        ("M", "KA M", None),
        ("Ma", "KA Ma", "ma"),
        # No such subject
        ("D", "KA D", None),
        # The title is no abbreviation, the last word of the text is
        ("Prüfung: E", "KA E", "en"),
        ("", "", None),
        ("Klassenarbeit", "Klassenarbeit", None),
    ],
)
def test_passendes_fach(kuerzel: str, text: str, fach: str | None) -> None:
    faecher = {"en": "Englisch", "ma": "Mathe", "mu": " Musik", "bio": "Biologie"}
    termin = Termin(
        uid="x", datum=date(2026, 11, 3), art="arbeit", text=text, kuerzel=kuerzel
    )
    assert passendes_fach(termin, faecher) == fach
