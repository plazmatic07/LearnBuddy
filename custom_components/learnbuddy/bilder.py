"""Images that belong to tasks: storage, upload and delivery.

The files live in ``<config>/learnbuddy/uploads`` and are part of the Home
Assistant backup. Uploaded images are re-encoded: that validates them, drops
metadata such as the location of a phone photo and limits their size.
"""

from __future__ import annotations

from http import HTTPStatus
from io import BytesIO
from pathlib import Path
import re
import time
from typing import TYPE_CHECKING, Final
import uuid

from aiohttp import BodyPartReader, web
from homeassistant.components.http.const import KEY_HASS_USER
from homeassistant.exceptions import Unauthorized
from homeassistant.helpers.http import KEY_HASS, HomeAssistantView
from homeassistant.util.hass_dict import HassKey
from PIL import Image, ImageOps, UnidentifiedImageError

from .const import DOMAIN, LOGGER

if TYPE_CHECKING:
    from collections.abc import Iterable

    from homeassistant.core import HomeAssistant

UPLOAD_ORDNER: Final = ("learnbuddy", "uploads")
URL_BILDER: Final = "/api/learnbuddy/bilder"
MAX_BYTES: Final = 10 * 1024 * 1024
MAX_KANTE: Final = 1600
# Pages of a book are read by the AI, small print must stay legible
MAX_KANTE_SEITE: Final = 2400
ZWECK_SEITE: Final = "seite"
# An upload is attached to its tasks right afterwards; until then it must
# survive a cleanup
SCHONFRIST: Final = 24 * 60 * 60
ERLAUBTE_FORMATE: Final = frozenset({"PNG", "JPEG", "WEBP", "GIF"})
MIME: Final = {"png": "image/png", "jpg": "image/jpeg"}
_BILD_ID: Final = re.compile(r"^[0-9a-f]{32}\.(?:png|jpg)$")
_BLOCK: Final = 64 * 1024

DATA_VIEWS: HassKey[bool] = HassKey(f"{DOMAIN}_bild_views")


class BildFehlerError(Exception):
    """An upload is not a usable image."""


def ist_bild_id(wert: object) -> bool:
    """Return whether a value has the form of an image id."""
    return isinstance(wert, str) and _BILD_ID.match(wert) is not None


def mime_typ(bild_id: str) -> str:
    """Return the MIME type of a stored image."""
    return MIME[bild_id.rpartition(".")[2]]


def _kodiere(roh: Image.Image, kante: int) -> tuple[bytes, str]:
    """Re-encode an opened image without its metadata."""
    # Apply the orientation of a phone photo before the metadata goes
    bild = ImageOps.exif_transpose(roh)
    bild.thumbnail((kante, kante))
    ausgabe = BytesIO()
    if roh.format == "JPEG":
        bild.convert("RGB").save(ausgabe, "JPEG", quality=88, optimize=True)
        return ausgabe.getvalue(), "jpg"
    if bild.mode not in ("RGB", "RGBA", "L", "LA", "P"):
        bild = bild.convert("RGBA")
    bild.save(ausgabe, "PNG", optimize=True)
    return ausgabe.getvalue(), "png"


def verarbeite(daten: bytes, kante: int = MAX_KANTE) -> tuple[bytes, str]:
    """Validate and re-encode an image; returns the data and its extension.

    Runs in the executor. Raises BildFehlerError for anything that is not an
    image in an accepted format.
    """
    try:
        with Image.open(BytesIO(daten)) as roh:
            if roh.format in ERLAUBTE_FORMATE:
                return _kodiere(roh, kante)
    except (
        UnidentifiedImageError,
        OSError,
        ValueError,
        Image.DecompressionBombError,
    ) as err:
        raise BildFehlerError from err
    raise BildFehlerError


