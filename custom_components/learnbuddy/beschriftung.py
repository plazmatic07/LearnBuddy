"""Labelling tasks: hide the labels of an image behind numbers.

Pure Pillow logic. A field is the box of one label as fractions of the image
({"nr", "x", "y", "b", "h"}), so that it does not depend on the size of the
stored image.
"""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
import statistics
from typing import TYPE_CHECKING, Any, Final, cast

from PIL import Image, ImageDraw, ImageFont

if TYPE_CHECKING:
    from collections.abc import Sequence

MAX_FELDER: Final = 30
# Smallest box (fraction of the image edge) that is still worth a number
MIN_KANTE: Final = 0.01
_SCHRIFTEN = Path(__file__).parent / "fonts"
_RAND = 5
_TINTE = (20, 20, 20)
_MIN_SCHRIFT = 14
# Largest number as a fraction of the shorter edge of the image
_MAX_SCHRIFT = 0.05


def pruefe_feld(roh: Any) -> dict[str, float] | None:
    """Return a cleaned field or None if it is not a usable box."""
    if not isinstance(roh, dict):
        return None
    try:
        nr = int(roh["nr"])
        x, y, b, h = (float(roh[k]) for k in ("x", "y", "b", "h"))
    except KeyError, TypeError, ValueError:
        return None
    x, y = min(max(x, 0.0), 1.0), min(max(y, 0.0), 1.0)
    b, h = min(b, 1.0 - x), min(h, 1.0 - y)
    if nr < 1 or b < MIN_KANTE or h < MIN_KANTE:
        return None
    return {"nr": nr, "x": x, "y": y, "b": b, "h": h}


def _schrift(groesse: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(_SCHRIFTEN / "DejaVuSans-Bold.ttf"), groesse)


def _hintergrund(bild: Image.Image, box: tuple[int, int, int, int]) -> tuple[int, ...]:
    """Return the colour around a box, so that the cover blends in."""
    links, oben, rechts, unten = box
    breite, hoehe = bild.size
    punkte: list[tuple[int, int]] = []
    for x in range(max(links, 0), min(rechts, breite), 3):
        punkte += [(x, max(oben - 2, 0)), (x, min(unten + 1, hoehe - 1))]
    for y in range(max(oben, 0), min(unten, hoehe), 3):
        punkte += [(max(links - 2, 0), y), (min(rechts + 1, breite - 1), y)]
    if not punkte:
        return (255, 255, 255)
    farben = [cast("tuple[int, ...]", bild.getpixel(p)) for p in punkte]
    return tuple(int(statistics.median(f[k] for f in farben)) for k in range(3))


def zeichne(daten: bytes, felder: Sequence[dict[str, float]]) -> bytes:
    """Return the image (PNG) with every field covered by its number."""
    with Image.open(BytesIO(daten)) as roh:
        bild = roh.convert("RGB")
    breite, hoehe = bild.size
    # Measure every cover on the untouched image so that covers do not tint
    # each other
    boxen = []
    for feld in felder:
        links = round(feld["x"] * breite) - _RAND
        oben = round(feld["y"] * hoehe) - _RAND
        rechts = round((feld["x"] + feld["b"]) * breite) + _RAND
        unten = round((feld["y"] + feld["h"]) * hoehe) + _RAND
        box = (links, oben, rechts, unten)
        boxen.append((feld, box, _hintergrund(bild, box)))
    maler = ImageDraw.Draw(bild)
    for feld, (links, oben, rechts, unten), farbe in boxen:
        nummer = str(int(feld["nr"]))
        # Tall boxes must not give some numbers a larger size than others
        groesse = max(
            min(int((unten - oben) * 0.7), int(min(breite, hoehe) * _MAX_SCHRIFT)),
            _MIN_SCHRIFT,
        )
        schrift = _schrift(groesse)
        text_box = maler.textbbox((0, 0), nummer, font=schrift)
        text_b, text_h = text_box[2] - text_box[0], text_box[3] - text_box[1]
        # A small box grows around its number
        mitte_x, mitte_y = (links + rechts) / 2, (oben + unten) / 2
        halb_b = max((rechts - links) / 2, text_b / 2 + 8)
        halb_h = max((unten - oben) / 2, text_h / 2 + 6)
        flaeche = (
            mitte_x - halb_b,
            mitte_y - halb_h,
            mitte_x + halb_b,
            mitte_y + halb_h,
        )
        maler.rectangle(flaeche, fill=farbe, outline=_TINTE, width=2)
        maler.text(
            (mitte_x - text_b / 2 - text_box[0], mitte_y - text_h / 2 - text_box[1]),
            nummer,
            font=schrift,
            fill=_TINTE,
        )
    ausgabe = BytesIO()
    bild.save(ausgabe, "PNG", optimize=True)
    return ausgabe.getvalue()


def gitter(daten: bytes) -> bytes:
    """Return the image (PNG) with a numbered grid for the AI.

    Models place boxes much better when they can read the position off lines
    labelled 0 to 1000 than when they have to estimate it.
    """
    with Image.open(BytesIO(daten)) as roh:
        bild = roh.convert("RGBA")
    breite, hoehe = bild.size
    ebene = Image.new("RGBA", bild.size, (0, 0, 0, 0))
    maler = ImageDraw.Draw(ebene)
    schrift = _schrift(max(10, min(breite, hoehe) // 45))
    farbe = (220, 0, 160)
    for wert in range(0, 1001, 100):
        x = min(round(wert / 1000 * breite), breite - 1)
        y = min(round(wert / 1000 * hoehe), hoehe - 1)
        maler.line([(x, 0), (x, hoehe)], fill=(*farbe, 110), width=1)
        maler.line([(0, y), (breite, y)], fill=(*farbe, 110), width=1)
        # The number sits at the lines of both edges and in the middle, so
        # that it can be read wherever a label is
        for ort in (0, hoehe // 2, hoehe - 1):
            maler.text(
                (x + 2, min(ort, hoehe - 14)),
                str(wert),
                font=schrift,
                fill=(*farbe, 255),
            )
        for ort in (0, breite // 2, breite - 1):
            maler.text(
                (min(ort, breite - 26), y + 1),
                str(wert),
                font=schrift,
                fill=(*farbe, 255),
            )
    ausgabe = BytesIO()
    Image.alpha_composite(bild, ebene).convert("RGB").save(
        ausgabe, "PNG", optimize=True
    )
    return ausgabe.getvalue()
