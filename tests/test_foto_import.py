"""Tests for reading vocabulary and math tasks from photos."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, patch

from homeassistant.core import HomeAssistant, ServiceCall
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from custom_components.learnbuddy.ai import (
    FOTO_MATHE_SCHEMA,
    FOTO_VOKABELN_SCHEMA,
    LOESUNG_SCHEMA,
    parse_foto_mathe,
    parse_foto_vokabeln,
)
from custom_components.learnbuddy.const import DOMAIN
from custom_components.learnbuddy.manager import LearnBuddyManager
from custom_components.learnbuddy.models import (
    MatheAufgabe,
    Quelle,
    Verifikation,
    Vokabel,
)

from .conftest import FACH_DATEN, FACH_ID, KIND_DATEN, KIND_ID, subentry
from .test_bilder import bild_daten
from .test_mathe_ablauf import GENERATE, MATHE_DATEN, MATHE_ID
from .test_sach_ablauf import SACH_DATEN, SACH_ID
from .test_websocket import Client

KI = "ai_task.test"


@pytest.fixture
async def entry(
    hass: HomeAssistant, notify_calls: list[ServiceCall]
) -> MockConfigEntry:
    """Set up a child with one subject of every kind and an AI that sees images."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        title="LearnBuddy",
        data={},
        options={"timeout_minuten": 60, "sprache": "de", "ki_entity": KI},
        subentries_data=[
            subentry("kind", KIND_ID, "Max", KIND_DATEN),
            subentry("fach", FACH_ID, "Englisch (Max)", FACH_DATEN),
            subentry("fach", MATHE_ID, "Mathe (Max)", MATHE_DATEN),
            subentry("fach", SACH_ID, "Biologie (Max)", SACH_DATEN),
        ],
    )
    config_entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    hass.states.async_set(KI, "unknown", {"supported_features": 3})
    return config_entry


@pytest.fixture
async def client(
    hass: HomeAssistant, entry: MockConfigEntry, hass_ws_client: WebSocketGenerator
) -> Client:
    """Return a websocket client of an admin."""
    return Client(await hass_ws_client(hass))


async def _seiten(entry: MockConfigEntry, anzahl: int = 1) -> list[str]:
    manager: LearnBuddyManager = entry.runtime_data
    return [
        await manager.bilder.async_speichere(bild_daten(), seite=True)
        for _ in range(anzahl)
    ]


def _vokabel(ziel: str, ausgang: str, **felder: Any) -> dict[str, Any]:
    return {
        "ziel": ziel,
        "ausgang": ausgang,
        "ziel_weitere": [],
        "ausgang_weitere": [],
        "hinweis": "p. 28",
        "seite": 231,
    } | felder


def test_parse_foto_vokabeln() -> None:
    assert parse_foto_vokabeln(None) is None
    assert parse_foto_vokabeln({"vokabeln": 1}) is None
    gelesen = parse_foto_vokabeln(
        {
            "vokabeln": [
                _vokabel(
                    " friend ",
                    "Freund, Freundin",
                    ausgang_weitere=[
                        "Freund",
                        "Freundin",
                        "freund",
                        "Freund, Freundin",
                    ],
                ),
                _vokabel("shy", "schüchtern", hinweis="", seite=0),
                _vokabel("", "leer"),
                _vokabel("x" * 201, "zu lang"),
                "kaputt",
                _vokabel("often", "oft", seite=True, hinweis=None),
            ]
        }
    )
    assert gelesen is not None
    assert [(g.ziel, g.ausgang) for g in gelesen] == [
        ("friend", "Freund, Freundin"),
        ("shy", "schüchtern"),
        ("often", "oft"),
    ]
    assert gelesen[0].ausgang_weitere == ["Freund", "Freundin"]
    assert (gelesen[0].hinweis, gelesen[0].seite) == ("p. 28", 231)
    # The reference of the first entry applies to the following ones
    assert (gelesen[1].hinweis, gelesen[1].seite) == ("p. 28", None)
    assert gelesen[2].seite is None
    ohne = parse_foto_vokabeln({"vokabeln": [_vokabel("a", "b", hinweis="")]})
    assert ohne is not None
    assert ohne[0].hinweis is None
    viele = parse_foto_vokabeln(
        {"vokabeln": [_vokabel(f"w{i}", "x") for i in range(200)]}
    )
    assert viele is not None
    assert len(viele) == 120


