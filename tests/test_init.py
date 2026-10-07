"""Tests for setup, unload and removal."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import device_registry as dr, entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.learnbuddy.const import DOMAIN

from .conftest import (
    ARBEIT_DATEN,
    ARBEIT_ID,
    FACH_DATEN,
    FACH_ID,
    KIND_ID,
    subentry,
)

AUFGABEN_DATEI = f"learnbuddy.{KIND_ID}_{FACH_ID}"


async def test_setup_und_unload(
    hass: HomeAssistant, setup_entry: MockConfigEntry
) -> None:
    assert setup_entry.state is ConfigEntryState.LOADED
    for service in ("submit_answer", "ask_now", "import_tasks", "pause", "resume"):
        assert hass.services.has_service(DOMAIN, service)

    device = dr.async_get(hass).async_get_device_by_identifier(
        (DOMAIN, KIND_ID), setup_entry.entry_id
    )
    assert device is not None
    assert device.name == "Max"
    assert device.config_entries_subentries == {setup_entry.entry_id: {KIND_ID}}
    entities = er.async_entries_for_device(er.async_get(hass), device.id)
    assert {e.unique_id for e in entities} == {
        f"{KIND_ID}_naechste_arbeit",
        f"{KIND_ID}_trefferquote",
        f"{KIND_ID}_offene_frage",
        f"{KIND_ID}_abfragen_aktiv",
        f"{KIND_ID}_jetzt_abfragen",
        f"{KIND_ID}_arbeiten",
    }
    assert all(e.config_subentry_id == KIND_ID for e in entities)

    assert await hass.config_entries.async_unload(setup_entry.entry_id)
    assert setup_entry.state is ConfigEntryState.NOT_LOADED
    # Actions stay registered, they are set up with the integration
    assert hass.services.has_service(DOMAIN, "ask_now")


async def test_verwaiste_subentries_werden_entfernt(hass: HomeAssistant) -> None:
    entry = MockConfigEntry(
        domain=DOMAIN,
        options={},
        subentries_data=[
            subentry("fach", FACH_ID, "Englisch (?)", FACH_DATEN),
            subentry("arbeit", ARBEIT_ID, "x", ARBEIT_DATEN),
            subentry("arbeit", "arbeit2", "y", {**ARBEIT_DATEN, "fach_id": "weg"}),
        ],
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.subentries == {}
    assert entry.state is ConfigEntryState.LOADED


async def test_kind_entfernen(
    hass: HomeAssistant,
    mit_vokabeln: MockConfigEntry,
    hass_storage: dict[str, Any],
) -> None:
    await mit_vokabeln.runtime_data.async_flush()
    assert AUFGABEN_DATEI in hass_storage
    assert hass_storage["learnbuddy.config"]["data"]["aufgaben_dateien"] == [
        AUFGABEN_DATEI
    ]

    hass.config_entries.async_remove_subentry(mit_vokabeln, KIND_ID)
    await hass.async_block_till_done()

    assert mit_vokabeln.state is ConfigEntryState.LOADED
    assert mit_vokabeln.subentries == {}
    assert AUFGABEN_DATEI not in hass_storage
    daten = hass_storage["learnbuddy.config"]["data"]
    assert daten["kinder"] == {}
    assert daten["aufgaben_dateien"] == []
    assert (
        dr.async_get(hass).async_get_device_by_identifier(
            (DOMAIN, KIND_ID), mit_vokabeln.entry_id
        )
        is None
    )
    assert hass.states.get("switch.max_abfragen_aktiv") is None


async def test_integration_entfernen(
    hass: HomeAssistant,
    mit_vokabeln: MockConfigEntry,
    hass_storage: dict[str, Any],
) -> None:
    await mit_vokabeln.runtime_data.async_flush()
    assert await hass.config_entries.async_remove(mit_vokabeln.entry_id)
    await hass.async_block_till_done()
    assert AUFGABEN_DATEI not in hass_storage
    assert "learnbuddy.config" not in hass_storage


async def test_offene_frage_ohne_aufgabe_wird_verworfen(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    notify_calls: list[ServiceCall],
    hass_storage: dict[str, Any],
) -> None:
    hass_storage["learnbuddy.config"] = {
        "version": 1,
        "minor_version": 1,
        "key": "learnbuddy.config",
        "data": {
            "kinder": {
                KIND_ID: {
                    "offene_frage": {
                        "fach_id": FACH_ID,
                        "aufgabe_id": "gibtsnicht",
                        "richtung": "de>en",
                        "gestellt_um": "2026-10-05T14:00:00+00:00",
                        "timeout_um": "2026-10-05T15:00:00+00:00",
                    }
                },
                "altes_kind": {"aktiv": False},
            },
            "arbeiten": {},
            "aufgaben_dateien": ["learnbuddy.alt_alt"],
        },
    }
    hass_storage["learnbuddy.alt_alt"] = {
        "version": 1,
        "minor_version": 1,
        "key": "learnbuddy.alt_alt",
        "data": {"aufgaben": []},
    }
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    manager = config_entry.runtime_data
    assert manager.zustand(KIND_ID).offene_frage is None
    assert "altes_kind" not in manager.config_store.kinder
    assert "learnbuddy.alt_alt" not in hass_storage
    assert not notify_calls


async def test_arbeit_aendern_ohne_reload_kind_mit_reload(
    hass: HomeAssistant, setup_entry: MockConfigEntry
) -> None:
    manager = setup_entry.runtime_data
    arbeit = setup_entry.subentries[ARBEIT_ID]
    hass.config_entries.async_update_subentry(
        setup_entry, arbeit, data={**arbeit.data, "datum": "2026-10-13"}
    )
    await hass.async_block_till_done()
    assert setup_entry.runtime_data is manager
    assert manager.arbeiten[ARBEIT_ID].datum.isoformat() == "2026-10-13"
    assert hass.states.get("sensor.max_nachste_arbeit").state == "2026-10-13"

    kind = setup_entry.subentries[KIND_ID]
    hass.config_entries.async_update_subentry(
        setup_entry, kind, data={**kind.data, "name": "Moritz"}
    )
    await hass.async_block_till_done()
    assert setup_entry.runtime_data is not manager
    assert setup_entry.runtime_data.kinder[KIND_ID].name == "Moritz"
