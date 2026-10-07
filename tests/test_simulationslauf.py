"""Tests for simulating an exam: the sheet to print and the run in the messenger."""

from __future__ import annotations

from datetime import timedelta
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, patch

from freezegun.api import FrozenDateTimeFactory
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ServiceValidationError
from homeassistant.util import dt as dt_util
import pytest
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_capture_events,
    async_fire_time_changed,
    async_mock_service,
)
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from custom_components.learnbuddy.const import DOMAIN
from custom_components.learnbuddy.manager import LearnBuddyManager
from custom_components.learnbuddy.models import (
    Ergebnis,
    MatheAufgabe,
    SachAufgabe,
    SachForm,
    SimAufgabe,
    Simulation,
)

from .conftest import ARBEIT_ID, FACH_ID, KIND_DATEN, KIND_ID, subentry
from .test_bilder import bild_daten
from .test_bildversand import _telegram
from .test_mathe_ablauf import GENERATE, MATHE_ID
from .test_sach_ablauf import ANTWORT, FRAGE, SACH_DATEN, SACH_ID
from .test_websocket import Client

FERTIG = "learnbuddy_simulation_finished"
EINLEITUNG = (
    "Hallo Max! 📝 Wir üben für die Klassenarbeit in Englisch: Unit 3\n"
    "Es sind 2 Aufgaben. Ich stelle sie nacheinander, "
    "die Auswertung bekommst du am Ende. Viel Erfolg! 🍀"
)


def _sim(entry: MockConfigEntry) -> Simulation:
    manager: LearnBuddyManager = entry.runtime_data
    simulation = manager.zustand(KIND_ID).simulation
    assert simulation is not None
    return simulation


def _loesung(entry: MockConfigEntry, index: int | None = None) -> str:
    """Return the correct answer to a task of the running simulation."""
    manager: LearnBuddyManager = entry.runtime_data
    simulation = _sim(entry)
    eintrag = simulation.aufgaben[simulation.index if index is None else index]
    aufgabe = manager.task_stores[simulation.fach_id].aufgaben[eintrag.aufgabe_id]
    return aufgabe.loesung_text(eintrag.richtung)


def _frage_text(entry: MockConfigEntry, index: int) -> str:
    manager: LearnBuddyManager = entry.runtime_data
    simulation = _sim(entry)
    eintrag = simulation.aufgaben[index]
    aufgabe = manager.task_stores[simulation.fach_id].aufgaben[eintrag.aufgabe_id]
    return aufgabe.frage_text(eintrag.richtung)


async def _antworte(hass: HomeAssistant, text: str) -> dict[str, Any]:
    ergebnis = await hass.services.async_call(
        DOMAIN,
        "submit_answer",
        {"kind_id": KIND_ID, "text": text},
        blocking=True,
        return_response=True,
    )
    await hass.async_block_till_done()
    assert isinstance(ergebnis, dict)
    return ergebnis


def _text(notify_calls: list[ServiceCall], index: int = -1) -> str:
    nachricht: str = notify_calls[index].data["message"]
    return nachricht


def _statistik(entry: MockConfigEntry) -> list[dict[str, Any]]:
    manager: LearnBuddyManager = entry.runtime_data
    return [
        {k: v.to_dict() for k, v in aufgabe.statistik.items()}
        for store in manager.task_stores.values()
        for aufgabe in store.aufgaben.values()
    ]


@pytest.fixture
async def client(
    hass: HomeAssistant,
    mit_vokabeln: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
) -> Client:
    """Return a websocket client of an admin."""
    return Client(await hass_ws_client(hass))


def test_simulation_roundtrip() -> None:
    simulation = Simulation(
        arbeit_id="a1",
        fach_id="f1",
        aufgaben=[
            SimAufgabe("x", "de>en", ergebnis=Ergebnis.TEILWEISE, erklaerung="fehlt"),
            SimAufgabe("y", "sach", optionen=["A", "B", "C"]),
        ],
        index=1,
        timeout_um=dt_util.utcnow(),
    )
    assert Simulation.from_dict(simulation.to_dict()) == simulation


