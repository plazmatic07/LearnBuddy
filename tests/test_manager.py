"""Tests for the question cycle."""

from __future__ import annotations

from datetime import timedelta
from typing import Any

from freezegun.api import FrozenDateTimeFactory
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import Event, HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers import issue_registry as ir
from homeassistant.util import dt as dt_util
import pytest
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_capture_events,
    async_fire_time_changed,
)

from custom_components.learnbuddy.const import DOMAIN
from custom_components.learnbuddy.manager import (
    LearnBuddyManager,
    normalisiere_absender,
)

from .conftest import ARBEIT_ID, FACH_ID, KIND_ID


async def _zeit(hass: HomeAssistant, freezer: FrozenDateTimeFactory, wann: str) -> None:
    """Move the time and let all timers fire."""
    freezer.move_to(wann)
    async_fire_time_changed(hass)
    await hass.async_block_till_done()


async def _antworte(hass: HomeAssistant, text: str, **daten: Any) -> dict[str, Any]:
    ergebnis = await hass.services.async_call(
        DOMAIN,
        "submit_answer",
        {"text": text, **(daten or {"kind_id": KIND_ID})},
        blocking=True,
        return_response=True,
    )
    await hass.async_block_till_done()
    assert isinstance(ergebnis, dict)
    return ergebnis


def _loesung(manager: LearnBuddyManager) -> str:
    """Return the correct answer of the open question."""
    frage = manager.zustand(KIND_ID).offene_frage
    assert frage is not None
    aufgabe = manager.task_stores[FACH_ID].aufgaben[frage.aufgabe_id]
    return aufgabe.frage[frage.richtung.split(">")[1]]


@pytest.mark.parametrize(
    ("roh", "erwartet"),
    [
        ("+49 170 1234567", "491701234567"),
        ("0049170/1234567", "491701234567"),
        ("491701234567", "491701234567"),
        ("@Max_Chat", "@max_chat"),
        ("-1001234", "1001234"),
        ("", ""),
    ],
)
def test_normalisiere_absender(roh: str, erwartet: str) -> None:
    assert normalisiere_absender(roh) == erwartet


async def test_geplante_frage(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    mit_vokabeln: MockConfigEntry,
    notify_calls: list[ServiceCall],
) -> None:
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    fragen = async_capture_events(hass, "learnbuddy_question_sent")
    assert manager.naechste_abfrage[KIND_ID] == dt_util.parse_datetime(
        "2026-10-06 16:00:00+02:00"
    )

    await _zeit(hass, freezer, "2026-10-06 15:59:00+02:00")
    assert not notify_calls

    await _zeit(hass, freezer, "2026-10-06 16:00:01+02:00")
    assert len(notify_calls) == 1
    daten = notify_calls[0].data
    assert daten["message"].startswith("Hallo Max! 📚 Englisch: Was heißt „")
    # The hint of a task is only for the parents and never sent along
    assert "Nomen" not in daten["message"]
    assert daten["target"] == ["491701234567"]
    assert "data" not in daten

    frage = manager.zustand(KIND_ID).offene_frage
    assert frage is not None
    assert frage.arbeit_id == ARBEIT_ID
    assert frage.timeout_um - frage.gestellt_um == timedelta(minutes=60)
    assert len(fragen) == 1
    assert fragen[0].data == {
        "kind_id": KIND_ID,
        "fach_id": FACH_ID,
        "aufgabe_id": frage.aufgabe_id,
        "arbeit_id": ARBEIT_ID,
        "richtung": frage.richtung,
    }
    assert hass.states.get("sensor.max_offene_frage").state == "offen"


