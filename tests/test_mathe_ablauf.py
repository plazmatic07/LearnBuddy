"""Tests for math subjects: asking, evaluating, explaining and generating."""

from __future__ import annotations

from datetime import timedelta
import os
import time
from typing import Any
from unittest.mock import AsyncMock, patch

from freezegun.api import FrozenDateTimeFactory
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers import issue_registry as ir
import pytest
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_capture_events,
    async_fire_time_changed,
)
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from custom_components.learnbuddy.ai import (
    AUFGABEN_SCHEMA,
    LOESUNG_SCHEMA,
    MATHE_SCHEMA,
    RECHENWEG_SCHEMA,
    GenerierteAufgabe,
    bereinige_mathetext,
    parse_aufgaben,
    parse_rechenweg,
)
from custom_components.learnbuddy.const import DOMAIN
from custom_components.learnbuddy.manager import LearnBuddyManager
from custom_components.learnbuddy.models import (
    AufgabenTyp,
    MatheAufgabe,
    Quelle,
    Verifikation,
    aufgabe_from_dict,
)

from .conftest import FACH_ID, KIND_DATEN, KIND_ID, subentry
from .test_bilder import bild_daten
from .test_websocket import Client

GENERATE = "custom_components.learnbuddy.ai._async_generate_data"
MATHE_ID = "mathe1"
MATHE_DATEN: dict[str, Any] = {"kind_id": KIND_ID, "name": "Mathe", "typ": "mathe"}
TIPP = (
    "\n\nLust auf mehr? Schick 👍 für eine weitere Aufgabe oder zum Beispiel „noch 5“."
)
ANGEBOT = "\n\nSoll ich dir den Rechenweg erklären? Antworte mit Ja."


def _entry(hass: HomeAssistant, **optionen: Any) -> MockConfigEntry:
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="LearnBuddy",
        data={},
        options={"timeout_minuten": 60, "sprache": "de", **optionen},
        subentries_data=[
            subentry("kind", KIND_ID, "Max", KIND_DATEN),
            subentry("fach", MATHE_ID, "Mathe (Max)", MATHE_DATEN),
        ],
    )
    entry.add_to_hass(hass)
    return entry


