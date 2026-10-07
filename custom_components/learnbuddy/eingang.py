"""Incoming answers taken directly from the events of messenger integrations.

The integration contains no messenger code. It only listens for the events
that existing integrations fire for incoming messages, so the order in which
they are set up does not matter.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from homeassistant.core import CALLBACK_TYPE, Event, HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError

from .const import (
    CONF_EINGANG_ABSENDER_FELD,
    CONF_EINGANG_EVENT,
    CONF_EINGANG_TELEGRAM,
    CONF_EINGANG_TEXT_FELD,
    CONF_EINGANG_WHATSAPP,
    DEFAULT_EINGANG_ABSENDER_FELD,
    DEFAULT_EINGANG_TEXT_FELD,
    EVENT_TELEGRAM_TEXT,
    EVENT_WHATSAPP_NACHRICHT,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

    from .manager import LearnBuddyManager

_LOGGER = logging.getLogger(__name__)

QUELLE_EINGANG = "eingang"
QUELLE_AKTION = "aktion"


def whatsapp_absender(wert: Any) -> str:
    """Return the phone number of a WhatsApp sender like 49170…:12@s.whatsapp.net."""
    return str(wert or "").split("@", 1)[0].split(":", 1)[0]


class Eingang:
    """Forward incoming messenger messages of known senders to the manager."""

    def __init__(
        self,
        hass: HomeAssistant,
        manager: LearnBuddyManager,
        optionen: Mapping[str, Any],
    ) -> None:
        """Initialize the listener."""
        self._hass = hass
        self._manager = manager
        self._telegram: bool = optionen.get(CONF_EINGANG_TELEGRAM, True)
        self._whatsapp: bool = optionen.get(CONF_EINGANG_WHATSAPP, True)
        self._event: str = (optionen.get(CONF_EINGANG_EVENT) or "").strip()
        self._absender_feld: str = (
            optionen.get(CONF_EINGANG_ABSENDER_FELD) or DEFAULT_EINGANG_ABSENDER_FELD
        ).strip()
        self._text_feld: str = (
            optionen.get(CONF_EINGANG_TEXT_FELD) or DEFAULT_EINGANG_TEXT_FELD
        ).strip()

    @callback
    def async_start(self) -> CALLBACK_TYPE:
        """Listen for the configured events and return a function to stop."""
        abmelden: list[CALLBACK_TYPE] = []
        if self._telegram:
            abmelden.append(
                self._hass.bus.async_listen(EVENT_TELEGRAM_TEXT, self._von_telegram)
            )
        if self._whatsapp:
            abmelden.append(
                self._hass.bus.async_listen(
                    EVENT_WHATSAPP_NACHRICHT, self._von_whatsapp
                )
            )
        if self._event and self._event not in (
            EVENT_TELEGRAM_TEXT if self._telegram else None,
            EVENT_WHATSAPP_NACHRICHT if self._whatsapp else None,
        ):
            abmelden.append(self._hass.bus.async_listen(self._event, self._von_event))

        @callback
        def stoppen() -> None:
            for funktion in abmelden:
                funktion()

        return stoppen

    @callback
    def _von_telegram(self, event: Event) -> None:
        self._annehmen(event.data.get("chat_id"), event.data.get("text"))

    @callback
    def _von_whatsapp(self, event: Event) -> None:
        if event.data.get("isGroup") or event.data.get("fromMe"):
            return
        self._annehmen(
            whatsapp_absender(event.data.get("from")), event.data.get("body")
        )

    @callback
    def _von_event(self, event: Event) -> None:
        self._annehmen(
            event.data.get(self._absender_feld), event.data.get(self._text_feld)
        )

    @callback
    def _annehmen(self, absender: Any, inhalt: Any) -> None:
        """Hand a message over if its sender is a known child."""
        if absender is None or inhalt is None:
            return
        nachricht = str(inhalt).strip()
        if not nachricht:
            return
        kind = self._manager.kind_per_absender(str(absender))
        if kind is None:
            return
        if self._manager.antwort_doppelt(kind.id, nachricht, QUELLE_EINGANG):
            return
        self._hass.async_create_task(
            self._async_antwort(kind.id, nachricht), "learnbuddy_eingang"
        )

    async def _async_antwort(self, kind_id: str, nachricht: str) -> None:
        try:
            await self._manager.async_antwort(kind_id, nachricht)
        except HomeAssistantError:
            # No sender, name or text in the log
            _LOGGER.warning("An incoming answer could not be processed")
