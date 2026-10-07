"""Tests for exam suggestions read from a calendar."""

from __future__ import annotations

from collections.abc import Callable
from datetime import timedelta
from typing import Any

from freezegun.api import FrozenDateTimeFactory
from homeassistant.core import (
    HomeAssistant,
    ServiceCall,
    ServiceResponse,
    SupportsResponse,
)
from homeassistant.exceptions import HomeAssistantError
from homeassistant.util import dt as dt_util
import pytest
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_fire_time_changed,
)
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from custom_components.learnbuddy.manager import LearnBuddyManager
from custom_components.learnbuddy.verwaltung import VerwaltungError

from .conftest import ARBEIT_ID, FACH_ID, KIND_DATEN, KIND_ID

KALENDER = "calendar.pruefungen"
TERMINE: list[dict[str, Any]] = [
    {
        "start": "2026-11-03T08:50:00+01:00",
        "end": "2026-11-03T09:35:00+01:00",
        "summary": "E",
        "description": "KA E",
    },
    {"start": "2026-10-09", "end": "2026-10-10", "summary": "M", "description": "HÜ M"},
    {
        "start": "2026-10-20T10:00:00+02:00",
        "end": "2026-10-20T10:45:00+02:00",
        "summary": "D",
        "description": "KA D",
    },
]

type Aufrufe = list[ServiceCall]


def _registriere(hass: HomeAssistant, zustand: dict[str, Any]) -> None:
    async def get_events(call: ServiceCall) -> ServiceResponse:
        zustand["aufrufe"].append(call)
        if zustand["fehler"] is not None:
            raise zustand["fehler"]
        return {KALENDER: {"events": zustand["termine"]}}

    hass.services.async_register(
        "calendar", "get_events", get_events, supports_response=SupportsResponse.ONLY
    )


@pytest.fixture
def kalender(hass: HomeAssistant) -> dict[str, Any]:
    """Mock the action of the calendar integration."""
    zustand: dict[str, Any] = {"aufrufe": [], "termine": list(TERMINE), "fehler": None}
    _registriere(hass, zustand)
    return zustand


@pytest.fixture
async def mit_kalender(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    notify_calls: list[ServiceCall],
    kalender: dict[str, Any],
) -> MockConfigEntry:
    """Set up the integration with a child that uses an exam calendar."""
    hass.config_entries.async_update_subentry(
        config_entry,
        config_entry.subentries[KIND_ID],
        data={
            **KIND_DATEN,
            "kalender_aktiv": True,
            "kalender_entity": KALENDER,
            "kalender_um": "20:00:00",
        },
    )
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    # Setting up the own calendar platform registers the real action
    _registriere(hass, kalender)
    return config_entry


def _vorschlaege(entry: MockConfigEntry) -> list[dict[str, Any]]:
    daten: dict[str, Any] = entry.runtime_data.verwaltung.dashboard(KIND_ID)
    liste: list[dict[str, Any]] = daten["vorschlaege"]
    return liste


async def test_ohne_kalender(
    hass: HomeAssistant, setup_entry: MockConfigEntry, kalender: dict[str, Any]
) -> None:
    manager: LearnBuddyManager = setup_entry.runtime_data
    daten = manager.verwaltung.dashboard(KIND_ID)
    assert daten["kalender"] is None
    assert daten["vorschlaege"] == []
    assert not await manager.async_kalender_pruefen(KIND_ID)
    with pytest.raises(VerwaltungError) as fehler:
        await manager.verwaltung.kalender_pruefen(KIND_ID)
    assert fehler.value.schluessel == "kalender_aus"
    async_fire_time_changed(hass, dt_util.utcnow() + timedelta(minutes=3))
    await hass.async_block_till_done()
    assert kalender["aufrufe"] == []


