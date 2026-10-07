"""Fixtures for the LearnBuddy tests."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Any

from freezegun.api import FrozenDateTimeFactory
from homeassistant.config_entries import ConfigSubentryData
from homeassistant.core import HomeAssistant, ServiceCall
import pytest
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_mock_service,
)

from custom_components.learnbuddy.const import DOMAIN

KIND_ID = "kind1"
FACH_ID = "fach1"
ARBEIT_ID = "arbeit1"

KIND_DATEN: dict[str, Any] = {
    "name": "Max",
    "muttersprache": "de",
    "klassenstufe": 6,
    "schulart": "gymnasium",
    "bundesland": "rp",
    "notify_service": "test",
    "notify_target": ["491701234567"],
    "absender_kennung": "+49 170 1234567",
    "werktag_von": "15:00:00",
    "werktag_bis": "19:00:00",
    "wochenende_aktiv": False,
    "wochenende_von": "10:00:00",
    "wochenende_bis": "18:00:00",
}
FACH_DATEN: dict[str, Any] = {
    "kind_id": KIND_ID,
    "name": "Englisch",
    "typ": "vokabel",
    "sprachen": ["de", "en"],
}
ARBEIT_DATEN: dict[str, Any] = {
    "fach_id": FACH_ID,
    "art": "arbeit",
    "datum": "2026-10-09",
    "thema": "Unit 3",
    "lektionen": [],
    "abfragen_pro_tag": 2,
    "start_tage_vorher": 7,
    "intensivierung": False,
}

VOKABELN = "Hund; dog|hound; Nomen\ngehen; to go\n"


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations: None) -> None:
    """Enable loading of the custom integration in all tests."""


@pytest.fixture(autouse=True)
async def zeit(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory
) -> AsyncGenerator[None]:
    """Freeze the time at Tuesday 2026-10-06 08:00 in Berlin."""
    await hass.config.async_set_time_zone("Europe/Berlin")
    hass.config.language = "de"
    freezer.move_to("2026-10-06 08:00:00+02:00")
    yield
    # A reload started by the last step of a test must finish while the time
    # is still frozen, otherwise it leaves timers behind
    await hass.async_block_till_done()


@pytest.fixture(autouse=True)
def upload_ordner(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Store uploaded images in a temporary folder."""
    ordner = tmp_path / "uploads"
    monkeypatch.setattr(
        "custom_components.learnbuddy.bilder.UPLOAD_ORDNER", (str(ordner),)
    )
    return ordner


@pytest.fixture(autouse=True)
def ki_entitaet(hass: HomeAssistant) -> None:
    """Let the AI entity of the tests exist; it cannot read images by default."""
    hass.states.async_set("ai_task.test", "unknown", {"supported_features": 1})


@pytest.fixture
def notify_calls(hass: HomeAssistant) -> list[ServiceCall]:
    """Mock the legacy notify action used by the test child."""
    return async_mock_service(hass, "notify", "test")


def subentry(
    typ: str, sid: str, titel: str, daten: dict[str, Any]
) -> ConfigSubentryData:
    """Build the data of a subentry."""
    return ConfigSubentryData(
        data=daten, subentry_id=sid, subentry_type=typ, title=titel, unique_id=None
    )


@pytest.fixture
def config_entry(hass: HomeAssistant) -> MockConfigEntry:
    """Return a config entry with one child, one subject and one exam."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="LearnBuddy",
        data={},
        options={"timeout_minuten": 60, "sprache": "de"},
        subentries_data=[
            subentry("kind", KIND_ID, "Max", KIND_DATEN),
            subentry("fach", FACH_ID, "Englisch (Max)", FACH_DATEN),
            subentry(
                "arbeit", ARBEIT_ID, "2026-10-09 Englisch (Max): Unit 3", ARBEIT_DATEN
            ),
        ],
    )
    entry.add_to_hass(hass)
    return entry


@pytest.fixture
async def setup_entry(
    hass: HomeAssistant, config_entry: MockConfigEntry, notify_calls: list[ServiceCall]
) -> MockConfigEntry:
    """Set up the integration."""
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    return config_entry


@pytest.fixture
async def mit_vokabeln(
    hass: HomeAssistant, setup_entry: MockConfigEntry
) -> MockConfigEntry:
    """Set up the integration and import two words."""
    await hass.services.async_call(
        DOMAIN,
        "import_tasks",
        {"fach_id": FACH_ID, "inhalt": VOKABELN, "lektion": "Unit 3"},
        blocking=True,
    )
    return setup_entry
