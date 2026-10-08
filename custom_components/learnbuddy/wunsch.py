"""Recognize the wish of a child for more questions (pure logic)."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from collections.abc import Sequence

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


# ----------------------------------------------------------------------
# The wish to practise a subject or a lesson
# ----------------------------------------------------------------------

# Words that show that the child asks for something
_UEBEN: Final = _AUSLOESER | frozenset(
    {
        "üben",
        "übe",
        "ueben",
        "lernen",
        "lerne",
        "abfragen",
        "abfrage",
        "frag",
        "frage",
        "möchte",
        "moechte",
        "will",
        "würde",
        "gib",
        "trainieren",
        "teste",
        "practice",
        "practise",
        "quiz",
        "ask",
        "want",
        "give",
        "test",
    }
)
# Words that stand for the vocabulary subject of a child
_VOKABELWOERTER: Final = frozenset(
    {"vokabel", "vokabeln", "wörter", "vocabulary", "vocab", "words"}
)
# Words in front of a lesson that is only a number
_LEKTIONSWOERTER: Final = frozenset(
    {"lektion", "unit", "kapitel", "thema", "lesson", "chapter", "topic"}
)
# Articles are no amount here ("eine Runde Mathe")
_ARTIKEL: Final = frozenset({"ein", "eine", "einen", "a", "an"})
_MAX_WOERTER_UEBEN: Final = 15
_MIN_KURZFORM: Final = 3


@dataclass(frozen=True, slots=True)
class WunschFach:
    """What is needed of a subject to find it in a message."""

    id: str
    name: str
    vokabeln: bool = False
    lektionen: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class Uebungswunsch:
    """The wish to practise; without a subject it could not be assigned."""

    fach_id: str | None = None
    lektion: str | None = None
    anzahl: int | None = None

    @property
    def eindeutig(self) -> bool:
        """Return whether it is clear what the child wants to practise."""
        return self.fach_id is not None


def _woerter(wert: str) -> list[str]:
    return _KEIN_WORT.sub(" ", wert.casefold()).split()


def _passt(wort: str, name: str) -> bool:
    """Return whether a word names a subject, also as a short form."""
    if wort == name:
        return True
    return (len(wort) >= _MIN_KURZFORM and name.startswith(wort)) or (
        len(name) >= _MIN_KURZFORM and wort.startswith(name)
    )


def _finde_lektionen(
    woerter: list[str], faecher: Sequence[WunschFach]
) -> tuple[list[tuple[str, str]], set[int]]:
    """Return the longest lessons named in a message and where they stand."""
    beste = 0
    treffer: list[tuple[str, str]] = []
    stellen: set[int] = set()
    for fach in faecher:
        for lektion in fach.lektionen:
            teile = _woerter(lektion)
            if not teile or len(teile) < beste:
                continue
            for start in range(len(woerter) - len(teile) + 1):
                if woerter[start : start + len(teile)] != teile:
                    continue
                if (
                    len(teile) == 1
                    and teile[0].isdecimal()
                    and (start == 0 or woerter[start - 1] not in _LEKTIONSWOERTER)
                ):
                    # A bare number is rather an amount
                    continue
                if len(teile) > beste:
                    beste = len(teile)
                    treffer = []
                    stellen = set()
                treffer.append((fach.id, lektion))
                stellen.update(range(start, start + len(teile)))
                break
    return treffer, stellen


def erkenne_uebungswunsch(
    nachricht: str, faecher: Sequence[WunschFach]
) -> Uebungswunsch | None:
    """Return what a child asks to practise, if the message is such a wish.

    The wish needs a word that asks for something. Without a subject or a
    lesson that could be assigned, the result names no subject.
    """
    woerter = _woerter(nachricht)
    if not woerter or len(woerter) > _MAX_WOERTER_UEBEN:
        return None
    if not any(wort in _UEBEN for wort in woerter):
        return None

    lektionen, stellen = _finde_lektionen(woerter, faecher)
    rest = [wort for stelle, wort in enumerate(woerter) if stelle not in stellen]

    zahlen = [
        int(wort) if wort.isdecimal() else _ZAHLWOERTER[wort]
        for wort in rest
        if wort not in _ARTIKEL and (wort.isdecimal() or wort in _ZAHLWOERTER)
    ]
    anzahl = zahlen[0] if len(zahlen) == 1 and zahlen[0] > 0 else None

    genannt = [
        fach
        for fach in faecher
        if any(
            _passt(wort, teil)
            for teil in _woerter(fach.name)
            if teil not in _VOKABELWOERTER
            for wort in rest
            if len(wort) >= 3 and wort not in _UEBEN
        )
    ]
    if not genannt and any(wort in _VOKABELWOERTER for wort in rest):
        genannt = [fach for fach in faecher if fach.vokabeln]

    if lektionen:
        passend = [
            (fach_id, lektion)
            for fach_id, lektion in lektionen
            if not genannt or any(fach.id == fach_id for fach in genannt)
        ]
        if len(passend) == 1:
            return Uebungswunsch(passend[0][0], passend[0][1], anzahl)
        if len(genannt) != 1:
            return Uebungswunsch(anzahl=anzahl)
    if len(genannt) == 1:
        return Uebungswunsch(genannt[0].id, None, anzahl)
    return Uebungswunsch(anzahl=anzahl)


def erkenne_anzahl(nachricht: str) -> int | None:
    """Return the amount a short message names ("5", "zehn Stück")."""
    woerter = _woerter(nachricht)
    if not woerter or len(woerter) > _MAX_WOERTER:
        return None
    zahlen = [
        int(wort) if wort.isdecimal() else _ZAHLWOERTER[wort]
        for wort in woerter
        if wort not in _ARTIKEL and (wort.isdecimal() or wort in _ZAHLWOERTER)
    ]
    return zahlen[0] if len(zahlen) == 1 and zahlen[0] > 0 else None