class BildAblage:
    """The stored images of the integration."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the storage."""
        self._hass = hass
        self.ordner = Path(hass.config.path(*UPLOAD_ORDNER))
        self.ids: set[str] = set()

    async def async_load(self) -> None:
        """Read which images exist."""
        self.ids = await self._hass.async_add_executor_job(self._liste)

    def _liste(self) -> set[str]:
        if not self.ordner.is_dir():
            return set()
        return {p.name for p in self.ordner.iterdir() if ist_bild_id(p.name)}

    def pfad(self, bild_id: str) -> Path | None:
        """Return the file of an image, None if it is unknown."""
        if bild_id not in self.ids:
            return None
        return self.ordner / bild_id

    async def async_speichere(self, daten: bytes, *, seite: bool = False) -> str:
        """Store an uploaded image and return its id.

        The photo of a page is kept larger than the image of a task.
        """
        inhalt, endung = await self._hass.async_add_executor_job(
            verarbeite, daten, MAX_KANTE_SEITE if seite else MAX_KANTE
        )
        bild_id = f"{uuid.uuid4().hex}.{endung}"
        await self._hass.async_add_executor_job(self._schreibe, bild_id, inhalt)
        self.ids.add(bild_id)
        return bild_id

    async def async_speichere_fertig(self, inhalt: bytes, endung: str = "png") -> str:
        """Store an image this integration made itself and return its id."""
        bild_id = f"{uuid.uuid4().hex}.{endung}"
        await self._hass.async_add_executor_job(self._schreibe, bild_id, inhalt)
        self.ids.add(bild_id)
        return bild_id

    def _schreibe(self, bild_id: str, inhalt: bytes) -> None:
        self.ordner.mkdir(parents=True, exist_ok=True)
        (self.ordner / bild_id).write_bytes(inhalt)

    async def async_loesche(self, bild_ids: Iterable[str]) -> None:
        """Delete images."""
        weg = [b for b in bild_ids if b in self.ids]
        if not weg:
            return
        self.ids.difference_update(weg)
        await self._hass.async_add_executor_job(self._entferne, weg)

    def _entferne(self, bild_ids: list[str]) -> None:
        for bild_id in bild_ids:
            try:
                (self.ordner / bild_id).unlink(missing_ok=True)
            except OSError as err:
                LOGGER.warning("Could not delete an image: %s", err)

    async def async_raeume_auf(self, verwendet: set[str]) -> None:
        """Delete images that no task uses, except recent uploads."""
        grenze = time.time() - SCHONFRIST
        alt = await self._hass.async_add_executor_job(
            self._aelter_als, self.ids - verwendet, grenze
        )
        await self.async_loesche(alt)

    def _aelter_als(self, bild_ids: set[str], grenze: float) -> list[str]:
        ergebnis = []
        for bild_id in bild_ids:
            try:
                if (self.ordner / bild_id).stat().st_mtime < grenze:
                    ergebnis.append(bild_id)
            except OSError:
                ergebnis.append(bild_id)
        return ergebnis


def _ablage(hass: HomeAssistant) -> BildAblage | None:
    """Return the image storage of the loaded config entry."""
    entries = hass.config_entries.async_loaded_entries(DOMAIN)
    if not entries:
        return None
    ablage: BildAblage = entries[0].runtime_data.bilder
    return ablage


class BildUploadView(HomeAssistantView):
    """Upload an image (administrators only)."""

    url = URL_BILDER
    name = "api:learnbuddy:bilder"

    async def post(self, request: web.Request) -> web.Response:
        """Store the uploaded image and return its id."""
        if not request[KEY_HASS_USER].is_admin:
            raise Unauthorized
        ablage = _ablage(request.app[KEY_HASS])
        if ablage is None:
            return self.json_message("nicht_geladen", HTTPStatus.SERVICE_UNAVAILABLE)
        try:
            leser = await request.multipart()
            teil = await leser.next()
        except ValueError, AssertionError:
            teil = None
        if not isinstance(teil, BodyPartReader):
            return self.json_message("bild_ungueltig", HTTPStatus.BAD_REQUEST)
        daten = bytearray()
        while block := await teil.read_chunk(_BLOCK):
            daten.extend(block)
            if len(daten) > MAX_BYTES:
                return self.json_message(
                    "bild_zu_gross", HTTPStatus.REQUEST_ENTITY_TOO_LARGE
                )
        try:
            bild_id = await ablage.async_speichere(
                bytes(daten), seite=request.query.get("zweck") == ZWECK_SEITE
            )
        except BildFehlerError:
            return self.json_message("bild_ungueltig", HTTPStatus.BAD_REQUEST)
        return self.json({"bild": bild_id})


class BildView(HomeAssistantView):
    """Deliver a stored image to a signed in user or a signed address."""

    url = URL_BILDER + "/{bild_id}"
    name = "api:learnbuddy:bild"

    async def get(self, request: web.Request, bild_id: str) -> web.StreamResponse:
        """Return the image file."""
        ablage = _ablage(request.app[KEY_HASS])
        pfad = None if ablage is None else ablage.pfad(bild_id)
        if pfad is None:
            return web.Response(status=HTTPStatus.NOT_FOUND)
        return web.FileResponse(
            pfad,
            headers={"Content-Type": mime_typ(bild_id), "Cache-Control": "private"},
        )


def async_register_views(hass: HomeAssistant) -> None:
    """Register the image views once per run."""
    if hass.data.get(DATA_VIEWS):
        return
    hass.http.register_view(BildUploadView())
    hass.http.register_view(BildView())
    hass.data[DATA_VIEWS] = True