async def test_ablauf_im_messenger(
    hass: HomeAssistant,
    mit_vokabeln: MockConfigEntry,
    client: Client,
    notify_calls: list[ServiceCall],
) -> None:
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    bewertet = async_capture_events(hass, "learnbuddy_answer_evaluated")
    fertig = async_capture_events(hass, FERTIG)
    vorher = _statistik(mit_vokabeln)

    ergebnis = await client.ok(
        "exams/simulate", arbeit_id=ARBEIT_ID, anzahl=5, weg="messenger"
    )
    # Only two tasks exist; the child cannot receive images
    assert ergebnis == {"weg": "messenger", "anzahl": 2, "bilder": []}
    assert _text(notify_calls, 0) == EINLEITUNG
    assert _text(notify_calls, 1).startswith("Aufgabe 1 von 2: Was heißt „")
    assert len(notify_calls) == 2
    assert manager.bilder.ids == set()

    zustand = (await client.ok("dashboard", kind_id=KIND_ID))["zustand"]
    assert zustand["simulation"] == {"arbeit_id": ARBEIT_ID, "nummer": 1, "anzahl": 2}
    # Nothing else is asked meanwhile
    assert zustand["naechste_abfrage"] is None
    with pytest.raises(ServiceValidationError) as fehler:
        await hass.services.async_call(
            DOMAIN, "ask_now", {"kind_id": KIND_ID}, blocking=True
        )
    assert fehler.value.translation_key == "simulation_laeuft"
    assert await client.fehler(
        "exams/simulate", arbeit_id=ARBEIT_ID, anzahl=2, weg="messenger"
    ) == {"code": "invalid_format", "message": "simulation_laeuft"}

    # A correct answer gets no feedback, only the next task
    assert await _antworte(hass, _loesung(mit_vokabeln)) == {
        "ergebnis": "simulation",
        "nummer": 1,
        "anzahl": 2,
    }
    assert len(notify_calls) == 3
    assert _text(notify_calls).startswith("Aufgabe 2 von 2: Was heißt „")
    # 👍 is an answer now, not a wish for more
    frage = _frage_text(mit_vokabeln, 1)
    loesung = _loesung(mit_vokabeln, 1)
    assert await _antworte(hass, "👍") == {
        "ergebnis": "simulation",
        "nummer": 2,
        "anzahl": 2,
    }
    assert len(notify_calls) == 4
    assert _text(notify_calls) == (
        "Geschafft, Max! 🎓 Du hast 1 von 2 Punkten (50 %)."
        "\n\nDas schauen wir uns noch einmal an:"
        f"\n2. {frage} → {loesung}"
    )

    assert manager.zustand(KIND_ID).simulation is None
    assert not bewertet
    assert len(fertig) == 1
    assert fertig[0].data == {
        "kind_id": KIND_ID,
        "fach_id": FACH_ID,
        "arbeit_id": ARBEIT_ID,
        "punkte": 1.0,
        "moeglich": 2,
        "prozent": 50,
        "vollstaendig": True,
    }
    # The learning statistics are untouched and the schedule goes on
    assert _statistik(mit_vokabeln) == vorher
    assert manager.naechste_abfrage[KIND_ID] is not None


async def test_alles_richtig(
    hass: HomeAssistant,
    mit_vokabeln: MockConfigEntry,
    client: Client,
    notify_calls: list[ServiceCall],
) -> None:
    await client.ok("exams/simulate", arbeit_id=ARBEIT_ID, anzahl=1, weg="messenger")
    assert "Es sind 1 Aufgaben" in _text(notify_calls, 0)
    await _antworte(hass, _loesung(mit_vokabeln))
    assert _text(notify_calls) == (
        "Geschafft, Max! 🎓 Du hast 1 von 1 Punkten (100 %)."
        "\n\nAlles richtig – super! 🎉"
    )


async def test_offene_frage_wird_ersetzt(
    hass: HomeAssistant, mit_vokabeln: MockConfigEntry, client: Client
) -> None:
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    await hass.services.async_call(
        DOMAIN, "ask_now", {"kind_id": KIND_ID}, blocking=True
    )
    manager.zustand(KIND_ID).zusatz_offen = 3
    bewertet = async_capture_events(hass, "learnbuddy_answer_evaluated")
    await client.ok("exams/simulate", arbeit_id=ARBEIT_ID, anzahl=2, weg="messenger")
    assert [e.data["ergebnis"] for e in bewertet] == ["unbeantwortet"]
    zustand = manager.zustand(KIND_ID)
    assert zustand.offene_frage is None
    assert zustand.zusatz_offen == 0