def test_parse_foto_mathe() -> None:
    assert parse_foto_mathe([]) is None
    gelesen = parse_foto_mathe(
        {
            "aufgaben": [
                {
                    "aufgabe": "Berechne. a) 3,5 + 2,75",
                    "loesung": "6,25",
                    "braucht_bild": False,
                    "seite": 57,
                },
                {
                    "aufgabe": "Lies ab.",
                    "loesung": "Mo",
                    "braucht_bild": True,
                    "seite": 0,
                },
                {"aufgabe": "\\frac{1}{2}", "loesung": "1", "braucht_bild": False},
                {"aufgabe": "Runde auf Zehntel: b) 12,949", "loesung": "12,9"},
                {"aufgabe": "Berechne den Umfang.", "loesung": "8 cm"},
                {"aufgabe": "c) (2 + 3) · 4", "loesung": "20"},
                {"aufgabe": "ohne Lösung", "loesung": ""},
                7,
            ]
        }
    )
    assert gelesen is not None
    assert [(g.aufgabe, g.loesung, g.braucht_bild, g.seite) for g in gelesen] == [
        ("3,5 + 2,75", "6,25", False, 57),
        ("Lies ab.", "Mo", True, None),
        ("Runde auf Zehntel: 12,949", "12,9", False, None),
        ("Berechne den Umfang.", "8 cm", False, None),
        ("(2 + 3) · 4", "20", False, None),
    ]


async def test_vokabeln_aus_foto(
    hass: HomeAssistant, entry: MockConfigEntry, client: Client
) -> None:
    manager: LearnBuddyManager = entry.runtime_data
    store = manager.task_stores[FACH_ID]
    store.add(Vokabel(fach_id=FACH_ID, frage={"de": "schüchtern", "en": "shy"}))
    store.lektion_hinzufuegen("Unit 2")
    seiten = await _seiten(entry, 2)
    ki = AsyncMock(
        return_value={
            "vokabeln": [
                _vokabel(
                    "friend", "Freund, Freundin", ausgang_weitere=["Freund", "Freundin"]
                ),
                _vokabel("shy", "schüchtern", hinweis="p. 30"),
                _vokabel("friend", "Freund, Freundin"),
            ]
        }
    )
    with patch(GENERATE, ki):
        vorschau = await client.ok(
            "tasks/photo_extract", fach_id=FACH_ID, seiten=seiten
        )
    await hass.async_block_till_done()
    assert vorschau == {
        "typ": "vokabel",
        "zeilen": [
            {
                "frage": {"de": "Freund, Freundin", "en": "friend"},
                "alternativen": {"de": ["Freund", "Freundin"]},
                "hinweis": "p. 28",
                "seite": 231,
                "vorhanden": False,
            },
            {
                "frage": {"de": "schüchtern", "en": "shy"},
                "alternativen": {},
                "hinweis": "p. 30",
                "seite": 231,
                "vorhanden": True,
            },
            # The same entry twice on the pages
            {
                "frage": {"de": "Freund, Freundin", "en": "friend"},
                "alternativen": {},
                "hinweis": "p. 28",
                "seite": 231,
                "vorhanden": True,
            },
        ],
    }
    aufruf = ki.await_args.kwargs
    assert aufruf["structure"] is FOTO_VOKABELN_SCHEMA
    assert len(aufruf["attachments"]) == 2
    prompt = aufruf["instructions"]
    assert "English school book" in prompt
    assert "German translation" in prompt
    assert "Max" not in prompt
    # Nothing was stored and the photos are gone
    assert len(store.aufgaben) == 1
    assert manager.bilder.ids == set()

    zeilen = vorschau["zeilen"]
    zeilen[0]["frage"]["de"] = "Freund"
    ergebnis = await client.ok(
        "tasks/photo_accept",
        fach_id=FACH_ID,
        zeilen=[*zeilen[:2], {"frage": {"de": "", "en": "x"}}, {"unsinn": 1}],
        lektion="unit 2",
    )
    assert ergebnis == {"importiert": 1, "uebersprungen": 1, "fehler": [2, 3]}
    neu = next(a for a in store.aufgaben.values() if a.lektion == "Unit 2")
    assert isinstance(neu, Vokabel)
    assert neu.frage == {"de": "Freund", "en": "friend"}
    assert neu.alternativen == {"de": ["Freund", "Freundin"]}
    assert (neu.hinweis, neu.seite) == ("p. 28", 231)
    assert neu.quelle is Quelle.UPLOAD
    assert neu.geprueft is True


