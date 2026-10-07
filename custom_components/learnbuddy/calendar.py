"""Calendar of the LearnBuddy integration."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING

from homeassistant.components.calendar import CalendarEntity, CalendarEvent
from homeassistant.util import dt as dt_util

from .entity import LearnBuddyEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

    from . import LearnBuddyConfigEntry
    from .manager import LearnBuddyManager
    from .models import Arbeit, Kind

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: LearnBuddyConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the calendars of all children."""
    manager = entry.runtime_data
    for kind in manager.kinder.values():
        async_add_entities(
            [ArbeitenCalendar(manager, kind)], config_subentry_id=kind.id
        )


class ArbeitenCalendar(LearnBuddyEntity, CalendarEntity):
    """Calendar with the exams of a child."""

    def __init__(self, manager: LearnBuddyManager, kind: Kind) -> None:
        """Initialize the calendar."""
        super().__init__(manager, kind, "arbeiten")

    def _event(self, arbeit: Arbeit) -> CalendarEvent:
        fach = self._manager.faecher[arbeit.fach_id]
        return CalendarEvent(
            start=arbeit.datum,
            end=arbeit.datum + timedelta(days=1),
            summary=f"{fach.name}: {arbeit.thema}",
            description=arbeit.art.value,
            uid=arbeit.id,
        )

    @property
    def event(self) -> CalendarEvent | None:
        """Return the next upcoming exam."""
        arbeit = self._manager.naechste_arbeit(self._kind.id)
        return None if arbeit is None else self._event(arbeit)

    async def async_get_events(
        self, hass: HomeAssistant, start_date: datetime, end_date: datetime
    ) -> list[CalendarEvent]:
        """Return the exams within a time range."""
        von = dt_util.as_local(start_date).date()
        bis = dt_util.as_local(end_date).date()
        return [
            self._event(arbeit)
            for arbeit in sorted(
                self._manager.arbeiten_von(self._kind.id), key=lambda a: a.datum
            )
            if von <= arbeit.datum <= bis
        ]
