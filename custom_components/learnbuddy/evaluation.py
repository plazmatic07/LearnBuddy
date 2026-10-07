"""Local evaluation of answers (pure logic, no Home Assistant dependency)."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING
import unicodedata

from .models import Ergebnis

if TYPE_CHECKING:
    from collections.abc import Iterable

ARTIKEL: dict[str, frozenset[str]] = {
    "de": frozenset(
        {"der", "die", "das", "ein", "eine", "einen", "einem", "einer", "eines"}
    ),
    "en": frozenset({"the", "a", "an"}),
    "fr": frozenset({"le", "la", "les", "un", "une", "des"}),
    "es": frozenset({"el", "la", "los", "las", "un", "una", "unos", "unas"}),
    "it": frozenset({"il", "lo", "la", "i", "gli", "le", "un", "uno", "una"}),
}
# Words in front of a verb that do not belong to the vocabulary itself
VERB_MARKER: dict[str, frozenset[str]] = {"en": frozenset({"to"})}
ELISIONEN: dict[str, tuple[str, ...]] = {"fr": ("l'", "d'"), "it": ("l'", "un'")}

# A typo is only tolerated for words of at least this length
MIN_LAENGE_TIPPFEHLER = 4

_APOSTROPHE = str.maketrans({"’": "'", "‘": "'", "`": "'", "´": "'"})
_TRENNER = re.compile(r"[/;,]")
_KLAMMER = re.compile(r"\(([^)]*)\)")
_UMLAUTE = str.maketrans({"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss"})


def normalisiere(text: str, sprache: str) -> str:
    """Normalize a word or phrase for comparison.

    Ignores case, punctuation, superfluous whitespace, a leading article and
    the English infinitive marker "to".
    """
    wert = unicodedata.normalize("NFKC", text).translate(_APOSTROPHE).casefold()
    wert = wert.strip()
    for elision in ELISIONEN.get(sprache, ()):
        if wert.startswith(elision) and len(wert) > len(elision):
            wert = wert[len(elision) :]
            break
    wert = wert.replace("'", "")
    wert = "".join(
        " " if unicodedata.category(zeichen)[0] in "PS" else zeichen for zeichen in wert
    )
    woerter = wert.split()
    vorsilben = ARTIKEL.get(sprache, frozenset()) | VERB_MARKER.get(
        sprache, frozenset()
    )
    if len(woerter) > 1 and woerter[0] in vorsilben:
        woerter = woerter[1:]
    return " ".join(woerter)


def varianten(text: str, sprache: str) -> set[str]:
    """Return all normalized forms that count as a correct answer."""
    roh = {text}
    if _KLAMMER.search(text):
        roh = {_KLAMMER.sub(" ", text), _KLAMMER.sub(r" \1 ", text)}
    ergebnis: set[str] = set()
    for eintrag in roh:
        ergebnis.add(normalisiere(eintrag, sprache))
        ergebnis.update(normalisiere(teil, sprache) for teil in _TRENNER.split(eintrag))
    ergebnis.discard("")
    return ergebnis


def editierdistanz(a: str, b: str) -> int:
    """Return the optimal string alignment distance (with transpositions)."""
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    vorletzte: list[int] = []
    letzte = list(range(len(b) + 1))
    for i, zeichen_a in enumerate(a, start=1):
        aktuelle = [i]
        for j, zeichen_b in enumerate(b, start=1):
            kosten = 0 if zeichen_a == zeichen_b else 1
            wert = min(
                letzte[j] + 1,
                aktuelle[j - 1] + 1,
                letzte[j - 1] + kosten,
            )
            if i > 1 and j > 1 and zeichen_a == b[j - 2] and a[i - 2] == zeichen_b:
                wert = min(wert, vorletzte[j - 2] + 1)
            aktuelle.append(wert)
        vorletzte, letzte = letzte, aktuelle
    return letzte[-1]


def _ohne_diakritika(text: str) -> str:
    """Remove all diacritics."""
    return "".join(
        zeichen
        for zeichen in unicodedata.normalize("NFD", text)
        if not unicodedata.combining(zeichen)
    )


def _fast_gleich(antwort: str, loesung: str) -> bool:
    """Return whether an answer is a tolerable misspelling of the solution."""
    if antwort.translate(_UMLAUTE) == loesung.translate(_UMLAUTE):
        return True
    antwort_glatt = _ohne_diakritika(antwort.replace("ß", "ss"))
    loesung_glatt = _ohne_diakritika(loesung.replace("ß", "ss"))
    if antwort_glatt == loesung_glatt:
        return True
    return (
        len(loesung_glatt) >= MIN_LAENGE_TIPPFEHLER
        and editierdistanz(antwort_glatt, loesung_glatt) <= 1
    )


def bewerte_vokabel(
    antwort: str, erwartet: str, alternativen: Iterable[str], sprache: str
) -> Ergebnis:
    """Evaluate a vocabulary answer locally."""
    loesungen = varianten(erwartet, sprache)
    for alternative in alternativen:
        loesungen |= varianten(alternative, sprache)

    gesamt = normalisiere(antwort, sprache)
    if not gesamt:
        return Ergebnis.FALSCH
    if gesamt in loesungen:
        return Ergebnis.RICHTIG

    teile = [
        teil
        for teil in (normalisiere(t, sprache) for t in _TRENNER.split(antwort))
        if teil
    ]
    if len(teile) > 1 and all(teil in loesungen for teil in teile):
        return Ergebnis.RICHTIG

    if any(_fast_gleich(gesamt, loesung) for loesung in loesungen):
        return Ergebnis.FAST_RICHTIG
    return Ergebnis.FALSCH