async def test_frist_beendet_die_simulation(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    mit_vokabeln: MockConfigEntry,
    client: Client,
    notify_calls: list[ServiceCall],
) -> None:
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    fertig = async_capture_events(hass, FERTIG)
    await client.ok("exams/simulate", arbeit_id=ARBEIT_ID, anzahl=2, weg="messenger")
    simulation = _sim(mit_vokabeln)
    assert simulation.timeout_um == dt_util.utcnow() + timedelta(minutes=60)
    await _antworte(hass, _loesung(mit_vokabeln))
    frage = _frage_text(mit_vokabeln, 1)
    loesung = _loesung(mit_vokabeln, 1)

    freezer.tick(timedelta(minutes=61))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert _text(notify_calls) == (
        "Die Zeit ist um, Max. Die Übungsarbeit endet hier: "
        "1 von 2 Punkten (50 %)."
        "\n\nDas schauen wir uns noch einmal an:"
        f"\n2. {frage} → {loesung}"
    )
    assert manager.zustand(KIND_ID).simulation is None
    assert fertig[0].data["vollstaendig"] is False


async def test_abbrechen_und_pause(
    hass: HomeAssistant,
    mit_vokabeln: MockConfigEntry,
    client: Client,
    notify_calls: list[ServiceCall],
) -> None:
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    fertig = async_capture_events(hass, FERTIG)
    await client.ok("exams/simulate", arbeit_id=ARBEIT_ID, anzahl=2, weg="messenger")
    assert await client.ok("exams/simulate_stop", kind_id=KIND_ID) == {
        "abgebrochen": True
    }
    assert _text(notify_calls) == "Die Übungsarbeit wurde beendet, Max."
    assert manager.zustand(KIND_ID).simulation is None
    assert manager.naechste_abfrage[KIND_ID] is not None
    assert await client.ok("exams/simulate_stop", kind_id=KIND_ID) == {
        "abgebrochen": False
    }
    assert await client.fehler("exams/simulate_stop", kind_id="x") == {
        "code": "not_found",
        "message": "kind_unbekannt",
    }

    # Pausing ends a simulation silently
    await client.ok("exams/simulate", arbeit_id=ARBEIT_ID, anzahl=2, weg="messenger")
    anzahl = len(notify_calls)
    await hass.services.async_call(DOMAIN, "pause", {"kind_id": KIND_ID}, blocking=True)
    assert manager.zustand(KIND_ID).simulation is None
    assert len(notify_calls) == anzahl
    assert not fertig


async def test_neustart_mitten_in_der_simulation(
    hass: HomeAssistant,
    mit_vokabeln: MockConfigEntry,
    client: Client,
    notify_calls: list[ServiceCall],
) -> None:
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    await client.ok("exams/simulate", arbeit_id=ARBEIT_ID, anzahl=2, weg="messenger")
    await _antworte(hass, "falsch")
    await manager.config_store.async_save()
    await manager.task_stores[FACH_ID].async_save()

    assert await hass.config_entries.async_reload(mit_vokabeln.entry_id)
    await hass.async_block_till_done()
    simulation = _sim(mit_vokabeln)
    assert simulation.index == 1
    assert simulation.aufgaben[0].ergebnis is Ergebnis.FALSCH
    await _antworte(hass, _loesung(mit_vokabeln))
    assert "Du hast 1 von 2 Punkten (50 %)." in _text(notify_calls)


async def test_arbeit_und_aufgabe_verschwinden(
    hass: HomeAssistant,
    mit_vokabeln: MockConfigEntry,
    client: Client,
    notify_calls: list[ServiceCall],
) -> None:
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    store = manager.task_stores[FACH_ID]
    await client.ok("exams/simulate", arbeit_id=ARBEIT_ID, anzahl=2, weg="messenger")
    simulation = _sim(mit_vokabeln)
    # The second task is deleted before its turn: it does not count
    store.remove(simulation.aufgaben[1].aufgabe_id)
    await _antworte(hass, _loesung(mit_vokabeln))
    assert _text(notify_calls) == (
        "Geschafft, Max! 🎓 Du hast 1 von 1 Punkten (100 %)."
        "\n\nAlles richtig – super! 🎉"
        "\n\nNicht bewertbare Antworten: 1. Sie zählen nicht mit."
    )

    # The task that waits for its answer is deleted
    await client.ok("exams/simulate", arbeit_id=ARBEIT_ID, anzahl=1, weg="messenger")
    store.remove(_sim(mit_vokabeln).aufgaben[0].aufgabe_id)
    await _antworte(hass, "egal")
    assert _text(notify_calls) == (
        "Die Übungsarbeit ist zu Ende, Max. Leider konnte ich keine Antwort bewerten."
        "\n\nNicht bewertbare Antworten: 1. Sie zählen nicht mit."
    )
    assert await client.fehler(
        "exams/simulate", arbeit_id=ARBEIT_ID, anzahl=1, weg="messenger"
    ) == {"code": "invalid_format", "message": "keine_aufgaben"}


