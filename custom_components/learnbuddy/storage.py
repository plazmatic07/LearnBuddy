"""Persistence of the LearnBuddy integration.

Two kinds of files live in ``.storage``:

* ``learnbuddy.config`` - runtime state per child and task assignments per exam
* ``learnbuddy.<kind_id>_<fach_id>`` - the tasks of one subject including statistics
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from homeassistant.helpers.storage import Store

from .const import (
    DOMAIN,
    STORAGE_KEY_CONFIG,
    STORAGE_MINOR_VERSION,
    STORAGE_VERSION,
)
from .models import Aufgabe, KindZustand, aufgabe_from_dict

if TYPE_CHECKING:
    from collections.abc import Iterable

    from homeassistant.core import HomeAssistant

SAVE_DELAY = 5


def task_store_key(kind_id: str, fach_id: str) -> str:
    """Return the storage key of the tasks of a subject."""
    return f"{DOMAIN}.{kind_id}_{fach_id}"


def migrate_config(
    old_major: int, old_minor: int, data: dict[str, Any]
) -> dict[str, Any]:
    """Migrate the data of the config store to the current version."""
    if old_major > STORAGE_VERSION:
        raise NotImplementedError
    if old_major == 1 and old_minor < 1:
        # 1.0 -> 1.1: registry of known task files was added
        data.setdefault("aufgaben_dateien", [])
    data.setdefault("kinder", {})
    data.setdefault("arbeiten", {})
    if old_major == 1 and old_minor < 6:
        # 1.5 -> 1.6: children can ask for extra questions
        for zustand in data["kinder"].values():
            zustand.setdefault("zusatz_offen", 0)
    if old_major == 1 and old_minor < 7:
        # 1.6 -> 1.7: a solution can be explained on request (math tasks)
        for zustand in data["kinder"].values():
            zustand.setdefault("rechenweg_angebot", None)
    if old_major == 1 and old_minor < 10:
        # 1.9 -> 1.10: an open choice question remembers the order of its options
        for zustand in data["kinder"].values():
            if zustand.get("offene_frage"):
                zustand["offene_frage"].setdefault("optionen", None)
    if old_major == 1 and old_minor < 11:
        # 1.10 -> 1.11: an exam can be simulated in the messenger
        for zustand in data["kinder"].values():
            zustand.setdefault("simulation", None)
    if old_major == 1 and old_minor < 12:
        # 1.11 -> 1.12: exam dates from a calendar can be ignored
        data.setdefault("kalender_ignoriert", {})
    return data


def migrate_tasks(
    old_major: int, old_minor: int, data: dict[str, Any]
) -> dict[str, Any]:
    """Migrate the data of a task store to the current version."""
    if old_major > STORAGE_VERSION:
        raise NotImplementedError
    if old_major == 1 and old_minor < 1:
        # 1.0 -> 1.1: every task carries its type
        for aufgabe in data.get("aufgaben", []):
            aufgabe.setdefault("typ", "vokabel")
    if old_major == 1 and old_minor < 2:
        # 1.1 -> 1.2: Leitner boxes are in use, derive them from the history
        for aufgabe in data.get("aufgaben", []):
            for stat in aufgabe.get("statistik", {}).values():
                bilanz = stat.get("richtig", 0) - stat.get("falsch", 0)
                stat["box"] = min(max(1 + bilanz, 1), 5)
    data.setdefault("aufgaben", [])
    if old_major == 1 and old_minor < 3:
        # 1.2 -> 1.3: lessons are managed explicitly instead of being free text
        data["lektionen"] = sorted(
            {a["lektion"] for a in data["aufgaben"] if a.get("lektion")}
        )
    data.setdefault("lektionen", [])
    if old_major == 1 and old_minor < 4:
        # 1.3 -> 1.4: asked questions are counted, start with the answered ones
        for aufgabe in data["aufgaben"]:
            for stat in aufgabe.get("statistik", {}).values():
                stat.setdefault(
                    "gefragt", stat.get("richtig", 0) + stat.get("falsch", 0)
                )
    if old_major == 1 and old_minor < 5:
        # 1.4 -> 1.5: tasks can carry the page of the textbook
        for aufgabe in data["aufgaben"]:
            aufgabe.setdefault("seite", None)
    if old_major == 1 and old_minor < 8:
        # 1.7 -> 1.8: math tasks keep the result found when recalculating
        for aufgabe in data["aufgaben"]:
            if aufgabe.get("typ") == "mathe":
                aufgabe.setdefault("vorschlag", None)
                aufgabe.setdefault("vorschlag_durch", None)
    if old_major == 1 and old_minor < 9:
        # 1.8 -> 1.9: math tasks can be about an image
        for aufgabe in data["aufgaben"]:
            if aufgabe.get("typ") == "mathe":
                aufgabe.setdefault("bild", None)
    if old_major == 1 and old_minor < 10:
        # 1.9 -> 1.10: answers can be right in part (knowledge subjects)
        for aufgabe in data["aufgaben"]:
            for stat in aufgabe.get("statistik", {}).values():
                stat.setdefault("teilweise", 0)
    return data


class _ConfigStore(Store[dict[str, Any]]):
    """Store of the runtime state with migration support."""

    async def _async_migrate_func(
        self, old_major_version: int, old_minor_version: int, old_data: dict[str, Any]
    ) -> dict[str, Any]:
        return migrate_config(old_major_version, old_minor_version, old_data)


class _TaskStore(Store[dict[str, Any]]):
    """Store of the tasks of a subject with migration support."""

    async def _async_migrate_func(
        self, old_major_version: int, old_minor_version: int, old_data: dict[str, Any]
    ) -> dict[str, Any]:
        return migrate_tasks(old_major_version, old_minor_version, old_data)


class ConfigStore:
    """Runtime state of all children and explicit task assignments of exams."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the store."""
        self._store = _ConfigStore(
            hass,
            STORAGE_VERSION,
            STORAGE_KEY_CONFIG,
            minor_version=STORAGE_MINOR_VERSION,
            atomic_writes=True,
        )
        self.kinder: dict[str, KindZustand] = {}
        self.arbeit_aufgaben: dict[str, list[str]] = {}
        # Planned time of the simulation that was already sent, per exam
        self.simulation_gesendet: dict[str, str] = {}
        # Calendar events the user does not want suggested: ID and day, per child
        self.kalender_ignoriert: dict[str, dict[str, str]] = {}
        self.aufgaben_dateien: set[str] = set()

    async def async_load(self) -> None:
        """Load the state from disk."""
        data = await self._store.async_load()
        if data is None:
            return
        self.kinder = {
            kind_id: KindZustand.from_dict(wert)
            for kind_id, wert in data.get("kinder", {}).items()
        }
        self.arbeit_aufgaben = {
            arbeit_id: list(wert.get("aufgaben_ids", []))
            for arbeit_id, wert in data.get("arbeiten", {}).items()
        }
        self.simulation_gesendet = {
            arbeit_id: wert["simulation_gesendet"]
            for arbeit_id, wert in data.get("arbeiten", {}).items()
            if wert.get("simulation_gesendet")
        }
        self.kalender_ignoriert = {
            kind_id: dict(wert)
            for kind_id, wert in data.get("kalender_ignoriert", {}).items()
        }
        self.aufgaben_dateien = set(data.get("aufgaben_dateien", []))

    def zustand(self, kind_id: str) -> KindZustand:
        """Return (and create if needed) the runtime state of a child."""
        return self.kinder.setdefault(kind_id, KindZustand())

    def bereinige(self, kind_ids: Iterable[str], arbeit_ids: Iterable[str]) -> bool:
        """Drop state of children and exams that no longer exist."""
        kinder = set(kind_ids)
        arbeiten = set(arbeit_ids)
        alte_kinder = self.kinder.keys() - kinder
        alte_arbeiten = (
            self.arbeit_aufgaben.keys() | self.simulation_gesendet.keys()
        ) - arbeiten
        for kind_id in alte_kinder:
            del self.kinder[kind_id]
        alte_ignorierte = self.kalender_ignoriert.keys() - kinder
        for kind_id in alte_ignorierte:
            del self.kalender_ignoriert[kind_id]
        for arbeit_id in alte_arbeiten:
            self.arbeit_aufgaben.pop(arbeit_id, None)
            self.simulation_gesendet.pop(arbeit_id, None)
        return bool(alte_kinder or alte_arbeiten or alte_ignorierte)

    def _data(self) -> dict[str, Any]:
        return {
            "kinder": {k: v.to_dict() for k, v in self.kinder.items()},
            "arbeiten": {
                k: {
                    "aufgaben_ids": list(self.arbeit_aufgaben.get(k, [])),
                    "simulation_gesendet": self.simulation_gesendet.get(k),
                }
                for k in self.arbeit_aufgaben.keys() | self.simulation_gesendet.keys()
            },
            "kalender_ignoriert": {
                kind_id: dict(wert)
                for kind_id, wert in self.kalender_ignoriert.items()
                if wert
            },
            "aufgaben_dateien": sorted(self.aufgaben_dateien),
        }

    def async_schedule_save(self) -> None:
        """Save the state after a short delay."""
        self._store.async_delay_save(self._data, SAVE_DELAY)

    async def async_save(self) -> None:
        """Save the state immediately."""
        await self._store.async_save(self._data())

    async def async_remove(self) -> None:
        """Delete the file."""
        await self._store.async_remove()


