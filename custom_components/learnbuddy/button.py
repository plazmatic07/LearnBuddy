"""Buttons of the LearnBuddy integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.button import ButtonEntity

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
    """Set up the buttons of all children."""
    manager = entry.runtime_data
    for kind in manager.kinder.values():
        async_add_entities(
            [JetztAbfragenButton(manager, kind)], config_subentry_id=kind.id
        )


class JetztAbfragenButton(LearnBuddyEntity, ButtonEntity):
    """Ask a child a question right now."""

    def __init__(self, manager: LearnBuddyManager, kind: Kind) -> None:
        """Initialize the button."""
        super().__init__(manager, kind, "jetzt_abfragen")

    async def async_press(self) -> None:
        """Send a question."""
        await self._manager.async_frage_stellen(self._kind.id)