async def test_richtige_antwort(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    mit_vokabeln: MockConfigEntry,
    notify_calls: list[ServiceCall],
) -> None:
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    bewertungen: list[Event] = async_capture_events(hass, "learnbuddy_answer_evaluated")
    await _zeit(hass, freezer, "2026-10-06 16:00:01+02:00")
    frage = manager.zustand(KIND_ID).offene_frage
    assert frage is not None
    loesung = _loesung(manager)

    ergebnis = await _antworte(hass, f" {loesung.upper()}! ")
    assert ergebnis == {
        "ergebnis": "richtig",
        "loesung": loesung,
        "bewertet_von": "lokal",
    }
    assert notify_calls[-1].data["message"].startswith("Richtig, Max!")
    assert manager.zustand(KIND_ID).offene_frage is None

    stat = (
        manager.task_stores[FACH_ID]
        .aufgaben[frage.aufgabe_id]
        .statistik[frage.richtung]
    )
    assert (stat.richtig, stat.falsch) == (1, 0)
    assert stat.box == 2
    assert stat.zuletzt_gefragt is not None
    assert bewertungen[0].data["ergebnis"] == "richtig"
    assert bewertungen[0].data["aufgabe_id"] == frage.aufgabe_id
    assert "name" not in bewertungen[0].data
    assert hass.states.get("sensor.max_trefferquote").state == "100.0"
    assert hass.states.get("sensor.max_offene_frage").state == "keine"
    # The next question follows at the second slot of the day
    assert manager.naechste_abfrage[KIND_ID] == dt_util.parse_datetime(
        "2026-10-06 18:00:00+02:00"
    )


async def test_falsche_antwort(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    mit_vokabeln: MockConfigEntry,
    notify_calls: list[ServiceCall],
) -> None:
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    await _zeit(hass, freezer, "2026-10-06 16:00:01+02:00")
    frage = manager.zustand(KIND_ID).offene_frage
    assert frage is not None

    ergebnis = await _antworte(hass, "quatsch", absender="0049 170 1234567")
    assert ergebnis["ergebnis"] == "falsch"
    assert notify_calls[-1].data["message"].startswith("Leider nicht richtig, Max.")
    stat = (
        manager.task_stores[FACH_ID]
        .aufgaben[frage.aufgabe_id]
        .statistik[frage.richtung]
    )
    assert (stat.richtig, stat.falsch) == (0, 1)
    assert stat.box == 1
    assert stat.zuletzt_falsch is not None
    assert hass.states.get("sensor.max_trefferquote").state == "0.0"


async def test_fast_richtige_antwort(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    mit_vokabeln: MockConfigEntry,
    notify_calls: list[ServiceCall],
) -> None:
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    await _zeit(hass, freezer, "2026-10-06 16:00:01+02:00")
    loesung = _loesung(manager)
    vertippt = loesung[:-1] + ("x" if loesung[-1] != "x" else "y")
    ergebnis = await _antworte(hass, vertippt)
    # "dog" is too short for a typo, the other words are tolerated
    if len(loesung.removeprefix("to ")) >= 4:
        assert ergebnis["ergebnis"] == "fast_richtig"
        assert notify_calls[-1].data["message"].startswith("Fast richtig, Max!")
    else:
        assert ergebnis["ergebnis"] == "falsch"


async def test_timeout(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    mit_vokabeln: MockConfigEntry,
    notify_calls: list[ServiceCall],
) -> None:
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    bewertungen = async_capture_events(hass, "learnbuddy_answer_evaluated")
    await _zeit(hass, freezer, "2026-10-06 16:00:01+02:00")
    frage = manager.zustand(KIND_ID).offene_frage
    assert frage is not None

    await _zeit(hass, freezer, "2026-10-06 16:59:00+02:00")
    assert manager.zustand(KIND_ID).offene_frage is not None

    await _zeit(hass, freezer, "2026-10-06 17:00:02+02:00")
    assert manager.zustand(KIND_ID).offene_frage is None
    assert notify_calls[-1].data["message"].startswith("Die Zeit ist um, Max.")
    assert bewertungen[0].data["ergebnis"] == "unbeantwortet"
    stat = (
        manager.task_stores[FACH_ID]
        .aufgaben[frage.aufgabe_id]
        .statistik[frage.richtung]
    )
    assert (stat.richtig, stat.falsch) == (0, 0)
    assert stat.box == 1
    assert manager.naechste_abfrage[KIND_ID] == dt_util.parse_datetime(
        "2026-10-06 18:00:00+02:00"
    )


async def test_antwort_ohne_offene_frage(
    hass: HomeAssistant,
    mit_vokabeln: MockConfigEntry,
    notify_calls: list[ServiceCall],
) -> None:
    ergebnis = await _antworte(hass, "dog")
    assert ergebnis == {"ergebnis": "keine_offene_frage"}
    assert (
        notify_calls[-1]
        .data["message"]
        .startswith("Hallo Max, im Moment ist keine Frage offen.")
    )