class TaskStore:
    """The tasks of one subject."""

    def __init__(self, hass: HomeAssistant, kind_id: str, fach_id: str) -> None:
        """Initialize the store."""
        self.key = task_store_key(kind_id, fach_id)
        self.fach_id = fach_id
        self._store = _TaskStore(
            hass,
            STORAGE_VERSION,
            self.key,
            minor_version=STORAGE_MINOR_VERSION,
            atomic_writes=True,
        )
        self.aufgaben: dict[str, Aufgabe] = {}
        # Lessons (or topics) of the subject in the order they were created
        self.lektionen: list[str] = []

    async def async_load(self) -> None:
        """Load the tasks from disk."""
        data = await self._store.async_load()
        if data is None:
            return
        self.lektionen = list(data.get("lektionen", []))
        self.aufgaben = {}
        for roh in data.get("aufgaben", []):
            if (aufgabe := aufgabe_from_dict(roh)) is not None:
                self.add(aufgabe)

    def lektion_finden(self, name: str) -> str | None:
        """Return the stored spelling of a lesson, ignoring case."""
        gesucht = name.strip().casefold()
        return next((x for x in self.lektionen if x.casefold() == gesucht), None)

    def lektion_hinzufuegen(self, name: str) -> bool:
        """Add a lesson; returns False if it already exists."""
        if self.lektion_finden(name) is not None:
            return False
        self.lektionen.append(name.strip())
        return True

    def lektion_entfernen(self, name: str) -> None:
        """Remove a lesson from the list."""
        self.lektionen = [x for x in self.lektionen if x != name]

    def lektion_verwendet(self, name: str) -> int:
        """Return how many tasks belong to a lesson."""
        return sum(1 for a in self.aufgaben.values() if a.lektion == name)

    def add(self, aufgabe: Aufgabe) -> None:
        """Add or replace a task; its lesson is registered if it is new."""
        if aufgabe.lektion:
            vorhanden = self.lektion_finden(aufgabe.lektion)
            if vorhanden is None:
                self.lektionen.append(aufgabe.lektion)
            else:
                aufgabe.lektion = vorhanden
        self.aufgaben[aufgabe.id] = aufgabe

    def remove(self, aufgabe_id: str) -> bool:
        """Remove a task."""
        return self.aufgaben.pop(aufgabe_id, None) is not None

    def _data(self) -> dict[str, Any]:
        return {
            "lektionen": list(self.lektionen),
            "aufgaben": [a.to_dict() for a in self.aufgaben.values()],
        }

    def async_schedule_save(self) -> None:
        """Save the tasks after a short delay."""
        self._store.async_delay_save(self._data, SAVE_DELAY)

    async def async_save(self) -> None:
        """Save the tasks immediately."""
        await self._store.async_save(self._data())

    async def async_remove(self) -> None:
        """Delete the file."""
        await self._store.async_remove()


async def async_remove_task_file(hass: HomeAssistant, key: str) -> None:
    """Delete an orphaned task file by its storage key."""
    await Store[dict[str, Any]](hass, STORAGE_VERSION, key).async_remove()
