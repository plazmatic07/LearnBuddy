"""Diagnostics of the LearnBuddy integration."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.diagnostics import async_redact_data

from .const import (
    CONF_ABSENDER_KENNUNG,
    CONF_BILD_AKTION,
    CONF_KALENDER_ENTITY,
    CONF_KALENDER_UID,
    CONF_NAME,
    CONF_NOTIFY_DATA,
    CONF_NOTIFY_ENTITY,
    CONF_NOTIFY_SERVICE,
    CONF_NOTIFY_TARGET,
    CONF_THEMA,
)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from . import LearnBuddyConfigEntry

# Titles of subentries contain the name of the child
TO_REDACT = {
    CONF_NAME,
    CONF_ABSENDER_KENNUNG,
    CONF_NOTIFY_ENTITY,
    CONF_NOTIFY_SERVICE,
    CONF_NOTIFY_TARGET,
    CONF_NOTIFY_DATA,
    CONF_BILD_AKTION,
    CONF_KALENDER_ENTITY,
    CONF_KALENDER_UID,
    CONF_THEMA,
    "title",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: LearnBuddyConfigEntry
) -> dict[str, Any]:
    """Return diagnostics without personal data and without task contents."""
    manager = entry.runtime_data
    kinder: dict[str, Any] = {}
    for kind_id in manager.kinder:
        zustand = manager.zustand(kind_id)
        naechste = manager.naechste_abfrage.get(kind_id)
        kinder[kind_id] = {
            "aktiv": zustand.aktiv,
            "pausiert_bis": (
                None
                if zustand.pausiert_bis is None
                else zustand.pausiert_bis.isoformat()
            ),
            "offene_frage": zustand.offene_frage is not None,
            "letzte_frage_um": (
                None
                if zustand.letzte_frage_um is None
                else zustand.letzte_frage_um.isoformat()
            ),
            "naechste_abfrage": None if naechste is None else naechste.isoformat(),
            "faecher": len(manager.faecher_von(kind_id)),
            "arbeiten": len(manager.arbeiten_von(kind_id)),
        }
    faecher: dict[str, Any] = {}
    for fach_id, fach in manager.faecher.items():
        aufgaben = manager.task_stores[fach_id].aufgaben.values()
        faecher[fach_id] = {
            "typ": fach.typ.value,
            "sprachen": list(fach.sprachen),
            "aufgaben": len(aufgaben),
            "geprueft": sum(1 for a in aufgaben if a.geprueft),
            "lektionen": len(manager.lektionen(fach_id)),
        }
    return {
        "entry": async_redact_data(entry.as_dict(), TO_REDACT),
        "kinder": kinder,
        "faecher": faecher,
    }
