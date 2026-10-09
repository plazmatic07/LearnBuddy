"""Delivery of messages through existing notify integrations."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.components.http.auth import async_sign_path
from homeassistant.core import CALLBACK_TYPE, Context, HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import (
    config_validation as cv,
    entity_registry as er,
    issue_registry as ir,
    script,
)
from homeassistant.helpers.event import async_call_later
from homeassistant.helpers.network import NoURLAvailableError, get_url

from .bilder import URL_BILDER
from .const import DOMAIN, LOGGER, SENDE_WIEDERHOLUNGEN

if TYPE_CHECKING:
    from datetime import datetime

    from .bilder import BildAblage
    from .models import Kind

NOTIFY_DOMAIN = "notify"
SERVICE_SEND_MESSAGE = "send_message"
TELEGRAM_DOMAIN = "telegram_bot"
WHATSAPP_DOMAIN = "whatsapp"
TELEGRAM_SEND_PHOTO = "send_photo"
# Telegram cuts captions of photos at this length
TELEGRAM_MAX_UNTERSCHRIFT = 1024
# The address of an image is only valid for a short time
BILD_URL_GUELTIG = timedelta(minutes=10)


def _issue_id(kind_id: str) -> str:
    return f"senden_fehlgeschlagen_{kind_id}"


def notify_ziel(kind: Kind) -> str:
    """Return a readable description of the notify target of a child."""
    if kind.notify_entity:
        return kind.notify_entity
    return f"{NOTIFY_DOMAIN}.{kind.notify_service}"


class Messenger:
    """Send messages to children using their configured notify target."""

    def __init__(self, hass: HomeAssistant, bilder: BildAblage) -> None:
        """Initialize the messenger."""
        self._hass = hass
        self._bilder = bilder
        self._wiederholungen: set[CALLBACK_TYPE] = set()
        self._gestoert: set[str] = set()

    def _ist_telegram(self, kind: Kind) -> bool:
        """Return whether the notify entity of a child belongs to Telegram."""
        if not kind.notify_entity:
            return False
        eintrag = er.async_get(self._hass).async_get(kind.notify_entity)
        return eintrag is not None and eintrag.platform == TELEGRAM_DOMAIN

    def _whatsapp_nummer(self, kind: Kind) -> str | None:
        """Return the number to write to if the child is reached via WhatsApp.

        A WhatsApp notify entity has a fixed recipient. The sender ID of the
        child is the number the answers come from, so questions go to the same
        number and cannot end up at a different chat.
        """
        if not kind.notify_entity or not kind.absender_kennung:
            return None
        eintrag = er.async_get(self._hass).async_get(kind.notify_entity)
        if eintrag is None or eintrag.platform != WHATSAPP_DOMAIN:
            return None
        roh = "".join(kind.absender_kennung.split())
        if not all(z.isdigit() or z in "+-()/." for z in roh):
            return None
        nummer = "".join(z for z in roh if z.isdigit()).removeprefix("00")
        if not nummer or not self._hass.services.has_service(
            WHATSAPP_DOMAIN, SERVICE_SEND_MESSAGE
        ):
            return None
        return nummer

    def kann_bilder(self, kind: Kind) -> bool:
        """Return whether images can be sent to a child."""
        return bool(kind.bild_aktion) or self._ist_telegram(kind)

    def _lokale_basis(self) -> str:
        """Return the address of this Home Assistant for requests from itself."""
        http = self._hass.http
        schema = "https" if http.ssl_certificate else "http"
        return f"{schema}://127.0.0.1:{http.server_port}"

    async def _async_bild(self, kind: Kind, nachricht: str, bild: str) -> None:
        """Send an image with its text.

        The image is passed as a signed address that is valid for a short
        time, so no folder has to be allowed in the configuration.
        """
        pfad = self._bilder.pfad(bild)
        if pfad is None:
            raise HomeAssistantError("The image of the task does not exist")
        signiert = async_sign_path(
            self._hass, f"{URL_BILDER}/{bild}", BILD_URL_GUELTIG, use_content_user=True
        )
        if kind.bild_aktion:
            try:
                basis = get_url(self._hass, allow_external=False, allow_cloud=False)
            except NoURLAvailableError:
                basis = self._lokale_basis()
            aktionen = await script.async_validate_actions_config(
                self._hass, cv.SCRIPT_SCHEMA(kind.bild_aktion)
            )
            await script.Script(
                self._hass, aktionen, "LearnBuddy image", DOMAIN
            ).async_run(
                {
                    "bild_url": basis + signiert,
                    "bild_pfad": str(pfad),
                    "text": nachricht,
                },
                Context(),
            )
            return
        if not self._ist_telegram(kind):
            raise HomeAssistantError("No way to send images to this child")
        basis = self._lokale_basis()
        daten: dict[str, Any] = {
            "entity_id": [kind.notify_entity],
            "url": basis + signiert,
            # The certificate does not match the local address
            "verify_ssl": not basis.startswith("https"),
        }
        passt = len(nachricht) <= TELEGRAM_MAX_UNTERSCHRIFT
        if passt:
            daten["caption"] = nachricht
        await self._hass.services.async_call(
            TELEGRAM_DOMAIN, TELEGRAM_SEND_PHOTO, daten, blocking=True
        )
        if not passt:
            await self._async_call(kind, nachricht)

    async def _async_call(
        self, kind: Kind, nachricht: str, bild: str | None = None
    ) -> None:
        """Call the notify action of a child."""
        if bild:
            await self._async_bild(kind, nachricht, bild)
            return
        nummer = self._whatsapp_nummer(kind)
        if nummer:
            await self._hass.services.async_call(
                WHATSAPP_DOMAIN,
                SERVICE_SEND_MESSAGE,
                {"number": nummer, "message": nachricht},
                blocking=True,
            )
            return
        if kind.notify_entity:
            await self._hass.services.async_call(
                NOTIFY_DOMAIN,
                SERVICE_SEND_MESSAGE,
                {"message": nachricht},
                target={"entity_id": kind.notify_entity},
                blocking=True,
            )
            return
        if not kind.notify_service:
            raise HomeAssistantError("No notify target configured")
        daten: dict[str, Any] = {"message": nachricht}
        if kind.notify_target:
            daten["target"] = list(kind.notify_target)
        if kind.notify_data:
            daten["data"] = dict(kind.notify_data)
        await self._hass.services.async_call(
            NOTIFY_DOMAIN, kind.notify_service, daten, blocking=True
        )

    async def async_send_or_raise(
        self, kind: Kind, nachricht: str, *, bild: str | None = None
    ) -> None:
        """Send a message and raise a translated error if that fails."""
        try:
            await self._async_call(kind, nachricht, bild)
        except Exception as err:
            self._melde_fehler(kind, err)
            raise HomeAssistantError(
                translation_domain=DOMAIN,
                translation_key="senden_fehlgeschlagen",
                translation_placeholders={"fehler": str(err)},
            ) from err
        self._melde_erfolg(kind)

    async def async_send(
        self,
        kind: Kind,
        nachricht: str,
        *,
        wiederholen: bool = False,
        bild: str | None = None,
    ) -> bool:
        """Send a message without ever raising.

        With ``wiederholen`` a failed message is retried in the background.
        """
        return await self._async_versuch(
            kind, nachricht, 0 if wiederholen else None, bild
        )

    async def _async_versuch(
        self, kind: Kind, nachricht: str, versuch: int | None, bild: str | None = None
    ) -> bool:
        try:
            await self._async_call(kind, nachricht, bild)
        except Exception as err:  # noqa: BLE001 - third party notify code must never crash us
            self._melde_fehler(kind, err)
            if versuch is not None and versuch < len(SENDE_WIEDERHOLUNGEN):
                self._plane_wiederholung(kind, nachricht, versuch, bild)
            else:
                self._erstelle_issue(kind)
            return False
        self._melde_erfolg(kind)
        return True

    def _plane_wiederholung(
        self, kind: Kind, nachricht: str, versuch: int, bild: str | None = None
    ) -> None:
        abbrechen: CALLBACK_TYPE

        async def _wiederhole(_jetzt: datetime) -> None:
            self._wiederholungen.discard(abbrechen)
            await self._async_versuch(kind, nachricht, versuch + 1, bild)

        abbrechen = async_call_later(
            self._hass, SENDE_WIEDERHOLUNGEN[versuch], _wiederhole
        )
        self._wiederholungen.add(abbrechen)

    def _melde_fehler(self, kind: Kind, err: Exception) -> None:
        """Log a failure once until the target works again."""
        if kind.id in self._gestoert:
            LOGGER.debug("Sending via %s still fails: %s", notify_ziel(kind), err)
            return
        self._gestoert.add(kind.id)
        LOGGER.warning("Sending via %s failed: %s", notify_ziel(kind), err)

    def _melde_erfolg(self, kind: Kind) -> None:
        if kind.id in self._gestoert:
            self._gestoert.discard(kind.id)
            LOGGER.info("Sending via %s works again", notify_ziel(kind))
        ir.async_delete_issue(self._hass, DOMAIN, _issue_id(kind.id))

    def _erstelle_issue(self, kind: Kind) -> None:
        ir.async_create_issue(
            self._hass,
            DOMAIN,
            _issue_id(kind.id),
            is_fixable=False,
            severity=ir.IssueSeverity.WARNING,
            translation_key="senden_fehlgeschlagen",
            translation_placeholders={"name": kind.name, "ziel": notify_ziel(kind)},
        )

    @callback
    def async_cancel(self) -> None:
        """Cancel all pending retries."""
        for abbrechen in self._wiederholungen:
            abbrechen()
        self._wiederholungen.clear()
