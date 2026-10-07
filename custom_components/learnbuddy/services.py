"""Actions of the LearnBuddy integration."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.core import (
    HomeAssistant,
    ServiceCall,
    ServiceResponse,
    SupportsResponse,
    callback,
)
from homeassistant.exceptions import ServiceValidationError
from homeassistant.helpers import config_validation as cv, device_registry as dr
import voluptuous as vol

from .const import (
    ATTR_ABSENDER,
    ATTR_ANZAHL,
    ATTR_BESCHREIBUNG,
    ATTR_BIS,
    ATTR_DEVICE_ID,
    ATTR_FACH,
    ATTR_FACH_ID,
    ATTR_GEPRUEFT,
    ATTR_INHALT,
    ATTR_KIND_ID,
    ATTR_LEKTION,
    ATTR_SCHWIERIGKEIT,
    ATTR_TEXT,
    ATTR_TRENNZEICHEN,
    DOMAIN,
    SERVICE_ASK_NOW,
    SERVICE_GENERATE_TASKS,
    SERVICE_IMPORT_TASKS,
    SERVICE_PAUSE,
    SERVICE_RESUME,
    SERVICE_SUBMIT_ANSWER,
)
from .eingang import QUELLE_AKTION
from .verwaltung import VerwaltungError

if TYPE_CHECKING:
    from .manager import LearnBuddyManager

_KIND_FELDER: dict[vol.Marker, Any] = {
    vol.Optional(ATTR_KIND_ID): cv.string,
    vol.Optional(ATTR_DEVICE_ID): cv.string,
}

SUBMIT_ANSWER_SCHEMA = vol.Schema(
    {
        **_KIND_FELDER,
        vol.Optional(ATTR_ABSENDER): vol.Coerce(str),
        vol.Required(ATTR_TEXT): vol.Coerce(str),
    }
)
KIND_SCHEMA = vol.Schema(_KIND_FELDER)
PAUSE_SCHEMA = vol.Schema({**_KIND_FELDER, vol.Optional(ATTR_BIS): cv.datetime})
IMPORT_TASKS_SCHEMA = vol.Schema(
    {
        **_KIND_FELDER,
        vol.Optional(ATTR_FACH): cv.string,
        vol.Optional(ATTR_FACH_ID): cv.string,
        vol.Required(ATTR_INHALT): cv.string,
        vol.Optional(ATTR_LEKTION): cv.string,
        vol.Optional(ATTR_TRENNZEICHEN): str,
        vol.Optional(ATTR_GEPRUEFT, default=True): cv.boolean,
    }
)


_FACH_FELDER: dict[vol.Marker, Any] = {
    **_KIND_FELDER,
    vol.Optional(ATTR_FACH): cv.string,
    vol.Optional(ATTR_FACH_ID): cv.string,
}
GENERATE_TASKS_SCHEMA = vol.Schema(
    {
        **_FACH_FELDER,
        vol.Required(ATTR_ANZAHL): vol.All(vol.Coerce(int), vol.Range(min=1, max=20)),
        vol.Optional(ATTR_LEKTION): cv.string,
        vol.Optional(ATTR_SCHWIERIGKEIT): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=5)
        ),
        vol.Optional(ATTR_BESCHREIBUNG): cv.string,
    }
)


def _fehler(schluessel: str) -> ServiceValidationError:
    return ServiceValidationError(translation_domain=DOMAIN, translation_key=schluessel)


def _manager(hass: HomeAssistant) -> LearnBuddyManager:
    """Return the manager of the loaded config entry."""
    entries = hass.config_entries.async_loaded_entries(DOMAIN)
    if not entries:
        raise _fehler("nicht_geladen")
    manager: LearnBuddyManager = entries[0].runtime_data
    return manager


def _kind_id(
    hass: HomeAssistant, manager: LearnBuddyManager, daten: dict[str, Any]
) -> str:
    """Resolve the child of an action call."""
    kind_id: str | None = None
    if ATTR_KIND_ID in daten:
        kind_id = daten[ATTR_KIND_ID]
    elif ATTR_DEVICE_ID in daten:
        device = dr.async_get(hass).async_get(daten[ATTR_DEVICE_ID])
        if device is not None:
            kind_id = next(
                (wert for domain, wert in device.identifiers if domain == DOMAIN),
                None,
            )
    elif ATTR_ABSENDER in daten:
        kind = manager.kind_per_absender(daten[ATTR_ABSENDER])
        kind_id = None if kind is None else kind.id
    else:
        raise _fehler("kind_fehlt")
    if kind_id is None or kind_id not in manager.kinder:
        raise _fehler("kind_unbekannt")
    return kind_id


DOPPELT = "doppelt"


async def _async_submit_answer(call: ServiceCall) -> ServiceResponse:
    manager = _manager(call.hass)
    kind_id = _kind_id(call.hass, manager, call.data)
    antwort: str = call.data[ATTR_TEXT]
    if manager.antwort_doppelt(kind_id, antwort.strip(), QUELLE_AKTION):
        # The built-in listener already took this message
        return {"ergebnis": DOPPELT}
    return await manager.async_antwort(kind_id, antwort)


async def _async_ask_now(call: ServiceCall) -> None:
    manager = _manager(call.hass)
    await manager.async_frage_stellen(_kind_id(call.hass, manager, call.data))


async def _async_pause(call: ServiceCall) -> None:
    manager = _manager(call.hass)
    kind_id = _kind_id(call.hass, manager, call.data)
    manager.async_set_aktiv(kind_id, aktiv=False, bis=call.data.get(ATTR_BIS))


async def _async_resume(call: ServiceCall) -> None:
    manager = _manager(call.hass)
    manager.async_set_aktiv(_kind_id(call.hass, manager, call.data), aktiv=True)


def _fach_id(call: ServiceCall, manager: LearnBuddyManager) -> str:
    """Resolve the subject of an action call."""
    if ATTR_FACH_ID in call.data:
        fach_id: str = call.data[ATTR_FACH_ID]
        if fach_id not in manager.faecher:
            raise _fehler("fach_unbekannt")
        return fach_id
    kind_id = _kind_id(call.hass, manager, call.data)
    fach = manager.fach_per_name(kind_id, call.data.get(ATTR_FACH, ""))
    if fach is None:
        raise _fehler("fach_unbekannt")
    return fach.id


async def _async_generate_tasks(call: ServiceCall) -> ServiceResponse:
    manager = _manager(call.hass)
    fach_id = _fach_id(call, manager)
    try:
        ergebnis = await manager.verwaltung.generiere(
            fach_id,
            anzahl=call.data[ATTR_ANZAHL],
            lektion=call.data.get(ATTR_LEKTION),
            schwierigkeit=call.data.get(ATTR_SCHWIERIGKEIT),
            beschreibung=call.data.get(ATTR_BESCHREIBUNG),
        )
    except VerwaltungError as err:
        raise _fehler(err.schluessel) from err
    return {k: v for k, v in ergebnis.items() if k != "aufgabe_ids"}


async def _async_import_tasks(call: ServiceCall) -> ServiceResponse:
    manager = _manager(call.hass)
    fach_id = _fach_id(call, manager)
    return manager.async_importiere(
        fach_id,
        call.data[ATTR_INHALT],
        lektion=call.data.get(ATTR_LEKTION),
        trennzeichen=call.data.get(ATTR_TRENNZEICHEN),
        geprueft=call.data[ATTR_GEPRUEFT],
    )


@callback
def async_setup_services(hass: HomeAssistant) -> None:
    """Register the actions of the integration."""
    hass.services.async_register(
        DOMAIN,
        SERVICE_SUBMIT_ANSWER,
        _async_submit_answer,
        schema=SUBMIT_ANSWER_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(
        DOMAIN, SERVICE_ASK_NOW, _async_ask_now, schema=KIND_SCHEMA
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_GENERATE_TASKS,
        _async_generate_tasks,
        schema=GENERATE_TASKS_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )
    hass.services.async_register(
        DOMAIN, SERVICE_PAUSE, _async_pause, schema=PAUSE_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_RESUME, _async_resume, schema=KIND_SCHEMA
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_IMPORT_TASKS,
        _async_import_tasks,
        schema=IMPORT_TASKS_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL,
    )
