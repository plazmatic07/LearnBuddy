"""Render the sheet of a simulated exam as images of A4 pages.

Everything here runs in the executor: it only uses Pillow and the fonts that
come with the integration.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from functools import lru_cache
from io import BytesIO
from pathlib import Path
from typing import TYPE_CHECKING

from PIL import Image, ImageDraw, ImageFont, ImageOps, UnidentifiedImageError

if TYPE_CHECKING:
    from collections.abc import Sequence

# A4 at 150 dpi
BREITE = 1240
HOEHE = 1754
RAND = 95
FUSS = 110
SCHWARZ = (20, 20, 20)
GRAU = (110, 110, 110)

_SCHRIFTEN = Path(__file__).parent / "fonts"
_EINZUG = 62
_SPALTE_PUNKTE = 150
_ZEILE = 40
_ABSTAND = 38
_BILD_HOEHE = 430
_RECHENPLATZ = 120
_SCHREIBZEILEN = 3
_SCHREIBZEILE = 56
_KASTEN = 26


class Art(StrEnum):
    """How the answer to a task is written down."""

    # One word or number on a line
    LINIE = "linie"
    # Room to calculate and a line for the result
    RECHNEN = "rechnen"
    # A few lines for sentences
    ZEILEN = "zeilen"
    # Boxes to tick
    AUSWAHL = "auswahl"


@dataclass(frozen=True, slots=True)
class BlattAufgabe:
    """A task as it is printed on the sheet."""

    text: str
    art: Art
    optionen: tuple[str, ...] = ()
    # File of the image the task is about
    bild: Path | None = None


@dataclass(frozen=True, slots=True)
class BlattTexte:
    """The words on the sheet in the language of the messages."""

    titel: str
    fach: str
    thema: str
    name: str
    klasse: str
    datum: str
    punkte: str
    punkt_kurz: str
    antwort: str
    unterschrift: str
    seite: str


@lru_cache(maxsize=16)
def _schrift(groesse: int, fett: bool = False) -> ImageFont.FreeTypeFont:
    datei = "DejaVuSans-Bold.ttf" if fett else "DejaVuSans.ttf"
    return ImageFont.truetype(str(_SCHRIFTEN / datei), groesse)


def _umbruch(text: str, schrift: ImageFont.FreeTypeFont, breite: float) -> list[str]:
    """Break a text into lines that fit a width."""
    zeilen: list[str] = []
    for absatz in text.split("\n"):
        aktuell = ""
        for wort in absatz.split():
            rest = wort
            # A word longer than the line is cut
            while schrift.getlength(rest) > breite:
                schnitt = len(rest)
                while schnitt > 1 and schrift.getlength(rest[:schnitt]) > breite:
                    schnitt -= 1
                if aktuell:
                    zeilen.append(aktuell)
                    aktuell = ""
                zeilen.append(rest[:schnitt])
                rest = rest[schnitt:]
            versuch = f"{aktuell} {rest}".strip()
            if schrift.getlength(versuch) <= breite:
                aktuell = versuch
            else:
                zeilen.append(aktuell)
                aktuell = rest
        zeilen.append(aktuell)
    return zeilen or [""]


def _lade_bild(datei: Path | None, breite: int) -> Image.Image | None:
    """Open the image of a task and fit it into the sheet."""
    if datei is None:
        return None
    try:
        with Image.open(datei) as roh:
            bild = ImageOps.exif_transpose(roh).convert("RGBA")
    except UnidentifiedImageError, OSError, ValueError:
        return None
    bild.thumbnail((breite, _BILD_HOEHE))
    # Transparent parts become white paper
    papier = Image.new("RGB", bild.size, "white")
    papier.paste(bild, mask=bild.getchannel("A"))
    return papier


@dataclass(slots=True)
class _Block:
    """A task broken into lines, ready to be drawn."""

    aufgabe: BlattAufgabe
    zeilen: list[str]
    optionen: list[list[str]]
    bild: Image.Image | None
    # The answer line fits next to a short text
    daneben: bool
    hoehe: int


class _Blatt:
    """The pages of a sheet while they are drawn."""

    def __init__(self, texte: BlattTexte, anzahl: int) -> None:
        self._texte = texte
        self._anzahl = anzahl
        self.seiten: list[Image.Image] = []
        self._zeichner: ImageDraw.ImageDraw
        self.y = 0
        self._neue_seite()

    @property
    def _text_x(self) -> int:
        return RAND + _EINZUG

    @property
    def text_breite(self) -> int:
        return BREITE - RAND - _SPALTE_PUNKTE - self._text_x

    def _linie(self, x0: float, x1: float, y: float, staerke: int = 2) -> None:
        self._zeichner.line([(x0, y), (x1, y)], fill=SCHWARZ, width=staerke)

    def _neue_seite(self) -> None:
        seite = Image.new("RGB", (BREITE, HOEHE), "white")
        self.seiten.append(seite)
        self._zeichner = ImageDraw.Draw(seite)
        if len(self.seiten) == 1:
            self._kopf()
        else:
            texte = self._texte
            self._zeichner.text(
                (RAND, RAND),
                f"{texte.titel} · {texte.fach}",
                font=_schrift(24),
                fill=GRAU,
            )
            self._linie(RAND, BREITE - RAND, RAND + 44, 1)
            self.y = RAND + 80

    def _kopf(self) -> None:
        texte = self._texte
        z = self._zeichner
        # Box for the points in the upper right corner
        kasten = (BREITE - RAND - 250, RAND, BREITE - RAND, RAND + 130)
        z.rectangle(kasten, outline=SCHWARZ, width=3)
        z.text(
            (kasten[0] + 18, kasten[1] + 14),
            texte.punkte,
            font=_schrift(24),
            fill=SCHWARZ,
        )
        ziel = f"/ {self._anzahl}"
        breite = _schrift(40, True).getlength(ziel)
        z.text(
            (kasten[2] - 20 - breite, kasten[1] + 62),
            ziel,
            font=_schrift(40, True),
            fill=SCHWARZ,
        )
        self._linie(kasten[0] + 20, kasten[2] - 34 - breite, kasten[1] + 106)

        links = kasten[0] - RAND - 30
        y = RAND - 6
        for zeile in _umbruch(texte.titel, _schrift(50, True), links):
            z.text((RAND, y), zeile, font=_schrift(50, True), fill=SCHWARZ)
            y += 62
        y += 6
        for zeile in _umbruch(texte.fach, _schrift(32, True), links):
            z.text((RAND, y), zeile, font=_schrift(32, True), fill=SCHWARZ)
            y += 42
        for zeile in _umbruch(texte.thema, _schrift(28), links)[:3]:
            z.text((RAND, y), zeile, font=_schrift(28), fill=SCHWARZ)
            y += 38
        y = max(y, kasten[3]) + 46

        # Name, class and date to fill in by hand
        schrift = _schrift(28)
        x = RAND
        for wort, breite_linie in (
            (texte.name, 430),
            (texte.klasse, 110),
            (texte.datum, 0),
        ):
            z.text((x, y), wort, font=schrift, fill=SCHWARZ)
            x += int(schrift.getlength(wort)) + 14
            ende = x + breite_linie if breite_linie else BREITE - RAND
            self._linie(x, ende, y + 34)
            x = ende + 34
        y += 74
        self._linie(RAND, BREITE - RAND, y, 4)
        self._linie(RAND, BREITE - RAND, y + 8, 1)
        self.y = y + 52

    def block(self, aufgabe: BlattAufgabe) -> _Block:
        """Break a task into lines and measure its height."""
        schrift = _schrift(28)
        zeilen = _umbruch(aufgabe.text, schrift, self.text_breite)
        bild = _lade_bild(aufgabe.bild, self.text_breite)
        hoehe = len(zeilen) * _ZEILE
        optionen: list[list[str]] = []
        daneben = False
        if aufgabe.art is Art.LINIE:
            daneben = (
                len(zeilen) == 1
                and schrift.getlength(zeilen[0]) < self.text_breite * 0.6
            )
            if not daneben:
                hoehe += _SCHREIBZEILE
        elif aufgabe.art is Art.RECHNEN:
            hoehe += _RECHENPLATZ + _SCHREIBZEILE
        elif aufgabe.art is Art.ZEILEN:
            hoehe += 8 + _SCHREIBZEILEN * _SCHREIBZEILE
        else:
            optionen = [
                _umbruch(option, schrift, self.text_breite - _KASTEN - 70)
                for option in aufgabe.optionen
            ]
            hoehe += 10 + sum(len(option) * _ZEILE + 10 for option in optionen)
        if bild is not None:
            hoehe += bild.height + 24
        return _Block(aufgabe, zeilen, optionen, bild, daneben, hoehe)

    def male(self, nummer: int, block: _Block) -> None:
        """Draw a task, on a new page if it does not fit any more."""
        if self.y + block.hoehe > HOEHE - FUSS - 20 and self.y > RAND + 100:
            self._neue_seite()
        z = self._zeichner
        schrift = _schrift(28)
        x = self._text_x
        y = self.y
        z.text((RAND, y), f"{nummer}.", font=_schrift(28, True), fill=SCHWARZ)
        punkte = f"/ 1 {self._texte.punkt_kurz}"
        breite = _schrift(22).getlength(punkte)
        rechts = BREITE - RAND
        z.text((rechts - breite, y + 6), punkte, font=_schrift(22), fill=GRAU)
        self._linie(rechts - breite - 62, rechts - breite - 10, y + 32, 1)

        for zeile in block.zeilen:
            z.text((x, y), zeile, font=schrift, fill=SCHWARZ)
            y += _ZEILE
        ende = x + self.text_breite
        if block.bild is not None:
            self.seiten[-1].paste(block.bild, (x, y + 8))
            z.rectangle(
                (x - 1, y + 7, x + block.bild.width, y + 8 + block.bild.height),
                outline=GRAU,
            )
            y += block.bild.height + 24

        aufgabe = block.aufgabe
        if aufgabe.art is Art.LINIE:
            if block.daneben:
                anfang = x + schrift.getlength(block.zeilen[0]) + 30
                self._linie(anfang, ende, y - 6, 1)
            else:
                self._linie(x, ende, y + _SCHREIBZEILE - 16, 1)
                y += _SCHREIBZEILE
        elif aufgabe.art is Art.RECHNEN:
            y += _RECHENPLATZ
            wort = self._texte.antwort
            z.text((x, y), wort, font=schrift, fill=SCHWARZ)
            self._linie(x + schrift.getlength(wort) + 16, ende, y + 34, 1)
            y += _SCHREIBZEILE
        elif aufgabe.art is Art.ZEILEN:
            y += 8
            for _ in range(_SCHREIBZEILEN):
                y += _SCHREIBZEILE
                self._linie(x, ende, y - 14, 1)
        else:
            y += 10
            for buchstabe, option in zip("ABCD", block.optionen, strict=False):
                z.rectangle(
                    (x, y + 4, x + _KASTEN, y + 4 + _KASTEN), outline=SCHWARZ, width=2
                )
                z.text(
                    (x + _KASTEN + 16, y), f"{buchstabe})", font=schrift, fill=SCHWARZ
                )
                for zeile in option:
                    z.text((x + _KASTEN + 70, y), zeile, font=schrift, fill=SCHWARZ)
                    y += _ZEILE
                y += 10
        self.y = y + _ABSTAND

    def fertig(self) -> list[bytes]:
        """Add the footers and return the pages as PNG files."""
        texte = self._texte
        seiten: list[bytes] = []
        for nummer, seite in enumerate(self.seiten, start=1):
            z = ImageDraw.Draw(seite)
            y = HOEHE - FUSS
            marke = f"{texte.seite} {nummer} / {len(self.seiten)}"
            breite = _schrift(22).getlength(marke)
            z.text((BREITE - RAND - breite, y + 8), marke, font=_schrift(22), fill=GRAU)
            if nummer == len(self.seiten):
                z.text((RAND, y), texte.unterschrift, font=_schrift(24), fill=SCHWARZ)
                anfang = RAND + _schrift(24).getlength(texte.unterschrift) + 14
                z.line(
                    [(anfang, y + 30), (anfang + 420, y + 30)], fill=SCHWARZ, width=1
                )
            ausgabe = BytesIO()
            seite.save(ausgabe, "PNG", optimize=True)
            seiten.append(ausgabe.getvalue())
        return seiten


def zeichne(texte: BlattTexte, aufgaben: Sequence[BlattAufgabe]) -> list[bytes]:
    """Return the pages of an exam sheet as PNG images."""
    blatt = _Blatt(texte, len(aufgaben))
    for nummer, aufgabe in enumerate(aufgaben, start=1):
        blatt.male(nummer, blatt.block(aufgabe))
    return blatt.fertig()