async def test_arbeit_wird_geloescht(
    hass: HomeAssistant, mit_vokabeln: MockConfigEntry, client: Client
) -> None:
    await client.ok("exams/simulate", arbeit_id=ARBEIT_ID, anzahl=2, weg="messenger")
    await client.ok("exams/delete", arbeit_id=ARBEIT_ID)
    await hass.async_block_till_done()
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    assert manager.zustand(KIND_ID).simulation is None


async def test_ausdruck(
    hass: HomeAssistant,
    mit_vokabeln: MockConfigEntry,
    client: Client,
    notify_calls: list[ServiceCall],
    upload_ordner: Path,
) -> None:
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    ergebnis = await client.ok(
        "exams/simulate", arbeit_id=ARBEIT_ID, anzahl=10, weg="ausdruck"
    )
    assert ergebnis["weg"] == "ausdruck"
    assert ergebnis["anzahl"] == 2
    (seite,) = ergebnis["bilder"]
    assert (upload_ordner / seite).read_bytes().startswith(b"\x89PNG")
    assert seite in manager.bilder.ids
    # Nothing is sent and nothing runs
    assert not notify_calls
    assert manager.zustand(KIND_ID).simulation is None

    for daten, fehler in (
        ({"anzahl": 0}, "anzahl_ungueltig"),
        ({"anzahl": 31}, "anzahl_ungueltig"),
        ({"weg": "fax"}, "weg_ungueltig"),
    ):
        eingabe = {"arbeit_id": ARBEIT_ID, "anzahl": 2, "weg": "ausdruck"} | daten
        assert await client.fehler("exams/simulate", **eingabe) == {
            "code": "invalid_format",
            "message": fehler,
        }
    assert await client.fehler(
        "exams/simulate", arbeit_id="x", anzahl=2, weg="ausdruck"
    ) == {"code": "not_found", "message": "arbeit_unbekannt"}

    manager.task_stores[FACH_ID].aufgaben.clear()
    assert await client.fehler(
        "exams/simulate", arbeit_id=ARBEIT_ID, anzahl=2, weg="ausdruck"
    ) == {"code": "invalid_format", "message": "keine_aufgaben"}


async def test_telegram_bekommt_das_blatt(
    hass: HomeAssistant, hass_ws_client: WebSocketGenerator
) -> None:
    fotos = async_mock_service(hass, "telegram_bot", "send_photo")
    texte = async_mock_service(hass, "notify", "send_message")
    entry = await _telegram(hass)
    manager: LearnBuddyManager = entry.runtime_data
    store = manager.task_stores[MATHE_ID]
    bild = await manager.bilder.async_speichere(bild_daten())
    store.add(
        MatheAufgabe(fach_id=MATHE_ID, aufgabe="Lies ab.", loesung="90", bild=bild)
    )
    for zahl in range(2, 9):
        store.add(
            MatheAufgabe(fach_id=MATHE_ID, aufgabe=f"{zahl} · 7", loesung=str(zahl * 7))
        )
    client = Client(await hass_ws_client(hass))
    arbeit_id = (
        await client.ok(
            "exams/save",
            arbeit={
                "fach_id": MATHE_ID,
                "datum": "2026-10-09",
                "thema": "Einmaleins",
                "art": "hue",
                "antwortfrist_minuten": 20,
            },
        )
    )["arbeit_id"]
    await hass.async_block_till_done()
    manager = entry.runtime_data
    assert (await client.ok("overview"))["arbeiten"][0]["simulierbar"] == {
        "ausdruck": 8,
        "messenger": 8,
    }

    ergebnis = await client.ok(
        "exams/simulate", arbeit_id=arbeit_id, anzahl=8, weg="messenger"
    )
    assert ergebnis["anzahl"] == 8
    simulation = manager.zustand(KIND_ID).simulation
    assert simulation is not None
    # The time to answer of the exam applies
    assert simulation.timeout_um == dt_util.utcnow() + timedelta(minutes=20)

    # Eight tasks with room to calculate need two pages
    erste = simulation.aufgaben[0].aufgabe_id
    mit_bild = isinstance(a := store.aufgaben[erste], MatheAufgabe) and a.bild
    seiten = [f for f in fotos if not f.data["caption"].startswith("Aufgabe ")]
    assert len(seiten) == 2
    assert (
        seiten[0]
        .data["caption"]
        .startswith(
            "Hallo Max! 📝 Wir üben für die Hausaufgabenüberprüfung in Mathe: Einmaleins"
        )
    )
    assert seiten[1].data["caption"] == "Seite 2"
    assert len(fotos) == (3 if mit_bild else 2)
    assert len(texte) == (0 if mit_bild else 1)
    assert len(manager.bilder.ids) == 3

    # Answer everything; the task with the image arrives as a photo
    for _ in range(8):
        index = simulation.index
        aufgabe = store.aufgaben[simulation.aufgaben[index].aufgabe_id]
        assert isinstance(aufgabe, MatheAufgabe)
        await hass.services.async_call(
            DOMAIN,
            "submit_answer",
            {"kind_id": KIND_ID, "text": aufgabe.loesung},
            blocking=True,
        )
    await hass.async_block_till_done()
    assert len(fotos) == 3
    assert fotos[-1].data["caption"].endswith(": Lies ab.") or any(
        f.data["caption"].endswith(": Lies ab.") for f in fotos
    )
    assert texte[-1].data["message"] == (
        "Geschafft, Max! 🎓 Du hast 8 von 8 Punkten (100 %)."
        "\n\nAlles richtig – super! 🎉"
    )