async def test_vorschlaege(
    hass: HomeAssistant, mit_kalender: MockConfigEntry, kalender: dict[str, Any]
) -> None:
    manager: LearnBuddyManager = mit_kalender.runtime_data
    daten = manager.verwaltung.dashboard(KIND_ID)
    assert daten["kalender"] == {"geprueft_um": None, "fehler": False, "ignoriert": 0}
    assert daten["vorschlaege"] == []

    assert await manager.verwaltung.kalender_pruefen(KIND_ID) == {"gelesen": True}
    aufruf = kalender["aufrufe"][0]
    assert aufruf.data["entity_id"] == KALENDER
    spanne = aufruf.data["end_date_time"] - aufruf.data["start_date_time"]
    assert spanne == timedelta(days=120)
    assert dt_util.as_local(aufruf.data["start_date_time"]).isoformat() == (
        "2026-10-06T00:00:00+02:00"
    )

    liste = _vorschlaege(mit_kalender)
    assert liste == [
        {
            "uid": "2026-10-09|HÜ M",
            "datum": "2026-10-09",
            "art": "hue",
            "text": "HÜ M",
            "fach_id": None,
            # The exam of the fixture is on that day
            "gleicher_tag": ["Englisch: Unit 3"],
        },
        {
            "uid": "2026-10-20|KA D",
            "datum": "2026-10-20",
            "art": "arbeit",
            "text": "KA D",
            "fach_id": None,
            "gleicher_tag": [],
        },
        {
            "uid": "2026-11-03|KA E",
            "datum": "2026-11-03",
            "art": "arbeit",
            "text": "KA E",
            # "E" fits exactly one subject
            "fach_id": FACH_ID,
            "gleicher_tag": [],
        },
    ]
    stand = manager.verwaltung.dashboard(KIND_ID)["kalender"]
    assert stand["geprueft_um"] == "2026-10-06T06:00:00+00:00"


async def test_taeglich_und_nach_start(
    hass: HomeAssistant,
    mit_kalender: MockConfigEntry,
    kalender: dict[str, Any],
    freezer: FrozenDateTimeFactory,
) -> None:
    assert kalender["aufrufe"] == []
    # Shortly after the start
    freezer.tick(timedelta(minutes=2, seconds=1))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert len(kalender["aufrufe"]) == 1
    assert len(_vorschlaege(mit_kalender)) == 3

    # Once a day at the time set for the child
    freezer.move_to("2026-10-06 19:59:59+02:00")
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert len(kalender["aufrufe"]) == 1
    freezer.move_to("2026-10-06 20:00:00+02:00")
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert len(kalender["aufrufe"]) == 2

    # Unloading stops the clock
    assert await hass.config_entries.async_unload(mit_kalender.entry_id)
    freezer.move_to("2026-10-07 20:00:00+02:00")
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert len(kalender["aufrufe"]) == 2


@pytest.mark.parametrize(
    "stoerung",
    [
        lambda k: k.update(fehler=HomeAssistantError("weg")),
        lambda k: k.update(termine="kaputt"),
    ],
)
async def test_kalender_nicht_lesbar(
    hass: HomeAssistant,
    mit_kalender: MockConfigEntry,
    kalender: dict[str, Any],
    stoerung: Callable[[dict[str, Any]], None],
) -> None:
    manager: LearnBuddyManager = mit_kalender.runtime_data
    assert await manager.async_kalender_pruefen(KIND_ID)
    stoerung(kalender)
    assert await manager.verwaltung.kalender_pruefen(KIND_ID) == {"gelesen": False}
    daten = manager.verwaltung.dashboard(KIND_ID)
    assert daten["kalender"]["fehler"] is True
    # What was read before stays
    assert len(daten["vorschlaege"]) == 3

    kalender.update(fehler=None, termine=[*TERMINE, {"start": 5}, "x"])
    assert await manager.async_kalender_pruefen(KIND_ID)
    daten = manager.verwaltung.dashboard(KIND_ID)
    assert daten["kalender"]["fehler"] is False
    assert len(daten["vorschlaege"]) == 3