async def test_antwort_auf_geloeschte_aufgabe(
    hass: HomeAssistant,
    mit_vokabeln: MockConfigEntry,
    notify_calls: list[ServiceCall],
) -> None:
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    await hass.services.async_call(
        DOMAIN, "ask_now", {"kind_id": KIND_ID}, blocking=True
    )
    frage = manager.zustand(KIND_ID).offene_frage
    assert frage is not None
    manager.task_stores[FACH_ID].remove(frage.aufgabe_id)
    ergebnis = await _antworte(hass, "dog")
    assert ergebnis == {"ergebnis": "keine_offene_frage"}
    assert manager.zustand(KIND_ID).offene_frage is None


async def test_ask_now(
    hass: HomeAssistant,
    mit_vokabeln: MockConfigEntry,
    notify_calls: list[ServiceCall],
) -> None:
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    bewertungen = async_capture_events(hass, "learnbuddy_answer_evaluated")
    await hass.services.async_call(
        DOMAIN, "ask_now", {"kind_id": KIND_ID}, blocking=True
    )
    erste = manager.zustand(KIND_ID).offene_frage
    assert erste is not None
    assert len(notify_calls) == 1

    # A second manual request replaces the open question with another task
    await hass.services.async_call(
        DOMAIN, "ask_now", {"kind_id": KIND_ID}, blocking=True
    )
    zweite = manager.zustand(KIND_ID).offene_frage
    assert zweite is not None
    assert zweite.aufgabe_id != erste.aufgabe_id
    assert bewertungen[0].data["ergebnis"] == "unbeantwortet"
    assert bewertungen[0].data["aufgabe_id"] == erste.aufgabe_id


async def test_ask_now_ohne_aufgaben(
    hass: HomeAssistant, setup_entry: MockConfigEntry
) -> None:
    with pytest.raises(ServiceValidationError) as fehler:
        await hass.services.async_call(
            DOMAIN, "ask_now", {"kind_id": KIND_ID}, blocking=True
        )
    assert fehler.value.translation_key == "keine_aufgaben"


async def test_ask_now_ohne_aktive_arbeit(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    mit_vokabeln: MockConfigEntry,
    notify_calls: list[ServiceCall],
) -> None:
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    # After the exam there is no schedule any more, a manual request still works
    await _zeit(hass, freezer, "2026-10-12 08:00:00+02:00")
    assert manager.naechste_abfrage[KIND_ID] is None
    await hass.services.async_call(
        DOMAIN, "ask_now", {"kind_id": KIND_ID}, blocking=True
    )
    frage = manager.zustand(KIND_ID).offene_frage
    assert frage is not None
    assert frage.arbeit_id is None


async def test_ask_now_sendefehler(
    hass: HomeAssistant, config_entry: MockConfigEntry
) -> None:
    # The notify action does not exist
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.services.async_call(
        DOMAIN,
        "import_tasks",
        {"fach_id": FACH_ID, "inhalt": "Hund;dog"},
        blocking=True,
    )
    with pytest.raises(HomeAssistantError) as fehler:
        await hass.services.async_call(
            DOMAIN, "ask_now", {"kind_id": KIND_ID}, blocking=True
        )
    assert fehler.value.translation_key == "senden_fehlgeschlagen"
    assert config_entry.runtime_data.zustand(KIND_ID).offene_frage is None


async def test_geplante_frage_ohne_aufgaben(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    setup_entry: MockConfigEntry,
    notify_calls: list[ServiceCall],
) -> None:
    manager: LearnBuddyManager = setup_entry.runtime_data
    await _zeit(hass, freezer, "2026-10-06 16:00:01+02:00")
    assert not notify_calls
    assert manager.zustand(KIND_ID).offene_frage is None
    # The slot is skipped instead of being retried in a loop
    assert manager.naechste_abfrage[KIND_ID] == dt_util.parse_datetime(
        "2026-10-06 18:00:00+02:00"
    )