async def test_sachfach_mit_teilpunkten(
    hass: HomeAssistant,
    notify_calls: list[ServiceCall],
    hass_ws_client: WebSocketGenerator,
) -> None:
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="LearnBuddy",
        data={},
        options={"timeout_minuten": 60, "sprache": "de", "ki_entity": "ai_task.test"},
        subentries_data=[
            subentry("kind", KIND_ID, "Max", KIND_DATEN),
            subentry("fach", SACH_ID, "Biologie (Max)", SACH_DATEN),
            subentry(
                "arbeit",
                "bioarbeit",
                "2026-10-09 Biologie (Max): Fotosynthese",
                {"fach_id": SACH_ID, "datum": "2026-10-09", "thema": "Fotosynthese"},
            ),
        ],
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    manager: LearnBuddyManager = entry.runtime_data
    store = manager.task_stores[SACH_ID]
    store.add(SachAufgabe(fach_id=SACH_ID, frage=FRAGE, antwort=ANTWORT))
    client = Client(await hass_ws_client(hass))

    await client.ok("exams/simulate", arbeit_id="bioarbeit", anzahl=1, weg="messenger")
    assert _text(notify_calls) == f"Aufgabe 1 von 1: {FRAGE}"
    with patch(
        GENERATE,
        AsyncMock(
            return_value={"ergebnis": "teilweise", "fehlt": "Es fehlt, wo genau."}
        ),
    ):
        await _antworte(hass, "in den Blättern")
    assert _text(notify_calls) == (
        "Geschafft, Max! 🎓 Du hast 0,5 von 1 Punkten (50 %)."
        "\n\nDas schauen wir uns noch einmal an:"
        f"\n1. {FRAGE} → {ANTWORT} 💡 Es fehlt, wo genau."
    )

    # The AI fails: the answer does not count
    await client.ok("exams/simulate", arbeit_id="bioarbeit", anzahl=1, weg="messenger")
    with patch(GENERATE, AsyncMock(side_effect=RuntimeError)):
        await _antworte(hass, "in den Blättern")
    assert _text(notify_calls).startswith("Die Übungsarbeit ist zu Ende, Max.")

    # A choice question shows its options in a fixed order and takes a letter
    store.aufgaben.clear()
    store.add(
        SachAufgabe(
            fach_id=SACH_ID,
            frage="Welcher Farbstoff?",
            antwort="Chlorophyll",
            form=SachForm.AUSWAHL,
            falsche_optionen=["Karotin", "Melanin"],
        )
    )
    await client.ok("exams/simulate", arbeit_id="bioarbeit", anzahl=1, weg="messenger")
    simulation = manager.zustand(KIND_ID).simulation
    assert simulation is not None
    optionen = simulation.aufgaben[0].optionen
    assert optionen is not None
    assert _text(notify_calls) == (
        "Aufgabe 1 von 1: Welcher Farbstoff?\n"
        + "\n".join(f"{b}) {o}" for b, o in zip("ABC", optionen, strict=True))
        + "\nAntworte mit dem Buchstaben."
    )
    await _antworte(hass, "ABC"[optionen.index("Chlorophyll")])
    assert "Du hast 1 von 1 Punkten (100 %)." in _text(notify_calls)


