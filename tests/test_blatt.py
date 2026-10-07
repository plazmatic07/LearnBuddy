"""Tests for rendering the sheet of a simulated exam."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

from PIL import Image

from custom_components.learnbuddy.blatt import (
    BREITE,
    HOEHE,
    Art,
    BlattAufgabe,
    BlattTexte,
    _schrift,
    _umbruch,
    zeichne,
)

from .test_bilder import bild_daten

TEXTE = BlattTexte(
    titel="Hausaufgabenüberprüfung",
    fach="Mathe",
    thema="Brüche · Größen „mit“ Maß²",
    name="Name:",
    klasse="Klasse:",
    datum="Datum:",
    punkte="Punkte",
    punkt_kurz="P.",
    antwort="Antwort:",
    unterschrift="Unterschrift:",
    seite="Seite",
)


def _seiten(aufgaben: list[BlattAufgabe]) -> list[Image.Image]:
    seiten = []
    for daten in zeichne(TEXTE, aufgaben):
        assert daten.startswith(b"\x89PNG")
        bild = Image.open(BytesIO(daten))
        assert bild.size == (BREITE, HOEHE)
        seiten.append(bild.convert("L"))
    return seiten


def _schwarz(bild: Image.Image) -> int:
    """Return how many pixels of a page carry ink."""
    return sum(bild.histogram()[:128])


def test_alle_aufgabenarten(tmp_path: Path) -> None:
    diagramm = tmp_path / "diagramm.png"
    diagramm.write_bytes(bild_daten("PNG", (400, 300)))
    kaputt = tmp_path / "kaputt.png"
    kaputt.write_bytes(b"kein bild")
    aufgaben = [
        BlattAufgabe("Übersetze ins Englische: Hund", Art.LINIE),
        BlattAufgabe("Übersetze: " + "ein sehr langer Ausdruck " * 6, Art.LINIE),
        BlattAufgabe("3/4 + 1/8 = ?", Art.RECHNEN),
        BlattAufgabe("Wie viele Ferientage hat Italien?", Art.RECHNEN, bild=diagramm),
        BlattAufgabe("Lies ab.", Art.RECHNEN, bild=kaputt),
        BlattAufgabe("Fehlt.", Art.RECHNEN, bild=tmp_path / "gibtsnicht.png"),
        BlattAufgabe("Wo findet die Fotosynthese statt?", Art.ZEILEN),
        BlattAufgabe(
            "Wie nehmen Pflanzen Wasser auf?",
            Art.AUSWAHL,
            optionen=("Durch die Blätter", "Durch die Wurzeln", "x" * 300),
        ),
    ]
    seiten = _seiten(aufgaben)
    # Eight tasks with an image do not fit on one page
    assert len(seiten) == 2
    assert all(_schwarz(seite) > 2000 for seite in seiten)
    # The header is only on the first page
    kopf = (0, 0, BREITE, 380)
    assert _schwarz(seiten[0].crop(kopf)) > 5 * _schwarz(seiten[1].crop(kopf))


def test_leeres_blatt_und_viele_aufgaben() -> None:
    assert len(_seiten([])) == 1
    viele = [BlattAufgabe(f"{i} · 7", Art.RECHNEN) for i in range(30)]
    seiten = _seiten(viele)
    assert len(seiten) >= 4
    # A task that is higher than a page starts on a fresh one and never loops
    riesig = BlattAufgabe("lang " * 900, Art.ZEILEN)
    assert len(_seiten([riesig])) == 2


def test_umlaute_haben_eigene_zeichen() -> None:
    schrift = _schrift(28)
    fehlend = schrift.getmask("￿").getbbox()
    for zeichen in "äöüßÄÖÜ€„“·²½√×→":
        maske = schrift.getmask(zeichen)
        assert maske.getbbox() is not None, zeichen
        assert maske.getbbox() != fehlend or bytes(maske) != bytes(
            schrift.getmask("￿")
        ), zeichen


def test_umbruch() -> None:
    schrift = _schrift(28)
    zeilen = _umbruch("eins zwei drei vier fünf sechs sieben acht", schrift, 200)
    assert len(zeilen) > 2
    assert " ".join(zeilen) == "eins zwei drei vier fünf sechs sieben acht"
    assert all(schrift.getlength(zeile) <= 200 for zeile in zeilen)
    # A word without spaces is cut, explicit line breaks are kept
    lang = _umbruch("x" * 100, schrift, 200)
    assert len(lang) > 3
    assert "".join(lang) == "x" * 100
    assert _umbruch("a\nb", schrift, 200) == ["a", "b"]
    gemischt = _umbruch("kurz " + "y" * 60, schrift, 200)
    assert gemischt[0] == "kurz"
    assert "".join(gemischt[1:]) == "y" * 60
    assert _umbruch("", schrift, 200) == [""]
