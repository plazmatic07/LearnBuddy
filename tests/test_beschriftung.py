"""Tests for numbering the labels of an image."""

from io import BytesIO

from PIL import Image

from custom_components.learnbuddy.beschriftung import pruefe_feld, zeichne


def _bild(farbe: tuple[int, int, int] = (250, 240, 200)) -> bytes:
    daten = BytesIO()
    Image.new("RGB", (400, 300), farbe).save(daten, "PNG")
    return daten.getvalue()


def test_feld_wird_bereinigt() -> None:
    """A box is cut to the image and numbers are integers."""
    feld = pruefe_feld({"nr": "2", "x": 0.9, "y": 0.1, "b": 0.5, "h": 0.1})
    assert feld == {"nr": 2, "x": 0.9, "y": 0.1, "b": 0.09999999999999998, "h": 0.1}


def test_unbrauchbare_felder_entfallen() -> None:
    """Missing values, number 0 and tiny boxes are dropped."""
    assert pruefe_feld("x") is None
    assert pruefe_feld({"nr": 1, "x": 0.1}) is None
    assert pruefe_feld({"nr": 0, "x": 0.1, "y": 0.1, "b": 0.2, "h": 0.2}) is None
    assert pruefe_feld({"nr": 1, "x": 0.1, "y": 0.1, "b": 0.001, "h": 0.2}) is None


def test_label_wird_abgedeckt() -> None:
    """The label area takes the colour around it and gets a dark number."""
    quelle = Image.new("RGB", (400, 300), (250, 240, 200))
    # A dark "label" inside the box
    for x in range(100, 160):
        for y in range(100, 120):
            quelle.putpixel((x, y), (0, 0, 0))
    daten = BytesIO()
    quelle.save(daten, "PNG")
    feld = {"nr": 3, "x": 0.25, "y": 0.33, "b": 0.15, "h": 0.07}
    ergebnis = Image.open(BytesIO(zeichne(daten.getvalue(), [feld]))).convert("RGB")
    assert ergebnis.size == (400, 300)
    # The edge of the box is the contour, the area beside the number is the
    # background colour of the surroundings
    assert ergebnis.getpixel((102, 102)) == (250, 240, 200)
    # Something dark (the number) is in the middle
    dunkel = sum(
        1
        for x in range(100, 160)
        for y in range(100, 120)
        if sum(ergebnis.getpixel((x, y))) < 150
    )
    assert 0 < dunkel < 60 * 20 / 2


def test_kleine_box_waechst_um_die_nummer() -> None:
    """A box smaller than its number is enlarged."""
    feld = {"nr": 12, "x": 0.5, "y": 0.5, "b": 0.02, "h": 0.02}
    ergebnis = Image.open(BytesIO(zeichne(_bild(), [feld]))).convert("RGB")
    dunkel = [
        (x, y)
        for x in range(400)
        for y in range(300)
        if sum(ergebnis.getpixel((x, y))) < 150
    ]
    assert max(x for x, _ in dunkel) - min(x for x, _ in dunkel) > 10