async def test_gemeinsames_bild_steht_einmal_auf_dem_blatt(
    hass: HomeAssistant, hass_ws_client: WebSocketGenerator
) -> None:
    async_mock_service(hass, "telegram_bot", "send_photo")
    async_mock_service(hass, "notify", "send_message")
    entry = await _telegram(hass)
    manager: LearnBuddyManager = entry.runtime_data
    store = manager.task_stores[MATHE_ID]
    bild = await manager.bilder.async_speichere(bild_daten())
    for teil in "abc":
        store.add(
            MatheAufgabe(
                fach_id=MATHE_ID, aufgabe=f"{teil}) Lies ab.", loesung="1", bild=bild
            )
        )
    for zahl in range(4):
        store.add(
            MatheAufgabe(fach_id=MATHE_ID, aufgabe=f"{zahl} + 1", loesung=str(zahl + 1))
        )
    client = Client(await hass_ws_client(hass))
    arbeit_id = (
        await client.ok(
            "exams/save",
            arbeit={"fach_id": MATHE_ID, "datum": "2026-10-09", "thema": "Diagramme"},
        )
    )["arbeit_id"]
    await hass.async_block_till_done()
    manager = entry.runtime_data
    arbeit = manager.arbeiten[arbeit_id]

    for _ in range(5):
        eintraege = manager.simulation_auswahl(arbeit, 7, messenger=False)
        mit_bild = [
            i
            for i, e in enumerate(eintraege)
            if isinstance(a := store.aufgaben[e.aufgabe_id], MatheAufgabe) and a.bild
        ]
        # The three parts follow each other
        assert len(mit_bild) == 3
        assert mit_bild[2] - mit_bild[0] == 2

    with patch(
        "custom_components.learnbuddy.manager.zeichne", return_value=[b"x"]
    ) as zeichne:
        await manager.async_simulation_blatt(arbeit, eintraege)
    gedruckt = zeichne.call_args.args[1]
    assert len(gedruckt) == 7
    assert sum(1 for aufgabe in gedruckt if aufgabe.bild is not None) == 1


# ---------------------------------------------------------------------------
# Planned simulations
# ---------------------------------------------------------------------------

ARBEIT_FELDER: dict[str, Any] = {
    "datum": "2026-10-09",
    "thema": "Unit 3",
    "abfragen_pro_tag": 2,
    "start_tage_vorher": 7,
    "intensivierung": False,
}


async def _plane(entry: MockConfigEntry, hass: HomeAssistant, **felder: Any) -> None:
    """Save the exam; the websocket would not survive the jumps in time."""
    manager: LearnBuddyManager = entry.runtime_data
    await manager.verwaltung.arbeit_speichern(ARBEIT_ID, ARBEIT_FELDER | felder)
    await hass.async_block_till_done()


async def _arbeit(entry: MockConfigEntry) -> dict[str, Any]:
    manager: LearnBuddyManager = entry.runtime_data
    arbeiten: list[dict[str, Any]] = manager.verwaltung.uebersicht()["arbeiten"]
    return arbeiten[0]


async def _springe(
    hass: HomeAssistant, freezer: FrozenDateTimeFactory, wann: str
) -> None:
    freezer.move_to(wann)
    async_fire_time_changed(hass)
    await hass.async_block_till_done()


