"""Tests for the AI based evaluation."""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import AsyncMock, patch

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
import pytest
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_capture_events,
)

from custom_components.learnbuddy import ai
from custom_components.learnbuddy.ai import (
    BEWERTUNG_SCHEMA,
    KiBewerter,
    KiBewertung,
    baue_prompt,
    bereinige_erklaerung,
    parse_bewertung,
)
from custom_components.learnbuddy.const import DOMAIN
from custom_components.learnbuddy.manager import LearnBuddyManager
from custom_components.learnbuddy.models import Ergebnis

from .conftest import FACH_ID, KIND_ID

GENERATE = "custom_components.learnbuddy.ai._async_generate_data"
ARGS: dict[str, Any] = {
    "wort": "Hund",
    "loesung": "dog",
    "alternativen": ["hound"],
    "antwort": "doggy",
    "von": "de",
    "nach": "en",
    "erklaersprache": "de",
}


def _antwort(daten: Any) -> Any:
    return daten


@pytest.mark.parametrize(
    ("daten", "erwartet"),
    [
        ({"ergebnis": "richtig"}, KiBewertung(Ergebnis.RICHTIG)),
        (
            {"ergebnis": "fast_richtig", "erklaerung": " Fast!  "},
            KiBewertung(Ergebnis.FAST_RICHTIG, "Fast!"),
        ),
        (
            {"ergebnis": "falsch", "erklaerung": 5},
            KiBewertung(Ergebnis.FALSCH),
        ),
        ({"ergebnis": "unbeantwortet"}, None),
        ({"ergebnis": "super"}, None),
        ({"ergebnis": None}, None),
        ({"ergebnis": ["richtig"]}, None),
        ({}, None),
        ("richtig", None),
        (None, None),
    ],
)
def test_parse_bewertung(daten: Any, erwartet: KiBewertung | None) -> None:
    assert parse_bewertung(daten) == erwartet


def test_bereinige_erklaerung() -> None:
    assert bereinige_erklaerung("**Gut**\n<b>gemacht</b> `x`") == "Gut bgemacht/b x"
    assert bereinige_erklaerung("   ") is None
    assert bereinige_erklaerung("*_*") is None
    assert bereinige_erklaerung(None) is None
    lang = bereinige_erklaerung("a" * 500)
    assert lang is not None
    assert len(lang) == 200
    assert lang.endswith("…")


def test_prompt_und_schema() -> None:
    prompt = baue_prompt(**ARGS)
    assert "Word (German): Hund" in prompt
    assert "Expected translation (English): dog" in prompt
    assert "hound" in prompt
    assert "<answer>\ndoggy\n</answer>" in prompt
    assert "in German" in prompt
    ohne = baue_prompt(**{**ARGS, "alternativen": [], "antwort": "x" * 999})
    assert "Other accepted translations: -" in ohne
    assert "x" * 300 in ohne
    assert "x" * 301 not in ohne
    assert BEWERTUNG_SCHEMA({"ergebnis": "richtig"}) == {"ergebnis": "richtig"}


async def test_bewerter_gueltig(hass: HomeAssistant) -> None:
    with patch(
        GENERATE, AsyncMock(return_value=_antwort({"ergebnis": "richtig"}))
    ) as generate:
        ergebnis = await KiBewerter(hass).async_bewerte_vokabel("ai_task.x", **ARGS)
    assert ergebnis == KiBewertung(Ergebnis.RICHTIG)
    kwargs = generate.call_args.kwargs
    assert kwargs["entity_id"] == "ai_task.x"
    assert kwargs["structure"] is BEWERTUNG_SCHEMA
    assert "doggy" in kwargs["instructions"]


async def test_bewerter_fehler_wird_einmal_geloggt(
    hass: HomeAssistant, caplog: pytest.LogCaptureFixture
) -> None:
    bewerter = KiBewerter(hass)
    with patch(GENERATE, AsyncMock(side_effect=HomeAssistantError("kaputt"))):
        assert await bewerter.async_bewerte_vokabel("ai_task.x", **ARGS) is None
        assert await bewerter.async_bewerte_vokabel("ai_task.x", **ARGS) is None
    assert caplog.text.count("AI task via ai_task.x failed") == 1

    with patch(GENERATE, AsyncMock(return_value=_antwort({"ergebnis": "quatsch"}))):
        assert await bewerter.async_bewerte_vokabel("ai_task.x", **ARGS) is None
    assert caplog.text.count("AI task via ai_task.x failed") == 1

    with patch(GENERATE, AsyncMock(return_value=_antwort({"ergebnis": "falsch"}))):
        assert await bewerter.async_bewerte_vokabel("ai_task.x", **ARGS) is not None
    assert "AI task via ai_task.x works again" in caplog.text


async def test_bewerter_ungueltige_daten(
    hass: HomeAssistant, caplog: pytest.LogCaptureFixture
) -> None:
    with patch(GENERATE, AsyncMock(return_value=_antwort("kein dict"))):
        assert await KiBewerter(hass).async_bewerte_vokabel("ai_task.x", **ARGS) is None
    assert "invalid structured data" in caplog.text


async def test_bewerter_timeout(hass: HomeAssistant) -> None:
    async def _langsam(*_: Any, **__: Any) -> Any:
        await asyncio.sleep(10)
        return _antwort({"ergebnis": "richtig"})

    with patch(GENERATE, _langsam), patch.object(ai, "KI_TIMEOUT", 0):
        assert await KiBewerter(hass).async_bewerte_vokabel("ai_task.x", **ARGS) is None


