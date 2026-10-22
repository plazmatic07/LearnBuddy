"""Tests for sentence tasks (gap, choice) next to vocabulary in a subject."""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant, ServiceCall
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.learnbuddy.const import DOMAIN
from custom_components.learnbuddy.manager import LearnBuddyManager
from custom_components.learnbuddy.models import (
    Fach,
    MatheAufgabe,
    SachAufgabe,
    SachForm,
    Vokabel,
    karten_richtungen,
)

from .conftest import FACH_ID, KIND_ID
from .test_websocket import Client, client  # noqa: F401


async def _satzbereich(client: Client) -> str:  # noqa: F811
    ergebnis = await client.ok(
        "sections/add", fach_id=FACH_ID, name="Personalpronomen", art="satz"
    )
    bereich: str = ergebnis["bereiche"][1]["id"]
    assert ergebnis["bereiche"][1]["art"] == "satz"
    return bereich


def test_karten_richtungen() -> None:
    richtungen = Fach(
        id="f", kind_id="k", name="Englisch", sprachen=("de", "en")
    ).richtungen
    assert richtungen == ("de>en", "en>de", "sach")
    vokabel = Vokabel(fach_id="f", frage={"de": "Hund", "en": "dog"})
    satz = SachAufgabe(fach_id="f", frage="I ___", antwort="am", form=SachForm.LUECKE)
    assert karten_richtungen(vokabel, richtungen) == ["de>en", "en>de"]
    assert karten_richtungen(satz, richtungen) == ["sach"]
    assert not vokabel.fragbar("sach")
    assert not satz.fragbar("de>en")
    mathe = MatheAufgabe(fach_id="f", aufgabe="1+1", loesung="2")
    assert karten_richtungen(mathe, ("mathe",)) == ["mathe"]


async def test_satzaufgaben_anlegen_und_verschieben(
    mit_vokabeln: MockConfigEntry,
    client: Client,  # noqa: F811
) -> None:
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    store = manager.task_stores[FACH_ID]
    bereich = await _satzbereich(client)

    aufgabe = await client.ok(
        "tasks/create",
        fach_id=FACH_ID,
        aufgabe={
            "bereich": bereich,
            "form": "luecke",
            "frage": "I ___ a boy.",
            "antwort": "am",
            "alternativen": ["'m"],
        },
    )
    assert aufgabe["typ"] == "sach"
    assert aufgabe["form"] == "luecke"
    assert aufgabe["alternativen"] == ["'m"]
    assert isinstance(store.aufgaben[aufgabe["id"]], SachAufgabe)

    # A vocabulary pair does not fit into the sentence section
    fehler = await client.fehler(
        "tasks/create",
        fach_id=FACH_ID,
        aufgabe={"bereich": bereich, "frage": {"de": "Hund", "en": "dog"}},
    )
    assert fehler["code"] == "invalid_format"

    # Tasks only move to a section of their own kind
    wort = next(a for a in store.aufgaben.values() if isinstance(a, Vokabel))
    fehler = await client.fehler(
        "tasks/update",
        fach_id=FACH_ID,
        aufgabe_id=wort.id,
        aenderungen={"bereich": bereich},
    )
    assert fehler["message"] == "bereich_art_ungueltig"
    fehler = await client.fehler(
        "tasks/update",
        fach_id=FACH_ID,
        aufgabe_id=aufgabe["id"],
        aenderungen={"bereich": "standard"},
    )
    assert fehler["message"] == "bereich_art_ungueltig"

    # Text and photo import only know vocabulary
    fehler = await client.fehler(
        "tasks/import_text",
        fach_id=FACH_ID,
        inhalt="Hund;dog",
        bereich=bereich,
    )
    assert fehler["message"] == "import_satz"
    fehler = await client.fehler(
        "tasks/photo_accept", fach_id=FACH_ID, zeilen=[{"frage": {}}], bereich=bereich
    )
    assert fehler["message"] == "foto_satz"


async def test_luecke_fragen_und_bewerten(
    hass: HomeAssistant,
    mit_vokabeln: MockConfigEntry,
    notify_calls: list[ServiceCall],
    client: Client,  # noqa: F811
) -> None:
    bereich = await _satzbereich(client)
    await client.ok(
        "tasks/create",
        fach_id=FACH_ID,
        aufgabe={
            "bereich": bereich,
            "form": "luecke",
            "frage": "I ___ a boy.",
            "antwort": "am",
            "alternativen": ["'m"],
        },
    )

    async def frage_und_antwort(antwort: str) -> dict[str, Any]:
        await client.ok(
            "ask", kind_id=KIND_ID, fach_id=FACH_ID, bereiche=[bereich], anzahl=1
        )
        await hass.async_block_till_done()
        ergebnis = await hass.services.async_call(
            DOMAIN,
            "submit_answer",
            {"kind_id": KIND_ID, "text": antwort},
            blocking=True,
            return_response=True,
        )
        await hass.async_block_till_done()
        assert isinstance(ergebnis, dict)
        return ergebnis

    ergebnis = await frage_und_antwort("Am")
    assert ergebnis["ergebnis"] == "richtig"
    assert ergebnis["bewertet_von"] == "lokal"
    fragen = [c.data["message"] for c in notify_calls]
    assert any("Setze ein: I ___ a boy." in f for f in fragen)

    assert (await frage_und_antwort("are"))["ergebnis"] == "falsch"
    assert (await frage_und_antwort("'m"))["ergebnis"] == "richtig"


async def test_export_import_mit_satzaufgaben(
    mit_vokabeln: MockConfigEntry,
    client: Client,  # noqa: F811
) -> None:
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    store = manager.task_stores[FACH_ID]
    bereich = await _satzbereich(client)
    await client.ok(
        "tasks/create",
        fach_id=FACH_ID,
        aufgabe={
            "bereich": bereich,
            "form": "auswahl",
            "frage": "___ name is Anna.",
            "antwort": "Her",
            "falsche_optionen": ["She", "Hers"],
        },
    )
    daten = await client.ok("tasks/export", fach_id=FACH_ID)
    satz = [a for a in daten["aufgaben"] if a["typ"] == "sach"]
    assert len(satz) == 1
    assert satz[0]["falsche_optionen"] == ["She", "Hers"]

    # The tasks go into the chosen section; vocabulary may not
    daten["aufgaben"] = [{**satz[0], "frage": "___ book is red."}]
    ergebnis = await client.ok(
        "tasks/import_json", fach_id=FACH_ID, daten=daten, bereich=bereich
    )
    assert ergebnis == {"importiert": 1, "uebersprungen": 0, "fehler": []}
    ergebnis = await client.ok("tasks/import_json", fach_id=FACH_ID, daten=daten)
    assert ergebnis["fehler"] == [0]
    assert sum(1 for a in store.aufgaben.values() if isinstance(a, SachAufgabe)) == 2
