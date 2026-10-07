"""Tests for the images of tasks."""

from __future__ import annotations

from datetime import timedelta
from io import BytesIO
import os
from pathlib import Path
import time
from typing import Any

from aiohttp import FormData
from homeassistant.components.http.auth import async_sign_path
from homeassistant.core import HomeAssistant
from PIL import Image
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.typing import ClientSessionGenerator

from custom_components.learnbuddy import bilder
from custom_components.learnbuddy.bilder import (
    BildFehlerError,
    ist_bild_id,
    mime_typ,
    verarbeite,
)
from custom_components.learnbuddy.manager import LearnBuddyManager

URL = "/api/learnbuddy/bilder"


def bild_daten(
    fmt: str = "PNG", groesse: tuple[int, int] = (40, 30), **optionen: Any
) -> bytes:
    """Return the bytes of a small test image."""
    modus = "RGBA" if fmt == "PNG" else "RGB"
    ausgabe = BytesIO()
    Image.new(modus, groesse, "red").save(ausgabe, fmt, **optionen)
    return ausgabe.getvalue()


def _formular(daten: bytes, name: str = "diagramm.png") -> FormData:
    formular = FormData()
    formular.add_field("file", daten, filename=name)
    return formular


def test_ist_bild_id() -> None:
    assert ist_bild_id("0" * 32 + ".png")
    assert ist_bild_id("abcdef0123456789abcdef0123456789.jpg")
    assert not ist_bild_id("../" + "0" * 29 + ".png")
    assert not ist_bild_id("0" * 32 + ".gif")
    assert not ist_bild_id("0" * 31 + ".png")
    assert not ist_bild_id(None)
    assert mime_typ("0" * 32 + ".jpg") == "image/jpeg"


def test_verarbeite_png_und_jpeg() -> None:
    inhalt, endung = verarbeite(bild_daten("PNG"))
    assert endung == "png"
    with Image.open(BytesIO(inhalt)) as bild:
        assert bild.format == "PNG"
        assert bild.size == (40, 30)

    exif = Image.Exif()
    exif[0x010F] = "Kamerahersteller"
    # Orientation 6: the photo is stored rotated
    exif[0x0112] = 6
    inhalt, endung = verarbeite(bild_daten("JPEG", exif=exif))
    assert endung == "jpg"
    with Image.open(BytesIO(inhalt)) as bild:
        assert bild.format == "JPEG"
        # The metadata is gone, the orientation was applied
        assert not bild.getexif()
        assert bild.size == (30, 40)
    assert b"Kamerahersteller" not in inhalt


def test_verarbeite_verkleinert_und_wandelt_um() -> None:
    inhalt, endung = verarbeite(bild_daten("JPEG", (4000, 1000)))
    with Image.open(BytesIO(inhalt)) as bild:
        assert bild.size == (1600, 400)
    inhalt, endung = verarbeite(bild_daten("WEBP"))
    assert endung == "png"
    cmyk = BytesIO()
    Image.new("CMYK", (10, 10)).save(cmyk, "TIFF")
    gif = BytesIO()
    Image.new("P", (10, 10)).save(gif, "GIF")
    assert verarbeite(gif.getvalue())[1] == "png"
    with pytest.raises(BildFehlerError):
        # TIFF is not an accepted format
        verarbeite(cmyk.getvalue())


@pytest.mark.parametrize(
    "daten", [b"", b"kein bild", b"\x89PNG\r\n\x1a\n kaputt", b"<svg></svg>"]
)
def test_verarbeite_ungueltig(daten: bytes) -> None:
    with pytest.raises(BildFehlerError):
        verarbeite(daten)


async def test_upload_und_abruf(
    hass: HomeAssistant,
    setup_entry: MockConfigEntry,
    hass_client: ClientSessionGenerator,
    hass_client_no_auth: ClientSessionGenerator,
    upload_ordner: Path,
) -> None:
    manager: LearnBuddyManager = setup_entry.runtime_data
    client = await hass_client()
    antwort = await client.post(URL, data=_formular(bild_daten()))
    assert antwort.status == 200
    bild_id = (await antwort.json())["bild"]
    assert ist_bild_id(bild_id)
    assert bild_id in manager.bilder.ids
    assert (upload_ordner / bild_id).is_file()

    antwort = await client.get(f"{URL}/{bild_id}")
    assert antwort.status == 200
    assert antwort.headers["Content-Type"] == "image/png"
    assert (await antwort.read()).startswith(b"\x89PNG")

    # Unknown ids are not found
    for pfad in ("0" * 32 + ".png", "x", "geheim.txt"):
        assert (await client.get(f"{URL}/{pfad}")).status == 404
    # Home Assistant itself rejects attempts to leave the folder
    assert (await client.get(f"{URL}/..%2Fgeheim.png")).status == 400

    # Without signing in only a signed address works
    anonym = await hass_client_no_auth()
    assert (await anonym.get(f"{URL}/{bild_id}")).status == 401
    signiert = async_sign_path(
        hass, f"{URL}/{bild_id}", timedelta(minutes=5), use_content_user=True
    )
    antwort = await anonym.get(signiert)
    assert antwort.status == 200
    assert (await anonym.post(URL, data=_formular(bild_daten()))).status == 401


