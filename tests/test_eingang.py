"""Tests for answers taken directly from messenger events."""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant, ServiceCall
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.learnbuddy.const import DOMAIN
from custom_components.learnbuddy.eingang import whatsapp_absender
from custom_components.learnbuddy.manager import LearnBuddyManager

from .conftest import KIND_ID


async def _frage(hass: HomeAssistant, manager: LearnBuddyManager) -> None:
    await hass.services.async_call(
        DOMAIN, "ask_now", {"kind_id": KIND_ID}, blocking=True
    )
    assert manager.zustand(KIND_ID).offene_frage is not None


def _gefragt(manager: LearnBuddyManager) -> bool:
    return manager.zustand(KIND_ID).offene_frage is not None


@pytest.mark.parametrize(
    ("wert", "nummer"),
    [
        ("491701234567@s.whatsapp.net", "491701234567"),
        ("491701234567:12@s.whatsapp.net", "491701234567"),
        ("491701234567", "491701234567"),
        (None, ""),
    ],
)
def test_whatsapp_absender(wert: Any, nummer: str) -> None:
    assert whatsapp_absender(wert) == nummer


@pytest.mark.parametrize(
    ("event", "daten"),
    [
        # Telegram delivers the chat ID as a number
        ("telegram_text", {"chat_id": 491701234567, "text": "x"}),
        (
            "whatsapp_message_received",
            {"from": "491701234567@s.whatsapp.net", "body": "x", "isGroup": False},
        ),
    ],
)
async def test_antwort_ohne_automation(
    hass: HomeAssistant,
    mit_vokabeln: MockConfigEntry,
    notify_calls: list[ServiceCall],
    event: str,
    daten: dict[str, Any],
) -> None:
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    await _frage(hass, manager)
    gesendet = len(notify_calls)

    hass.bus.async_fire(event, daten)
    await hass.async_block_till_done()

    assert not _gefragt(manager)
    # The child got its feedback
    assert len(notify_calls) == gesendet + 1


@pytest.mark.parametrize(
    ("event", "daten"),
    [
        ("telegram_text", {"chat_id": 999, "text": "x"}),
        ("telegram_text", {"chat_id": 491701234567, "text": "  "}),
        ("telegram_text", {"chat_id": 491701234567}),
        ("telegram_text", {"text": "x"}),
        (
            "whatsapp_message_received",
            {"from": "491701234567@s.whatsapp.net", "body": "x", "isGroup": True},
        ),
        ("whatsapp_message_received", {"from": "4999@s.whatsapp.net", "body": "x"}),
        # No custom event is configured
        ("mein_messenger", {"sender": "491701234567", "text": "x"}),
    ],
)
async def test_ignoriert(
    hass: HomeAssistant,
    mit_vokabeln: MockConfigEntry,
    notify_calls: list[ServiceCall],
    event: str,
    daten: dict[str, Any],
) -> None:
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    await _frage(hass, manager)
    gesendet = len(notify_calls)

    hass.bus.async_fire(event, daten)
    await hass.async_block_till_done()

    assert _gefragt(manager)
    assert len(notify_calls) == gesendet


async def test_abgeschaltet_und_eigenes_event(
    hass: HomeAssistant,
    mit_vokabeln: MockConfigEntry,
    notify_calls: list[ServiceCall],
) -> None:
    hass.config_entries.async_update_entry(
        mit_vokabeln,
        options={
            **mit_vokabeln.options,
            "eingang_telegram": False,
            "eingang_whatsapp": False,
            "eingang_event": "mein_messenger",
            "eingang_absender_feld": "nummer",
            "eingang_text_feld": "inhalt",
        },
    )
    await hass.async_block_till_done()
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    await _frage(hass, manager)

    hass.bus.async_fire("telegram_text", {"chat_id": 491701234567, "text": "x"})
    hass.bus.async_fire(
        "whatsapp_message_received", {"from": "491701234567", "body": "x"}
    )
    await hass.async_block_till_done()
    assert _gefragt(manager)

    hass.bus.async_fire("mein_messenger", {"nummer": "+49 170 1234567", "inhalt": "x"})
    await hass.async_block_till_done()
    assert not _gefragt(manager)


async def test_eigenes_event_mit_vorgabefeldern(
    hass: HomeAssistant, mit_vokabeln: MockConfigEntry
) -> None:
    hass.config_entries.async_update_entry(
        mit_vokabeln,
        options={**mit_vokabeln.options, "eingang_event": "mein_messenger"},
    )
    await hass.async_block_till_done()
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    await _frage(hass, manager)

    hass.bus.async_fire("mein_messenger", {"sender": "491701234567", "text": "x"})
    await hass.async_block_till_done()
    assert not _gefragt(manager)


async def test_nach_entladen_still(
    hass: HomeAssistant, mit_vokabeln: MockConfigEntry
) -> None:
    assert await hass.config_entries.async_unload(mit_vokabeln.entry_id)
    hass.bus.async_fire("telegram_text", {"chat_id": 491701234567, "text": "x"})
    await hass.async_block_till_done()


async def test_automation_und_eingang_zaehlen_einmal(
    hass: HomeAssistant,
    mit_vokabeln: MockConfigEntry,
    notify_calls: list[ServiceCall],
) -> None:
    """An old blueprint automation next to the listener must not double count."""
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    await _frage(hass, manager)
    gesendet = len(notify_calls)

    hass.bus.async_fire("telegram_text", {"chat_id": 491701234567, "text": "👍"})
    ergebnis = await hass.services.async_call(
        DOMAIN,
        "submit_answer",
        {"absender": "491701234567", "text": "👍"},
        blocking=True,
        return_response=True,
    )
    await hass.async_block_till_done()

    assert ergebnis == {"ergebnis": "doppelt"}
    # One feedback, and the thumb was not taken as a wish for another task
    assert len(notify_calls) == gesendet + 1
    assert not _gefragt(manager)


async def test_aktion_zuerst_dann_eingang(
    hass: HomeAssistant,
    mit_vokabeln: MockConfigEntry,
    notify_calls: list[ServiceCall],
) -> None:
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    await _frage(hass, manager)

    ergebnis = await hass.services.async_call(
        DOMAIN,
        "submit_answer",
        {"kind_id": KIND_ID, "text": "👍"},
        blocking=True,
        return_response=True,
    )
    assert ergebnis is not None
    assert ergebnis["ergebnis"] == "falsch"
    gesendet = len(notify_calls)

    hass.bus.async_fire("telegram_text", {"chat_id": 491701234567, "text": "👍"})
    await hass.async_block_till_done()
    assert len(notify_calls) == gesendet
    assert not _gefragt(manager)


async def test_gleiche_antwort_zweimal_auf_einem_weg(
    hass: HomeAssistant, mit_vokabeln: MockConfigEntry
) -> None:
    """Repeating an answer on the same path is no duplicate."""
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    assert not manager.antwort_doppelt(KIND_ID, "ja", "aktion")
    assert not manager.antwort_doppelt(KIND_ID, "ja", "aktion")
    assert manager.antwort_doppelt(KIND_ID, "ja", "eingang")
    assert not manager.antwort_doppelt(KIND_ID, "nein", "eingang")