async def test_ignorieren_und_wiederherstellen(
    hass: HomeAssistant,
    mit_kalender: MockConfigEntry,
    kalender: dict[str, Any],
    freezer: FrozenDateTimeFactory,
) -> None:
    manager: LearnBuddyManager = mit_kalender.runtime_data
    verwaltung = manager.verwaltung
    await manager.async_kalender_pruefen(KIND_ID)

    verwaltung.kalender_ignorieren(KIND_ID, "2026-10-20|KA D")
    verwaltung.kalender_ignorieren(KIND_ID, "2026-10-09|HÜ M")
    assert [v["text"] for v in _vorschlaege(mit_kalender)] == ["KA E"]
    assert verwaltung.dashboard(KIND_ID)["kalender"]["ignoriert"] == 2
    for kind_id, uid, schluessel in (
        (KIND_ID, "gibtsnicht", "termin_unbekannt"),
        ("gibtsnicht", "2026-11-03|KA E", "kind_unbekannt"),
    ):
        with pytest.raises(VerwaltungError) as fehler:
            verwaltung.kalender_ignorieren(kind_id, uid)
        assert fehler.value.schluessel == schluessel

    # Survives a reload
    await hass.config_entries.async_reload(mit_kalender.entry_id)
    await hass.async_block_till_done()
    manager = mit_kalender.runtime_data
    verwaltung = manager.verwaltung
    await manager.async_kalender_pruefen(KIND_ID)
    assert [v["text"] for v in _vorschlaege(mit_kalender)] == ["KA E"]

    # Ignored dates of the past are dropped when the calendar is read
    freezer.move_to("2026-10-12 08:00:00+02:00")
    await manager.async_kalender_pruefen(KIND_ID)
    assert manager.config_store.kalender_ignoriert[KIND_ID] == {
        "2026-10-20|KA D": "2026-10-20"
    }

    verwaltung.kalender_wiederherstellen(KIND_ID)
    verwaltung.kalender_wiederherstellen(KIND_ID)
    assert [v["text"] for v in _vorschlaege(mit_kalender)] == ["KA D", "KA E"]
    with pytest.raises(VerwaltungError):
        verwaltung.kalender_wiederherstellen("gibtsnicht")
    with pytest.raises(VerwaltungError):
        await verwaltung.kalender_pruefen("gibtsnicht")


async def test_eingetragen_verschwindet(
    hass: HomeAssistant, mit_kalender: MockConfigEntry, kalender: dict[str, Any]
) -> None:
    manager: LearnBuddyManager = mit_kalender.runtime_data
    await manager.async_kalender_pruefen(KIND_ID)
    arbeit_id = await manager.verwaltung.arbeit_speichern(
        None,
        {
            "fach_id": FACH_ID,
            "datum": "2026-11-03",
            "thema": "KA E",
            "kalender_uid": "2026-11-03|KA E",
        },
    )
    await hass.async_block_till_done()
    assert manager.arbeiten[arbeit_id].kalender_uid == "2026-11-03|KA E"
    assert [v["text"] for v in _vorschlaege(mit_kalender)] == ["HÜ M", "KA D"]

    # Editing keeps the link, in the panel and in the form
    await manager.verwaltung.arbeit_speichern(
        arbeit_id, {"datum": "2026-11-04", "thema": "Unit 5"}
    )
    await hass.async_block_till_done()
    assert manager.arbeiten[arbeit_id].kalender_uid == "2026-11-03|KA E"
    result = await hass.config_entries.subentries.async_init(
        (mit_kalender.entry_id, "arbeit"),
        context={"source": "reconfigure", "subentry_id": arbeit_id},
    )
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"],
        {
            "art": "arbeit",
            "datum": "2026-11-05",
            "thema": "Unit 6",
            "lektionen": [],
            "abfragen_pro_tag": 2,
            "start_tage_vorher": 7,
            "intensivierung": True,
            "simulation_aktiv": False,
        },
    )
    await hass.async_block_till_done()
    assert mit_kalender.subentries[arbeit_id].data["kalender_uid"] == "2026-11-03|KA E"
    assert [v["text"] for v in _vorschlaege(mit_kalender)] == ["HÜ M", "KA D"]

    # An exam without a calendar date carries none
    assert manager.arbeiten[ARBEIT_ID].kalender_uid is None


@pytest.mark.parametrize(
    ("daten", "name", "typ", "sprachen"),
    [
        (
            {"typ": "fremdsprache", "sprache": "fr"},
            "Französisch",
            "vokabel",
            ("de", "fr"),
        ),
        (
            {"typ": "fremdsprache", "sprache": "es", "name": " Spanisch AG "},
            "Spanisch AG",
            "vokabel",
            ("de", "es"),
        ),
        ({"typ": "mathe"}, "Mathe", "mathe", ()),
        ({"typ": "sach", "name": "Deutsch"}, "Deutsch", "sach", ()),
    ],
)
async def test_fach_anlegen(  # noqa: PLR0917
    hass: HomeAssistant,
    mit_vokabeln: MockConfigEntry,
    daten: dict[str, Any],
    name: str,
    typ: str,
    sprachen: tuple[str, ...],
) -> None:
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    fach_id = await manager.verwaltung.fach_anlegen(KIND_ID, daten)
    await hass.async_block_till_done()

    # No reload: the panel would be thrown out by one
    assert mit_vokabeln.runtime_data is manager
    fach = manager.faecher[fach_id]
    assert (fach.name, fach.typ.value, fach.sprachen) == (name, typ, sprachen)
    assert mit_vokabeln.subentries[fach_id].title == f"{name} (Max)"
    assert fach_id in manager.task_stores
    # The subject works right away: an exam can be entered for it
    arbeit_id = await manager.verwaltung.arbeit_speichern(
        None, {"fach_id": fach_id, "datum": "2026-11-03", "thema": "KA"}
    )
    await hass.async_block_till_done()
    assert manager.arbeiten[arbeit_id].fach_id == fach_id

    # And it is still there after a reload
    await hass.config_entries.async_reload(mit_vokabeln.entry_id)
    await hass.async_block_till_done()
    neu: LearnBuddyManager = mit_vokabeln.runtime_data
    assert neu.faecher[fach_id].name == name
    assert arbeit_id in neu.arbeiten


