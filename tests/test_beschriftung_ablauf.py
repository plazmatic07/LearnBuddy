"""Tests for labelling tasks: find labels, edit, ask, evaluate."""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, patch

from homeassistant.core import HomeAssistant
import pytest
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_mock_service,
)
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from custom_components.learnbuddy.ai import parse_beschriftungen
from custom_components.learnbuddy.const import DOMAIN
from custom_components.learnbuddy.manager import LearnBuddyManager
from custom_components.learnbuddy.models import SachAufgabe, SachForm

from .conftest import FACH_DATEN, FACH_ID, KIND_DATEN, KIND_ID, subentry
from .test_bilder import bild_daten
from .test_bildversand import AKTION
from .test_mathe_ablauf import GENERATE
from .test_sach_ablauf import SACH_DATEN, SACH_ID
from .test_websocket import Client

KI = "ai_task.test"


@pytest.fixture
async def entry(hass: HomeAssistant) -> MockConfigEntry:
    """Set up a child who gets images through an action, with an AI."""
    config_entry = MockConfigEntry(
        domain=DOMAIN,
        title="LearnBuddy",
        data={},
        options={"timeout_minuten": 60, "sprache": "de", "ki_entity": KI},
        subentries_data=[
            subentry("kind", KIND_ID, "Max", {**KIND_DATEN, "bild_aktion": AKTION}),
            subentry("fach", FACH_ID, "Englisch (Max)", FACH_DATEN),
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


def _feld(nr: int, text: str = "", **felder: Any) -> dict[str, Any]:
    return {
        "nr": nr,
        "x": 0.1 * nr,
        "y": 0.1,
        "b": 0.08,
        "h": 0.05,
        "text": text,
        "alternativen": [],
    } | felder


def test_parse_beschriftungen() -> None:
    assert parse_beschriftungen(None) is None
    assert parse_beschriftungen({"beschriftungen": 1}) is None
    gefunden = parse_beschriftungen(
        {
            "beschriftungen": [
                {"text": "Tubus", "ymin": 120, "xmin": 500, "ymax": 150, "xmax": 560},
                {"text": " Okular ", "ymin": 60, "xmin": 300, "ymax": 90, "xmax": 380},
                {"text": "Blende", "ymin": 600, "xmin": 400, "ymax": 640, "xmax": 470},
                {"text": "Leer", "ymin": 5, "xmin": 5, "ymax": 5, "xmax": 50},
                {"text": "", "ymin": 1, "xmin": 1, "ymax": 9, "xmax": 9},
                {"text": "Kaputt", "ymin": "x"},
                "kaputt",
            ]
        }
    )
    assert gefunden is not None
    assert [g.text for g in gefunden] == ["Okular", "Tubus", "Blende"]
    assert (gefunden[0].x, gefunden[0].y) == (0.3, 0.06)
    assert gefunden[0].b == pytest.approx(0.08)


async def test_beschriftungen_erkennen_und_speichern(
    hass: HomeAssistant, entry: MockConfigEntry, client: Client
) -> None:
    manager: LearnBuddyManager = entry.runtime_data
    store = manager.task_stores[SACH_ID]
    original = await manager.bilder.async_speichere(bild_daten())

    ki = AsyncMock(
        return_value={
            "beschriftungen": [
                {"text": "Okular", "ymin": 60, "xmin": 300, "ymax": 90, "xmax": 380},
                {"text": "Tubus", "ymin": 120, "xmin": 500, "ymax": 150, "xmax": 560},
            ]
        }
    )
    with patch(GENERATE, ki):
        erkannt = await client.ok("tasks/label_detect", fach_id=SACH_ID, bild=original)
    await hass.async_block_till_done()
    assert [(f["nr"], f["text"]) for f in erkannt["felder"]] == [
        (1, "Okular"),
        (2, "Tubus"),
    ]
    assert "Everything written on the image" in ki.call_args.kwargs["instructions"]

    felder = [_feld(1, "Okular", alternativen=["Okular-Linse"]), _feld(2, "Tubus")]
    vorschau = await client.ok(
        "tasks/label_preview", fach_id=SACH_ID, bild=original, felder=felder
    )
    assert manager.bilder.pfad(vorschau["vorschau"]) is not None
    zweite = await client.ok(
        "tasks/label_preview",
        fach_id=SACH_ID,
        bild=original,
        felder=felder,
        vorherige=vorschau["vorschau"],
    )
    assert manager.bilder.pfad(vorschau["vorschau"]) is None

    ergebnis = await client.ok(
        "tasks/label_save",
        fach_id=SACH_ID,
        bild=original,
        felder=felder,
        vorschau=zweite["vorschau"],
    )
    assert ergebnis == {"neu": 2, "geaendert": 0, "entfernt": 0}
    assert manager.bilder.pfad(zweite["vorschau"]) is None
    aufgaben = [a for a in store.aufgaben.values() if isinstance(a, SachAufgabe)]
    assert [(a.frage, a.antwort, a.form) for a in aufgaben] == [
        ("Nr. 1", "Okular", SachForm.BESCHRIFTUNG),
        ("Nr. 2", "Tubus", SachForm.BESCHRIFTUNG),
    ]
    assert aufgaben[0].alternativen == ["Okular-Linse"]
    assert aufgaben[0].bild == aufgaben[1].bild != original
    assert aufgaben[0].original_bild == original
    assert {aufgaben[0].bild, original} <= manager.verwendete_bilder()

    # Correct the labels: number 2 changes, number 1 goes, number 3 is new
    aufgaben[1].statistik_fuer("sach").richtig = 4
    alt_bild = aufgaben[0].bild
    gelesen = await client.ok("tasks/label_get", fach_id=SACH_ID, bild=original)
    assert [(f["nr"], f["text"]) for f in gelesen["felder"]] == [
        (1, "Okular"),
        (2, "Tubus"),
    ]
    ergebnis = await client.ok(
        "tasks/label_save",
        fach_id=SACH_ID,
        bild=original,
        felder=[_feld(2, "Tubus (Rohr)"), _feld(3, "Stativ")],
    )
    assert ergebnis == {"neu": 1, "geaendert": 1, "entfernt": 1}
    rest = {a.frage: a for a in store.aufgaben.values()}
    assert sorted(rest) == ["Nr. 2", "Nr. 3"]
    assert rest["Nr. 2"].statistik["sach"].richtig == 4
    assert rest["Nr. 2"].antwort == "Tubus (Rohr)"
    assert rest["Nr. 2"].bild == rest["Nr. 3"].bild != alt_bild
    # The old numbered image is gone, the original stays
    assert manager.bilder.pfad(alt_bild) is None
    assert manager.bilder.pfad(original) is not None

    # Deleting the tasks frees the images
    await client.ok(
        "tasks/delete",
        fach_id=SACH_ID,
        aufgabe_ids=[a.id for a in rest.values()],
        bestaetigt=True,
    )
    assert manager.verwendete_bilder() == set()


async def test_beschriftung_fehler(
    hass: HomeAssistant, entry: MockConfigEntry, client: Client
) -> None:
    manager: LearnBuddyManager = entry.runtime_data
    original = await manager.bilder.async_speichere(bild_daten())

    async def _fehler(typ: str, **daten: Any) -> str:
        fehler = await client.fehler(f"tasks/{typ}", **daten)
        return fehler["message"]

    felder = [_feld(1, "Okular")]
    assert (
        await _fehler("label_preview", fach_id=FACH_ID, bild=original, felder=felder)
        == "beschriftung_nur_sachfach"
    )
    assert (
        await _fehler(
            "label_preview", fach_id=SACH_ID, bild="0" * 32 + ".png", felder=felder
        )
        == "bild_unbekannt"
    )
    for kaputt in ([], [_feld(0, "x")], [_feld(1, "a"), _feld(1, "b")]):
        assert (
            await _fehler(
                "label_preview", fach_id=SACH_ID, bild=original, felder=kaputt
            )
            == "beschriftung_felder_ungueltig"
        )
    assert (
        await _fehler("label_save", fach_id=SACH_ID, bild=original, felder=[_feld(1)])
        == "sach_antwort_ungueltig"
    )
    assert (
        await _fehler(
            "label_save",
            fach_id=SACH_ID,
            bild=original,
            felder=felder,
            lektion="gibt es nicht",
        )
        == "lektion_unbekannt"
    )
    assert (
        await _fehler("label_get", fach_id=SACH_ID, bild=original)
        == "aufgabe_unbekannt"
    )


async def test_beschriftung_fragen_und_bewerten(
    hass: HomeAssistant, entry: MockConfigEntry, client: Client
) -> None:
    manager: LearnBuddyManager = entry.runtime_data
    original = await manager.bilder.async_speichere(bild_daten())
    await client.ok(
        "tasks/label_save",
        fach_id=SACH_ID,
        bild=original,
        felder=[_feld(3, "Objektträger", alternativen=["Objekttraeger"])],
    )
    aufgabe = next(iter(manager.task_stores[SACH_ID].aufgaben.values()))
    assert isinstance(aufgabe, SachAufgabe)
    aufrufe = async_mock_service(hass, "test", "bild")

    await hass.services.async_call(
        DOMAIN, "ask_now", {"kind_id": KIND_ID}, blocking=True
    )
    await hass.async_block_till_done()
    assert len(aufrufe) == 1
    assert aufrufe[0].data["text"] == (
        "Hallo Max! 🔬 Biologie: Was steht im Bild bei Nummer 3?"
    )
    assert aufrufe[0].data["datei"].endswith(aufgabe.bild)

    async def _antwort(text: str) -> str:
        ergebnis = await hass.services.async_call(
            DOMAIN,
            "submit_answer",
            {"kind_id": KIND_ID, "text": text},
            blocking=True,
            return_response=True,
        )
        await hass.async_block_till_done()
        assert isinstance(ergebnis, dict)
        assert ergebnis["bewertet_von"] == "lokal"
        return str(ergebnis["ergebnis"])

    assert await _antwort("objektträger") == "richtig"
    await hass.services.async_call(
        DOMAIN, "ask_now", {"kind_id": KIND_ID}, blocking=True
    )
    await hass.async_block_till_done()
    assert await _antwort("Objekttraeger") == "richtig"
    await hass.services.async_call(
        DOMAIN, "ask_now", {"kind_id": KIND_ID}, blocking=True
    )
    await hass.async_block_till_done()
    assert await _antwort("Blende") == "falsch"
    assert aufgabe.statistik["sach"].richtig == 2
    assert aufgabe.statistik["sach"].falsch == 1


async def test_beschriftung_ohne_bildweg_wird_nicht_gefragt(
    hass: HomeAssistant, entry: MockConfigEntry, client: Client
) -> None:
    """A child who cannot get images is not asked what is in a picture."""
    manager: LearnBuddyManager = entry.runtime_data
    original = await manager.bilder.async_speichere(bild_daten())
    await client.ok(
        "tasks/label_save", fach_id=SACH_ID, bild=original, felder=[_feld(1, "Tubus")]
    )
    aufgabe = next(iter(manager.task_stores[SACH_ID].aufgaben.values()))
    kind = manager.kinder[KIND_ID]
    with patch.object(manager.messenger, "kann_bilder", return_value=False):
        assert manager._zustellbar(kind.id, [aufgabe]) == []
    assert manager._zustellbar(kind.id, [aufgabe]) == [aufgabe]