async def test_sendefehler_wird_wiederholt(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    config_entry: MockConfigEntry,
    caplog: pytest.LogCaptureFixture,
) -> None:
    aufrufe: list[ServiceCall] = []
    fehlerhaft = True

    async def _notify(call: ServiceCall) -> None:
        aufrufe.append(call)
        if fehlerhaft:
            raise HomeAssistantError("kaputt")

    hass.services.async_register("notify", "test", _notify)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    manager: LearnBuddyManager = config_entry.runtime_data
    await hass.services.async_call(
        DOMAIN,
        "import_tasks",
        {"fach_id": FACH_ID, "inhalt": "Hund;dog"},
        blocking=True,
    )

    await _zeit(hass, freezer, "2026-10-06 16:00:01+02:00")
    assert len(aufrufe) == 1
    assert manager.zustand(KIND_ID).offene_frage is None
    assert caplog.text.count("Sending via notify.test failed") == 1

    # First retry after 30 seconds fails as well, it is only logged once
    await _zeit(hass, freezer, "2026-10-06 16:00:32+02:00")
    assert len(aufrufe) == 2
    assert caplog.text.count("Sending via notify.test failed") == 1

    fehlerhaft = False
    await _zeit(hass, freezer, "2026-10-06 16:02:33+02:00")
    assert len(aufrufe) == 3
    assert manager.zustand(KIND_ID).offene_frage is not None
    assert "Sending via notify.test works again" in caplog.text


async def test_sendefehler_gibt_auf(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    config_entry: MockConfigEntry,
) -> None:
    aufrufe: list[ServiceCall] = []

    async def _notify(call: ServiceCall) -> None:
        aufrufe.append(call)
        raise ValueError("kaputt")

    hass.services.async_register("notify", "test", _notify)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    manager: LearnBuddyManager = config_entry.runtime_data
    await hass.services.async_call(
        DOMAIN,
        "import_tasks",
        {"fach_id": FACH_ID, "inhalt": "Hund;dog"},
        blocking=True,
    )
    for wann in ("16:00:01", "16:00:32", "16:02:33", "16:12:34"):
        await _zeit(hass, freezer, f"2026-10-06 {wann}+02:00")
    assert len(aufrufe) == 4
    assert manager.zustand(KIND_ID).offene_frage is None
    assert manager.naechste_abfrage[KIND_ID] == dt_util.parse_datetime(
        "2026-10-06 18:00:00+02:00"
    )
    issue = ir.async_get(hass).async_get_issue(
        DOMAIN, f"senden_fehlgeschlagen_{KIND_ID}"
    )
    assert issue is not None
    assert issue.translation_placeholders == {"name": "Max", "ziel": "notify.test"}


async def test_feedback_wird_wiederholt(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    config_entry: MockConfigEntry,
) -> None:
    aufrufe: list[ServiceCall] = []
    fehlerhaft = False

    async def _notify(call: ServiceCall) -> None:
        aufrufe.append(call)
        if fehlerhaft:
            raise HomeAssistantError("kaputt")

    hass.services.async_register("notify", "test", _notify)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.services.async_call(
        DOMAIN,
        "import_tasks",
        {"fach_id": FACH_ID, "inhalt": "Hund;dog"},
        blocking=True,
    )
    await hass.services.async_call(
        DOMAIN, "ask_now", {"kind_id": KIND_ID}, blocking=True
    )
    fehlerhaft = True
    await _antworte(hass, "quatsch")
    assert len(aufrufe) == 2
    fehlerhaft = False
    await _zeit(hass, freezer, "2026-10-06 08:00:31+02:00")
    assert len(aufrufe) == 3
    assert aufrufe[2].data["message"] == aufrufe[1].data["message"]
    assert (
        ir.async_get(hass).async_get_issue(DOMAIN, f"senden_fehlgeschlagen_{KIND_ID}")
        is None
    )


