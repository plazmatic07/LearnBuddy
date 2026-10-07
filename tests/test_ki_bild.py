"""Tests for passing the image of a task to the AI."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, patch

from homeassistant.components import media_source
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.setup import async_setup_component
import pytest
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_mock_service,
)
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from custom_components.learnbuddy.ai import (
    AUFGABEN_SCHEMA,
    LOESUNG_SCHEMA,
    MATHE_SCHEMA,
    RECHENWEG_SCHEMA,
)
from custom_components.learnbuddy.const import DOMAIN
from custom_components.learnbuddy.manager import LearnBuddyManager
from custom_components.learnbuddy.models import MatheAufgabe, Verifikation

from .conftest import KIND_DATEN, KIND_ID, subentry
from .test_bilder import bild_daten
from .test_mathe_ablauf import GENERATE, MATHE_DATEN, MATHE_ID
from .test_websocket import Client

KI = "ai_task.test"


@pytest.fixture
async def entry(hass: HomeAssistant) -> MockConfigEntry:
    """Set up a Telegram child with a math subject and an AI entity."""
    async_mock_service(hass, "telegram_bot", "send_photo")
    async_mock_service(hass, "notify", "send_message")
    eintrag = er.async_get(hass).async_get_or_create(
        "notify", "telegram_bot", "chat1", suggested_object_id="max_chat"
    )
    kind = {
        k: v
        for k, v in KIND_DATEN.items()
        if k not in ("notify_service", "notify_target")
    } | {"notify_entity": eintrag.entity_id}
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        title="LearnBuddy",
        data={},
        options={"timeout_minuten": 60, "sprache": "de", "ki_entity": KI},
        subentries_data=[
            subentry("kind", KIND_ID, "Max", kind),
            subentry("fach", MATHE_ID, "Mathe (Max)", MATHE_DATEN),
        ],
    )
    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    return config_entry


def _sieht_bilder(hass: HomeAssistant, an: bool = True) -> None:
    """Set whether the AI entity accepts attachments."""
    hass.states.async_set(KI, "unknown", {"supported_features": 3 if an else 1})


async def _neu(
    entry: MockConfigEntry, aufgabe: str, loesung: str, **felder: Any
) -> MatheAufgabe:
    manager: LearnBuddyManager = entry.runtime_data
    bild = await manager.bilder.async_speichere(bild_daten())
    neu = MatheAufgabe(
        fach_id=MATHE_ID, aufgabe=aufgabe, loesung=loesung, bild=bild, **felder
    )
    manager.task_stores[MATHE_ID].add(neu)
    return neu


def _anhang(aufgabe: MatheAufgabe) -> list[dict[str, str]]:
    return [
        {
            "media_content_id": f"media-source://learnbuddy/{aufgabe.bild}",
            "media_content_type": "image/png",
        }
    ]


async def _frage(hass: HomeAssistant) -> None:
    await hass.services.async_call(
        DOMAIN, "ask_now", {"kind_id": KIND_ID}, blocking=True
    )


async def _antworte(hass: HomeAssistant, text: str) -> dict[str, Any]:
    ergebnis = await hass.services.async_call(
        DOMAIN,
        "submit_answer",
        {"kind_id": KIND_ID, "text": text},
        blocking=True,
        return_response=True,
    )
    assert isinstance(ergebnis, dict)
    return ergebnis


async def test_media_source(hass: HomeAssistant, entry: MockConfigEntry) -> None:
    assert await async_setup_component(hass, "media_source", {})
    manager: LearnBuddyManager = entry.runtime_data
    aufgabe = await _neu(entry, "a)", "1")
    assert aufgabe.bild is not None
    medium = await media_source.async_resolve_media(
        hass, f"media-source://learnbuddy/{aufgabe.bild}", None
    )
    assert medium.path == manager.bilder.ordner / aufgabe.bild
    assert medium.mime_type == "image/png"
    assert medium.url == f"/api/learnbuddy/bilder/{aufgabe.bild}"
    with pytest.raises(media_source.Unresolvable):
        await media_source.async_resolve_media(
            hass, "media-source://learnbuddy/" + "0" * 32 + ".png", None
        )
    # Nothing is offered for browsing
    wurzel = await media_source.async_browse_media(hass, "media-source://learnbuddy")
    assert not wurzel.children

    assert await hass.config_entries.async_unload(entry.entry_id)
    with pytest.raises(media_source.Unresolvable):
        await media_source.async_resolve_media(
            hass, f"media-source://learnbuddy/{aufgabe.bild}", None
        )


async def test_bewertung_und_rechenweg_mit_bild(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    _sieht_bilder(hass)
    manager: LearnBuddyManager = entry.runtime_data
    aufgabe = await _neu(entry, "a) Welches Land hat die meisten Ferientage?", "Türkei")

    await _frage(hass)
    with patch(GENERATE, AsyncMock(return_value={"ergebnis": "falsch"})) as generate:
        assert (await _antworte(hass, "Frankreich"))["ergebnis"] == "falsch"
    aufruf = generate.call_args.kwargs
    assert aufruf["structure"] is MATHE_SCHEMA
    assert aufruf["attachments"] == _anhang(aufgabe)
    assert "The attached image belongs to the task" in aufruf["instructions"]
    assert "Max" not in aufruf["instructions"]
    # The AI can see the diagram, so it may explain the solution
    assert manager.zustand(KIND_ID).rechenweg_angebot is not None

    schritte = {"schritte": ["Suche den höchsten Balken.", "Das ist TR, die Türkei."]}
    with patch(GENERATE, AsyncMock(return_value=schritte)) as generate:
        assert await _antworte(hass, "ja") == {"ergebnis": "rechenweg"}
    aufruf = generate.call_args.kwargs
    assert aufruf["structure"] is RECHENWEG_SCHEMA
    assert aufruf["attachments"] == _anhang(aufgabe)
    assert "The attached image belongs to the task" in aufruf["instructions"]
    assert aufgabe.rechenweg == [
        "Suche den höchsten Balken.",
        "Das ist TR, die Türkei.",
    ]


async def test_ki_ohne_bildunterstuetzung(
    hass: HomeAssistant, entry: MockConfigEntry
) -> None:
    _sieht_bilder(hass, an=False)
    manager: LearnBuddyManager = entry.runtime_data
    aufgabe = await _neu(entry, "a) Welches Land hat die meisten Ferientage?", "Türkei")

    await _frage(hass)
    with patch(GENERATE, AsyncMock(return_value={"ergebnis": "falsch"})) as generate:
        await _antworte(hass, "Frankreich")
    # The answer is judged against the solution alone
    aufruf = generate.call_args.kwargs
    assert aufruf["attachments"] is None
    assert "attached image" not in aufruf["instructions"]
    # Without seeing the image the AI would only guess the steps
    assert manager.zustand(KIND_ID).rechenweg_angebot is None

    # Stored steps are still offered
    aufgabe.rechenweg = ["Suche den höchsten Balken."]
    await _frage(hass)
    with patch(GENERATE, AsyncMock(return_value={"ergebnis": "falsch"})):
        await _antworte(hass, "Frankreich")
    assert manager.zustand(KIND_ID).rechenweg_angebot is not None

    # The entity does not exist at all
    hass.states.async_remove(KI)
    assert manager.ki.kann_bilder(KI) is False


async def test_nachrechnen_und_rechenwege_mit_bild(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = Client(await hass_ws_client(hass))
    manager: LearnBuddyManager = entry.runtime_data
    # The text alone would be a calculation, but the image belongs to it
    rechnung = await _neu(entry, "7 · 8", "54")
    text = await _neu(entry, "b) Wie viele Ferientage hat Italien?", "90")
    ids = [rechnung.id, text.id]

    async def _ki(hass: HomeAssistant, **kwargs: Any) -> Any:
        assert kwargs["attachments"] is not None
        assert "The attached image belongs to the task" in kwargs["instructions"]
        if kwargs["structure"] is LOESUNG_SCHEMA:
            return {"loesung": "90"}
        assert kwargs["structure"] is RECHENWEG_SCHEMA
        return {"schritte": ["Lies den Balken ab."]}

    # An AI that cannot see images cannot check these tasks
    _sieht_bilder(hass, an=False)
    with patch(GENERATE, AsyncMock(side_effect=_ki)) as generate:
        ergebnis = await client.ok("tasks/verify", fach_id=MATHE_ID, aufgabe_ids=ids)
        assert ergebnis == {"bestaetigt": 0, "abweichend": [], "nicht_pruefbar": 2}
        schritte = await client.ok(
            "tasks/generate_steps", fach_id=MATHE_ID, aufgabe_ids=ids
        )
        assert schritte["erzeugt"] == 0
        assert schritte["fehlgeschlagen"] == 2
    generate.assert_not_called()

    _sieht_bilder(hass)
    with patch(GENERATE, AsyncMock(side_effect=_ki)) as generate:
        ergebnis = await client.ok("tasks/verify", fach_id=MATHE_ID, aufgabe_ids=ids)
    assert generate.call_count == 2
    assert ergebnis["bestaetigt"] == 1
    assert [a["berechnet"] for a in ergebnis["abweichend"]] == ["90"]
    assert ergebnis["abweichend"][0]["durch"] == "ki"
    assert text.verifikation is Verifikation.KI
    assert rechnung.verifikation is Verifikation.ABWEICHUNG

    with patch(GENERATE, AsyncMock(side_effect=_ki)):
        schritte = await client.ok(
            "tasks/generate_steps", fach_id=MATHE_ID, aufgabe_ids=[text.id]
        )
    assert schritte["erzeugt"] == 1
    assert text.rechenweg == ["Lies den Balken ab."]

    # Tasks about an image are no examples for new tasks
    ohne = MatheAufgabe(fach_id=MATHE_ID, aufgabe="3 + 4", loesung="7")
    manager.task_stores[MATHE_ID].add(ohne)
    with patch(GENERATE, AsyncMock(return_value={"aufgaben": []})) as generate:
        await client.ok(
            "tasks/generate", fach_id=MATHE_ID, anzahl=2, beispiel_ids=[text.id]
        )
    aufruf = generate.call_args.kwargs
    assert aufruf["structure"] is AUFGABEN_SCHEMA
    assert aufruf["attachments"] is None
    assert "Ferientage" not in aufruf["instructions"]
    assert "- 3 + 4 → 7" in aufruf["instructions"]
