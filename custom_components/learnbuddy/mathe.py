"""Local evaluation of answers to math tasks (pure logic)."""

from __future__ import annotations

from fractions import Fraction
import re
from typing import TYPE_CHECKING, Final
import unicodedata

from .models import Ergebnis
from .rechnen import BRUCHZEICHEN

if TYPE_CHECKING:
    from collections.abc import Iterable

# "x = 3" or "= 3": only the value counts
_VORSATZ: Final = re.compile(r"^(?:[a-z]\s*)?=\s*")
_GEMISCHT: Final = re.compile(r"^([+-]?)(\d+)\s+(\d+)\s*/\s*(\d+)")
_BRUCH: Final = re.compile(r"^([+-]?\d+)\s*/\s*(\d+)")
_ZAHL: Final = re.compile(r"^[+-]?(?:\d+(?:[.,]\d+)*|[.,]\d+)")
_TAUSENDER: Final = re.compile(r"^[+-]?\d{1,3}(?:\.\d{3})+$")
_MINUS: Final = str.maketrans({"−": "-", "–": "-"})
_EINHEIT: Final = re.compile(r"^[a-zäöüßµ°€$%²³/]{0,12}$")
_MIN_STELLEN_GERUNDET: Final = 2

# Spellings of units that mean the same
_EINHEITEN: Final[dict[str, str]] = {
    "meter": "m",
    "metern": "m",
    "zentimeter": "cm",
    "millimeter": "mm",
    "kilometer": "km",
    "gramm": "g",
    "kilogramm": "kg",
    "kilo": "kg",
    "liter": "l",
    "milliliter": "ml",
    "euro": "€",
    "eur": "€",
    "cent": "ct",
    "prozent": "%",
    "percent": "%",
    "stunden": "h",
    "stunde": "h",
    "std": "h",
    "minuten": "min",
    "minute": "min",
    "sekunden": "s",
    "sekunde": "s",
    "sek": "s",
    "grad": "°",
    "quadratmeter": "m²",
    "qm": "m²",
    "m2": "m²",
    "cm2": "cm²",
    "m3": "m³",
    "cm3": "cm³",
    "stück": "stk",
    "stueck": "stk",
}


def _dezimal(text: str) -> tuple[Fraction, int] | None:
    """Parse a decimal number; returns the value and its decimal places."""
    if "," in text and "." in text:
        # 1.234,5: the dot groups thousands
        text = text.replace(".", "").replace(",", ".")
    elif _TAUSENDER.match(text):
        text = text.replace(".", "")
    else:
        text = text.replace(",", ".")
    if text.count(".") > 1:
        return None
    stellen = len(text.partition(".")[2])
    try:
        return Fraction(text), stellen
    except ValueError, ZeroDivisionError:
        return None


def zerlege(text: str) -> tuple[Fraction, str, int | None] | None:
    """Split a result into value, unit and written decimal places.

    The decimal places are None if the value was not written as a decimal
    number. Returns None if the text does not start with a number.
    """
    wert = unicodedata.normalize("NFC", text).translate(_MINUS).strip().casefold()
    wert = _VORSATZ.sub("", wert).rstrip(".!").strip()
    for zeichen, bruch in BRUCHZEICHEN.items():
        if zeichen in wert:
            # 1½ is a mixed number
            wert = re.sub(rf"(?<=\d){zeichen}", f" {bruch}", wert).replace(
                zeichen, bruch
            )
    zahl: Fraction
    stellen: int | None = None
    if treffer := _GEMISCHT.match(wert):
        vorzeichen, ganze, zaehler, nenner = treffer.groups()
        if int(nenner) == 0:
            return None
        zahl = int(ganze) + Fraction(int(zaehler), int(nenner))
        if vorzeichen == "-":
            zahl = -zahl
    elif treffer := _BRUCH.match(wert):
        if int(treffer.group(2)) == 0:
            return None
        zahl = Fraction(int(treffer.group(1)), int(treffer.group(2)))
    elif treffer := _ZAHL.match(wert):
        dezimal = _dezimal(treffer.group(0))
        if dezimal is None:
            return None
        zahl, stellen = dezimal
        if stellen == 0:
            stellen = None
    else:
        return None
    einheit = "".join(wert[treffer.end() :].split()).rstrip(".")
    einheit = _EINHEITEN.get(einheit, einheit)
    if not _EINHEIT.match(einheit):
        # More than a number with a unit, for example two results
        return None
    return zahl, einheit, stellen


def _text(wert: str) -> str:
    return "".join(
        unicodedata.normalize("NFC", wert).translate(_MINUS).casefold().split()
    )


def _vergleiche(
    antwort: tuple[Fraction, str, int | None], loesung: tuple[Fraction, str, int | None]
) -> Ergebnis:
    wert, einheit, stellen = antwort
    soll, soll_einheit, _ = loesung
    gleich = wert == soll
    if (
        not gleich
        and stellen is not None
        and stellen >= _MIN_STELLEN_GERUNDET
        and soll.denominator not in (1, 2, 4, 5, 8, 10)
    ):
        # A rounded decimal for a fraction like 1/3
        gleich = round(soll, stellen) == wert
    if not gleich:
        return Ergebnis.FALSCH
    if einheit == soll_einheit or not soll_einheit:
        return Ergebnis.RICHTIG
    if not einheit:
        return Ergebnis.FAST_RICHTIG
    return Ergebnis.FALSCH


def bewerte_mathe(
    antwort: str, loesung: str, alternativen: Iterable[str] = ()
) -> Ergebnis | None:
    """Evaluate the answer to a math task locally.

    Returns None if that is not possible, for example because the solution is
    not a number. A correct value without its unit is almost correct.
    """
    if not antwort.strip():
        return Ergebnis.FALSCH
    erwartet = [loesung, *alternativen]
    if _text(antwort) in {_text(e) for e in erwartet}:
        return Ergebnis.RICHTIG
    gegeben = zerlege(antwort)
    ergebnisse: list[Ergebnis] = []
    unklar = gegeben is None
    for eintrag in erwartet:
        soll = zerlege(eintrag)
        if soll is None:
            unklar = True
        elif gegeben is not None:
            ergebnisse.append(_vergleiche(gegeben, soll))
    for ergebnis in (Ergebnis.RICHTIG, Ergebnis.FAST_RICHTIG):
        if ergebnis in ergebnisse:
            return ergebnis
    return None if unklar else Ergebnis.FALSCH
