"""Tests for withdrawing an open question."""

from __future__ import annotations

from homeassistant.core import HomeAssistant, ServiceCall
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_capture_events,
)
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from custom_components.learnbuddy.const import DOMAIN
from custom_components.learnbuddy.manager import LearnBuddyManager

from .conftest import FACH_ID, KIND_ID


def _summe(manager: LearnBuddyManager) -> dict[str, int]:
    """Add up the counters of all tasks."""
    summe = {"gefragt": 0, "richtig": 0, "falsch": 0}
    for aufgabe in manager.task_stores[FACH_ID].aufgaben.values():
        for stat in aufgabe.statistik.values():
            summe["gefragt"] += stat.gefragt
            summe["richtig"] += stat.richtig
            summe["falsch"] += stat.falsch
    return summe


def _boxen(manager: LearnBuddyManager) -> list[int]:
    return [
        stat.box
        for aufgabe in manager.task_stores[FACH_ID].aufgaben.values()
        for stat in aufgabe.statistik.values()
    ]


async def test_frage_abbrechen_zaehlt_nicht(
    hass: HomeAssistant,
    mit_vokabeln: MockConfigEntry,
    notify_calls: list[ServiceCall],
) -> None:
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    bewertungen = async_capture_events(hass, "learnbuddy_answer_evaluated")

    await hass.services.async_call(
        DOMAIN, "ask_now", {"kind_id": KIND_ID}, blocking=True
    )
    assert _summe(manager)["gefragt"] == 1
    gesendet = len(notify_calls)

    await hass.services.async_call(
        DOMAIN, "cancel_question", {"kind_id": KIND_ID}, blocking=True
    )
    await hass.async_block_till_done()

    assert manager.zustand(KIND_ID).offene_frage is None
    assert _summe(manager) == {"gefragt": 0, "richtig": 0, "falsch": 0}
    # The level of the task did not move
    assert set(_boxen(manager)) == {1}
    assert bewertungen == []
    # The child is told, without the solution
    assert len(notify_calls) == gesendet + 1
    nachricht = notify_calls[-1].data["message"]
    assert "zurückgezogen" in nachricht
    assert "Max" in nachricht

    # A late answer finds no open question
    ergebnis = await hass.services.async_call(
        DOMAIN,
        "submit_answer",
        {"kind_id": KIND_ID, "text": "dog"},
        blocking=True,
        return_response=True,
    )
    assert ergebnis == {"ergebnis": "keine_offene_frage"}
    assert _summe(manager)["gefragt"] == 0


async def test_frage_abbrechen_ohne_frage(
    hass: HomeAssistant,
    mit_vokabeln: MockConfigEntry,
    notify_calls: list[ServiceCall],
) -> None:
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    gesendet = len(notify_calls)
    assert not await manager.async_frage_abbrechen(KIND_ID)
    assert len(notify_calls) == gesendet


async def test_frage_abbrechen_beendet_zusatzaufgaben(
    hass: HomeAssistant,
    mit_vokabeln: MockConfigEntry,
    notify_calls: list[ServiceCall],
) -> None:
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    # The child asks for three more questions; the first one is sent
    await manager.async_antwort(KIND_ID, "noch 3")
    zustand = manager.zustand(KIND_ID)
    assert zustand.offene_frage is not None
    assert zustand.zusatz_offen > 0

    assert await manager.async_frage_abbrechen(KIND_ID)
    assert zustand.offene_frage is None
    assert zustand.zusatz_offen == 0


async def test_frage_abbrechen_websocket(
    hass: HomeAssistant,
    mit_vokabeln: MockConfigEntry,
    notify_calls: list[ServiceCall],
    hass_ws_client: WebSocketGenerator,
) -> None:
    ws = await hass_ws_client(hass)

    async def befehl(kind_id: str) -> dict:
        await ws.send_json_auto_id(
            {"type": "learnbuddy/cancel_question", "kind_id": kind_id}
        )
        antwort: dict = await ws.receive_json()
        return antwort

    assert (await befehl(KIND_ID))["result"] == {"abgebrochen": False}
    await hass.services.async_call(
        DOMAIN, "ask_now", {"kind_id": KIND_ID}, blocking=True
    )
    assert (await befehl(KIND_ID))["result"] == {"abgebrochen": True}
    fehler = await befehl("gibtsnicht")
    assert fehler["error"]["message"] == "kind_unbekannt"

    assert await hass.config_entries.async_unload(mit_vokabeln.entry_id)
    assert (await befehl(KIND_ID))["error"]["message"] == "nicht_geladen"
