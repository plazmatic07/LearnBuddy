"""Tests for the actions."""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import device_registry as dr
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry
import voluptuous as vol

from custom_components.learnbuddy.const import DOMAIN
from custom_components.learnbuddy.manager import LearnBuddyManager

from .conftest import FACH_ID, KIND_ID


async def _importiere(hass: HomeAssistant, **daten: Any) -> dict[str, Any]:
    ergebnis = await hass.services.async_call(
        DOMAIN, "import_tasks", daten, blocking=True, return_response=True
    )
    assert isinstance(ergebnis, dict)
    return ergebnis


async def test_nicht_geladen(hass: HomeAssistant, setup_entry: MockConfigEntry) -> None:
    assert await hass.config_entries.async_unload(setup_entry.entry_id)
    with pytest.raises(ServiceValidationError) as fehler:
        await hass.services.async_call(
            DOMAIN, "ask_now", {"kind_id": KIND_ID}, blocking=True
        )
    assert fehler.value.translation_key == "nicht_geladen"


@pytest.mark.parametrize(
    ("daten", "schluessel"),
    [
        ({}, "kind_fehlt"),
        ({"kind_id": "gibtsnicht"}, "kind_unbekannt"),
        ({"device_id": "gibtsnicht"}, "kind_unbekannt"),
        ({"absender": "999"}, "kind_unbekannt"),
        ({"absender": " "}, "kind_unbekannt"),
    ],
)
async def test_kind_nicht_gefunden(
    hass: HomeAssistant,
    setup_entry: MockConfigEntry,
    daten: dict[str, Any],
    schluessel: str,
) -> None:
    with pytest.raises(ServiceValidationError) as fehler:
        await hass.services.async_call(
            DOMAIN, "submit_answer", {**daten, "text": "x"}, blocking=True
        )
    assert fehler.value.translation_key == schluessel


async def test_kind_per_device_und_absender(
    hass: HomeAssistant,
    mit_vokabeln: MockConfigEntry,
    notify_calls: list[ServiceCall],
) -> None:
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    device = dr.async_get(hass).async_get_device_by_identifier(
        (DOMAIN, KIND_ID), mit_vokabeln.entry_id
    )
    assert device is not None
    await hass.services.async_call(
        DOMAIN, "ask_now", {"device_id": device.id}, blocking=True
    )
    assert manager.zustand(KIND_ID).offene_frage is not None

    # Chat IDs may arrive as numbers
    ergebnis = await hass.services.async_call(
        DOMAIN,
        "submit_answer",
        {"absender": 491701234567, "text": "x"},
        blocking=True,
        return_response=True,
    )
    assert ergebnis is not None
    assert ergebnis["ergebnis"] == "falsch"


async def test_submit_answer_ohne_text(
    hass: HomeAssistant, setup_entry: MockConfigEntry
) -> None:
    with pytest.raises(vol.Invalid):
        await hass.services.async_call(
            DOMAIN, "submit_answer", {"kind_id": KIND_ID}, blocking=True
        )


async def test_import(hass: HomeAssistant, setup_entry: MockConfigEntry) -> None:
    manager: LearnBuddyManager = setup_entry.runtime_data
    inhalt = (
        "# Unit 3\n"
        "Hund; dog|hound; Nomen\n"
        "\n"
        "gehen; to go\n"
        "kaputt\n"
        "der Hund; The Dog\n"
        ";leer\n"
    )
    ergebnis = await _importiere(
        hass, fach_id=FACH_ID, inhalt=inhalt, lektion=" Unit 3 "
    )
    assert ergebnis == {"importiert": 2, "uebersprungen": 1, "fehlerzeilen": [5, 7]}

    aufgaben = list(manager.task_stores[FACH_ID].aufgaben.values())
    assert len(aufgaben) == 2
    hund = aufgaben[0]
    assert hund.frage == {"de": "Hund", "en": "dog"}
    assert hund.alternativen == {"en": ["hound"]}
    assert hund.hinweis == "Nomen"
    assert hund.lektion == "Unit 3"
    assert hund.quelle == "manuell"
    assert hund.geprueft is True
    assert aufgaben[1].alternativen == {}
    assert manager.lektionen(FACH_ID) == ["Unit 3"]

    # Importing the same content again adds nothing
    ergebnis = await _importiere(hass, fach_id=FACH_ID, inhalt="Hund;dog")
    assert ergebnis == {"importiert": 0, "uebersprungen": 1, "fehlerzeilen": []}


async def test_import_per_kind_und_fachname(
    hass: HomeAssistant, setup_entry: MockConfigEntry
) -> None:
    manager: LearnBuddyManager = setup_entry.runtime_data
    ergebnis = await _importiere(
        hass,
        kind_id=KIND_ID,
        fach=" englisch ",
        inhalt="Katze = cat",
        trennzeichen="=",
        geprueft=False,
    )
    assert ergebnis["importiert"] == 1
    aufgabe = next(iter(manager.task_stores[FACH_ID].aufgaben.values()))
    assert aufgabe.geprueft is False
    assert aufgabe.lektion is None


@pytest.mark.parametrize(
    ("daten", "schluessel"),
    [
        ({"fach_id": "gibtsnicht", "inhalt": "a;b"}, "fach_unbekannt"),
        ({"kind_id": KIND_ID, "fach": "Mathe", "inhalt": "a;b"}, "fach_unbekannt"),
        ({"kind_id": KIND_ID, "inhalt": "a;b"}, "fach_unbekannt"),
        ({"inhalt": "a;b"}, "kind_fehlt"),
        ({"fach_id": FACH_ID, "inhalt": "# nur Kommentar\nkaputt"}, "import_leer"),
    ],
)
async def test_import_fehler(
    hass: HomeAssistant,
    setup_entry: MockConfigEntry,
    daten: dict[str, Any],
    schluessel: str,
) -> None:
    with pytest.raises(ServiceValidationError) as fehler:
        await _importiere(hass, **daten)
    assert fehler.value.translation_key == schluessel
