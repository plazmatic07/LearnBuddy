"""Tests for the daily log in the running integration, progress and weekly report."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any

from freezegun.api import FrozenDateTimeFactory
from homeassistant.core import HomeAssistant, ServiceCall
import pytest
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_fire_time_changed,
)
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from custom_components.learnbuddy.const import DOMAIN
from custom_components.learnbuddy.manager import LearnBuddyManager
from custom_components.learnbuddy.verlauf import KindVerlauf, SimErgebnis
from custom_components.learnbuddy.verwaltung import VerwaltungError

from .conftest import ARBEIT_ID, FACH_ID, KIND_ID

HEUTE = date(2026, 10, 6)


async def _frage(hass: HomeAssistant) -> None:
    await hass.services.async_call(
        DOMAIN, "ask_now", {"kind_id": KIND_ID}, blocking=True
    )


def _verlauf(entry: MockConfigEntry) -> KindVerlauf:
    manager: LearnBuddyManager = entry.runtime_data
    return manager.verlauf_store.kind(KIND_ID)


def _richtige_antwort(manager: LearnBuddyManager) -> str:
    frage = manager.zustand(KIND_ID).offene_frage
    assert frage is not None
    aufgabe = manager.task_stores[FACH_ID].aufgaben[frage.aufgabe_id]
    return aufgabe.loesung_text(frage.richtung)


async def test_antworten_werden_gezaehlt(
    hass: HomeAssistant,
    mit_vokabeln: MockConfigEntry,
    notify_calls: list[ServiceCall],
) -> None:
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    # Nothing happened yet
    assert _verlauf(mit_vokabeln).tage == {}
    assert _verlauf(mit_vokabeln).seit is None

    await _frage(hass)
    frage = manager.zustand(KIND_ID).offene_frage
    assert frage is not None
    await manager.async_antwort(KIND_ID, "ganz falsch")
    await _frage(hass)
    await manager.async_antwort(KIND_ID, _richtige_antwort(manager))

    eintrag = _verlauf(mit_vokabeln).tage[HEUTE][FACH_ID]
    assert (eintrag.gefragt, eintrag.richtig, eintrag.falsch) == (2, 1, 1)
    assert eintrag.lektionen == {"Unit 3": [1, 1]}
    assert eintrag.aufgaben_falsch == {frage.aufgabe_id: 1}
    # The level of the subject is noted with every answer: 2 words, 2 directions
    assert (eintrag.karten, eintrag.sicher) == (4, 0)
    assert _verlauf(mit_vokabeln).seit == HEUTE


async def test_frist_und_abbruch(
    hass: HomeAssistant,
    mit_vokabeln: MockConfigEntry,
    notify_calls: list[ServiceCall],
) -> None:
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    await _frage(hass)
    await manager.async_timeout(KIND_ID)
    eintrag = _verlauf(mit_vokabeln).tage[HEUTE][FACH_ID]
    assert (eintrag.gefragt, eintrag.unbeantwortet) == (1, 1)

    # A withdrawn question is taken back in the log as well
    await _frage(hass)
    assert eintrag.gefragt == 2
    assert await manager.async_frage_abbrechen(KIND_ID)
    assert (eintrag.gefragt, eintrag.unbeantwortet) == (1, 1)
    assert eintrag.richtig == eintrag.falsch == 0


async def test_simulation_steht_nur_in_der_liste(
    hass: HomeAssistant,
    mit_vokabeln: MockConfigEntry,
    notify_calls: list[ServiceCall],
) -> None:
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    await manager.verwaltung.simulieren(ARBEIT_ID, 2, "messenger")
    for _ in range(2):
        await manager.async_antwort(KIND_ID, "x")
    await hass.async_block_till_done()
    assert manager.zustand(KIND_ID).simulation is None

    verlauf = _verlauf(mit_vokabeln)
    assert verlauf.simulationen == [
        SimErgebnis(HEUTE, ARBEIT_ID, FACH_ID, 0, 2, vollstaendig=True)
    ]
    # The answers of a simulation are no practice and are not counted per day
    assert verlauf.tage == {}


async def test_tageswechsel_haelt_den_lernstand_fest(
    hass: HomeAssistant, mit_vokabeln: MockConfigEntry, freezer: FrozenDateTimeFactory
) -> None:
    freezer.move_to("2026-10-07 00:00:10+02:00")
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    morgen = _verlauf(mit_vokabeln).tage[HEUTE + timedelta(days=1)][FACH_ID]
    assert (morgen.karten, morgen.sicher) == (4, 0)


async def test_abgeschaltet(
    hass: HomeAssistant,
    config_entry: MockConfigEntry,
    notify_calls: list[ServiceCall],
    hass_storage: dict[str, Any],
) -> None:
    """Switched off, nothing is logged, and what was logged before stays."""
    alt = KindVerlauf()
    alt.frage(HEUTE - timedelta(days=3), FACH_ID)
    hass_storage["learnbuddy.verlauf"] = {
        "version": 1,
        "minor_version": 1,
        "key": "learnbuddy.verlauf",
        "data": {"kinder": {KIND_ID: alt.to_dict()}},
    }
    hass.config_entries.async_update_entry(
        config_entry, options={**config_entry.options, "verlauf": False}
    )
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    manager: LearnBuddyManager = config_entry.runtime_data
    await hass.services.async_call(
        DOMAIN,
        "import_tasks",
        {"fach_id": FACH_ID, "inhalt": "Hund; dog", "lektion": "Unit 3"},
        blocking=True,
    )
    await _frage(hass)
    await manager.async_antwort(KIND_ID, "x")
    await _frage(hass)
    await manager.async_frage_abbrechen(KIND_ID)
    await manager.verwaltung.simulieren(ARBEIT_ID, 1, "messenger")
    await manager.async_antwort(KIND_ID, "x")
    await manager.async_flush()

    verlauf = _verlauf(config_entry)
    assert list(verlauf.tage) == [HEUTE - timedelta(days=3)]
    assert verlauf.simulationen == []
    uebersicht = manager.verwaltung.uebersicht()
    assert uebersicht["verlauf"] is False
    assert uebersicht["wochenreport"] is False
    with pytest.raises(VerwaltungError) as fehler:
        manager.verwaltung.fortschritt(KIND_ID, 30)
    assert fehler.value.schluessel == "verlauf_aus"
    with pytest.raises(VerwaltungError) as fehler:
        manager.verwaltung.wochenreport(KIND_ID, -1)
    assert fehler.value.schluessel == "wochenreport_aus"


async def test_nur_wochenreport_aus(
    hass: HomeAssistant, config_entry: MockConfigEntry, notify_calls: list[ServiceCall]
) -> None:
    hass.config_entries.async_update_entry(
        config_entry, options={**config_entry.options, "wochenreport": False}
    )
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    verwaltung = config_entry.runtime_data.verwaltung
    uebersicht = verwaltung.uebersicht()
    assert (uebersicht["verlauf"], uebersicht["wochenreport"]) == (True, False)
    assert verwaltung.fortschritt(KIND_ID, 7)["reihe"]
    with pytest.raises(VerwaltungError):
        verwaltung.wochenreport(KIND_ID, -1)


def _fuelle(manager: LearnBuddyManager) -> str:
    """Log two weeks by hand and return the ID of a task."""
    verlauf = manager.verlauf_store.kind(KIND_ID)
    aufgabe_id = next(iter(manager.task_stores[FACH_ID].aufgaben))
    # Last week: Monday 2026-09-28 to Sunday 2026-10-04
    for tag, ergebnisse in (
        (date(2026, 9, 22), ["richtig", "falsch"]),
        (date(2026, 9, 29), ["richtig", "richtig", "falsch", "falsch"]),
        (date(2026, 10, 1), ["richtig", "unbeantwortet"]),
    ):
        for ergebnis in ergebnisse:
            verlauf.frage(tag, FACH_ID)
            verlauf.ergebnis(
                tag, FACH_ID, ergebnis, lektion="Unit 3", aufgabe_id=aufgabe_id
            )
    verlauf.ergebnis(date(2026, 10, 1), FACH_ID, "falsch", aufgabe_id="geloescht")
    verlauf.lernstand(date(2026, 9, 22), FACH_ID, 4, 1)
    verlauf.lernstand(date(2026, 10, 1), FACH_ID, 4, 2)
    verlauf.simulation(SimErgebnis(date(2026, 9, 30), ARBEIT_ID, FACH_ID, 3.5, 5))
    verlauf.simulation(SimErgebnis(date(2026, 9, 30), "weg", FACH_ID, 1, 2, False))
    return aufgabe_id


async def test_fortschritt(hass: HomeAssistant, mit_vokabeln: MockConfigEntry) -> None:
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    aufgabe_id = _fuelle(manager)
    aufgabe = manager.task_stores[FACH_ID].aufgaben[aufgabe_id]
    daten = manager.verwaltung.fortschritt(KIND_ID, 30)

    assert (daten["seit"], daten["von"], daten["bis"]) == (
        "2026-09-22",
        "2026-09-07",
        "2026-10-06",
    )
    assert len(daten["reihe"]) == 30
    nach_tag = {e["tag"]: e for e in daten["reihe"]}
    assert nach_tag["2026-09-29"]["richtig"] == 2
    assert nach_tag["2026-09-29"]["falsch"] == 2
    assert nach_tag["2026-10-01"]["unbeantwortet"] == 1
    assert nach_tag["2026-09-08"]["trefferquote"] is None
    assert [f["name"] for f in daten["faecher"]] == ["Englisch"]
    lernstand = daten["faecher"][0]["lernstand"]
    assert len(lernstand) == 30
    assert lernstand[0] is None
    assert lernstand[-1] == 50
    assert daten["lektionen"] == [
        {
            "fach_id": FACH_ID,
            "fach": "Englisch",
            "lektion": "Unit 3",
            "richtig": 4,
            "falsch": 3,
            "fehlerquote": 43,
        }
    ]
    # The deleted task is left out
    assert daten["aufgaben"] == [
        {
            "fach": "Englisch",
            "aufgabe": aufgabe.frage_text("de>en"),
            "loesung": aufgabe.loesung_text("de>en"),
            "falsch": 3,
        }
    ]
    assert daten["simulationen"] == [
        {
            "tag": "2026-09-30",
            "fach": "Englisch",
            "thema": "Unit 3",
            "punkte": 3.5,
            "moeglich": 5,
            "prozent": 70,
            "vollstaendig": True,
        },
        {
            "tag": "2026-09-30",
            "fach": "Englisch",
            "thema": None,
            "punkte": 1,
            "moeglich": 2,
            "prozent": 50,
            "vollstaendig": False,
        },
    ]
    assert len(manager.verwaltung.fortschritt(KIND_ID, 7)["reihe"]) == 7
    for kind_id, tage, schluessel in (
        ("gibtsnicht", 30, "kind_unbekannt"),
        (KIND_ID, 31, "zeitraum_ungueltig"),
    ):
        with pytest.raises(VerwaltungError) as fehler:
            manager.verwaltung.fortschritt(kind_id, tage)
        assert fehler.value.schluessel == schluessel


async def test_wochenreport(hass: HomeAssistant, mit_vokabeln: MockConfigEntry) -> None:
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    _fuelle(manager)
    report = manager.verwaltung.wochenreport(KIND_ID, -1)

    assert (report["von"], report["bis"], report["laufend"]) == (
        "2026-09-28",
        "2026-10-04",
        False,
    )
    assert report["kennzahlen"] == {
        "gefragt": 6,
        "richtig": 3,
        "teilweise": 0,
        "falsch": 3,
        "unbeantwortet": 1,
        "trefferquote": 50,
        "tage_aktiv": 2,
    }
    assert report["vorwoche"]["gefragt"] == 2
    assert report["vorwoche"]["trefferquote"] == 50
    assert report["faecher"] == [{"name": "Englisch", "lernstand": 50, "vorher": 25}]
    assert [e["lektion"] for e in report["lektionen"]] == ["Unit 3"]
    assert len(report["aufgaben"]) == 1
    assert report["aufgaben"][0]["falsch"] == 2
    # The exam of the fixture is in three days
    assert report["arbeiten"] == [
        {
            "fach": "Englisch",
            "thema": "Unit 3",
            "art": "arbeit",
            "datum": "2026-10-09",
            "tage_bis": 3,
            "sicher": 0,
        }
    ]
    assert report["vorschlaege"] == []
    assert len(report["simulationen"]) == 2

    laufend = manager.verwaltung.wochenreport(KIND_ID, 0)
    assert (laufend["von"], laufend["laufend"]) == ("2026-10-05", True)
    assert laufend["kennzahlen"]["gefragt"] == 0
    assert laufend["vorwoche"]["gefragt"] == 6
    # The level known today (carried on from the last entry), not of the Sunday
    # still to come
    assert laufend["faecher"][0] == {"name": "Englisch", "lernstand": 50, "vorher": 50}
    for kind_id, versatz, schluessel in (
        ("gibtsnicht", -1, "kind_unbekannt"),
        (KIND_ID, 1, "zeitraum_ungueltig"),
    ):
        with pytest.raises(VerwaltungError) as fehler:
            manager.verwaltung.wochenreport(kind_id, versatz)
        assert fehler.value.schluessel == schluessel


async def test_websocket_und_speicher(
    hass: HomeAssistant,
    mit_vokabeln: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    hass_storage: dict[str, Any],
) -> None:
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    _fuelle(manager)
    ws = await hass_ws_client(hass)

    async def befehl(typ: str, /, **daten: Any) -> dict[str, Any]:
        await ws.send_json_auto_id({"type": f"learnbuddy/{typ}", **daten})
        antwort: dict[str, Any] = await ws.receive_json()
        return antwort

    uebersicht = (await befehl("overview"))["result"]
    assert (uebersicht["verlauf"], uebersicht["wochenreport"]) == (True, True)
    fortschritt = (await befehl("progress", kind_id=KIND_ID))["result"]
    assert len(fortschritt["reihe"]) == 30
    kurz = (await befehl("progress", kind_id=KIND_ID, tage=7))["result"]
    assert len(kurz["reihe"]) == 7
    report = (await befehl("weekly_report", kind_id=KIND_ID))["result"]
    assert report["von"] == "2026-09-28"
    fehler = await befehl("weekly_report", kind_id=KIND_ID, versatz=2)
    assert fehler["error"]["message"] == "zeitraum_ungueltig"

    # Written to its own file, and gone with the subject and with the entry
    await manager.async_flush()
    gespeichert = hass_storage["learnbuddy.verlauf"]
    assert gespeichert["version"] == 1
    assert "2026-09-29" in gespeichert["data"]["kinder"][KIND_ID]["tage"]

    hass.config_entries.async_remove_subentry(mit_vokabeln, FACH_ID)
    await hass.async_block_till_done()
    neu: LearnBuddyManager = mit_vokabeln.runtime_data
    assert neu.verlauf_store.kind(KIND_ID).tage == {}
    assert neu.verlauf_store.kind(KIND_ID).simulationen == []

    await neu.async_flush()
    assert await hass.config_entries.async_remove(mit_vokabeln.entry_id)
    await hass.async_block_till_done()
    assert "learnbuddy.verlauf" not in hass_storage
