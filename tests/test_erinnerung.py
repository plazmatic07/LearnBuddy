"""Tests for the timeout, the reminder and the pause of an open question."""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from typing import Any

from freezegun.api import FrozenDateTimeFactory
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.util import dt as dt_util
import pytest
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_fire_time_changed,
)

from custom_components.learnbuddy.const import DOMAIN
from custom_components.learnbuddy.manager import LearnBuddyManager

from .conftest import FACH_ID, KIND_ID, VOKABELN

Starte = Callable[..., Coroutine[Any, Any, LearnBuddyManager]]


@pytest.fixture
def starte(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    notify_calls: list[ServiceCall],
) -> Starte:
    """Set up the integration with the given options and two words."""

    async def _starte(**optionen: Any) -> LearnBuddyManager:
        hass.config_entries.async_update_entry(
            config_entry, options={**config_entry.options, **optionen}
        )
        assert await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done()
        await hass.services.async_call(
            DOMAIN,
            "import_tasks",
            {"fach_id": FACH_ID, "inhalt": VOKABELN, "lektion": "Unit 3"},
            blocking=True,
        )
        manager: LearnBuddyManager = config_entry.runtime_data
        return manager

    return _starte


async def _zeit(hass: HomeAssistant, freezer: FrozenDateTimeFactory, wann: str) -> None:
    freezer.move_to(wann)
    async_fire_time_changed(hass)
    await hass.async_block_till_done()


async def test_timeout_null_laeuft_nie_ab(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory, starte: Starte
) -> None:
    manager = await starte(timeout_minuten=0)
    await _zeit(hass, freezer, "2026-10-06 16:00:01+02:00")
    frage = manager.zustand(KIND_ID).offene_frage
    assert frage is not None
    assert frage.timeout_um is None

    await _zeit(hass, freezer, "2026-10-08 12:00:00+02:00")
    assert manager.zustand(KIND_ID).offene_frage is frage


async def test_erinnerung_einmal_dann_timeout(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    starte: Starte,
    notify_calls: list[ServiceCall],
) -> None:
    manager = await starte(erinnerung_minuten=20)
    await _zeit(hass, freezer, "2026-10-06 16:00:01+02:00")
    frage = manager.zustand(KIND_ID).offene_frage
    assert frage is not None
    anzahl = len(notify_calls)
    frage_text = notify_calls[-1].data["message"]

    await _zeit(hass, freezer, "2026-10-06 16:19:00+02:00")
    assert len(notify_calls) == anzahl

    await _zeit(hass, freezer, "2026-10-06 16:20:02+02:00")
    assert len(notify_calls) == anzahl + 1
    erinnerung = notify_calls[-1].data["message"]
    assert erinnerung.startswith("Hey Max, du hast noch eine offene Aufgabe:\n\n")
    wort = frage_text.split("„")[1].split("“")[0]
    assert wort in erinnerung
    assert manager.zustand(KIND_ID).offene_frage is frage

    # Only one reminder, the timeout still applies
    await _zeit(hass, freezer, "2026-10-06 16:50:00+02:00")
    assert len(notify_calls) == anzahl + 1
    await _zeit(hass, freezer, "2026-10-06 17:00:02+02:00")
    assert manager.zustand(KIND_ID).offene_frage is None
    assert notify_calls[-1].data["message"].startswith("Die Zeit ist um, Max.")


async def test_keine_erinnerung_nach_dem_timeout(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    starte: Starte,
    notify_calls: list[ServiceCall],
) -> None:
    manager = await starte(erinnerung_minuten=90)
    await _zeit(hass, freezer, "2026-10-06 16:00:01+02:00")
    frage = manager.zustand(KIND_ID).offene_frage
    assert frage is not None
    assert frage.erinnerung_um is None


async def test_erinnerung_ohne_timeout(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    starte: Starte,
    notify_calls: list[ServiceCall],
) -> None:
    manager = await starte(timeout_minuten=0, erinnerung_minuten=30)
    await _zeit(hass, freezer, "2026-10-06 16:00:01+02:00")
    anzahl = len(notify_calls)
    await _zeit(hass, freezer, "2026-10-06 16:30:02+02:00")
    assert len(notify_calls) == anzahl + 1
    assert manager.zustand(KIND_ID).offene_frage is not None


async def test_pause_haelt_die_zeit_an(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    starte: Starte,
    notify_calls: list[ServiceCall],
) -> None:
    manager = await starte(erinnerung_minuten=20)
    await _zeit(hass, freezer, "2026-10-06 16:00:01+02:00")
    assert manager.zustand(KIND_ID).offene_frage is not None
    anzahl = len(notify_calls)

    # Paused after 10 minutes: 10 minutes to the reminder, 50 to the timeout
    await _zeit(hass, freezer, "2026-10-06 16:10:01+02:00")
    manager.async_set_aktiv(KIND_ID, False)
    await hass.async_block_till_done()
    assert manager.zustand(KIND_ID).offene_frage.angehalten_seit is not None

    await _zeit(hass, freezer, "2026-10-07 10:00:00+02:00")
    frage = manager.zustand(KIND_ID).offene_frage
    assert frage is not None
    assert len(notify_calls) == anzahl

    manager.async_set_aktiv(KIND_ID, True)
    await hass.async_block_till_done()
    assert frage.angehalten_seit is None
    assert frage.erinnerung_um == dt_util.parse_datetime("2026-10-07 10:10:00+02:00")
    assert frage.timeout_um == dt_util.parse_datetime("2026-10-07 10:50:00+02:00")

    await _zeit(hass, freezer, "2026-10-07 10:10:01+02:00")
    assert len(notify_calls) == anzahl + 1
    await _zeit(hass, freezer, "2026-10-07 10:49:00+02:00")
    assert manager.zustand(KIND_ID).offene_frage is not None
    await _zeit(hass, freezer, "2026-10-07 10:50:02+02:00")
    assert manager.zustand(KIND_ID).offene_frage is None


async def test_pause_bis_setzt_von_selbst_fort(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory, starte: Starte
) -> None:
    manager = await starte()
    await _zeit(hass, freezer, "2026-10-06 16:00:01+02:00")
    await _zeit(hass, freezer, "2026-10-06 16:30:01+02:00")
    manager.async_set_aktiv(
        KIND_ID, True, bis=dt_util.parse_datetime("2026-10-06 22:00:00+02:00")
    )
    await hass.async_block_till_done()

    await _zeit(hass, freezer, "2026-10-06 21:59:00+02:00")
    frage = manager.zustand(KIND_ID).offene_frage
    assert frage is not None
    assert frage.angehalten_seit is not None

    # Paused for 5.5 hours, 30 minutes of the hour were left
    await _zeit(hass, freezer, "2026-10-06 22:00:01+02:00")
    assert frage.angehalten_seit is None
    assert frage.timeout_um == dt_util.parse_datetime("2026-10-06 22:30:01+02:00")
    await _zeit(hass, freezer, "2026-10-06 22:30:03+02:00")
    assert manager.zustand(KIND_ID).offene_frage is None
