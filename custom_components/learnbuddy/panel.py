"""Sidebar panel of the LearnBuddy integration."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import TYPE_CHECKING

from homeassistant.components import frontend, panel_custom
from homeassistant.components.http.server import StaticPathConfig
from homeassistant.core import callback
from homeassistant.loader import async_get_integration
from homeassistant.util.hass_dict import HassKey

from .const import DOMAIN

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

PANEL_URL_PATH = DOMAIN
PANEL_COMPONENT = "learnbuddy-panel"
PANEL_TITLE = "LearnBuddy"
PANEL_ICON = "mdi:school"
STATIC_URL = "/learnbuddy_static"
FRONTEND_DIR = Path(__file__).parent / "frontend"
PANEL_FILE = "learnbuddy-panel.js"

DATA_STATIC_REGISTERED: HassKey[bool] = HassKey(f"{DOMAIN}_static_registered")
DATA_PANEL_VERSION: HassKey[str] = HassKey(f"{DOMAIN}_panel_version")


def _pruefsumme() -> str:
    """Return a short checksum of the panel bundle."""
    inhalt = (FRONTEND_DIR / PANEL_FILE).read_bytes()
    return hashlib.sha256(inhalt).hexdigest()[:8]


async def async_register_panel(hass: HomeAssistant) -> None:
    """Serve the panel files and add the panel to the sidebar (admins only)."""
    if not hass.data.get(DATA_STATIC_REGISTERED):
        # Static paths cannot be removed, so this happens once per run
        await hass.http.async_register_static_paths(
            [StaticPathConfig(STATIC_URL, str(FRONTEND_DIR), cache_headers=False)]
        )
        hass.data[DATA_STATIC_REGISTERED] = True

    integration = await async_get_integration(hass, DOMAIN)
    # The content is part of the address, so that browsers load a changed
    # bundle even if the version stayed the same
    pruefsumme = await hass.async_add_executor_job(_pruefsumme)
    version = f"{integration.version}-{pruefsumme}"
    # An open panel compares this with what it loaded and asks for a reload
    hass.data[DATA_PANEL_VERSION] = version
    await panel_custom.async_register_panel(
        hass,
        frontend_url_path=PANEL_URL_PATH,
        webcomponent_name=PANEL_COMPONENT,
        sidebar_title=PANEL_TITLE,
        sidebar_icon=PANEL_ICON,
        module_url=f"{STATIC_URL}/{PANEL_FILE}?v={version}",
        embed_iframe=False,
        require_admin=True,
    )


@callback
def panel_version(hass: HomeAssistant) -> str | None:
    """Return the version of the panel bundle that is served right now."""
    return hass.data.get(DATA_PANEL_VERSION)


@callback
def async_unregister_panel(hass: HomeAssistant) -> None:
    """Remove the panel from the sidebar."""
    frontend.async_remove_panel(hass, PANEL_URL_PATH, warn_if_unknown=False)