async def test_neustart_mit_offener_frage(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    mit_vokabeln: MockConfigEntry,
    notify_calls: list[ServiceCall],
    hass_storage: dict[str, Any],
) -> None:
    await _zeit(hass, freezer, "2026-10-06 16:00:01+02:00")
    alt = mit_vokabeln.runtime_data.zustand(KIND_ID).offene_frage
    assert alt is not None

    assert await hass.config_entries.async_unload(mit_vokabeln.entry_id)
    assert mit_vokabeln.state is ConfigEntryState.NOT_LOADED
    assert (
        hass_storage["learnbuddy.config"]["data"]["kinder"][KIND_ID]["offene_frage"][
            "aufgabe_id"
        ]
        == alt.aufgabe_id
    )
    assert len(hass_storage[f"learnbuddy.{KIND_ID}_{FACH_ID}"]["data"]["aufgaben"]) == 2

    assert await hass.config_entries.async_setup(mit_vokabeln.entry_id)
    await hass.async_block_till_done()
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    assert manager.zustand(KIND_ID).offene_frage == alt

    # The timeout still fires after the restart
    await _zeit(hass, freezer, "2026-10-06 17:00:02+02:00")
    assert manager.zustand(KIND_ID).offene_frage is None
    assert notify_calls[-1].data["message"].startswith("Die Zeit ist um")


async def test_pause_und_resume(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    mit_vokabeln: MockConfigEntry,
    notify_calls: list[ServiceCall],
) -> None:
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    assert hass.states.get("switch.max_abfragen_aktiv").state == "on"

    await hass.services.async_call(DOMAIN, "pause", {"kind_id": KIND_ID}, blocking=True)
    assert hass.states.get("switch.max_abfragen_aktiv").state == "off"
    assert manager.naechste_abfrage[KIND_ID] is None
    await _zeit(hass, freezer, "2026-10-06 16:00:01+02:00")
    assert not notify_calls

    await hass.services.async_call(
        DOMAIN, "resume", {"kind_id": KIND_ID}, blocking=True
    )
    assert hass.states.get("switch.max_abfragen_aktiv").state == "on"
    assert manager.naechste_abfrage[KIND_ID] == dt_util.parse_datetime(
        "2026-10-06 18:00:00+02:00"
    )


async def test_pause_bis(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    mit_vokabeln: MockConfigEntry,
) -> None:
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    await hass.services.async_call(
        DOMAIN,
        "pause",
        {"kind_id": KIND_ID, "bis": "2026-10-07 17:00:00"},
        blocking=True,
    )
    assert hass.states.get("switch.max_abfragen_aktiv").state == "off"
    assert manager.naechste_abfrage[KIND_ID] == dt_util.parse_datetime(
        "2026-10-07 18:00:00+02:00"
    )
    freezer.move_to("2026-10-07 17:30:00+02:00")
    assert not manager.zustand(KIND_ID).ist_pausiert(dt_util.utcnow())


async def test_tageswechsel(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    setup_entry: MockConfigEntry,
) -> None:
    assert hass.states.get("sensor.max_nachste_arbeit").state == "2026-10-09"
    await _zeit(hass, freezer, "2026-10-10 00:00:11+02:00")
    assert hass.states.get("sensor.max_nachste_arbeit").state == "unknown"


async def test_daumen_hoch_stellt_eine_weitere_frage(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    mit_vokabeln: MockConfigEntry,
    notify_calls: list[ServiceCall],
) -> None:
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    await _zeit(hass, freezer, "2026-10-06 16:00:01+02:00")
    await _antworte(hass, _loesung(manager))
    assert manager.zustand(KIND_ID).offene_frage is None
    vorher = len(notify_calls)

    assert await _antworte(hass, "👍") == {"ergebnis": "zusatzaufgaben", "anzahl": 1}
    # Only the question is sent, a single one needs no announcement
    assert len(notify_calls) == vorher + 1
    # In a running conversation the question comes without a greeting
    assert notify_calls[-1].data["message"].startswith("Was heißt „")
    assert manager.zustand(KIND_ID).offene_frage is not None
    assert manager.zustand(KIND_ID).zusatz_offen == 0

    # After the answer nothing more follows
    await _antworte(hass, _loesung(manager))
    assert manager.zustand(KIND_ID).offene_frage is None


