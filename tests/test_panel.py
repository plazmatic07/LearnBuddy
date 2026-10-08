"""Tests for the sidebar panel."""

from __future__ import annotations

import re

from homeassistant.components.frontend import DATA_PANELS
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.typing import ClientSessionGenerator


async def test_panel_registrierung(
    hass: HomeAssistant, setup_entry: MockConfigEntry
) -> None:
    panel = hass.data[DATA_PANELS]["learnbuddy"]
    assert panel.require_admin is True
    assert panel.sidebar_title == "LearnBuddy"
    assert panel.sidebar_icon == "mdi:school"
    custom = panel.config["_panel_custom"]
    assert custom["name"] == "learnbuddy-panel"
    assert custom["embed_iframe"] is False
    # Version and checksum of the bundle make browsers load a changed file
    assert re.fullmatch(
        r"/learnbuddy_static/learnbuddy-panel\.js\?v=\d+\.\d+\.\d+-[0-9a-f]{8}",
        custom["module_url"],
    )
    # The panel learns which bundle is current and can ask for a reload
    version = setup_entry.runtime_data.verwaltung.uebersicht()["panel_version"]
    assert custom["module_url"].endswith(f"?v={version}")

    assert await hass.config_entries.async_unload(setup_entry.entry_id)
    assert "learnbuddy" not in hass.data[DATA_PANELS]

    # Setting up again must not fail although the static path already exists
    assert await hass.config_entries.async_setup(setup_entry.entry_id)
    await hass.async_block_till_done()
    assert "learnbuddy" in hass.data[DATA_PANELS]


async def test_panel_datei_wird_ausgeliefert(
    hass: HomeAssistant,
    setup_entry: MockConfigEntry,
    hass_client: ClientSessionGenerator,
) -> None:
    client = await hass_client()
    antwort = await client.get("/learnbuddy_static/learnbuddy-panel.js")
    assert antwort.status == 200
    assert "javascript" in antwort.headers["Content-Type"]


def test_bundle_registriert_alle_elemente() -> None:
    """The built panel defines all of its custom elements."""
    from pathlib import Path  # noqa: PLC0415

    bundle = (
        Path(__file__).parent.parent
        / "custom_components/learnbuddy/frontend/learnbuddy-panel.js"
    ).read_text(encoding="utf-8")
    for element in ("learnbuddy-panel", "lh-uebersicht", "lh-fortschritt"):
        assert f'customElements.define("{element}"' in bundle
