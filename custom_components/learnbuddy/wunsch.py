"""Recognize the wish of a child for more questions (pure logic)."""

from __future__ import annotations

import re
from typing import Final

# Thumbs up, optionally with a skin tone or a variation selector
_DAUMEN: Final = re.compile(r"^(?:\U0001F44D[\U0001F3FB-\U0001F3FF️]?\s*)+$")
_KEIN_WORT: Final = re.compile(r"[^\w\s]", re.UNICODE)

# Words that ask for more
_AUSLOESER: Final = frozenset(
    {
        "noch",
        "mehr",
        "weiter",
        "weitere",
        "nochmal",
        "more",
        "another",
        "next",
        "again",
    }
)
# Words that may accompany the wish
_FUELLWOERTER: Final = frozenset(
    {
        "bitte",
        "mal",
        "aufgabe",
        "aufgaben",
        "frage",
        "fragen",
        "vokabel",
        "vokabeln",
        "please",
        "question",
        "questions",
        "word",
        "words",
        "task",
        "tasks",
    }
)
_ZAHLWOERTER: Final[dict[str, int]] = {
    "ein": 1,
    "eine": 1,
    "einen": 1,
    "eins": 1,
    "zwei": 2,
    "drei": 3,
    "vier": 4,
    "fünf": 5,
    "sechs": 6,
    "sieben": 7,
    "acht": 8,
    "neun": 9,
    "zehn": 10,
    "elf": 11,
    "zwölf": 12,
    "fünfzehn": 15,
    "zwanzig": 20,
    "a": 1,
    "an": 1,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
    "fifteen": 15,
    "twenty": 20,
}
_MAX_WOERTER: Final = 5


def erkenne_zusatzwunsch(nachricht: str) -> int | None:
    """Return how many more questions a message asks for, if it does.

    A thumbs up or a wish without a number asks for one question.
    """
    roh = nachricht.strip()
    if _DAUMEN.match(roh):
        return 1
    woerter = _KEIN_WORT.sub(" ", roh.casefold()).split()
    if not woerter or len(woerter) > _MAX_WOERTER:
        return None
    anzahl: int | None = None
    ausloeser = False
    for wort in woerter:
        if wort in _AUSLOESER:
            ausloeser = True
        elif wort.isdecimal() or wort in _ZAHLWOERTER:
            if anzahl is not None:
                return None
            anzahl = int(wort) if wort.isdecimal() else _ZAHLWOERTER[wort]
        elif wort not in _FUELLWOERTER:
            return None
    if not ausloeser or anzahl == 0:
        return None
    return 1 if anzahl is None else anzahl


_JA: Final = frozenset(
    {
        "ja",
        "j",
        "jo",
        "jap",
        "jep",
        "klar",
        "gerne",
        "gern",
        "bitte",
        "ok",
        "okay",
        "yes",
        "yep",
        "yeah",
        "sure",
        "please",
    }
)
_NEIN: Final = frozenset(
    {"nein", "n", "nö", "noe", "nee", "ne", "danke", "no", "nope", "thanks"}
)
_MAX_WOERTER_JA: Final = 3


def _nur_aus(nachricht: str, erlaubt: frozenset[str]) -> bool:
    woerter = _KEIN_WORT.sub(" ", nachricht.casefold()).split()
    return 0 < len(woerter) <= _MAX_WOERTER_JA and all(w in erlaubt for w in woerter)


def erkenne_ja(nachricht: str) -> bool:
    """Return whether a message accepts an offer (also a thumbs up)."""
    return bool(_DAUMEN.match(nachricht.strip())) or _nur_aus(nachricht, _JA)


def erkenne_nein(nachricht: str) -> bool:
    """Return whether a message declines an offer."""
    woerter = _KEIN_WORT.sub(" ", nachricht.casefold()).split()
    return _nur_aus(nachricht, _NEIN) and woerter[0] != "danke"
