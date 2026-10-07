"""Sensors of the LearnBuddy integration."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE

from .entity import LearnBuddyEntity

if TYPE_CHECKING:
    from datetime import date

    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

    from . import LearnBuddyConfigEntry
    from .manager import LearnBuddyManager
    from .models import Kind

PARALLEL_UPDATES = 0

FRAGE_KEINE = "keine"
FRAGE_OFFEN = "offen"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: LearnBuddyConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the sensors of all children."""
    manager = entry.runtime_data
    for kind in manager.kinder.values():
        async_add_entities(
            [
                NaechsteArbeitSensor(manager, kind),
                TrefferquoteSensor(manager, kind),
                OffeneFrageSensor(manager, kind),
            ],
            config_subentry_id=kind.id,
        )


class NaechsteArbeitSensor(LearnBuddyEntity, SensorEntity):
    """Date of the next exam of a child."""

    _attr_device_class = SensorDeviceClass.DATE

    def __init__(self, manager: LearnBuddyManager, kind: Kind) -> None:
        """Initialize the sensor."""
        super().__init__(manager, kind, "naechste_arbeit")

    @property
    def native_value(self) -> date | None:
        """Return the date of the next exam."""
        arbeit = self._manager.naechste_arbeit(self._kind.id)
        return None if arbeit is None else arbeit.datum

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return details of the next exam."""
        arbeit = self._manager.naechste_arbeit(self._kind.id)
        if arbeit is None:
            return None
        return {
            "thema": arbeit.thema,
            "art": arbeit.art.value,
            "fach": self._manager.faecher[arbeit.fach_id].name,
        }


class TrefferquoteSensor(LearnBuddyEntity, SensorEntity):
    """Share of correct answers of a child."""

    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_suggested_display_precision = 0

    def __init__(self, manager: LearnBuddyManager, kind: Kind) -> None:
        """Initialize the sensor."""
        super().__init__(manager, kind, "trefferquote")

    @property
    def native_value(self) -> float | None:
        """Return the share of correct answers in percent."""
        return self._manager.trefferquote(self._kind.id)


class OffeneFrageSensor(LearnBuddyEntity, SensorEntity):
    """Whether a child has an open question."""

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = [FRAGE_KEINE, FRAGE_OFFEN]

    def __init__(self, manager: LearnBuddyManager, kind: Kind) -> None:
        """Initialize the sensor."""
        super().__init__(manager, kind, "offene_frage")

    @property
    def native_value(self) -> str:
        """Return whether a question is open."""
        frage = self._manager.zustand(self._kind.id).offene_frage
        return FRAGE_KEINE if frage is None else FRAGE_OFFEN

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return when the question was asked and when it expires."""
        frage = self._manager.zustand(self._kind.id).offene_frage
        if frage is None:
            return None
        return {
            "gestellt_um": frage.gestellt_um.isoformat(),
            "timeout_um": frage.timeout_um.isoformat(),
            "fach": self._manager.faecher[frage.fach_id].name,
        }