async def test_upload_ungueltig(
    setup_entry: MockConfigEntry,
    hass_client: ClientSessionGenerator,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    manager: LearnBuddyManager = setup_entry.runtime_data
    client = await hass_client()
    antwort = await client.post(URL, data=_formular(b"kein bild", "x.png"))
    assert antwort.status == 400
    assert (await antwort.json())["message"] == "bild_ungueltig"
    antwort = await client.post(URL, data=b"kein formular")
    assert antwort.status == 400

    monkeypatch.setattr(bilder, "MAX_BYTES", 100)
    antwort = await client.post(URL, data=_formular(bild_daten("PNG", (300, 300))))
    assert antwort.status == 413
    assert (await antwort.json())["message"] == "bild_zu_gross"
    assert not manager.bilder.ids


async def test_upload_nur_admin(
    setup_entry: MockConfigEntry,
    hass_client: ClientSessionGenerator,
    hass_read_only_access_token: str,
) -> None:
    client = await hass_client(hass_read_only_access_token)
    antwort = await client.post(URL, data=_formular(bild_daten()))
    assert antwort.status == 401
    assert not setup_entry.runtime_data.bilder.ids


async def test_views_ohne_geladene_integration(
    hass: HomeAssistant,
    setup_entry: MockConfigEntry,
    hass_client: ClientSessionGenerator,
) -> None:
    client = await hass_client()
    antwort = await client.post(URL, data=_formular(bild_daten()))
    bild_id = (await antwort.json())["bild"]
    assert await hass.config_entries.async_unload(setup_entry.entry_id)
    assert (await client.get(f"{URL}/{bild_id}")).status == 404
    antwort = await client.post(URL, data=_formular(bild_daten()))
    assert antwort.status == 503


async def test_aufraeumen(
    hass: HomeAssistant, setup_entry: MockConfigEntry, upload_ordner: Path
) -> None:
    manager: LearnBuddyManager = setup_entry.runtime_data
    ablage = manager.bilder
    benutzt = await ablage.async_speichere(bild_daten())
    frisch = await ablage.async_speichere(bild_daten())
    alt = await ablage.async_speichere(bild_daten("JPEG"))
    gestern = time.time() - 2 * 24 * 60 * 60
    for bild_id in (benutzt, alt):
        os.utime(upload_ordner / bild_id, (gestern, gestern))
    (upload_ordner / "notiz.txt").write_text("bleibt")

    await ablage.async_raeume_auf({benutzt})
    # A fresh upload is kept: its tasks are created right afterwards
    assert ablage.ids == {benutzt, frisch}
    assert not (upload_ordner / alt).exists()
    assert (upload_ordner / "notiz.txt").exists()

    # After a restart the folder is read again
    await hass.config_entries.async_reload(setup_entry.entry_id)
    await hass.async_block_till_done()
    assert setup_entry.runtime_data.bilder.ids == {frisch}
    assert setup_entry.runtime_data.bilder.pfad(frisch) == upload_ordner / frisch
    assert setup_entry.runtime_data.bilder.pfad("x") is None

    # A file that vanished is simply forgotten
    (upload_ordner / frisch).unlink()
    await setup_entry.runtime_data.bilder.async_raeume_auf(set())
    assert not setup_entry.runtime_data.bilder.ids


async def test_upload_einer_seite_bleibt_groesser(
    setup_entry: MockConfigEntry,
    hass_client: ClientSessionGenerator,
    upload_ordner: Path,
) -> None:
    client = await hass_client()
    foto = bild_daten("JPEG", (3000, 1500))
    groessen = []
    for adresse in (URL, f"{URL}?zweck=seite"):
        antwort = await client.post(adresse, data=_formular(foto, "seite.jpg"))
        assert antwort.status == 200
        with Image.open(upload_ordner / (await antwort.json())["bild"]) as bild:
            groessen.append(bild.size)
    assert groessen == [(1600, 800), (2400, 1200)]
