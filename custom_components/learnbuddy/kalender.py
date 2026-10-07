"""Exam dates read from a calendar: pure logic without Home Assistant.

The events come from the action ``calendar.get_events`` of whatever calendar
integration the user has. They only serve as suggestions in the panel.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
import re
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping
    from datetime import tzinfo

ART_ARBEIT = "arbeit"
ART_HUE = "hue"

_WORT = re.compile(r"[^\W\d_]+", re.UNICODE)
_ARBEIT_WOERTER = frozenset(
    {"ka", "klassenarbeit", "arbeit", "klausur", "schulaufgabe", "exam"}
)
_HUE_WOERTER = frozenset(
    {
        "hü",
        "hue",
        "test",
        "kurztest",
        "überprüfung",
        "ueberpruefung",
        "hausaufgabenüberprüfung",
        "lernkontrolle",
        "quiz",
    }
)
# A subject abbreviation is short; longer titles are no abbreviation
_MAX_KUERZEL = 5


@dataclass(slots=True, frozen=True)
class Termin:
    """An exam date found in a calendar."""

    uid: str
    datum: date
    art: str
    # What the calendar says about it, used as the topic
    text: str
    # Title of the event, at school usually the abbreviation of the subject
    kuerzel: str

    def to_dict(self) -> dict[str, Any]:
        """Return the date for the panel."""
        return {
            "uid": self.uid,
            "datum": self.datum.isoformat(),
            "art": self.art,
            "text": self.text,
        }


def erkenne_art(*texte: str) -> str:
    """Tell an exam from a short test by the words of an event."""
    woerter = {
        wort.casefold() for inhalt in texte for wort in _WORT.findall(inhalt or "")
    }
    if woerter & _ARBEIT_WOERTER:
        return ART_ARBEIT
    if woerter & _HUE_WOERTER:
        return ART_HUE
    return ART_ARBEIT


def _datum(wert: Any, zone: tzinfo) -> date | None:
    """Return the local day of a start value: a date or a date with time."""
    if isinstance(wert, datetime):
        return wert.astimezone(zone).date() if wert.tzinfo else wert.date()
    if isinstance(wert, date):
        return wert
    if not isinstance(wert, str) or not wert:
        return None
    try:
        if "T" not in wert and " " not in wert:
            return date.fromisoformat(wert)
        zeitpunkt = datetime.fromisoformat(wert)
    except ValueError:
        return None
    return zeitpunkt.astimezone(zone).date() if zeitpunkt.tzinfo else zeitpunkt.date()


def lies_termin(roh: Mapping[str, Any], zone: tzinfo) -> Termin | None:
    """Turn one calendar event into an exam date, None if it is unusable."""
    datum = _datum(roh.get("start"), zone)
    if datum is None:
        return None
    titel = str(roh.get("summary") or "").strip()
    beschreibung = str(roh.get("description") or "").strip()
    text = beschreibung or titel
    if not text:
        return None
    # Not every calendar gives its events an ID
    uid = str(roh.get("uid") or "").strip() or f"{datum.isoformat()}|{text}"
    return Termin(
        uid=uid,
        datum=datum,
        art=erkenne_art(titel, beschreibung),
        text=text,
        kuerzel=titel,
    )


def lies_termine(
    rohe: Iterable[Mapping[str, Any]], zone: tzinfo, heute: date
) -> list[Termin]:
    """Return the upcoming exam dates of a calendar, earliest first."""
    termine: dict[str, Termin] = {}
    for roh in rohe:
        termin = lies_termin(roh, zone)
        if termin is not None and termin.datum >= heute:
            termine.setdefault(termin.uid, termin)
    return sorted(termine.values(), key=lambda t: (t.datum, t.text))


def passendes_fach(termin: Termin, fachnamen: Mapping[str, str]) -> str | None:
    """Guess the subject of a date, only if exactly one subject fits.

    School calendars name the subject by an abbreviation such as "E". It fits
    a subject whose name starts with it.
    """
    kandidaten = [termin.kuerzel]
    woerter = termin.text.split()
    if woerter:
        kandidaten.append(woerter[-1])
    for kuerzel in kandidaten:
        kurz = kuerzel.strip().casefold()
        if not kurz or len(kurz) > _MAX_KUERZEL:
            continue
        treffer = [
            fach_id
            for fach_id, name in fachnamen.items()
            if name.strip().casefold().startswith(kurz)
        ]
        if len(treffer) == 1:
            return treffer[0]
    return None