@pytest.fixture
async def mathe(
    hass: HomeAssistant, notify_calls: list[ServiceCall]
) -> MockConfigEntry:
    """Set up a child with a math subject, without an AI entity."""
    entry = _entry(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


@pytest.fixture
async def mathe_ki(
    hass: HomeAssistant, notify_calls: list[ServiceCall]
) -> MockConfigEntry:
    """Set up a child with a math subject and an AI entity."""
    entry = _entry(hass, ki_entity="ai_task.test")
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


def _neu(
    entry: MockConfigEntry, aufgabe: str, loesung: str, **felder: Any
) -> MatheAufgabe:
    manager: LearnBuddyManager = entry.runtime_data
    neu = MatheAufgabe(fach_id=MATHE_ID, aufgabe=aufgabe, loesung=loesung, **felder)
    manager.task_stores[MATHE_ID].add(neu)
    return neu


async def _frage(hass: HomeAssistant) -> None:
    await hass.services.async_call(
        DOMAIN, "ask_now", {"kind_id": KIND_ID}, blocking=True
    )
    await hass.async_block_till_done()


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


# ---------------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------------


def test_mathe_aufgabe_roundtrip() -> None:
    aufgabe = MatheAufgabe(
        fach_id="f1",
        aufgabe="3/4 + 1/8",
        loesung="7/8",
        alternativen=["0,875"],
        rechenweg=["Erweitere 3/4 auf 6/8.", "6/8 + 1/8 = 7/8"],
        schwierigkeit=2,
        verifikation=Verifikation.RECHNERISCH,
        lektion="Brüche",
        quelle=Quelle.GENERIERT,
        geprueft=False,
        hinweis="p.12",
        seite=40,
    )
    aufgabe.statistik_fuer("mathe").richtig = 1
    daten = aufgabe.to_dict()
    assert daten["typ"] == "mathe"
    assert aufgabe_from_dict(daten) == aufgabe
    assert aufgabe.typ is AufgabenTyp.MATHE
    assert aufgabe.fragbar("mathe")
    assert not aufgabe.fragbar("de>en")
    assert aufgabe.frage_text("mathe") == "3/4 + 1/8"
    assert aufgabe.loesung_text("mathe") == "7/8"
    assert aufgabe_from_dict({**daten, "typ": "chemie"}) is None


# ---------------------------------------------------------------------------
# Asking and evaluating
# ---------------------------------------------------------------------------


async def test_import_und_richtige_antwort(
    hass: HomeAssistant, mathe: MockConfigEntry, notify_calls: list[ServiceCall]
) -> None:
    manager: LearnBuddyManager = mathe.runtime_data
    ergebnis = await hass.services.async_call(
        DOMAIN,
        "import_tasks",
        {
            "fach_id": MATHE_ID,
            "inhalt": "# Kopfrechnen\n7 · 8 = ?; 56 | sechsundfünfzig; Einmaleins\n"
            "7 · 8 = ?; 56\nnur eine Spalte\n; 5\n",
            "lektion": "Einmaleins",
        },
        blocking=True,
        return_response=True,
    )
    assert ergebnis == {"importiert": 1, "uebersprungen": 1, "fehlerzeilen": [4, 5]}
    (aufgabe,) = manager.task_stores[MATHE_ID].aufgaben.values()
    assert isinstance(aufgabe, MatheAufgabe)
    assert aufgabe.aufgabe == "7 · 8 = ?"
    assert aufgabe.loesung == "56"
    assert aufgabe.alternativen == ["sechsundfünfzig"]
    assert aufgabe.hinweis == "Einmaleins"
    assert aufgabe.lektion == "Einmaleins"

    fragen = async_capture_events(hass, "learnbuddy_question_sent")
    await _frage(hass)
    assert _text(notify_calls) == "Hallo Max! 🔢 Mathe: 7 · 8 = ?"
    assert fragen[0].data["richtung"] == "mathe"

    assert await _antworte(hass, " 56 ") == {
        "ergebnis": "richtig",
        "loesung": "56",
        "bewertet_von": "lokal",
    }
    assert _text(notify_calls) == "Richtig, Max! 🎉 Die Lösung ist 56." + TIPP
    stat = aufgabe.statistik["mathe"]
    assert (stat.gefragt, stat.richtig, stat.falsch, stat.box) == (1, 1, 0, 2)


async def test_falsch_ohne_ki_ohne_rechenweg(
    hass: HomeAssistant, mathe: MockConfigEntry, notify_calls: list[ServiceCall]
) -> None:
    manager: LearnBuddyManager = mathe.runtime_data
    _neu(mathe, "7 · 8", "56")
    await _frage(hass)
    assert (await _antworte(hass, "54"))["ergebnis"] == "falsch"
    # Nobody could explain the solution, so it is not offered
    assert _text(notify_calls) == (
        "Leider nicht richtig, Max. Die Lösung ist 56. 💪" + TIPP
    )
    assert manager.zustand(KIND_ID).rechenweg_angebot is None


async def test_einheit_fehlt_ist_fast_richtig(
    hass: HomeAssistant, mathe: MockConfigEntry, notify_calls: list[ServiceCall]
) -> None:
    aufgabe = _neu(mathe, "Wie lang ist die Strecke?", "3 m")
    await _frage(hass)
    assert (await _antworte(hass, "3"))["ergebnis"] == "fast_richtig"
    assert _text(notify_calls).startswith(
        "Fast richtig, Max! 👍 Denk an die Einheit: 3 m."
    )
    assert aufgabe.statistik["mathe"].richtig == 1


async def test_timeout(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    mathe: MockConfigEntry,
    notify_calls: list[ServiceCall],
) -> None:
    _neu(mathe, "7 · 8", "56")
    await _frage(hass)
    freezer.move_to("2026-10-06 09:00:02+02:00")
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert _text(notify_calls) == "Die Zeit ist um, Max. Die Lösung ist 56."


async def test_textantwort_ohne_ki_ist_falsch(
    hass: HomeAssistant, mathe: MockConfigEntry
) -> None:
    _neu(mathe, "Ist 7 gerade oder ungerade?", "ungerade")
    await _frage(hass)
    assert (await _antworte(hass, "7 ist ungerade")) == {
        "ergebnis": "falsch",
        "loesung": "ungerade",
        "bewertet_von": "lokal",
    }


async def test_textantwort_bewertet_die_ki(
    hass: HomeAssistant, mathe_ki: MockConfigEntry, notify_calls: list[ServiceCall]
) -> None:
    _neu(mathe_ki, "Ist 7 gerade oder ungerade?", "ungerade", alternativen=["odd"])
    await _frage(hass)
    with patch(GENERATE, AsyncMock(return_value={"ergebnis": "richtig"})) as generate:
        ergebnis = await _antworte(hass, "7 ist ungerade")
    assert ergebnis["ergebnis"] == "richtig"
    assert ergebnis["bewertet_von"] == "ki"
    assert generate.call_args.kwargs["structure"] is MATHE_SCHEMA
    prompt = generate.call_args.kwargs["instructions"]
    assert "Ist 7 gerade oder ungerade?" in prompt
    assert "<answer>\n7 ist ungerade\n</answer>" in prompt
    assert "odd" in prompt
    assert "Max" not in prompt

    # A failing AI leaves the answer wrong
    await _frage(hass)
    with patch(GENERATE, AsyncMock(side_effect=HomeAssistantError("kaputt"))):
        ergebnis = await _antworte(hass, "7 ist ungerade")
    assert ergebnis["ergebnis"] == "falsch"
    assert ergebnis["bewertet_von"] == "lokal"

    # Numbers never need the AI
    _neu(mathe_ki, "7 · 8", "56")
    manager: LearnBuddyManager = mathe_ki.runtime_data
    del manager.task_stores[MATHE_ID].aufgaben[
        next(iter(manager.task_stores[MATHE_ID].aufgaben))
    ]
    await _frage(hass)
    with patch(GENERATE, AsyncMock()) as generate:
        assert (await _antworte(hass, "56"))["ergebnis"] == "richtig"
    generate.assert_not_called()


# ---------------------------------------------------------------------------
# Explaining the solution on request
# ---------------------------------------------------------------------------


async def test_gespeicherter_rechenweg_auf_nachfrage(
    hass: HomeAssistant, mathe: MockConfigEntry, notify_calls: list[ServiceCall]
) -> None:
    manager: LearnBuddyManager = mathe.runtime_data
    zustand = manager.zustand(KIND_ID)
    aufgabe = _neu(
        mathe,
        "3/4 + 1/8",
        "7/8",
        rechenweg=["Erweitere 3/4 auf 6/8.", "6/8 + 1/8 = 7/8"],
    )
    await _frage(hass)
    await _antworte(hass, "4/12")
    assert _text(notify_calls) == (
        "Leider nicht richtig, Max. Die Lösung ist 7/8. 💪" + ANGEBOT
    )
    angebot = zustand.rechenweg_angebot
    assert angebot is not None
    assert (angebot.fach_id, angebot.aufgabe_id) == (MATHE_ID, aufgabe.id)

    assert await _antworte(hass, "Ja bitte!") == {"ergebnis": "rechenweg"}
    assert _text(notify_calls) == (
        "So geht es, Max:\n1. Erweitere 3/4 auf 6/8.\n2. 6/8 + 1/8 = 7/8"
    )
    assert zustand.rechenweg_angebot is None
    # The offer is gone afterwards
    assert await _antworte(hass, "ja") == {"ergebnis": "keine_offene_frage"}


async def test_rechenweg_von_der_ki_wird_gespeichert(
    hass: HomeAssistant, mathe_ki: MockConfigEntry, notify_calls: list[ServiceCall]
) -> None:
    manager: LearnBuddyManager = mathe_ki.runtime_data
    aufgabe = _neu(mathe_ki, "12 · 12", "144")
    await _frage(hass)
    await _antworte(hass, "124")
    assert _text(notify_calls).endswith(ANGEBOT)

    schritte = {
        "schritte": ["Rechne 12 * 10 = 120.", " 12 · 2 = 24 ", "120 + 24 = 12^2"]
    }
    with patch(GENERATE, AsyncMock(return_value=schritte)) as generate:
        assert await _antworte(hass, "👍") == {"ergebnis": "rechenweg"}
    assert generate.call_args.kwargs["structure"] is RECHENWEG_SCHEMA
    prompt = generate.call_args.kwargs["instructions"]
    assert "12 · 12" in prompt
    assert "German" in prompt
    assert "Max" not in prompt
    assert aufgabe.rechenweg == [
        "Rechne 12 · 10 = 120.",
        "12 · 2 = 24",
        "120 + 24 = 12²",
    ]
    assert _text(notify_calls) == (
        "So geht es, Max:\n1. Rechne 12 · 10 = 120.\n2. 12 · 2 = 24\n3. 120 + 24 = 12²"
    )

    # The second time the stored steps are used
    manager.zustand(KIND_ID).offene_frage = None
    await _frage(hass)
    await _antworte(hass, "1")
    with patch(GENERATE, AsyncMock()) as generate:
        await _antworte(hass, "ja")
    generate.assert_not_called()
    assert _text(notify_calls).startswith("So geht es, Max:\n1. Rechne")


@pytest.mark.parametrize(
    "antwort_ki",
    [
        HomeAssistantError("kaputt"),
        {"schritte": []},
        {"schritte": ["\\frac{1}{2}"]},
        {"schritte": ["x"] * 9},
        {"etwas": "anderes"},
    ],
)
async def test_rechenweg_ki_liefert_nichts(
    hass: HomeAssistant,
    mathe_ki: MockConfigEntry,
    notify_calls: list[ServiceCall],
    antwort_ki: Any,
) -> None:
    aufgabe = _neu(mathe_ki, "12 · 12", "144")
    await _frage(hass)
    await _antworte(hass, "124")
    mock = (
        AsyncMock(side_effect=antwort_ki)
        if isinstance(antwort_ki, Exception)
        else AsyncMock(return_value=antwort_ki)
    )
    with patch(GENERATE, mock):
        assert await _antworte(hass, "ja") == {"ergebnis": "rechenweg"}
    assert _text(notify_calls) == (
        "Max, den Rechenweg kann ich dir gerade leider nicht erklären."
    )
    assert aufgabe.rechenweg == []


async def test_angebot_ablehnen_oder_ignorieren(
    hass: HomeAssistant, mathe: MockConfigEntry, notify_calls: list[ServiceCall]
) -> None:
    manager: LearnBuddyManager = mathe.runtime_data
    zustand = manager.zustand(KIND_ID)
    _neu(mathe, "1 + 1", "2", rechenweg=["Zähle eins weiter."])

    await _frage(hass)
    await _antworte(hass, "3")
    assert await _antworte(hass, "Nein danke") == {"ergebnis": "keine_offene_frage"}
    assert _text(notify_calls) == "Alles klar, Max!" + TIPP
    assert zustand.rechenweg_angebot is None

    # Something else is not taken as a yes
    await _frage(hass)
    await _antworte(hass, "3")
    assert await _antworte(hass, "hä?") == {"ergebnis": "keine_offene_frage"}
    assert _text(notify_calls).startswith("Hallo Max, im Moment ist keine Frage offen.")
    assert zustand.rechenweg_angebot is None

    # A wish for more questions wins over the offer
    await _frage(hass)
    await _antworte(hass, "3")
    assert await _antworte(hass, "noch 2") == {
        "ergebnis": "zusatzaufgaben",
        "anzahl": 2,
    }
    assert zustand.rechenweg_angebot is None
    assert zustand.offene_frage is not None


async def test_angebot_verfaellt(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    mathe: MockConfigEntry,
    notify_calls: list[ServiceCall],
) -> None:
    manager: LearnBuddyManager = mathe.runtime_data
    zustand = manager.zustand(KIND_ID)
    _neu(mathe, "1 + 1", "2", rechenweg=["Zähle eins weiter."])
    await _antworte(hass, "noch 3")
    await _antworte(hass, "3")
    assert zustand.rechenweg_angebot is not None
    assert zustand.zusatz_offen == 2

    freezer.move_to("2026-10-06 09:30:00+02:00")
    assert await _antworte(hass, "ja") == {"ergebnis": "keine_offene_frage"}
    assert zustand.rechenweg_angebot is None
    # The series that waited for the reply is over as well
    assert zustand.zusatz_offen == 0


async def test_neue_frage_beendet_das_angebot(
    hass: HomeAssistant, mathe: MockConfigEntry
) -> None:
    manager: LearnBuddyManager = mathe.runtime_data
    zustand = manager.zustand(KIND_ID)
    _neu(mathe, "1 + 1", "2", rechenweg=["Zähle eins weiter."])
    await _frage(hass)
    await _antworte(hass, "3")
    assert zustand.rechenweg_angebot is not None
    await _frage(hass)
    assert zustand.rechenweg_angebot is None

    # A scheduled question also ends a series that waits for the reply
    await _antworte(hass, "3")
    zustand.zusatz_offen = 4
    await manager._async_geplante_frage(KIND_ID)
    assert zustand.rechenweg_angebot is None
    assert zustand.zusatz_offen == 0


async def test_serie_wartet_auf_antwort_zum_angebot(
    hass: HomeAssistant, mathe: MockConfigEntry, notify_calls: list[ServiceCall]
) -> None:
    manager: LearnBuddyManager = mathe.runtime_data
    zustand = manager.zustand(KIND_ID)
    _neu(mathe, "1 + 1", "2", rechenweg=["Zähle eins weiter."])
    _neu(mathe, "2 + 2", "4", rechenweg=["Zähle zwei weiter."])

    await _antworte(hass, "noch 3")
    assert _text(notify_calls, -2) == "Super, Max! 💪 Es kommen 3 weitere Aufgaben."
    assert _text(notify_calls) in ("1 + 1", "2 + 2")
    assert zustand.zusatz_offen == 2

    # A wrong answer: the next question waits for the reply to the offer
    anzahl = len(notify_calls)
    await _antworte(hass, "99")
    assert len(notify_calls) == anzahl + 1
    assert _text(notify_calls).endswith(ANGEBOT)
    assert zustand.offene_frage is None
    assert zustand.zusatz_offen == 2

    assert await _antworte(hass, "ja") == {"ergebnis": "rechenweg"}
    assert _text(notify_calls, -2).startswith("So geht es, Max:")
    assert _text(notify_calls) in ("1 + 1", "2 + 2")
    assert zustand.offene_frage is not None
    assert zustand.zusatz_offen == 1

    # Declining goes on with the series, too
    await _antworte(hass, "99")
    assert await _antworte(hass, "nö") == {"ergebnis": "zusatzaufgaben", "anzahl": 1}
    assert _text(notify_calls) in ("1 + 1", "2 + 2")
    assert zustand.zusatz_offen == 0

    frage = zustand.offene_frage
    assert frage is not None
    aufgabe = manager.task_stores[MATHE_ID].aufgaben[frage.aufgabe_id]
    assert isinstance(aufgabe, MatheAufgabe)
    await _antworte(hass, aufgabe.loesung)
    assert _text(notify_calls).endswith(TIPP)
    assert zustand.offene_frage is None


# ---------------------------------------------------------------------------
# Validation of AI results
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("roh", "erwartet"),
    [
        ("  3/4   + 1/8 ", "3/4 + 1/8"),
        ("5^2 und 2**3", "5² und 2³"),
        ("3 * 4", "3 · 4"),
        ("**fett** `code` #", "fett code"),
        ("\\frac{3}{4}", None),
        ("$x$", None),
        ("", None),
        ("   ", None),
        ("x" * 501, None),
        (5, None),
    ],
)
def test_bereinige_mathetext(roh: Any, erwartet: str | None) -> None:
    assert bereinige_mathetext(roh, 500) == erwartet


