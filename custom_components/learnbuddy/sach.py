"""Pure logic for knowledge questions: choice options and exact answers."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING
import unicodedata

from .models import Ergebnis

if TYPE_CHECKING:
    from collections.abc import Sequence
    from random import Random

BUCHSTABEN = "ABCD"

# "b", "B)", "(b)", "b.", "Antwort b", "answer: b"
_BUCHSTABE = re.compile(
    r"^(?:antwort|answer|option|lösung|loesung)?\s*[:=]?\s*\(?([a-d])\)?[.:]?$"
)


def normalisiere(text: str) -> str:
    """Normalize an answer for comparison: case, punctuation and whitespace."""
    wert = unicodedata.normalize("NFKC", text).casefold()
    wert = "".join(
        " " if unicodedata.category(zeichen)[0] in "PS" else zeichen for zeichen in wert
    )
    return " ".join(wert.split())


def mische(antwort: str, falsche: Sequence[str], rng: Random) -> list[str]:
    """Return the options of a choice question in random order."""
    optionen = [antwort, *falsche[: len(BUCHSTABEN) - 1]]
    rng.shuffle(optionen)
    return optionen


def formatiere(optionen: Sequence[str]) -> str:
    """Return the options as lines with their letters."""
    return "\n".join(
        f"{buchstabe}) {option}"
        for buchstabe, option in zip(BUCHSTABEN, optionen, strict=False)
    )


def gewaehlt(eingabe: str, optionen: Sequence[str]) -> str | None:
    """Return the option an answer picks, by letter or by its text."""
    kurz = eingabe.strip().casefold()
    treffer = _BUCHSTABE.match(kurz)
    if treffer:
        index = BUCHSTABEN.casefold().index(treffer.group(1))
        return optionen[index] if index < len(optionen) else None
    gesucht = normalisiere(eingabe)
    if not gesucht:
        return None
    return next((o for o in optionen if normalisiere(o) == gesucht), None)


def bewerte_auswahl(eingabe: str, optionen: Sequence[str], antwort: str) -> Ergebnis:
    """Evaluate the answer to a choice question."""
    wahl = gewaehlt(eingabe, optionen)
    return Ergebnis.RICHTIG if wahl is not None and wahl == antwort else Ergebnis.FALSCH


def gleiche_antwort(eingabe: str, antwort: str) -> bool:
    """Return whether an answer repeats the model answer word for word."""
    gesucht = normalisiere(eingabe)
    return bool(gesucht) and gesucht == normalisiere(antwort)