async def test_geplante_simulation(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    mit_vokabeln: MockConfigEntry,
    client: Client,
    notify_calls: list[ServiceCall],
) -> None:
    # A time without a zone is local time
    await _plane(
        mit_vokabeln, hass, simulation_um="2026-10-06T15:00", simulation_anzahl=2
    )
    arbeit = await _arbeit(mit_vokabeln)
    assert arbeit["simulation_um"] == "2026-10-06T13:00:00+00:00"
    assert arbeit["simulation_anzahl"] == 2
    assert arbeit["simulation_geplant"] is True
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    assert manager.zustand(KIND_ID).simulation is None

    await _springe(hass, freezer, "2026-10-06 14:59:00+02:00")
    assert manager.zustand(KIND_ID).simulation is None
    await _springe(hass, freezer, "2026-10-06 15:00:01+02:00")
    simulation = manager.zustand(KIND_ID).simulation
    assert simulation is not None
    assert len(simulation.aufgaben) == 2
    assert any(call.data["message"] == EINLEITUNG for call in notify_calls)
    assert (await _arbeit(mit_vokabeln))["simulation_geplant"] is False

    # It is sent once, also when the exam is saved again
    assert await manager.async_simulation_abbrechen(KIND_ID)
    await manager.config_store.async_save()
    await _plane(
        mit_vokabeln, hass, simulation_um="2026-10-06T15:00", simulation_anzahl=2
    )
    await _springe(hass, freezer, "2026-10-06 15:05:00+02:00")
    assert manager.zustand(KIND_ID).simulation is None
    assert (await _arbeit(mit_vokabeln))["simulation_geplant"] is False

    # A new time plans it again
    await _plane(mit_vokabeln, hass, simulation_um="2026-10-06T16:00:00+02:00")
    arbeit = await _arbeit(mit_vokabeln)
    assert (arbeit["simulation_geplant"], arbeit["simulation_anzahl"]) == (True, 10)
    # Removing the time cancels the plan
    await _plane(mit_vokabeln, hass, simulation_um=None)
    await _springe(hass, freezer, "2026-10-06 16:00:01+02:00")
    assert manager.zustand(KIND_ID).simulation is None
    assert (await _arbeit(mit_vokabeln))["simulation_um"] is None


async def test_geplante_simulation_eingaben(
    hass: HomeAssistant, mit_vokabeln: MockConfigEntry, client: Client
) -> None:
    for felder, fehler in (
        ({"simulation_um": "2026-10-06T07:00"}, "simulation_um_vergangen"),
        ({"simulation_um": "morgen"}, "simulation_um_ungueltig"),
        (
            {"simulation_um": "2026-10-07T15:00", "simulation_anzahl": 31},
            "anzahl_ungueltig",
        ),
    ):
        assert await client.fehler(
            "exams/save", arbeit_id=ARBEIT_ID, arbeit=ARBEIT_FELDER | felder
        ) == {"code": "invalid_format", "message": fehler}


async def test_geplante_simulation_wird_uebersprungen(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    mit_vokabeln: MockConfigEntry,
    client: Client,
    notify_calls: list[ServiceCall],
) -> None:
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    # The child is paused when the time comes
    await _plane(mit_vokabeln, hass, simulation_um="2026-10-06T15:00")
    await hass.services.async_call(DOMAIN, "pause", {"kind_id": KIND_ID}, blocking=True)
    await _springe(hass, freezer, "2026-10-06 15:00:01+02:00")
    assert manager.zustand(KIND_ID).simulation is None
    assert not notify_calls
    assert (await _arbeit(mit_vokabeln))["simulation_geplant"] is False
    await hass.services.async_call(
        DOMAIN, "resume", {"kind_id": KIND_ID}, blocking=True
    )

    # There is nothing to ask
    manager.task_stores[FACH_ID].aufgaben.clear()
    await _plane(mit_vokabeln, hass, simulation_um="2026-10-06T17:00")
    await _springe(hass, freezer, "2026-10-06 17:00:01+02:00")
    assert manager.zustand(KIND_ID).simulation is None
    assert (await _arbeit(mit_vokabeln))["simulation_geplant"] is False


@pytest.mark.parametrize(("stunden", "gestartet"), [(1, True), (7, False)])
async def test_verpasste_simulation(  # noqa: PLR0917
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    mit_vokabeln: MockConfigEntry,
    client: Client,
    stunden: int,
    gestartet: bool,
) -> None:
    await _plane(
        mit_vokabeln, hass, simulation_um="2026-10-06T09:00", simulation_anzahl=1
    )
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    await manager.task_stores[FACH_ID].async_save()
    # Home Assistant is off at that time and starts later
    assert await hass.config_entries.async_unload(mit_vokabeln.entry_id)
    freezer.move_to(f"2026-10-06 {9 + stunden}:00:00+02:00")
    assert await hass.config_entries.async_setup(mit_vokabeln.entry_id)
    await hass.async_block_till_done()
    freezer.tick(timedelta(seconds=31))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    manager = mit_vokabeln.runtime_data
    assert (manager.zustand(KIND_ID).simulation is not None) is gestartet