def test_parse_rechenweg() -> None:
    assert parse_rechenweg({"schritte": [" a ", "b"]}) == ["a", "b"]
    assert parse_rechenweg(["a"]) == ["a"]
    assert parse_rechenweg(
        ["Schritt 1: Erweitere.", "2. Addiere.", "step 3) Kürze.", "12 · 2 = 24"]
    ) == ["Erweitere.", "Addiere.", "Kürze.", "12 · 2 = 24"]
    assert parse_rechenweg({"schritte": "a"}) is None
    assert parse_rechenweg({"schritte": ["a", 5]}) is None
    assert parse_rechenweg(None) is None


def test_parse_aufgaben() -> None:
    assert parse_aufgaben(None) is None
    assert parse_aufgaben({"aufgaben": "x"}) is None
    aufgaben = parse_aufgaben(
        {
            "aufgaben": [
                {
                    "aufgabe": "3/4 + 1/8",
                    "loesung": "7/8",
                    "rechnung": "3/4+1/8",
                    "rechenweg": ["a", "b"],
                    "schwierigkeit": 2.0,
                },
                {
                    "aufgabe": "1 + 1",
                    "loesung": "2",
                    "rechnung": "",
                    "schwierigkeit": 9,
                },
                {"aufgabe": "2 + 2", "loesung": "4", "rechnung": 4, "rechenweg": "x"},
                {"aufgabe": "3 + 3", "loesung": "6", "schwierigkeit": True},
                "kaputt",
                {"aufgabe": "\\frac{1}{2}", "loesung": "1"},
                {"aufgabe": "ohne Lösung", "loesung": ""},
                {"loesung": "5"},
            ]
        }
    )
    assert aufgaben == [
        GenerierteAufgabe("3/4 + 1/8", "7/8", "3/4+1/8", ["a", "b"], 2),
        GenerierteAufgabe("1 + 1", "2", None, [], None),
        GenerierteAufgabe("2 + 2", "4", None, [], None),
        GenerierteAufgabe("3 + 3", "6", None, [], None),
    ]
    viele = {"aufgaben": [{"aufgabe": f"{i} + 1", "loesung": "x"} for i in range(30)]}
    assert len(parse_aufgaben(viele) or []) == 20


# ---------------------------------------------------------------------------
# Generating tasks
# ---------------------------------------------------------------------------

VORSCHLAEGE = {
    "aufgaben": [
        # Verified by calculating
        {
            "aufgabe": "1/4 + 2/4",
            "loesung": "3/4",
            "rechnung": "1/4 + 2/4",
            "rechenweg": ["Addiere die Zähler.", "1 + 2 = 3, also 3/4"],
            "schwierigkeit": 1,
        },
        # The calculation does not give the solution
        {
            "aufgabe": "1/2 + 1/4",
            "loesung": "2/6",
            "rechnung": "1/2 + 1/4",
            "rechenweg": [],
            "schwierigkeit": 1,
        },
        # No calculation: the AI solves it again and agrees
        {
            "aufgabe": "Wie viele Ecken hat ein Würfel?",
            "loesung": "8 Ecken",
            "rechnung": "",
            "rechenweg": ["Zähle oben 4 und unten 4."],
            "schwierigkeit": 2,
        },
        # No calculation: the AI disagrees
        {
            "aufgabe": "Wie viele Kanten hat ein Würfel?",
            "loesung": "10",
            "rechnung": "",
            "rechenweg": [],
            "schwierigkeit": 2,
        },
        # Already exists
        {
            "aufgabe": "3/4 + 1/8",
            "loesung": "7/8",
            "rechnung": "3/4 + 1/8",
            "rechenweg": [],
            "schwierigkeit": 1,
        },
        # Not usable in a messenger
        {
            "aufgabe": "\\frac{1}{2} + 1",
            "loesung": "1,5",
            "rechnung": "1/2 + 1",
            "rechenweg": [],
            "schwierigkeit": 1,
        },
    ]
}
ZWEITE_LOESUNG = {
    "Wie viele Ecken hat ein Würfel?": {"loesung": "8"},
    "Wie viele Kanten hat ein Würfel?": {"loesung": "12"},
}


