"""Base entity of the LearnBuddy integration."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import Entity

from .const import DOMAIN, signal_kind_update

if TYPE_CHECKING:
    from .manager import LearnBuddyManager
    from .models import Kind


class LearnBuddyEntity(Entity):
    """Entity that belongs to a child."""

    _attr_has_entity_name = True
    _attr_should_poll = False

    def __init__(self, manager: LearnBuddyManager, kind: Kind, key: str) -> None:
        """Initialize the entity."""
        self._manager = manager
        self._kind = kind
        self._attr_translation_key = key
        self._attr_unique_id = f"{kind.id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, kind.id)},
            name=kind.name,
            manufacturer="LearnBuddy",
            entry_type=DeviceEntryType.SERVICE,
        )

    async def async_added_to_hass(self) -> None:
        """Update when the data of the child changes."""
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, signal_kind_update(self._kind.id), self.async_write_ha_state
            )
        )
