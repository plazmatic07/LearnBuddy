"""Switches of the LearnBuddy integration."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import EntityCategory
from homeassistant.util import dt as dt_util

from .entity import LearnBuddyEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

    from . import LearnBuddyConfigEntry
    from .manager import LearnBuddyManager
    from .models import Kind

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: LearnBuddyConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the switches of all children."""
    manager = entry.runtime_data
    for kind in manager.kinder.values():
        async_add_entities(
            [AbfragenAktivSwitch(manager, kind)], config_subentry_id=kind.id
        )


class AbfragenAktivSwitch(LearnBuddyEntity, SwitchEntity):
    """Enable or disable the questions of a child."""

    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, manager: LearnBuddyManager, kind: Kind) -> None:
        """Initialize the switch."""
        super().__init__(manager, kind, "abfragen_aktiv")

    @property
    def is_on(self) -> bool:
        """Return whether questions are asked."""
        return not self._manager.zustand(self._kind.id).ist_pausiert(dt_util.utcnow())

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Resume the questions."""
        self._manager.async_set_aktiv(self._kind.id, aktiv=True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Stop the questions."""
        self._manager.async_set_aktiv(self._kind.id, aktiv=False)