async def _ki(hass: HomeAssistant, **kwargs: Any) -> Any:
    """Answer like an AI task entity."""
    if kwargs["structure"] is AUFGABEN_SCHEMA:
        return VORSCHLAEGE
    assert kwargs["structure"] is LOESUNG_SCHEMA
    for aufgabe, antwort in ZWEITE_LOESUNG.items():
        if aufgabe in kwargs["instructions"]:
            return antwort
    raise AssertionError(kwargs["instructions"])


@pytest.fixture
async def client(
    hass: HomeAssistant, mathe_ki: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> Client:
    """Return a websocket client of an admin."""
    return Client(await hass_ws_client(hass))


async def test_generieren(
    hass: HomeAssistant, mathe_ki: MockConfigEntry, client: Client
) -> None:
    manager: LearnBuddyManager = mathe_ki.runtime_data
    store = manager.task_stores[MATHE_ID]
    vorhanden = _neu(mathe_ki, "3/4 + 1/8", "7/8", lektion="Brüche")
    anderes = _neu(mathe_ki, "7 · 8", "56", lektion="Einmaleins")

    with patch(GENERATE, AsyncMock(side_effect=_ki)) as generate:
        ergebnis = await client.ok(
            "tasks/generate",
            fach_id=MATHE_ID,
            anzahl=6,
            lektion="brüche",
            schwierigkeit=2,
            beschreibung="gleichnamige Brüche",
        )
    assert ergebnis["erzeugt"] == 2
    assert ergebnis["verworfen"] == 2
    assert ergebnis["uebersprungen"] == 1
    neu = [store.aufgaben[i] for i in ergebnis["aufgabe_ids"]]
    assert all(isinstance(a, MatheAufgabe) for a in neu)
    eins, zwei = neu
    assert isinstance(eins, MatheAufgabe)
    assert isinstance(zwei, MatheAufgabe)
    assert (eins.aufgabe, eins.loesung) == ("1/4 + 2/4", "3/4")
    assert eins.verifikation is Verifikation.RECHNERISCH
    assert eins.rechenweg == ["Addiere die Zähler.", "1 + 2 = 3, also 3/4"]
    assert eins.schwierigkeit == 1
    assert zwei.verifikation is Verifikation.KI
    for aufgabe in neu:
        assert aufgabe.quelle is Quelle.GENERIERT
        assert aufgabe.geprueft is False
        assert aufgabe.lektion == "Brüche"
    assert len(store.aufgaben) == 4

    # Only the school level is sent, nothing about the child
    prompt = generate.call_args_list[0].kwargs["instructions"]
    assert "Create 6 new math practice tasks" in prompt
    assert "grade 6" in prompt
    assert "school type gymnasium" in prompt
    assert "German state RP" in prompt
    assert "Topic: Brüche" in prompt
    assert "gleichnamige Brüche" in prompt
    assert "Difficulty 2" in prompt
    assert f"- {vorhanden.aufgabe} → 7/8" in prompt
    assert anderes.aufgabe not in prompt
    for aufruf in generate.call_args_list:
        assert "Max" not in aufruf.kwargs["instructions"]
        assert KIND_ID not in aufruf.kwargs["instructions"]
    # The second call does not know the solution
    loesen = [
        a.kwargs["instructions"]
        for a in generate.call_args_list
        if a.kwargs["structure"] is LOESUNG_SCHEMA
    ]
    assert len(loesen) == 2
    assert all("8 Ecken" not in p for p in loesen)

    # Unapproved tasks are not asked
    await _frage(hass)
    frage = manager.zustand(KIND_ID).offene_frage
    assert frage is not None
    assert frage.aufgabe_id in (vorhanden.id, anderes.id)


async def test_generieren_mit_markierten_beispielen_und_auto_freigabe(
    hass: HomeAssistant, mathe_ki: MockConfigEntry, client: Client
) -> None:
    hass.config_entries.async_update_entry(
        mathe_ki, options={**mathe_ki.options, "auto_freigabe": True}
    )
    await hass.async_block_till_done()
    manager: LearnBuddyManager = mathe_ki.runtime_data
    eins = _neu(mathe_ki, "7 · 8", "56")
    _neu(mathe_ki, "9 · 9", "81")

    with patch(GENERATE, AsyncMock(side_effect=_ki)) as generate:
        ergebnis = await client.ok(
            "tasks/generate", fach_id=MATHE_ID, anzahl=1, beispiel_ids=[eins.id]
        )
    # Only as many as asked for are kept
    assert ergebnis["erzeugt"] == 1
    assert ergebnis["verworfen"] == 0
    prompt = generate.call_args_list[0].kwargs["instructions"]
    assert "- 7 · 8 → 56" in prompt
    assert "9 · 9" not in prompt
    assert "Topic:" not in prompt
    aufgabe = manager.task_stores[MATHE_ID].aufgaben[ergebnis["aufgabe_ids"][0]]
    assert aufgabe.geprueft is True
    assert aufgabe.lektion is None


@pytest.mark.parametrize(
    ("daten", "fehler"),
    [
        ({"fach_id": "gibtsnicht", "anzahl": 3}, ("not_found", "fach_unbekannt")),
        ({"anzahl": 0}, ("invalid_format", "anzahl_ungueltig")),
        ({"anzahl": 21}, ("invalid_format", "anzahl_ungueltig")),
        (
            {"anzahl": 3, "schwierigkeit": 6},
            ("invalid_format", "schwierigkeit_ungueltig"),
        ),
        ({"anzahl": 3, "lektion": "Algebra"}, ("invalid_format", "lektion_unbekannt")),
        (
            {"anzahl": 3, "beschreibung": "x" * 501},
            ("invalid_format", "beschreibung_ungueltig"),
        ),
        # Nothing to go by: no examples, no topic, no description
        ({"anzahl": 3}, ("invalid_format", "generieren_ohne_vorgabe")),
    ],
)
async def test_generieren_ungueltig(
    client: Client, daten: dict[str, Any], fehler: tuple[str, str]
) -> None:
    with patch(GENERATE, AsyncMock()) as generate:
        ergebnis = await client.fehler(
            "tasks/generate", **{"fach_id": MATHE_ID, **daten}
        )
    assert (ergebnis["code"], ergebnis["message"]) == fehler
    generate.assert_not_called()


async def test_generieren_ki_fehler(mathe_ki: MockConfigEntry, client: Client) -> None:
    # A call that does not get through and an answer that is unusable differ
    for mock, schluessel in (
        (AsyncMock(side_effect=HomeAssistantError("kaputt")), "ki_nicht_erreichbar"),
        (AsyncMock(return_value={}), "ki_fehler"),
    ):
        with patch(GENERATE, mock):
            fehler = await client.fehler(
                "tasks/generate", fach_id=MATHE_ID, anzahl=3, beschreibung="Brüche"
            )
        assert fehler == {"code": "home_assistant_error", "message": schluessel}

    # The second AI call fails: the task cannot be verified
    async def _nur_vorschlaege(hass: HomeAssistant, **kwargs: Any) -> Any:
        if kwargs["structure"] is AUFGABEN_SCHEMA:
            return {"aufgaben": [VORSCHLAEGE["aufgaben"][2]]}
        raise HomeAssistantError("kaputt")

    with patch(GENERATE, AsyncMock(side_effect=_nur_vorschlaege)):
        ergebnis = await client.ok(
            "tasks/generate", fach_id=MATHE_ID, anzahl=3, beschreibung="Würfel"
        )
    assert (ergebnis["erzeugt"], ergebnis["verworfen"]) == (0, 1)


async def test_generieren_ohne_ki_und_falsche_fachart(
    hass: HomeAssistant, mathe: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = Client(await hass_ws_client(hass))
    fehler = await client.fehler(
        "tasks/generate", fach_id=MATHE_ID, anzahl=3, beschreibung="Brüche"
    )
    assert fehler == {"code": "invalid_format", "message": "ki_fehlt"}


async def test_generieren_nur_fuer_mathe(
    hass: HomeAssistant,
    mit_vokabeln: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
) -> None:
    client = Client(await hass_ws_client(hass))
    fehler = await client.fehler("tasks/generate", fach_id=FACH_ID, anzahl=3)
    assert fehler == {"code": "invalid_format", "message": "generieren_nur_mathe"}


async def test_generieren_nur_admin(
    hass: HomeAssistant,
    mathe_ki: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    hass_admin_user: Any,
) -> None:
    hass_admin_user.groups = []
    ws = await hass_ws_client(hass)
    await ws.send_json_auto_id(
        {"type": "learnbuddy/tasks/generate", "fach_id": MATHE_ID, "anzahl": 3}
    )
    antwort = await ws.receive_json()
    assert antwort["error"]["code"] == "unauthorized"


async def test_aktion_generate_tasks(
    hass: HomeAssistant, mathe_ki: MockConfigEntry
) -> None:
    _neu(mathe_ki, "3/4 + 1/8", "7/8")
    with patch(GENERATE, AsyncMock(side_effect=_ki)):
        ergebnis = await hass.services.async_call(
            DOMAIN,
            "generate_tasks",
            {"kind_id": KIND_ID, "fach": "mathe", "anzahl": 6, "schwierigkeit": 2},
            blocking=True,
            return_response=True,
        )
    assert ergebnis == {"erzeugt": 2, "verworfen": 2, "uebersprungen": 1}

    with pytest.raises(ServiceValidationError) as fehler:
        await hass.services.async_call(
            DOMAIN,
            "generate_tasks",
            {"fach_id": MATHE_ID, "anzahl": 3, "lektion": "Algebra"},
            blocking=True,
            return_response=True,
        )
    assert fehler.value.translation_key == "lektion_unbekannt"
    with pytest.raises(ServiceValidationError) as fehler:
        await hass.services.async_call(
            DOMAIN,
            "generate_tasks",
            {"kind_id": KIND_ID, "fach": "Physik", "anzahl": 3},
            blocking=True,
            return_response=True,
        )
    assert fehler.value.translation_key == "fach_unbekannt"


# ---------------------------------------------------------------------------
# Panel API
# ---------------------------------------------------------------------------


async def test_ws_mathe_aufgaben(mathe_ki: MockConfigEntry, client: Client) -> None:
    manager: LearnBuddyManager = mathe_ki.runtime_data
    await client.ok("lessons/add", fach_id=MATHE_ID, name="Brüche")
    neu = await client.ok(
        "tasks/create",
        fach_id=MATHE_ID,
        aufgabe={
            "aufgabe": " 3/4 + 1/8 ",
            "loesung": "7/8",
            "alternativen": ["0,875", " "],
            "rechenweg": ["Erweitere.", "Addiere."],
            "schwierigkeit": 2,
            "lektion": "brüche",
            "seite": 40,
            "hinweis": "p.12",
        },
    )
    assert neu["typ"] == "mathe"
    assert neu["aufgabe"] == "3/4 + 1/8"
    assert neu["loesung"] == "7/8"
    assert neu["alternativen"] == ["0,875"]
    assert neu["rechenweg"] == ["Erweitere.", "Addiere."]
    assert neu["schwierigkeit"] == 2
    assert neu["lektion"] == "Brüche"
    assert neu["verifikation"] == "keine"
    assert neu["quelle"] == "manuell"
    assert neu["fehlerquote"] is None

    aufgabe = manager.task_stores[MATHE_ID].aufgaben[neu["id"]]
    assert isinstance(aufgabe, MatheAufgabe)
    aufgabe.verifikation = Verifikation.RECHNERISCH
    geaendert = await client.ok(
        "tasks/update",
        fach_id=MATHE_ID,
        aufgabe_id=neu["id"],
        aenderungen={"geprueft": False, "schwierigkeit": None},
    )
    assert geaendert["geprueft"] is False
    assert geaendert["schwierigkeit"] is None
    assert geaendert["verifikation"] == "rechnerisch"
    # A changed task is not the verified one any more
    geaendert = await client.ok(
        "tasks/update",
        fach_id=MATHE_ID,
        aufgabe_id=neu["id"],
        aenderungen={"loesung": "0,875", "rechenweg": []},
    )
    assert geaendert["loesung"] == "0,875"
    assert geaendert["rechenweg"] == []
    assert geaendert["verifikation"] == "keine"

    liste = await client.ok("tasks/list", fach_id=MATHE_ID)
    assert [a["id"] for a in liste["aufgaben"]] == [neu["id"]]
    uebersicht = await client.ok("overview")
    assert uebersicht["faecher"][0]["typ"] == "mathe"
    assert uebersicht["faecher"][0]["sprachen"] == []


@pytest.mark.parametrize(
    ("aufgabe", "schluessel"),
    [
        ({}, "aufgabe_ungueltig"),
        ({"aufgabe": "1 + 1"}, "loesung_ungueltig"),
        ({"aufgabe": " ", "loesung": "2"}, "aufgabe_ungueltig"),
        ({"aufgabe": "x" * 501, "loesung": "2"}, "aufgabe_ungueltig"),
        ({"aufgabe": "1 + 1", "loesung": "2" * 101}, "loesung_ungueltig"),
        (
            {"aufgabe": "1 + 1", "loesung": "2", "alternativen": {"de": ["zwei"]}},
            "alternativen_ungueltig",
        ),
        (
            {"aufgabe": "1 + 1", "loesung": "2", "alternativen": ["2"] * 9},
            "alternativen_ungueltig",
        ),
        (
            {"aufgabe": "1 + 1", "loesung": "2", "alternativen": ["2" * 101]},
            "alternativen_ungueltig",
        ),
        (
            {"aufgabe": "1 + 1", "loesung": "2", "rechenweg": ["x"] * 9},
            "rechenweg_ungueltig",
        ),
        (
            {"aufgabe": "1 + 1", "loesung": "2", "schwierigkeit": 6},
            "schwierigkeit_ungueltig",
        ),
        ({"aufgabe": "1 + 1", "loesung": "2", "seite": 0}, "seite_ungueltig"),
        (
            {"aufgabe": "1 + 1", "loesung": "2", "lektion": "Algebra"},
            "lektion_unbekannt",
        ),
    ],
)
async def test_ws_mathe_ungueltig(
    client: Client, aufgabe: dict[str, Any], schluessel: str
) -> None:
    fehler = await client.fehler("tasks/create", fach_id=MATHE_ID, aufgabe=aufgabe)
    assert fehler == {"code": "invalid_format", "message": schluessel}


async def test_ws_mathe_import_export(
    hass: HomeAssistant,
    mathe_ki: MockConfigEntry,
    client: Client,
) -> None:
    manager: LearnBuddyManager = mathe_ki.runtime_data
    store = manager.task_stores[MATHE_ID]
    inhalt = "7 · 8; 56\n3,5 - 1,2 = ?; 2,3 | 2.3; Kommazahlen\n7 · 8; 56"
    vorschau = await client.ok(
        "tasks/import_text", fach_id=MATHE_ID, inhalt=inhalt, vorschau=True
    )
    assert vorschau["zeilen"] == [
        {
            "aufgabe": "7 · 8",
            "loesung": "56",
            "alternativen": [],
            "hinweis": None,
            "vorhanden": False,
        },
        {
            "aufgabe": "3,5 - 1,2 = ?",
            "loesung": "2,3",
            "alternativen": ["2.3"],
            "hinweis": "Kommazahlen",
            "vorhanden": False,
        },
        {
            "aufgabe": "7 · 8",
            "loesung": "56",
            "alternativen": [],
            "hinweis": None,
            "vorhanden": True,
        },
    ]
    assert not store.aufgaben
    ergebnis = await client.ok("tasks/import_text", fach_id=MATHE_ID, inhalt=inhalt)
    assert ergebnis == {"importiert": 2, "uebersprungen": 1, "fehlerzeilen": []}

    erste = next(iter(store.aufgaben.values()))
    assert isinstance(erste, MatheAufgabe)
    erste.verifikation = Verifikation.KI
    erste.rechenweg = ["Rechne 7 · 8."]
    export = await client.ok("tasks/export", fach_id=MATHE_ID)
    assert export["typ"] == "mathe"
    assert export["sprachen"] == []
    assert len(export["aufgaben"]) == 2

    # Same subject: everything exists already
    ergebnis = await client.ok("tasks/import_json", fach_id=MATHE_ID, daten=export)
    assert ergebnis == {"importiert": 0, "uebersprungen": 2, "fehler": []}

    await client.ok(
        "tasks/delete",
        fach_id=MATHE_ID,
        aufgabe_ids=list(store.aufgaben),
        bestaetigt=True,
    )
    export["aufgaben"].append({"aufgabe": "ohne Lösung"})
    export["aufgaben"].append({"aufgabe": "1 + 1", "loesung": "2", "verifikation": "x"})
    ergebnis = await client.ok("tasks/import_json", fach_id=MATHE_ID, daten=export)
    assert ergebnis == {"importiert": 2, "uebersprungen": 0, "fehler": [2, 3]}
    neu = [a for a in store.aufgaben.values() if isinstance(a, MatheAufgabe)]
    assert {a.aufgabe for a in neu} == {"7 · 8", "3,5 - 1,2 = ?"}
    wieder = next(a for a in neu if a.aufgabe == "7 · 8")
    assert wieder.verifikation is Verifikation.KI
    assert wieder.rechenweg == ["Rechne 7 · 8."]

    # A vocabulary export does not fit a math subject
    fehler = await client.fehler(
        "tasks/import_json",
        fach_id=MATHE_ID,
        daten={**export, "typ": "vokabel", "sprachen": ["de", "en"]},
    )
    assert fehler == {"code": "invalid_format", "message": "export_typ"}


async def test_dashboard_mit_mathe(
    hass: HomeAssistant, mathe_ki: MockConfigEntry, client: Client
) -> None:
    _neu(mathe_ki, "7 · 8", "56")
    await _frage(hass)
    await _antworte(hass, "54")
    daten = await client.ok("dashboard", kind_id=KIND_ID)
    fach = daten["faecher"][0]
    assert fach["typ"] == "mathe"
    assert fach["ki"] is True
    assert fach["boxen"] == [1, 0, 0, 0, 0]
    assert daten["schwierig"][0]["aufgabe"] == "7 · 8"
    assert daten["schwierig"][0]["frage"] is None


async def test_nachrechnen(mathe_ki: MockConfigEntry, client: Client) -> None:
    richtig = _neu(mathe_ki, "3/4 + 1/8 = ?", "7/8")
    alternative = _neu(mathe_ki, "1/2 + 1/4", "0,75", alternativen=["0,8"])
    falsch = _neu(mathe_ki, "7 · 8", "54")
    text_gut = _neu(mathe_ki, "Wie viele Ecken hat ein Würfel?", "8 Ecken")
    text_schlecht = _neu(mathe_ki, "Wie viele Kanten hat ein Würfel?", "10")
    text_offen = _neu(mathe_ki, "Wie viele Flächen hat ein Würfel?", "6")
    nicht_gewaehlt = _neu(mathe_ki, "1 + 1", "3")

    async def _ki_loest(hass: HomeAssistant, **kwargs: Any) -> Any:
        assert kwargs["structure"] is LOESUNG_SCHEMA
        assert "Max" not in kwargs["instructions"]
        if "Flächen" in kwargs["instructions"]:
            raise HomeAssistantError("kaputt")
        return await _ki(hass, **kwargs)

    ids = [
        a.id
        for a in (richtig, alternative, falsch, text_gut, text_schlecht, text_offen)
    ]
    with patch(GENERATE, AsyncMock(side_effect=_ki_loest)) as generate:
        ergebnis = await client.ok(
            "tasks/verify", fach_id=MATHE_ID, aufgabe_ids=[*ids, "gibtsnicht"]
        )
    # Plain calculations never need the AI
    assert generate.call_count == 3
    assert ergebnis["bestaetigt"] == 3
    assert ergebnis["nicht_pruefbar"] == 1
    assert ergebnis["abweichend"] == [
        {
            "id": falsch.id,
            "aufgabe": "7 · 8",
            "loesung": "54",
            "berechnet": "56",
            "durch": "lokal",
        },
        {
            "id": text_schlecht.id,
            "aufgabe": "Wie viele Kanten hat ein Würfel?",
            "loesung": "10",
            "berechnet": "12",
            "durch": "ki",
        },
    ]
    assert richtig.verifikation is Verifikation.RECHNERISCH
    assert alternative.verifikation is Verifikation.RECHNERISCH
    assert falsch.verifikation is Verifikation.ABWEICHUNG
    assert text_gut.verifikation is Verifikation.KI
    assert text_schlecht.verifikation is Verifikation.ABWEICHUNG
    assert text_offen.verifikation is Verifikation.KEINE
    assert nicht_gewaehlt.verifikation is Verifikation.KEINE
    # Nothing but the mark is changed
    assert falsch.loesung == "54"
    # The result that was found is kept as a suggestion
    assert (falsch.vorschlag, falsch.vorschlag_durch) == ("56", "lokal")
    assert (text_schlecht.vorschlag, text_schlecht.vorschlag_durch) == ("12", "ki")
    assert richtig.vorschlag is None
    export = await client.ok("tasks/export", fach_id=MATHE_ID)
    assert all("vorschlag" not in a for a in export["aufgaben"])

    # Correcting the solution removes the mark
    geaendert = await client.ok(
        "tasks/update",
        fach_id=MATHE_ID,
        aufgabe_id=falsch.id,
        aenderungen={"loesung": "56"},
    )
    assert geaendert["verifikation"] == "keine"
    assert geaendert["vorschlag"] is None
    with patch(GENERATE, AsyncMock()) as generate:
        ergebnis = await client.ok(
            "tasks/verify", fach_id=MATHE_ID, aufgabe_ids=[falsch.id]
        )
    generate.assert_not_called()
    assert ergebnis == {"bestaetigt": 1, "abweichend": [], "nicht_pruefbar": 0}

    fehler = await client.fehler("tasks/verify", fach_id=MATHE_ID, aufgabe_ids=[])
    assert fehler == {"code": "invalid_format", "message": "auswahl_ungueltig"}
    fehler = await client.fehler(
        "tasks/verify", fach_id=MATHE_ID, aufgabe_ids=["x"] * 101
    )
    assert fehler == {"code": "invalid_format", "message": "auswahl_ungueltig"}


async def test_nachrechnen_ohne_ki(
    hass: HomeAssistant, mathe: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = Client(await hass_ws_client(hass))
    rechnung = _neu(mathe, "2,5 · 4", "10")
    bruch = _neu(mathe, "1/3 + 1/3", "1/3")
    text = _neu(mathe, "Wie viele Ecken hat ein Würfel?", "8")
    ergebnis = await client.ok(
        "tasks/verify", fach_id=MATHE_ID, aufgabe_ids=[rechnung.id, bruch.id, text.id]
    )
    assert ergebnis["bestaetigt"] == 1
    assert ergebnis["nicht_pruefbar"] == 1
    assert [a["berechnet"] for a in ergebnis["abweichend"]] == ["2/3"]


async def test_nachrechnen_nur_mathe(
    hass: HomeAssistant,
    mit_vokabeln: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
) -> None:
    client = Client(await hass_ws_client(hass))
    fehler = await client.fehler("tasks/verify", fach_id=FACH_ID, aufgabe_ids=["x"])
    assert fehler == {"code": "invalid_format", "message": "nachrechnen_nur_mathe"}


async def test_vorschlag_uebernehmen(
    hass: HomeAssistant, mathe_ki: MockConfigEntry, client: Client
) -> None:
    manager: LearnBuddyManager = mathe_ki.runtime_data
    falsch = _neu(
        mathe_ki,
        "1/4 + 1/4 = ?",
        "2/8",
        alternativen=["0,25", "2/4", "0,5"],
        rechenweg=["Addiere die Zähler und die Nenner."],
    )
    falsch.statistik_fuer("mathe").falsch = 3
    text = _neu(mathe_ki, "Wie viele Kanten hat ein Würfel?", "10")
    richtig = _neu(mathe_ki, "7 · 8", "56", rechenweg=["Rechne 7 · 8."])
    ids = [falsch.id, text.id, richtig.id]
    with patch(GENERATE, AsyncMock(side_effect=_ki)):
        await client.ok("tasks/verify", fach_id=MATHE_ID, aufgabe_ids=ids)
    assert falsch.vorschlag == "1/2"

    # The child is asked this task while the parents correct it
    manager.task_stores[MATHE_ID].aufgaben = {falsch.id: falsch}
    await _frage(hass)
    manager.task_stores[MATHE_ID].aufgaben = {a.id: a for a in (falsch, text, richtig)}

    ergebnis = await client.ok(
        "tasks/accept_suggestion", fach_id=MATHE_ID, aufgabe_ids=[*ids, "gibtsnicht"]
    )
    assert ergebnis == {"uebernommen": 2}
    assert falsch.loesung == "1/2"
    # Only spellings of the new solution are kept
    assert falsch.alternativen == ["2/4", "0,5"]
    assert falsch.rechenweg == []
    assert falsch.verifikation is Verifikation.RECHNERISCH
    assert falsch.vorschlag is None
    assert falsch.vorschlag_durch is None
    assert text.loesung == "12"
    assert text.verifikation is Verifikation.KI
    # A task without a suggestion stays as it is
    assert richtig.loesung == "56"
    assert richtig.rechenweg == ["Rechne 7 · 8."]

    # The open question is judged against the corrected solution
    assert (await _antworte(hass, "0,5"))["ergebnis"] == "richtig"
    stat = falsch.statistik["mathe"]
    assert (stat.richtig, stat.falsch) == (1, 0)

    assert await client.ok(
        "tasks/accept_suggestion", fach_id=MATHE_ID, aufgabe_ids=ids
    ) == {"uebernommen": 0}


async def test_als_geprueft_markieren(
    mathe_ki: MockConfigEntry, client: Client
) -> None:
    offen = _neu(mathe_ki, "3/4 + 1/4", "1", rechenweg=["Addiere die Zähler."])
    offen.statistik_fuer("mathe").richtig = 2
    abweichend = _neu(
        mathe_ki,
        "Wie viele Ferientage hat Italien?",
        "90",
        verifikation=Verifikation.ABWEICHUNG,
    )
    abweichend.vorschlag = "110"
    abweichend.vorschlag_durch = "ki"
    nicht_gewaehlt = _neu(mathe_ki, "2 + 2", "4")
    ids = [offen.id, abweichend.id]

    ergebnis = await client.ok(
        "tasks/mark_verified", fach_id=MATHE_ID, aufgabe_ids=[*ids, "gibtsnicht"]
    )
    assert ergebnis == {"markiert": 2}
    assert offen.verifikation is Verifikation.MANUELL
    # Nothing but the mark changes
    assert offen.loesung == "1"
    assert offen.rechenweg == ["Addiere die Zähler."]
    assert offen.statistik["mathe"].richtig == 2
    # The parent decided against the result of the AI
    assert abweichend.verifikation is Verifikation.MANUELL
    assert abweichend.loesung == "90"
    assert abweichend.vorschlag is None
    assert abweichend.vorschlag_durch is None
    assert nicht_gewaehlt.verifikation is Verifikation.KEINE

    assert await client.ok(
        "tasks/mark_verified", fach_id=MATHE_ID, aufgabe_ids=ids
    ) == {"markiert": 0}

    # A changed solution is no longer the one that was checked
    await client.ok(
        "tasks/update",
        fach_id=MATHE_ID,
        aufgabe_id=offen.id,
        aenderungen={"loesung": "2"},
    )
    assert offen.verifikation is Verifikation.KEINE


async def test_als_geprueft_markieren_nur_mathe(
    hass: HomeAssistant,
    mit_vokabeln: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
) -> None:
    client = Client(await hass_ws_client(hass))
    fehler = await client.fehler(
        "tasks/mark_verified", fach_id=FACH_ID, aufgabe_ids=["x"]
    )
    assert fehler == {"code": "invalid_format", "message": "nachrechnen_nur_mathe"}


async def test_rechenwege_erzeugen(mathe_ki: MockConfigEntry, client: Client) -> None:
    ohne = _neu(mathe_ki, "12 · 12", "144")
    mit = _neu(mathe_ki, "7 · 8", "56", rechenweg=["Rechne 7 · 8."])
    abweichend = _neu(mathe_ki, "1 + 1", "3", verifikation=Verifikation.ABWEICHUNG)
    kaputt = _neu(mathe_ki, "Wie viele Flächen hat ein Würfel?", "6")
    nicht_gewaehlt = _neu(mathe_ki, "2 + 2", "4")

    async def _schritte(hass: HomeAssistant, **kwargs: Any) -> Any:
        assert kwargs["structure"] is RECHENWEG_SCHEMA
        assert "Max" not in kwargs["instructions"]
        if "Flächen" in kwargs["instructions"]:
            raise HomeAssistantError("kaputt")
        return {"schritte": ["12 · 10 = 120", "12 · 2 = 24", "120 + 24 = 144"]}

    ids = [ohne.id, mit.id, abweichend.id, kaputt.id, "gibtsnicht"]
    with patch(GENERATE, AsyncMock(side_effect=_schritte)) as generate:
        ergebnis = await client.ok(
            "tasks/generate_steps", fach_id=MATHE_ID, aufgabe_ids=ids
        )
    assert ergebnis == {
        "erzeugt": 1,
        "vorhanden": 1,
        "abweichend": 1,
        "fehlgeschlagen": 1,
    }
    assert generate.call_count == 2
    assert ohne.rechenweg == ["12 · 10 = 120", "12 · 2 = 24", "120 + 24 = 144"]
    assert mit.rechenweg == ["Rechne 7 · 8."]
    assert abweichend.rechenweg == []
    assert kaputt.rechenweg == []
    assert nicht_gewaehlt.rechenweg == []

    fehler = await client.fehler(
        "tasks/generate_steps", fach_id=MATHE_ID, aufgabe_ids=[]
    )
    assert fehler == {"code": "invalid_format", "message": "auswahl_ungueltig"}


async def test_rechenwege_erzeugen_ohne_ki_oder_mathe(
    hass: HomeAssistant, mathe: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> None:
    client = Client(await hass_ws_client(hass))
    aufgabe = _neu(mathe, "12 · 12", "144")
    fehler = await client.fehler(
        "tasks/generate_steps", fach_id=MATHE_ID, aufgabe_ids=[aufgabe.id]
    )
    assert fehler == {"code": "invalid_format", "message": "ki_fehlt"}


async def test_rechenwege_erzeugen_nur_mathe(
    hass: HomeAssistant,
    mit_vokabeln: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
) -> None:
    client = Client(await hass_ws_client(hass))
    fehler = await client.fehler(
        "tasks/generate_steps", fach_id=FACH_ID, aufgabe_ids=["x"]
    )
    assert fehler == {"code": "invalid_format", "message": "rechenweg_nur_mathe"}


async def test_aufgaben_mit_bild(
    hass: HomeAssistant, mathe_ki: MockConfigEntry, client: Client
) -> None:
    manager: LearnBuddyManager = mathe_ki.runtime_data
    ablage = manager.bilder
    bild = await ablage.async_speichere(bild_daten())
    anderes = await ablage.async_speichere(bild_daten())

    fehler = await client.fehler(
        "tasks/create",
        fach_id=MATHE_ID,
        aufgabe={"aufgabe": "a)", "loesung": "1", "bild": "0" * 32 + ".png"},
    )
    assert fehler == {"code": "invalid_format", "message": "bild_unbekannt"}

    # Several parts of one exercise share the image
    teile = [
        await client.ok(
            "tasks/create",
            fach_id=MATHE_ID,
            aufgabe={"aufgabe": text, "loesung": loesung, "bild": bild},
        )
        for text, loesung in (
            ("a) Meiste Ferientage?", "Türkei"),
            ("b) Wie viele?", "110"),
        )
    ]
    assert all(t["bild"] == bild for t in teile)
    ohne = await client.ok(
        "tasks/create", fach_id=MATHE_ID, aufgabe={"aufgabe": "7 · 8", "loesung": "56"}
    )
    assert ohne["bild"] is None
    assert manager.verwendete_bilder() == {bild}

    # The image file is not part of an export, so its tasks are left out
    export = await client.ok("tasks/export", fach_id=MATHE_ID)
    assert export["ausgelassen_mit_bild"] == 2
    assert [a["aufgabe"] for a in export["aufgaben"]] == ["7 · 8"]
    assert "bild" not in export["aufgaben"][0]

    # The image stays while one task uses it
    alt = time.time() - 2 * 24 * 60 * 60
    for bild_id in (bild, anderes):
        os.utime(ablage.ordner / bild_id, (alt, alt))
    await client.ok(
        "tasks/delete", fach_id=MATHE_ID, aufgabe_ids=[teile[0]["id"]], bestaetigt=True
    )
    await hass.async_block_till_done()
    # The unused upload is gone, the shared one is still needed
    assert ablage.ids == {bild}

    await client.ok(
        "tasks/update",
        fach_id=MATHE_ID,
        aufgabe_id=teile[1]["id"],
        aenderungen={"bild": None},
    )
    await hass.async_block_till_done()
    assert not ablage.ids
    assert not (ablage.ordner / bild).exists()


async def test_nachrechnen_vergleicht_texte_nach_bedeutung(
    mathe_ki: MockConfigEntry, client: Client
) -> None:
    gleich = _neu(
        mathe_ki,
        "Stimmt das auf jeden Fall?",
        "Nein, das Diagramm zeigt nur Ferientage.",
    )
    anders = _neu(mathe_ki, "Ist 7 gerade oder ungerade?", "gerade")
    offen = _neu(mathe_ki, "Ist 8 gerade oder ungerade?", "gerade")
    antworten = {"Stimmt das": "Nein", "Ist 7": "ungerade", "Ist 8": "gerade Zahl"}

    async def _ki_text(hass: HomeAssistant, **kwargs: Any) -> Any:
        prompt = kwargs["instructions"]
        if kwargs["structure"] is LOESUNG_SCHEMA:
            return {"loesung": next(v for k, v in antworten.items() if k in prompt)}
        assert kwargs["structure"] is MATHE_SCHEMA
        # The solution of the AI is judged like an answer
        if "Ist 8" in prompt:
            raise HomeAssistantError("kaputt")
        return {
            "ergebnis": "richtig" if "<answer>\nNein\n</answer>" in prompt else "falsch"
        }

    with patch(GENERATE, AsyncMock(side_effect=_ki_text)) as generate:
        ergebnis = await client.ok(
            "tasks/verify",
            fach_id=MATHE_ID,
            aufgabe_ids=[gleich.id, anders.id, offen.id],
        )
    assert generate.call_count == 6
    assert ergebnis["bestaetigt"] == 1
    assert ergebnis["nicht_pruefbar"] == 1
    assert [(a["id"], a["berechnet"]) for a in ergebnis["abweichend"]] == [
        (anders.id, "ungerade")
    ]
    assert gleich.verifikation is Verifikation.KI
    assert anders.verifikation is Verifikation.ABWEICHUNG
    assert offen.verifikation is Verifikation.KEINE


async def test_ki_nicht_verfuegbar(
    hass: HomeAssistant, mathe_ki: MockConfigEntry, client: Client
) -> None:
    manager: LearnBuddyManager = mathe_ki.runtime_data
    aufgabe = _neu(mathe_ki, "7 · 8", "56")

    def _status() -> str:
        status: str = manager.verwaltung.uebersicht()["faecher"][0]["ki_status"]
        return status

    assert _status() == "ohne_bilder"
    hass.states.async_set("ai_task.test", "unknown", {"supported_features": 3})
    assert _status() == "ok"
    # The integration behind the entity is not loaded, or the entity is gone
    for weg in ("unavailable", None):
        if weg is None:
            hass.states.async_remove("ai_task.test")
        else:
            hass.states.async_set("ai_task.test", weg)
        assert _status() == "nicht_verfuegbar"
        fach = manager.verwaltung.uebersicht()["faecher"][0]
        assert (fach["ki"], fach["ki_bilder"]) == (True, False)
        for befehl, daten in (
            ("tasks/generate", {"anzahl": 3, "beschreibung": "Brüche"}),
            ("tasks/generate_steps", {"aufgabe_ids": [aufgabe.id]}),
            ("tasks/photo_extract", {"seiten": ["x"]}),
        ):
            assert await client.fehler(befehl, fach_id=MATHE_ID, **daten) == {
                "code": "invalid_format",
                "message": "ki_nicht_verfuegbar",
            }


async def test_reparatur_hinweis_fuer_die_ki(
    hass: HomeAssistant,
    freezer: FrozenDateTimeFactory,
    mathe_ki: MockConfigEntry,
    client: Client,
) -> None:
    register = ir.async_get(hass)
    hinweis = "ki_ai_task.test"
    manager: LearnBuddyManager = mathe_ki.runtime_data

    async def _generiere(mock: AsyncMock) -> None:
        with patch(GENERATE, mock):
            await client.fehler(
                "tasks/generate", fach_id=MATHE_ID, anzahl=1, beschreibung="x"
            )

    kaputt = AsyncMock(side_effect=HomeAssistantError("kaputt"))
    await _generiere(kaputt)
    await _generiere(kaputt)
    assert register.async_get_issue(DOMAIN, hinweis) is None
    # The third failure in a row tells the user
    await _generiere(kaputt)
    issue = register.async_get_issue(DOMAIN, hinweis)
    assert issue is not None
    assert issue.translation_key == "ki_gestoert"
    assert issue.translation_placeholders == {"entity": "ai_task.test"}
    # While calls fail, the entity being there does not clear the issue
    manager.async_pruefe_ki()
    assert register.async_get_issue(DOMAIN, hinweis) is not None

    with patch(GENERATE, AsyncMock(side_effect=_ki)):
        await client.ok("tasks/generate", fach_id=MATHE_ID, anzahl=1, beschreibung="x")
    assert register.async_get_issue(DOMAIN, hinweis) is None

    # An entity that is gone is found a few minutes after the start and daily
    hass.states.async_remove("ai_task.test")
    freezer.tick(timedelta(minutes=6))
    async_fire_time_changed(hass)
    await hass.async_block_till_done()
    assert register.async_get_issue(DOMAIN, hinweis) is not None
    hass.states.async_set("ai_task.test", "unknown")
    manager.async_pruefe_ki()
    assert register.async_get_issue(DOMAIN, hinweis) is None
