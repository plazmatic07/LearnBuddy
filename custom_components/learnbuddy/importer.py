"""Parsing of task lists (pure logic, no Home Assistant dependency)."""

from __future__ import annotations

from dataclasses import dataclass, field

TRENNZEICHEN = (";", "\t", "=", " - ", " – ", ",")
# Math tasks contain "=", "-" and "," themselves
MATHE_TRENNZEICHEN = (";", "\t")
ALTERNATIV_TRENNER = "|"
KOMMENTAR = "#"


@dataclass(slots=True)
class ImportZeile:
    """One parsed vocabulary pair."""

    ausgang: str
    ziel: str
    ausgang_alternativen: list[str] = field(default_factory=list)
    ziel_alternativen: list[str] = field(default_factory=list)
    hinweis: str | None = None


@dataclass(slots=True)
class ImportErgebnis:
    """Result of parsing a vocabulary list."""

    zeilen: list[ImportZeile] = field(default_factory=list)
    fehlerzeilen: list[int] = field(default_factory=list)


def _teile(
    zeile: str, trennzeichen: str | None, kandidaten: tuple[str, ...] = TRENNZEICHEN
) -> list[str]:
    """Split a line into its columns."""
    if trennzeichen:
        return zeile.split(trennzeichen)
    for kandidat in kandidaten:
        if kandidat in zeile:
            return zeile.split(kandidat)
    return [zeile]


def _wort(spalte: str) -> tuple[str, list[str]]:
    """Split a column into the main word and its alternatives."""
    werte = [w.strip() for w in spalte.split(ALTERNATIV_TRENNER)]
    werte = [w for w in werte if w]
    if not werte:
        return "", []
    return werte[0], werte[1:]


def parse_vokabeln(inhalt: str, trennzeichen: str | None = None) -> ImportErgebnis:
    """Parse a vocabulary list with one pair per line.

    Format: ``source; target[; hint]``. Alternatives are separated by ``|``.
    Empty lines and lines starting with ``#`` are ignored.
    """
    ergebnis = ImportErgebnis()
    for nummer, roh in enumerate(inhalt.splitlines(), start=1):
        zeile = roh.strip()
        if not zeile or zeile.startswith(KOMMENTAR):
            continue
        spalten = [s.strip() for s in _teile(zeile, trennzeichen)]
        if len(spalten) < 2:
            ergebnis.fehlerzeilen.append(nummer)
            continue
        ausgang, ausgang_alt = _wort(spalten[0])
        ziel, ziel_alt = _wort(spalten[1])
        if not ausgang or not ziel:
            ergebnis.fehlerzeilen.append(nummer)
            continue
        hinweis = " ".join(s for s in spalten[2:] if s) or None
        ergebnis.zeilen.append(
            ImportZeile(
                ausgang=ausgang,
                ziel=ziel,
                ausgang_alternativen=ausgang_alt,
                ziel_alternativen=ziel_alt,
                hinweis=hinweis,
            )
        )
    return ergebnis


def parse_mathe(inhalt: str, trennzeichen: str | None = None) -> ImportErgebnis:
    """Parse a list of math tasks with one task per line.

    Format: ``task; result[; hint]``. Other accepted spellings of the result
    are separated by ``|``. The task is the source, the result the target of
    a parsed line.
    """
    ergebnis = ImportErgebnis()
    for nummer, roh in enumerate(inhalt.splitlines(), start=1):
        zeile = roh.strip()
        if not zeile or zeile.startswith(KOMMENTAR):
            continue
        spalten = [s.strip() for s in _teile(zeile, trennzeichen, MATHE_TRENNZEICHEN)]
        if len(spalten) < 2:
            ergebnis.fehlerzeilen.append(nummer)
            continue
        loesung, weitere = _wort(spalten[1])
        if not spalten[0] or not loesung:
            ergebnis.fehlerzeilen.append(nummer)
            continue
        ergebnis.zeilen.append(
            ImportZeile(
                ausgang=spalten[0],
                ziel=loesung,
                ziel_alternativen=weitere,
                hinweis=" ".join(s for s in spalten[2:] if s) or None,
            )
        )
    return ergebnis