# --- integration with the question cycle ------------------------------------


async def _frage_und_antwort(
    hass: HomeAssistant, entry: MockConfigEntry, antwort: str
) -> dict[str, Any]:
    await hass.services.async_call(
        DOMAIN, "ask_now", {"kind_id": KIND_ID}, blocking=True
    )
    ergebnis = await hass.services.async_call(
        DOMAIN,
        "submit_answer",
        {"kind_id": KIND_ID, "text": antwort},
        blocking=True,
        return_response=True,
    )
    await hass.async_block_till_done()
    assert isinstance(ergebnis, dict)
    return ergebnis


@pytest.fixture
async def mit_ki(hass: HomeAssistant, mit_vokabeln: MockConfigEntry) -> MockConfigEntry:
    """Enable the AI evaluation globally."""
    hass.config_entries.async_update_entry(
        mit_vokabeln, options={**mit_vokabeln.options, "ki_entity": "ai_task.test"}
    )
    await hass.async_block_till_done()
    await hass.services.async_call(
        DOMAIN,
        "import_tasks",
        {"fach_id": FACH_ID, "inhalt": "Hund; dog\ngehen; to go"},
        blocking=True,
    )
    return mit_vokabeln


async def test_ki_wertet_synonym_als_richtig(
    hass: HomeAssistant, mit_ki: MockConfigEntry, notify_calls: list[ServiceCall]
) -> None:
    manager: LearnBuddyManager = mit_ki.runtime_data
    bewertungen = async_capture_events(hass, "learnbuddy_answer_evaluated")
    antwort_ki = _antwort({"ergebnis": "richtig", "erklaerung": "Das passt auch."})
    with patch(GENERATE, AsyncMock(return_value=antwort_ki)) as generate:
        ergebnis = await _frage_und_antwort(hass, mit_ki, "ein Synonym")
    assert ergebnis["ergebnis"] == "richtig"
    assert ergebnis["bewertet_von"] == "ki"
    assert ergebnis["erklaerung"] == "Das passt auch."
    nachricht = notify_calls[-1].data["message"]
    assert nachricht.startswith("Richtig, Max!")
    assert "💡 Das passt auch.\n\nLust auf mehr?" in nachricht
    assert bewertungen[-1].data["bewertet_von"] == "ki"
    assert bewertungen[-1].data["ergebnis"] == "richtig"

    # No personal data in the prompt
    prompt = generate.call_args.kwargs["instructions"]
    assert "Max" not in prompt
    assert "1234567" not in prompt
    assert "gymnasium" not in prompt.lower()
    assert generate.call_args.kwargs["entity_id"] == "ai_task.test"

    stats = [
        stat
        for aufgabe in manager.task_stores[FACH_ID].aufgaben.values()
        for stat in aufgabe.statistik.values()
        if stat.richtig or stat.falsch
    ]
    assert [(s.richtig, s.falsch, s.box) for s in stats] == [(1, 0, 2)]


async def test_ki_bestaetigt_falsch(
    hass: HomeAssistant, mit_ki: MockConfigEntry, notify_calls: list[ServiceCall]
) -> None:
    with patch(GENERATE, AsyncMock(return_value=_antwort({"ergebnis": "falsch"}))):
        ergebnis = await _frage_und_antwort(hass, mit_ki, "quatsch")
    assert ergebnis["ergebnis"] == "falsch"
    assert ergebnis["bewertet_von"] == "ki"
    assert "erklaerung" not in ergebnis
    assert "💡" not in notify_calls[-1].data["message"]


async def test_ki_fehler_nutzt_lokales_ergebnis(
    hass: HomeAssistant, mit_ki: MockConfigEntry
) -> None:
    with patch(GENERATE, AsyncMock(side_effect=HomeAssistantError("kaputt"))):
        ergebnis = await _frage_und_antwort(hass, mit_ki, "quatsch")
    assert ergebnis["ergebnis"] == "falsch"
    assert ergebnis["bewertet_von"] == "lokal"


async def test_ki_wird_nur_bei_falsch_gefragt(
    hass: HomeAssistant, mit_ki: MockConfigEntry
) -> None:
    manager: LearnBuddyManager = mit_ki.runtime_data
    with patch(GENERATE, AsyncMock()) as generate:
        await hass.services.async_call(
            DOMAIN, "ask_now", {"kind_id": KIND_ID}, blocking=True
        )
        frage = manager.zustand(KIND_ID).offene_frage
        assert frage is not None
        aufgabe = manager.task_stores[FACH_ID].aufgaben[frage.aufgabe_id]
        loesung = aufgabe.frage[frage.richtung.split(">")[1]]
        ergebnis = await hass.services.async_call(
            DOMAIN,
            "submit_answer",
            {"kind_id": KIND_ID, "text": loesung},
            blocking=True,
            return_response=True,
        )
        assert ergebnis is not None
        assert ergebnis["bewertet_von"] == "lokal"
        # An empty answer is not sent to the AI either
        leer = await _frage_und_antwort(hass, mit_ki, "   ")
        assert leer["ergebnis"] == "falsch"
    generate.assert_not_called()


async def test_ohne_ki_entity_kein_aufruf(
    hass: HomeAssistant, mit_vokabeln: MockConfigEntry
) -> None:
    with patch(GENERATE, AsyncMock()) as generate:
        ergebnis = await _frage_und_antwort(hass, mit_vokabeln, "quatsch")
    assert ergebnis["bewertet_von"] == "lokal"
    generate.assert_not_called()