@pytest.mark.parametrize(
    ("kind_id", "daten", "schluessel"),
    [
        ("gibtsnicht", {"typ": "mathe"}, "kind_unbekannt"),
        (KIND_ID, {"typ": "kunst"}, "fachart_ungueltig"),
        (KIND_ID, {"typ": "fremdsprache"}, "sprache_ungueltig"),
        # The native language is no foreign language
        (KIND_ID, {"typ": "fremdsprache", "sprache": "de"}, "sprache_ungueltig"),
        (KIND_ID, {"typ": "fremdsprache", "sprache": "en"}, "fach_vorhanden"),
        (KIND_ID, {"typ": "sach", "name": " englisch "}, "fach_vorhanden"),
        (KIND_ID, {"typ": "sach", "name": "  "}, "name_leer"),
    ],
)
async def test_fach_anlegen_fehler(
    hass: HomeAssistant,
    mit_vokabeln: MockConfigEntry,
    kind_id: str,
    daten: dict[str, Any],
    schluessel: str,
) -> None:
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    anzahl = len(manager.faecher)
    with pytest.raises(VerwaltungError) as fehler:
        await manager.verwaltung.fach_anlegen(kind_id, daten)
    assert fehler.value.schluessel == schluessel
    assert len(manager.faecher) == anzahl


async def test_websocket(
    hass: HomeAssistant,
    mit_kalender: MockConfigEntry,
    kalender: dict[str, Any],
    hass_ws_client: WebSocketGenerator,
) -> None:
    ws = await hass_ws_client(hass)

    async def befehl(typ: str, /, **daten: Any) -> dict[str, Any]:
        await ws.send_json_auto_id({"type": f"learnbuddy/{typ}", **daten})
        antwort: dict[str, Any] = await ws.receive_json()
        return antwort

    async def ok(typ: str, /, **daten: Any) -> Any:
        antwort = await befehl(typ, **daten)
        assert antwort["success"], antwort
        return antwort["result"]

    assert await ok("calendar/refresh", kind_id=KIND_ID) == {"gelesen": True}
    daten = await ok("dashboard", kind_id=KIND_ID)
    assert [v["text"] for v in daten["vorschlaege"]] == ["HÜ M", "KA D", "KA E"]

    await ok("calendar/ignore", kind_id=KIND_ID, uid="2026-10-09|HÜ M")
    fach = await ok("subjects/create", kind_id=KIND_ID, typ="sach", name="Deutsch")
    await ok(
        "exams/save",
        arbeit={
            "fach_id": fach["fach_id"],
            "datum": "2026-10-20",
            "thema": "KA D",
            "kalender_uid": "2026-10-20|KA D",
        },
    )
    await hass.async_block_till_done()
    daten = await ok("dashboard", kind_id=KIND_ID)
    assert [v["text"] for v in daten["vorschlaege"]] == ["KA E"]
    assert daten["kalender"]["ignoriert"] == 1
    await ok("calendar/restore", kind_id=KIND_ID)
    daten = await ok("dashboard", kind_id=KIND_ID)
    assert [v["text"] for v in daten["vorschlaege"]] == ["HÜ M", "KA E"]

    fehler = await befehl(
        "subjects/create", kind_id=KIND_ID, typ="sach", name="deutsch"
    )
    assert fehler["error"]["message"] == "fach_vorhanden"
    fehler = await befehl("calendar/refresh", kind_id="x")
    assert fehler["error"]["message"] == "kind_unbekannt"

    assert await hass.config_entries.async_unload(mit_kalender.entry_id)
    for typ, daten_ in (
        ("calendar/refresh", {"kind_id": KIND_ID}),
        ("subjects/create", {"kind_id": KIND_ID, "typ": "mathe"}),
    ):
        fehler = await befehl(typ, **daten_)
        assert fehler["error"]["message"] == "nicht_geladen"
