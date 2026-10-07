"""Tests for sending tasks with an image."""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers import entity_registry as er
import pytest
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_mock_service,
)
from pytest_homeassistant_custom_component.typing import ClientSessionGenerator

from custom_components.learnbuddy.const import DOMAIN
from custom_components.learnbuddy.manager import LearnBuddyManager
from custom_components.learnbuddy.models import MatheAufgabe

from .conftest import KIND_DATEN, KIND_ID, subentry
from .test_bilder import bild_daten
from .test_mathe_ablauf import MATHE_DATEN, MATHE_ID

AKTION = [
    {
        "action": "test.bild",
        "data": {
            "url": "{{ bild_url }}",
            "datei": "{{ bild_pfad }}",
            "text": "{{ text }}",
        },
    }
]


async def _setup(hass: HomeAssistant, **kind: Any) -> MockConfigEntry:
    daten = {k: v for k, v in {**KIND_DATEN, **kind}.items() if v is not None}
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="LearnBuddy",
        data={},
        options={"timeout_minuten": 60, "sprache": "de"},
        subentries_data=[
            subentry("kind", KIND_ID, "Max", daten),
            subentry("fach", MATHE_ID, "Mathe (Max)", MATHE_DATEN),
        ],
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


async def _telegram(hass: HomeAssistant) -> MockConfigEntry:
    """Set up a child whose notify entity belongs to the Telegram integration."""
    eintrag = er.async_get(hass).async_get_or_create(
        "notify", "telegram_bot", "chat1", suggested_object_id="max_chat"
    )
    return await _setup(
        hass, notify_service=None, notify_target=None, notify_entity=eintrag.entity_id
    )


async def _mit_bild(
    entry: MockConfigEntry, aufgabe: str = "a) Welches Land hat die meisten Ferientage?"
) -> MatheAufgabe:
    manager: LearnBuddyManager = entry.runtime_data
    bild = await manager.bilder.async_speichere(bild_daten())
    neu = MatheAufgabe(fach_id=MATHE_ID, aufgabe=aufgabe, loesung="Türkei", bild=bild)
    manager.task_stores[MATHE_ID].add(neu)
    return neu


async def _frage(hass: HomeAssistant) -> None:
    await hass.services.async_call(
        DOMAIN, "ask_now", {"kind_id": KIND_ID}, blocking=True
    )
    await hass.async_block_till_done()


async def test_telegram_bekommt_das_bild(
    hass: HomeAssistant, hass_client_no_auth: ClientSessionGenerator
) -> None:
    fotos = async_mock_service(hass, "telegram_bot", "send_photo")
    texte = async_mock_service(hass, "notify", "send_message")
    entry = await _telegram(hass)
    manager: LearnBuddyManager = entry.runtime_data
    assert manager.messenger.kann_bilder(manager.kinder[KIND_ID])
    aufgabe = await _mit_bild(entry)

    await _frage(hass)
    assert not texte
    assert len(fotos) == 1
    daten = fotos[0].data
    assert daten["entity_id"] == ["notify.max_chat"]
    assert daten["caption"] == (
        "Hallo Max! 🔢 Mathe: a) Welches Land hat die meisten Ferientage?"
    )
    assert daten["verify_ssl"] is True
    port = hass.http.server_port
    assert daten["url"].startswith(
        f"http://127.0.0.1:{port}/api/learnbuddy/bilder/{aufgabe.bild}?authSig="
    )
    frage = manager.zustand(KIND_ID).offene_frage
    assert frage is not None
    assert frage.aufgabe_id == aufgabe.id

    # The address works without signing in, as long as it is valid
    client = await hass_client_no_auth()
    pfad = daten["url"].removeprefix(f"http://127.0.0.1:{port}")
    antwort = await client.get(pfad)
    assert antwort.status == 200
    assert antwort.headers["Content-Type"] == "image/png"

    # The answer and its result are plain text again
    await hass.services.async_call(
        DOMAIN, "submit_answer", {"kind_id": KIND_ID, "text": "Türkei"}, blocking=True
    )
    assert len(fotos) == 1
    assert texte[-1].data["message"].startswith("Richtig, Max!")


