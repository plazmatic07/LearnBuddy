"""The LearnBuddy integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.helpers import config_validation as cv

from .bilder import async_register_views
from .const import (
    CONF_FACH_ID,
    CONF_KIND_ID,
    DOMAIN,
    PLATFORMS,
    SUBENTRY_ARBEIT,
    SUBENTRY_FACH,
)
from .eingang import Eingang
from .manager import LearnBuddyManager
from .panel import async_register_panel, async_unregister_panel
from .services import async_setup_services
from .storage import ConfigStore, VerlaufStore, async_remove_task_file
from .websocket_api import async_setup_websocket_api

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.typing import ConfigType

type LearnBuddyConfigEntry = ConfigEntry[LearnBuddyManager]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the integration and register its actions."""
    async_setup_services(hass)
    async_setup_websocket_api(hass)
    return True


def _entferne_verwaiste_subentries(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Remove subjects without child and exams without subject."""
    for subentry in list(entry.subentries.values()):
        if (
            subentry.subentry_type == SUBENTRY_FACH
            and subentry.data[CONF_KIND_ID] not in entry.subentries
        ):
            hass.config_entries.async_remove_subentry(entry, subentry.subentry_id)
    for subentry in list(entry.subentries.values()):
        if (
            subentry.subentry_type == SUBENTRY_ARBEIT
            and subentry.data[CONF_FACH_ID] not in entry.subentries
        ):
            hass.config_entries.async_remove_subentry(entry, subentry.subentry_id)


async def async_setup_entry(hass: HomeAssistant, entry: LearnBuddyConfigEntry) -> bool:
    """Set up LearnBuddy from a config entry."""
    _entferne_verwaiste_subentries(hass, entry)

    manager = LearnBuddyManager(hass, entry)
    await manager.async_setup()
    entry.runtime_data = manager

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    await async_register_panel(hass)
    async_register_views(hass)
    entry.async_on_unload(lambda: async_unregister_panel(hass))
    manager.async_start()
    entry.async_on_unload(Eingang(hass, manager, entry.options).async_start())
    entry.async_on_unload(manager.async_stop)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def _async_update_listener(
    hass: HomeAssistant, entry: LearnBuddyConfigEntry
) -> None:
    """Apply changes of the entry.

    Exams are applied in place: reloading would remove the panel for a moment
    and throw the user out of it. Everything else reloads the entry.
    """
    manager = entry.runtime_data
    if manager.async_nur_arbeiten_geaendert():
        manager.async_arbeiten_aktualisieren()
        return
    hass.config_entries.async_schedule_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: LearnBuddyConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        await entry.runtime_data.async_flush()
    return unload_ok


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Delete all stored data when the integration is removed."""
    store = ConfigStore(hass)
    await store.async_load()
    for key in store.aufgaben_dateien:
        await async_remove_task_file(hass, key)
    await store.async_remove()
    await VerlaufStore(hass).async_remove()