async def test_mehrere_zusatzaufgaben_nacheinander(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    mit_vokabeln: MockConfigEntry,
    notify_calls: list[ServiceCall],
) -> None:
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    zustand = manager.zustand(KIND_ID)

    ergebnis = await _antworte(hass, "noch 3 mehr")
    assert ergebnis == {"ergebnis": "zusatzaufgaben", "anzahl": 3}
    assert notify_calls[-2].data["message"] == (
        "Super, Max! 💪 Es kommen 3 weitere Aufgaben."
    )
    assert notify_calls[-1].data["message"].startswith("Was heißt „")
    assert zustand.zusatz_offen == 2

    # Each answer is followed by its result and the next question
    await _antworte(hass, _loesung(manager))
    assert notify_calls[-2].data["message"].startswith("Richtig, Max!")
    assert notify_calls[-1].data["message"].startswith("Was heißt „")
    assert zustand.zusatz_offen == 1
    await _antworte(hass, "quatsch")
    assert zustand.zusatz_offen == 0
    assert zustand.offene_frage is not None

    await _antworte(hass, _loesung(manager))
    assert zustand.offene_frage is None
    assert notify_calls[-1].data["message"].startswith("Richtig, Max!")
    # Only the last result tells how to get more
    assert (
        notify_calls[-1]
        .data["message"]
        .endswith(
            "\n\nLust auf mehr? Schick 👍 für eine weitere Aufgabe "
            "oder zum Beispiel „noch 5“."
        )
    )
    assert "Lust auf mehr" not in notify_calls[-3].data["message"]


async def test_zusatzaufgaben_werden_begrenzt(
    hass: HomeAssistant,
    mit_vokabeln: MockConfigEntry,
    notify_calls: list[ServiceCall],
) -> None:
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    ergebnis = await _antworte(hass, "noch 100")
    assert ergebnis == {"ergebnis": "zusatzaufgaben", "anzahl": 20}
    assert notify_calls[-2].data["message"] == (
        "Super, Max! 💪 Mehr als 20 auf einmal gehen nicht, "
        "es kommen 20 weitere Aufgaben."
    )
    assert manager.zustand(KIND_ID).zusatz_offen == 19


async def test_zusatzaufgaben_enden_ohne_antwort(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    mit_vokabeln: MockConfigEntry,
    notify_calls: list[ServiceCall],
) -> None:
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    zustand = manager.zustand(KIND_ID)
    await _antworte(hass, "noch 5")
    assert zustand.zusatz_offen == 4

    await _zeit(hass, freezer, "2026-10-06 09:00:02+02:00")
    assert notify_calls[-1].data["message"].startswith("Die Zeit ist um")
    assert zustand.offene_frage is None
    assert zustand.zusatz_offen == 0


async def test_zusatzaufgaben_enden_beim_abschalten(
    hass: HomeAssistant, mit_vokabeln: MockConfigEntry
) -> None:
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    zustand = manager.zustand(KIND_ID)
    await _antworte(hass, "noch 5")
    manager.async_set_aktiv(KIND_ID, False)
    assert zustand.zusatz_offen == 0
    # The open question may still be answered, but nothing follows
    await _antworte(hass, _loesung(manager))
    assert zustand.offene_frage is None

    # While switched off a wish is not accepted
    assert await _antworte(hass, "👍") == {"ergebnis": "keine_offene_frage"}


async def test_antwort_bei_offener_frage_ist_kein_wunsch(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    mit_vokabeln: MockConfigEntry,
) -> None:
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    await _zeit(hass, freezer, "2026-10-06 16:00:01+02:00")
    ergebnis = await _antworte(hass, "mehr")
    assert ergebnis["ergebnis"] == "falsch"
    assert manager.zustand(KIND_ID).offene_frage is None


async def test_zusatzaufgaben_ohne_aufgaben(
    hass: HomeAssistant,
    setup_entry: MockConfigEntry,
    notify_calls: list[ServiceCall],
) -> None:
    manager: LearnBuddyManager = setup_entry.runtime_data
    ergebnis = await _antworte(hass, "noch 3")
    assert ergebnis == {"ergebnis": "zusatzaufgaben", "anzahl": 3}
    assert notify_calls[-1].data["message"] == (
        "Max, im Moment gibt es keine Aufgaben für dich."
    )
    assert manager.zustand(KIND_ID).zusatz_offen == 0
    assert manager.zustand(KIND_ID).offene_frage is None