async def test_telegram_langer_text_kommt_getrennt(hass: HomeAssistant) -> None:
    fotos = async_mock_service(hass, "telegram_bot", "send_photo")
    texte = async_mock_service(hass, "notify", "send_message")
    entry = await _telegram(hass)
    await _mit_bild(entry, "x" * 1100)
    await _frage(hass)
    assert "caption" not in fotos[0].data
    assert len(texte) == 1
    assert texte[0].data["message"].endswith("x" * 1100)


async def test_eigene_aktion(
    hass: HomeAssistant, notify_calls: list[ServiceCall]
) -> None:
    aufrufe = async_mock_service(hass, "test", "bild")
    fotos = async_mock_service(hass, "telegram_bot", "send_photo")
    entry = await _setup(hass, bild_aktion=AKTION)
    manager: LearnBuddyManager = entry.runtime_data
    aufgabe = await _mit_bild(entry)
    assert aufgabe.bild is not None

    await _frage(hass)
    assert not fotos
    assert not notify_calls
    daten = aufrufe[0].data
    assert daten["text"] == (
        "Hallo Max! 🔢 Mathe: a) Welches Land hat die meisten Ferientage?"
    )
    assert daten["datei"] == str(manager.bilder.ordner / aufgabe.bild)
    assert f"/api/learnbuddy/bilder/{aufgabe.bild}?authSig=" in daten["url"]
    assert daten["url"].startswith("http")


async def test_eigene_aktion_hat_vorrang_vor_telegram(hass: HomeAssistant) -> None:
    aufrufe = async_mock_service(hass, "test", "bild")
    fotos = async_mock_service(hass, "telegram_bot", "send_photo")
    eintrag = er.async_get(hass).async_get_or_create(
        "notify", "telegram_bot", "chat1", suggested_object_id="max_chat"
    )
    entry = await _setup(
        hass,
        notify_service=None,
        notify_target=None,
        notify_entity=eintrag.entity_id,
        bild_aktion=AKTION,
    )
    await _mit_bild(entry)
    await _frage(hass)
    assert len(aufrufe) == 1
    assert not fotos


async def test_ohne_bildweg_werden_bild_aufgaben_ausgelassen(
    hass: HomeAssistant, notify_calls: list[ServiceCall]
) -> None:
    entry = await _setup(hass)
    manager: LearnBuddyManager = entry.runtime_data
    assert not manager.messenger.kann_bilder(manager.kinder[KIND_ID])
    await _mit_bild(entry)

    # Only a task with an image: nothing can be asked
    with pytest.raises(ServiceValidationError) as fehler:
        await _frage(hass)
    assert fehler.value.translation_key == "keine_aufgaben"
    assert not notify_calls

    ohne = MatheAufgabe(fach_id=MATHE_ID, aufgabe="7 · 8", loesung="56")
    manager.task_stores[MATHE_ID].add(ohne)
    for _ in range(3):
        await _frage(hass)
        frage = manager.zustand(KIND_ID).offene_frage
        assert frage is not None
        assert frage.aufgabe_id == ohne.id
    assert notify_calls[-1].data["message"] == "Hallo Max! 🔢 Mathe: 7 · 8"


async def test_fehler_beim_bildversand(hass: HomeAssistant) -> None:
    async def _kaputt(call: ServiceCall) -> None:
        raise HomeAssistantError("Telegram nicht erreichbar")

    hass.services.async_register("telegram_bot", "send_photo", _kaputt)
    entry = await _telegram(hass)
    manager: LearnBuddyManager = entry.runtime_data
    aufgabe = await _mit_bild(entry)
    with pytest.raises(HomeAssistantError) as fehler:
        await _frage(hass)
    assert fehler.value.translation_key == "senden_fehlgeschlagen"
    assert manager.zustand(KIND_ID).offene_frage is None

    # A scheduled question does not raise, it reports the failure
    kind = manager.kinder[KIND_ID]
    assert await manager.messenger.async_send(kind, "Text", bild=aufgabe.bild) is False

    # The file of the image is gone
    assert aufgabe.bild is not None
    await manager.bilder.async_loesche([aufgabe.bild])
    with pytest.raises(HomeAssistantError):
        await manager.messenger.async_send_or_raise(kind, "Text", bild=aufgabe.bild)
