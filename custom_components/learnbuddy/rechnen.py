"""Safe evaluation of arithmetic expressions (pure logic).

Used to verify the solution of generated math tasks. Only numbers, the
basic operations, brackets and small integer powers are allowed; nothing is
ever executed.
"""

from __future__ import annotations

import ast
from fractions import Fraction
import re
from typing import Final

MAX_LAENGE: Final = 200
MAX_EXPONENT: Final = 10
# Numerator and denominator must stay below this number of digits
MAX_STELLEN: Final = 60

BRUCHZEICHEN: Final[dict[str, str]] = {
    "½": "1/2",
    "⅓": "1/3",
    "⅔": "2/3",
    "¼": "1/4",
    "¾": "3/4",
    "⅕": "1/5",
    "⅖": "2/5",
    "⅗": "3/5",
    "⅘": "4/5",
    "⅙": "1/6",
    "⅚": "5/6",
    "⅛": "1/8",
    "⅜": "3/8",
    "⅝": "5/8",
    "⅞": "7/8",
}
_ERSETZUNGEN: Final[dict[str, str]] = {
    "×": "*",
    "·": "*",
    "⋅": "*",
    "∙": "*",
    ":": "/",
    "÷": "/",
    "−": "-",
    "–": "-",
    "^": "**",
    "²": "**2",
    "³": "**3",
}
_DEZIMALKOMMA: Final = re.compile(r"(?<=\d),(?=\d)")
_PROZENT: Final = re.compile(r"(\d+(?:\.\d+)?)\s*%")
_ERLAUBT: Final = re.compile(r"^[\d\s.+\-*/()]+$")


class _UngueltigError(Exception):
    """The expression is not a plain calculation."""


def _begrenze(wert: Fraction) -> Fraction:
    if (
        len(str(abs(wert.numerator))) > MAX_STELLEN
        or len(str(wert.denominator)) > MAX_STELLEN
    ):
        raise _UngueltigError
    return wert


def _potenz(basis: Fraction, exponent: Fraction) -> Fraction:
    if exponent.denominator != 1 or abs(exponent) > MAX_EXPONENT:
        raise _UngueltigError
    if exponent < 0 and basis == 0:
        raise _UngueltigError
    return basis ** int(exponent)


def _werte_aus(knoten: ast.AST) -> Fraction:
    if isinstance(knoten, ast.Constant):
        wert = knoten.value
        if isinstance(wert, bool) or not isinstance(wert, (int, float)):
            raise _UngueltigError
        # repr keeps the decimal digits that were written
        return _begrenze(Fraction(repr(wert)))
    if isinstance(knoten, ast.UnaryOp):
        operand = _werte_aus(knoten.operand)
        if isinstance(knoten.op, ast.USub):
            return -operand
        if isinstance(knoten.op, ast.UAdd):
            return operand
        raise _UngueltigError
    if isinstance(knoten, ast.BinOp):
        links = _werte_aus(knoten.left)
        rechts = _werte_aus(knoten.right)
        if isinstance(knoten.op, ast.Add):
            return _begrenze(links + rechts)
        if isinstance(knoten.op, ast.Sub):
            return _begrenze(links - rechts)
        if isinstance(knoten.op, ast.Mult):
            return _begrenze(links * rechts)
        if isinstance(knoten.op, ast.Div):
            if rechts == 0:
                raise _UngueltigError
            return _begrenze(links / rechts)
        if isinstance(knoten.op, ast.Pow):
            return _begrenze(_potenz(links, rechts))
    raise _UngueltigError


def berechne(ausdruck: str) -> Fraction | None:
    """Return the exact value of an arithmetic expression, None if invalid."""
    text = ausdruck.strip()
    if not text or len(text) > MAX_LAENGE:
        return None
    for zeichen, bruch in BRUCHZEICHEN.items():
        text = text.replace(zeichen, f"({bruch})")
    for zeichen, ersatz in _ERSETZUNGEN.items():
        text = text.replace(zeichen, ersatz)
    text = _DEZIMALKOMMA.sub(".", text)
    text = _PROZENT.sub(r"(\1/100)", text)
    if not _ERLAUBT.match(text):
        return None
    try:
        baum = ast.parse(text.strip(), mode="eval")
        return _werte_aus(baum.body)
    except _UngueltigError, SyntaxError, ValueError, RecursionError, MemoryError:
        return None