async def test_mathe_aus_foto(
    hass: HomeAssistant, entry: MockConfigEntry, client: Client
) -> None:
    manager: LearnBuddyManager = entry.runtime_data
    store = manager.task_stores[MATHE_ID]

    async def _ki(hass: HomeAssistant, **kwargs: Any) -> Any:
        if kwargs["structure"] is FOTO_MATHE_SCHEMA:
            assert "Max" not in kwargs["instructions"]
            assert len(kwargs["attachments"]) == 1
            return {
                "aufgaben": [
                    {
                        "aufgabe": "3,5 + 2,75",
                        "loesung": "6,25",
                        "braucht_bild": False,
                        "seite": 57,
                    },
                    {
                        "aufgabe": "0,6 · 0,4",
                        "loesung": "2,4",
                        "braucht_bild": False,
                        "seite": 57,
                    },
                    {
                        "aufgabe": "Lena kauft 3 Hefte zu je 1,25 €. Wie viel bezahlt sie?",
                        "loesung": "3,75 €",
                        "braucht_bild": False,
                        "seite": 57,
                    },
                    {
                        "aufgabe": "An welchem Tag fiel am meisten Regen?",
                        "loesung": "Dienstag",
                        "braucht_bild": True,
                        "seite": 57,
                    },
                ]
            }
        assert kwargs["structure"] is LOESUNG_SCHEMA
        # The AI solves the word problem without seeing the stored result
        assert "3,75" not in kwargs["instructions"]
        assert "Regen" not in kwargs["instructions"]
        return {"loesung": "3,75 €"}

    with patch(GENERATE, AsyncMock(side_effect=_ki)):
        vorschau = await client.ok(
            "tasks/photo_extract", fach_id=MATHE_ID, seiten=await _seiten(entry)
        )
    await hass.async_block_till_done()
    assert vorschau["typ"] == "mathe"
    assert [
        (z["aufgabe"], z["verifikation"], z["vorschlag"], z["braucht_bild"])
        for z in vorschau["zeilen"]
    ] == [
        ("3,5 + 2,75", "rechnerisch", None, False),
        # The printed or guessed result does not hold
        ("0,6 · 0,4", "abweichung", "6/25", False),
        ("Lena kauft 3 Hefte zu je 1,25 €. Wie viel bezahlt sie?", "ki", None, False),
        ("An welchem Tag fiel am meisten Regen?", "keine", None, True),
    ]
    assert vorschau["zeilen"][1]["vorschlag_durch"] == "lokal"
    assert manager.bilder.ids == set()
    assert store.aufgaben == {}

    zeilen = vorschau["zeilen"][:3]
    # The parent corrected the second line by hand
    zeilen[1] = {**zeilen[1], "loesung": "0,24", "verifikation": "keine"}
    assert await client.ok("tasks/photo_accept", fach_id=MATHE_ID, zeilen=zeilen) == {
        "importiert": 3,
        "uebersprungen": 0,
        "fehler": [],
    }
    eins, zwei, drei = store.aufgaben.values()
    assert isinstance(eins, MatheAufgabe)
    assert isinstance(zwei, MatheAufgabe)
    assert isinstance(drei, MatheAufgabe)
    assert (eins.loesung, eins.verifikation, eins.seite) == (
        "6,25",
        Verifikation.RECHNERISCH,
        57,
    )
    assert (zwei.loesung, zwei.verifikation) == ("0,24", Verifikation.KEINE)
    assert drei.verifikation is Verifikation.KI
    assert eins.quelle is Quelle.UPLOAD
    assert eins.lektion is None


async def test_foto_fehler(
    hass: HomeAssistant, entry: MockConfigEntry, client: Client
) -> None:
    manager: LearnBuddyManager = entry.runtime_data

    async def _fehler(typ: str, **daten: Any) -> str:
        fehler = await client.fehler(f"tasks/{typ}", **daten)
        await hass.async_block_till_done()
        return fehler["message"]

    seiten = await _seiten(entry)
    assert (
        await _fehler("photo_extract", fach_id=SACH_ID, seiten=seiten)
        == "foto_sachfach"
    )
    assert manager.bilder.ids == set()
    assert (
        await _fehler("photo_extract", fach_id=FACH_ID, seiten=[]) == "seiten_ungueltig"
    )
    for fach_id in (FACH_ID, MATHE_ID):
        with patch(GENERATE, AsyncMock(return_value={"falsch": 1})):
            assert (
                await _fehler(
                    "photo_extract", fach_id=fach_id, seiten=await _seiten(entry)
                )
                == "ki_fehler"
            )
    hass.states.async_set(KI, "unknown", {"supported_features": 1})
    assert (
        await _fehler("photo_extract", fach_id=FACH_ID, seiten=await _seiten(entry))
        == "ki_ohne_bilder"
    )

    zeile = {"frage": {"de": "a", "en": "b"}}
    assert (
        await _fehler("photo_accept", fach_id=SACH_ID, zeilen=[zeile])
        == "foto_sachfach"
    )
    assert (
        await _fehler("photo_accept", fach_id=FACH_ID, zeilen=[]) == "auswahl_ungueltig"
    )
    assert (
        await _fehler("photo_accept", fach_id=FACH_ID, zeilen=[zeile] * 201)
        == "auswahl_ungueltig"
    )
    assert (
        await _fehler("photo_accept", fach_id=FACH_ID, zeilen=[zeile], lektion="x")
        == "lektion_unbekannt"
    )
