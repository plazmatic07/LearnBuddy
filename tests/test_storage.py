"""Tests for the storage layer."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util
import pytest
from pytest_homeassistant_custom_component.common import async_fire_time_changed

from custom_components.learnbuddy.models import OffeneFrage, Vokabel
from custom_components.learnbuddy.storage import (
    ConfigStore,
    TaskStore,
    async_remove_task_file,
    migrate_config,
    migrate_tasks,
    task_store_key,
)

JETZT = datetime(2026, 10, 6, 15, 0, tzinfo=UTC)


def _vokabel(**kwargs: Any) -> Vokabel:
    return Vokabel(fach_id="f1", frage={"de": "Hund", "en": "dog"}, **kwargs)


def test_task_store_key() -> None:
    assert task_store_key("k1", "f1") == "learnbuddy.k1_f1"


async def test_config_store_roundtrip(
    hass: HomeAssistant, hass_storage: dict[str, Any]
) -> None:
    store = ConfigStore(hass)
    await store.async_load()
    assert store.kinder == {}

    zustand = store.zustand("k1")
    zustand.aktiv = False
    zustand.offene_frage = OffeneFrage(
        fach_id="f1",
        aufgabe_id="a1",
        richtung="de>en",
        gestellt_um=JETZT,
        timeout_um=JETZT + timedelta(hours=1),
    )
    store.arbeit_aufgaben["x1"] = ["a1"]
    store.aufgaben_dateien.add("learnbuddy.k1_f1")
    await store.async_save()

    gespeichert = hass_storage["learnbuddy.config"]
    assert gespeichert["version"] == 1
    assert gespeichert["minor_version"] == 12
    assert gespeichert["data"]["kinder"]["k1"]["aktiv"] is False

    neu = ConfigStore(hass)
    await neu.async_load()
    assert neu.kinder == store.kinder
    assert neu.arbeit_aufgaben == {"x1": ["a1"]}
    assert neu.aufgaben_dateien == {"learnbuddy.k1_f1"}


async def test_config_store_delayed_save(
    hass: HomeAssistant, hass_storage: dict[str, Any]
) -> None:
    store = ConfigStore(hass)
    store.zustand("k1")
    store.async_schedule_save()
    assert "learnbuddy.config" not in hass_storage
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=10))
    await hass.async_block_till_done()
    assert "k1" in hass_storage["learnbuddy.config"]["data"]["kinder"]

    await store.async_remove()
    assert "learnbuddy.config" not in hass_storage


def test_config_store_bereinige(hass: HomeAssistant) -> None:
    store = ConfigStore(hass)
    store.zustand("k1")
    store.zustand("k2")
    store.arbeit_aufgaben = {"x1": [], "x2": []}
    assert store.bereinige(["k1"], ["x2"]) is True
    assert set(store.kinder) == {"k1"}
    assert set(store.arbeit_aufgaben) == {"x2"}
    assert store.bereinige(["k1"], ["x2"]) is False


async def test_config_store_migration_from_1_0(
    hass: HomeAssistant, hass_storage: dict[str, Any]
) -> None:
    hass_storage["learnbuddy.config"] = {
        "version": 1,
        "minor_version": 0,
        "key": "learnbuddy.config",
        "data": {"kinder": {"k1": {"aktiv": False}}},
    }
    store = ConfigStore(hass)
    await store.async_load()
    assert store.kinder["k1"].aktiv is False
    assert store.arbeit_aufgaben == {}
    assert hass_storage["learnbuddy.config"]["minor_version"] == 12
    assert hass_storage["learnbuddy.config"]["data"]["aufgaben_dateien"] == []


def test_migration_rejects_future_major() -> None:
    with pytest.raises(NotImplementedError):
        migrate_config(2, 1, {})
    with pytest.raises(NotImplementedError):
        migrate_tasks(2, 1, {})


def test_migration_is_noop_for_current_version() -> None:
    config = {
        "kinder": {},
        "arbeiten": {},
        "aufgaben_dateien": ["x"],
        "kalender_ignoriert": {"k": {"uid": "2026-11-03"}},
    }
    assert migrate_config(1, 12, dict(config)) == config
    # 1.11 -> 1.12 adds the ignored calendar dates
    alt = {"kinder": {}, "arbeiten": {}, "aufgaben_dateien": []}
    assert migrate_config(1, 11, dict(alt)) == {**alt, "kalender_ignoriert": {}}
    aufgaben = {
        "lektionen": ["B"],
        "aufgaben": [{"id": "a", "lektion": "A", "statistik": {"de>en": {"box": 4}}}],
    }
    kopie = {
        "lektionen": ["B"],
        "aufgaben": [{"id": "a", "lektion": "A", "statistik": {"de>en": {"box": 4}}}],
    }
    assert migrate_tasks(1, 11, kopie) == aufgaben


async def test_task_store_roundtrip(
    hass: HomeAssistant, hass_storage: dict[str, Any]
) -> None:
    store = TaskStore(hass, "k1", "f1")
    await store.async_load()
    assert store.aufgaben == {}

    eins = _vokabel(lektion="Unit 3")
    zwei = _vokabel(lektion="Unit 1")
    drei = _vokabel()
    for aufgabe in (eins, zwei, drei):
        store.add(aufgabe)
    assert store.lektionen == ["Unit 3", "Unit 1"]
    assert store.remove(drei.id) is True
    assert store.remove("gibtsnicht") is False
    await store.async_save()

    neu = TaskStore(hass, "k1", "f1")
    await neu.async_load()
    assert neu.aufgaben == {eins.id: eins, zwei.id: zwei}
    assert neu.lektionen == ["Unit 3", "Unit 1"]

    await neu.async_remove()
    assert "learnbuddy.k1_f1" not in hass_storage


async def test_task_store_delayed_save(
    hass: HomeAssistant, hass_storage: dict[str, Any]
) -> None:
    store = TaskStore(hass, "k1", "f1")
    store.add(_vokabel())
    store.async_schedule_save()
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(seconds=10))
    await hass.async_block_till_done()
    assert len(hass_storage["learnbuddy.k1_f1"]["data"]["aufgaben"]) == 1


async def test_task_store_migration_from_1_0(
    hass: HomeAssistant, hass_storage: dict[str, Any]
) -> None:
    alt = _vokabel().to_dict()
    del alt["typ"]
    hass_storage["learnbuddy.k1_f1"] = {
        "version": 1,
        "minor_version": 0,
        "key": "learnbuddy.k1_f1",
        "data": {"aufgaben": [alt]},
    }
    store = TaskStore(hass, "k1", "f1")
    await store.async_load()
    assert len(store.aufgaben) == 1
    gespeichert = hass_storage["learnbuddy.k1_f1"]
    assert gespeichert["minor_version"] == 12
    assert gespeichert["data"]["aufgaben"][0]["typ"] == "vokabel"


@pytest.mark.parametrize(
    ("richtig", "falsch", "box"),
    [(0, 0, 1), (3, 1, 3), (9, 0, 5), (1, 4, 1)],
)
async def test_task_store_migration_from_1_1(
    hass: HomeAssistant,
    hass_storage: dict[str, Any],
    richtig: int,
    falsch: int,
    box: int,
) -> None:
    alt = _vokabel().to_dict()
    alt["statistik"] = {"de>en": {"box": 1, "richtig": richtig, "falsch": falsch}}
    hass_storage["learnbuddy.k1_f1"] = {
        "version": 1,
        "minor_version": 1,
        "key": "learnbuddy.k1_f1",
        "data": {"aufgaben": [alt]},
    }
    store = TaskStore(hass, "k1", "f1")
    await store.async_load()
    aufgabe = next(iter(store.aufgaben.values()))
    assert aufgabe.statistik["de>en"].box == box
    assert hass_storage["learnbuddy.k1_f1"]["minor_version"] == 12


async def test_remove_task_file(
    hass: HomeAssistant, hass_storage: dict[str, Any]
) -> None:
    store = TaskStore(hass, "k1", "f1")
    store.add(_vokabel())
    await store.async_save()
    assert "learnbuddy.k1_f1" in hass_storage
    await async_remove_task_file(hass, "learnbuddy.k1_f1")
    assert "learnbuddy.k1_f1" not in hass_storage


async def test_task_store_migration_from_1_2(
    hass: HomeAssistant, hass_storage: dict[str, Any]
) -> None:
    hass_storage["learnbuddy.k1_f1"] = {
        "version": 1,
        "minor_version": 2,
        "key": "learnbuddy.k1_f1",
        "data": {
            "aufgaben": [
                _vokabel(lektion="Unit 3").to_dict(),
                _vokabel(lektion="Unit 1").to_dict(),
                _vokabel(lektion="Unit 3").to_dict(),
                _vokabel().to_dict(),
            ]
        },
    }
    store = TaskStore(hass, "k1", "f1")
    await store.async_load()
    assert store.lektionen == ["Unit 1", "Unit 3"]
    gespeichert = hass_storage["learnbuddy.k1_f1"]
    assert gespeichert["minor_version"] == 12
    assert gespeichert["data"]["lektionen"] == ["Unit 1", "Unit 3"]


def test_task_store_lektionen(hass: HomeAssistant) -> None:
    store = TaskStore(hass, "k1", "f1")
    assert store.lektion_hinzufuegen(" Unit 1 ") is True
    assert store.lektion_hinzufuegen("unit 1") is False
    assert store.lektion_finden("UNIT 1") == "Unit 1"
    assert store.lektion_finden("Unit 2") is None

    # A task adopts the stored spelling, an unknown lesson is registered
    eins = _vokabel(lektion="unit 1")
    store.add(eins)
    store.add(_vokabel(lektion="Unit 2"))
    assert eins.lektion == "Unit 1"
    assert store.lektionen == ["Unit 1", "Unit 2"]
    assert store.lektion_verwendet("Unit 1") == 1
    store.lektion_entfernen("Unit 2")
    assert store.lektionen == ["Unit 1"]


async def test_task_store_migration_from_1_3(
    hass: HomeAssistant, hass_storage: dict[str, Any]
) -> None:
    alt = _vokabel().to_dict()
    alt["statistik"] = {"de>en": {"box": 2, "richtig": 3, "falsch": 2}}
    hass_storage["learnbuddy.k1_f1"] = {
        "version": 1,
        "minor_version": 3,
        "key": "learnbuddy.k1_f1",
        "data": {"lektionen": [], "aufgaben": [alt]},
    }
    store = TaskStore(hass, "k1", "f1")
    await store.async_load()
    aufgabe = next(iter(store.aufgaben.values()))
    assert aufgabe.statistik["de>en"].gefragt == 5
    gespeichert = hass_storage["learnbuddy.k1_f1"]["data"]["aufgaben"][0]
    assert gespeichert["statistik"]["de>en"]["gefragt"] == 5


async def test_task_store_migration_from_1_4(
    hass: HomeAssistant, hass_storage: dict[str, Any]
) -> None:
    alt = _vokabel().to_dict()
    del alt["seite"]
    hass_storage["learnbuddy.k1_f1"] = {
        "version": 1,
        "minor_version": 4,
        "key": "learnbuddy.k1_f1",
        "data": {"lektionen": [], "aufgaben": [alt]},
    }
    store = TaskStore(hass, "k1", "f1")
    await store.async_load()
    assert next(iter(store.aufgaben.values())).seite is None
    gespeichert = hass_storage["learnbuddy.k1_f1"]
    assert gespeichert["minor_version"] == 12
    assert gespeichert["data"]["aufgaben"][0]["seite"] is None


def test_config_migration_from_1_5() -> None:
    daten = migrate_config(1, 5, {"kinder": {"k1": {"aktiv": True}}})
    assert daten["kinder"]["k1"]["zusatz_offen"] == 0


def test_task_migration_from_1_7() -> None:
    daten = migrate_tasks(
        1,
        7,
        {
            "lektionen": [],
            "aufgaben": [
                {"id": "m", "typ": "mathe", "statistik": {}},
                {"id": "v", "typ": "vokabel", "statistik": {}},
            ],
        },
    )
    assert daten["aufgaben"][0]["vorschlag"] is None
    assert daten["aufgaben"][0]["vorschlag_durch"] is None
    assert daten["aufgaben"][0]["bild"] is None
    assert "bild" not in daten["aufgaben"][1]
    assert "vorschlag" not in daten["aufgaben"][1]


def test_migration_from_1_9() -> None:
    aufgaben = migrate_tasks(
        1,
        9,
        {
            "lektionen": [],
            "aufgaben": [{"id": "a", "statistik": {"de>en": {"box": 2}}}],
        },
    )
    assert aufgaben["aufgaben"][0]["statistik"]["de>en"]["teilweise"] == 0
    config = migrate_config(
        1,
        9,
        {"kinder": {"k1": {"offene_frage": {"fach_id": "f"}}, "k2": {}}},
    )
    assert config["kinder"]["k1"]["offene_frage"]["optionen"] is None
    assert config["kinder"]["k2"]["simulation"] is None
