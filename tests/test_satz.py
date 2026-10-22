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


KI = "ai_task.test"
LUECKE_SATZ = {
    "satz": "I ____ a boy.",
    "form": "luecke",
    "antwort": "am",
    "alternativen": ["'m", "am"],
    "falsche_optionen": [],
}
AUSWAHL_SATZ = {
    "satz": "___ name is Anna.",
    "form": "auswahl",
    "antwort": "Her",
    "alternativen": [],
    "falsche_optionen": ["She", "Hers", "Her"],
}


def test_parse_satzaufgaben() -> None:
    from custom_components.learnbuddy.ai import parse_satzaufgaben  # noqa: PLC0415

    assert parse_satzaufgaben({}) is None
    ergebnis = parse_satzaufgaben(
        {
            "saetze": [
                LUECKE_SATZ,
                AUSWAHL_SATZ,
                # No gap, two gaps, no answer, wrong form, too few options
                {**LUECKE_SATZ, "satz": "I am a boy."},
                {**LUECKE_SATZ, "satz": "___ am ___ boy."},
                {**LUECKE_SATZ, "antwort": ""},
                {**LUECKE_SATZ, "form": "kurz"},
                {**AUSWAHL_SATZ, "falsche_optionen": ["She"]},
                # Other spellings of the gap are normalised
                {**LUECKE_SATZ, "satz": "She [...] nice.", "antwort": "is"},
                "kein Objekt",
            ]
        }
    )
    assert ergebnis is not None
    assert [(s.satz, s.form.value) for s in ergebnis] == [
        ("I ___ a boy.", "luecke"),
        ("___ name is Anna.", "auswahl"),
        ("She ___ nice.", "luecke"),
    ]
    # The answer is no alternative of itself, nor a wrong option
    assert ergebnis[0].alternativen == ["'m"]
    assert ergebnis[1].falsche_optionen == ["She", "Hers"]


async def _mit_ki(hass: HomeAssistant, entry: MockConfigEntry) -> LearnBuddyManager:
    hass.states.async_set(KI, "unknown", {"supported_features": 3})
    hass.config_entries.async_update_entry(
        entry, options={**entry.options, "ki_entity": KI}
    )
    await hass.async_block_till_done()
    manager: LearnBuddyManager = entry.runtime_data
    return manager


async def test_satzaufgaben_erzeugen(
    hass: HomeAssistant,
    mit_vokabeln: MockConfigEntry,
    client: Client,  # noqa: F811
) -> None:
    from unittest.mock import AsyncMock, patch  # noqa: PLC0415

    manager = await _mit_ki(hass, mit_vokabeln)
    store = manager.task_stores[FACH_ID]
    bereich = await _satzbereich(client)

    ki = AsyncMock(return_value={"saetze": [LUECKE_SATZ, AUSWAHL_SATZ, LUECKE_SATZ]})
    with patch("custom_components.learnbuddy.ai._async_generate_data", ki):
        ergebnis = await client.ok(
            "tasks/generate_sentences",
            fach_id=FACH_ID,
            bereich=bereich,
            anzahl=3,
            form="gemischt",
            beschreibung="Personalpronomen in kurzen Sätzen",
        )
    assert (ergebnis["erzeugt"], ergebnis["uebersprungen"]) == (2, 1)
    instruktionen = ki.await_args.kwargs["instructions"]
    assert "Personalpronomen in kurzen Sätzen" in instruktionen
    assert "in English" in instruktionen
    assert ki.await_args.kwargs["attachments"] is None
    for aufgabe_id in ergebnis["aufgabe_ids"]:
        aufgabe = store.aufgaben[aufgabe_id]
        assert isinstance(aufgabe, SachAufgabe)
        assert aufgabe.bereich == bereich
        # Nothing can verify a sentence, so it waits for approval
        assert aufgabe.geprueft is False

    # Without a text or photos there is nothing to go on
    fehler = await client.fehler(
        "tasks/generate_sentences", fach_id=FACH_ID, bereich=bereich, anzahl=3
    )
    assert fehler["message"] == "generieren_ohne_vorgabe"
    # Only into a sentence section
    fehler = await client.fehler(
        "tasks/generate_sentences",
        fach_id=FACH_ID,
        bereich="standard",
        anzahl=3,
        beschreibung="x",
    )
    assert fehler["message"] == "saetze_nur_satzbereich"


async def test_satzaufgaben_aus_fotos(
    hass: HomeAssistant,
    mit_vokabeln: MockConfigEntry,
    client: Client,  # noqa: F811
) -> None:
    from unittest.mock import AsyncMock, patch  # noqa: PLC0415

    from .test_sach_ablauf import _seiten  # noqa: PLC0415

    manager = await _mit_ki(hass, mit_vokabeln)
    bereich = await _satzbereich(client)
    seiten = await _seiten(mit_vokabeln, 2)

    ki = AsyncMock(return_value={"saetze": [LUECKE_SATZ]})
    with patch("custom_components.learnbuddy.ai._async_generate_data", ki):
        ergebnis = await client.ok(
            "tasks/generate_sentences",
            fach_id=FACH_ID,
            bereich=bereich,
            anzahl=1,
            form="luecke",
            seiten=seiten,
            uebernehmen=True,
        )
    assert ergebnis["erzeugt"] == 1
    assert "Take over the exercises" in ki.await_args.kwargs["instructions"]
    assert len(ki.await_args.kwargs["attachments"]) == 2
    # The pages are not kept
    assert all(manager.bilder.pfad(seite) is None for seite in seiten)


UEBERSETZUNG = {
    "satz": "Ich bin ein Junge.",
    "form": "uebersetzung",
    "antwort": "I am a boy.",
    "alternativen": ["I'm a boy."],
    "falsche_optionen": [],
}


def test_parse_uebersetzung() -> None:
    from custom_components.learnbuddy.ai import parse_satzaufgaben  # noqa: PLC0415

    ergebnis = parse_satzaufgaben(
        {
            "saetze": [
                UEBERSETZUNG,
                # A sentence to translate has no gap
                {**UEBERSETZUNG, "satz": "Ich ___ ein Junge."},
            ]
        }
    )
    assert ergebnis is not None
    assert [(s.satz, s.form.value, s.alternativen) for s in ergebnis] == [
        ("Ich bin ein Junge.", "uebersetzung", ["I'm a boy."])
    ]


async def test_uebersetzung_fragen_und_bewerten(
    hass: HomeAssistant,
    mit_vokabeln: MockConfigEntry,
    notify_calls: list[ServiceCall],
    client: Client,  # noqa: F811
) -> None:
    from unittest.mock import AsyncMock, patch  # noqa: PLC0415

    bereich = await _satzbereich(client)
    await client.ok(
        "tasks/create",
        fach_id=FACH_ID,
        aufgabe={
            "bereich": bereich,
            "form": "uebersetzung",
            "frage": "Ich bin ein Junge.",
            "antwort": "I am a boy.",
            "alternativen": ["I'm a boy."],
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

    ergebnis = await frage_und_antwort("i am a boy")
    assert ergebnis["ergebnis"] == "richtig"
    assert ergebnis["bewertet_von"] == "lokal"
    assert (
        "Übersetze ins Englische: Ich bin ein Junge." in notify_calls[0].data["message"]
    )
    assert (await frage_und_antwort("I'm a boy."))["ergebnis"] == "richtig"
    # Without an AI a wrong sentence is wrong
    assert (await frage_und_antwort("He is a boy."))["ergebnis"] == "falsch"

    # With an AI another wording is judged by it
    manager = await _mit_ki(hass, mit_vokabeln)
    assert manager is not None
    ki = AsyncMock(return_value={"ergebnis": "richtig", "erklaerung": "Stimmt."})
    with patch("custom_components.learnbuddy.ai._async_generate_data", ki):
        ergebnis = await frage_und_antwort("I am a young boy.")
    assert (ergebnis["ergebnis"], ergebnis["bewertet_von"]) == ("richtig", "ki")
    assert "Ich bin ein Junge." in ki.await_args.kwargs["instructions"]


async def test_uebersetzungen_erzeugen(
    hass: HomeAssistant,
    mit_vokabeln: MockConfigEntry,
    client: Client,  # noqa: F811
) -> None:
    from unittest.mock import AsyncMock, patch  # noqa: PLC0415

    manager = await _mit_ki(hass, mit_vokabeln)
    bereich = await _satzbereich(client)
    ki = AsyncMock(return_value={"saetze": [UEBERSETZUNG]})
    with patch("custom_components.learnbuddy.ai._async_generate_data", ki):
        ergebnis = await client.ok(
            "tasks/generate_sentences",
            fach_id=FACH_ID,
            bereich=bereich,
            anzahl=1,
            form="uebersetzung",
            beschreibung="Personalpronomen",
        )
    assert ergebnis["erzeugt"] == 1
    instruktionen = ki.await_args.kwargs["instructions"]
    assert "Form of all tasks: uebersetzung." in instruktionen
    assert "in German" in instruktionen
    aufgabe = manager.task_stores[FACH_ID].aufgaben[ergebnis["aufgabe_ids"][0]]
    assert isinstance(aufgabe, SachAufgabe)
    assert aufgabe.form is SachForm.UEBERSETZUNG
    assert aufgabe.alternativen == ["I'm a boy."]


async def test_erzeugen_haelt_sich_an_die_form(
    hass: HomeAssistant,
    mit_vokabeln: MockConfigEntry,
    client: Client,  # noqa: F811
) -> None:
    from unittest.mock import AsyncMock, patch  # noqa: PLC0415

    manager = await _mit_ki(hass, mit_vokabeln)
    bereich = await _satzbereich(client)
    ki = AsyncMock(return_value={"saetze": [UEBERSETZUNG, LUECKE_SATZ, AUSWAHL_SATZ]})
    with patch("custom_components.learnbuddy.ai._async_generate_data", ki):
        ergebnis = await client.ok(
            "tasks/generate_sentences",
            fach_id=FACH_ID,
            bereich=bereich,
            anzahl=3,
            form="uebersetzung",
            beschreibung="Personalpronomen",
        )
        # "gemischt" means gap and choice, no translations
        gemischt = await client.ok(
            "tasks/generate_sentences",
            fach_id=FACH_ID,
            bereich=bereich,
            anzahl=3,
            form="gemischt",
            beschreibung="Personalpronomen",
        )
    store = manager.task_stores[FACH_ID]
    assert [store.aufgaben[i].form.value for i in ergebnis["aufgabe_ids"]] == [  # type: ignore[union-attr]
        "uebersetzung"
    ]
    assert ergebnis["verworfen"] == 2
    assert [store.aufgaben[i].form.value for i in gemischt["aufgabe_ids"]] == [  # type: ignore[union-attr]
        "luecke",
        "auswahl",
    ]


async def test_hilfe_bei_luecke_und_auswahl(
    hass: HomeAssistant,
    mit_vokabeln: MockConfigEntry,
    notify_calls: list[ServiceCall],
    client: Client,  # noqa: F811
) -> None:
    from unittest.mock import AsyncMock, patch  # noqa: PLC0415

    manager = await _mit_ki(hass, mit_vokabeln)
    store = manager.task_stores[FACH_ID]
    bereich = await _satzbereich(client)
    aufgabe = await client.ok(
        "tasks/create",
        fach_id=FACH_ID,
        aufgabe={
            "bereich": bereich,
            "form": "luecke",
            "frage": "___ is my best friend.",
            "antwort": "he",
            "hilfe": "Er ist mein bester Freund.",
        },
    )
    assert aufgabe["hilfe"] == "Er ist mein bester Freund."
    fehler = await client.fehler(
        "tasks/create",
        fach_id=FACH_ID,
        aufgabe={
            "bereich": bereich,
            "form": "luecke",
            "frage": "x ___",
            "antwort": "y",
            "hilfe": "z" * 501,
        },
    )
    assert fehler["message"] == "hilfe_ungueltig"

    # The translation is only sent when the task says so
    assert aufgabe["hilfe_senden"] is False
    await client.ok(
        "ask", kind_id=KIND_ID, fach_id=FACH_ID, bereiche=[bereich], anzahl=1
    )
    await hass.async_block_till_done()
    assert (
        notify_calls[-1].data["message"].endswith("Setze ein: ___ is my best friend.")
    )
    await client.ok(
        "tasks/update",
        fach_id=FACH_ID,
        aufgabe_id=aufgabe["id"],
        aenderungen={"hilfe_senden": True},
    )
    await client.ok(
        "ask", kind_id=KIND_ID, fach_id=FACH_ID, bereiche=[bereich], anzahl=1
    )
    await hass.async_block_till_done()
    assert (
        notify_calls[-1]
        .data["message"]
        .endswith("Setze ein: ___ is my best friend.\n(Er ist mein bester Freund.)")
    )
    fehler = await client.fehler(
        "tasks/update",
        fach_id=FACH_ID,
        aufgabe_id=aufgabe["id"],
        aenderungen={"hilfe_senden": "ja"},
    )
    assert fehler["code"] == "invalid_format"

    # The AI delivers it with gap tasks only
    ki = AsyncMock(
        return_value={
            "saetze": [
                {**LUECKE_SATZ, "hilfe": "Ich bin ein Junge."},
                {**AUSWAHL_SATZ, "hilfe": "Ihr Name ist Anna."},
                {**UEBERSETZUNG, "hilfe": "wird ignoriert"},
            ]
        }
    )
    with patch("custom_components.learnbuddy.ai._async_generate_data", ki):
        ergebnis = await client.ok(
            "tasks/generate_sentences",
            fach_id=FACH_ID,
            bereich=bereich,
            anzahl=3,
            form="gemischt",
            beschreibung="Pronomen",
        )
    assert "hilfe" in ki.await_args.kwargs["instructions"]
    hilfen = [store.aufgaben[i].hilfe for i in ergebnis["aufgabe_ids"]]  # type: ignore[union-attr]
    # Only gap tasks carry a translation
    assert hilfen == ["Ich bin ein Junge.", None]
    # Whether it is sent is the parents' choice
    assert not any(
        store.aufgaben[i].hilfe_senden  # type: ignore[union-attr]
        for i in ergebnis["aufgabe_ids"]
    )


def test_hilfe_senden_aus_alten_daten() -> None:
    from custom_components.learnbuddy.models import aufgabe_from_dict  # noqa: PLC0415

    basis = SachAufgabe(
        fach_id="f", frage="I ___", antwort="am", form=SachForm.LUECKE
    ).to_dict()
    basis.pop("hilfe_senden")
    # Version 0.9.2 always sent a translation, new tasks do not
    alt = aufgabe_from_dict({**basis, "hilfe": "Ich bin."})
    assert isinstance(alt, SachAufgabe)
    assert alt.hilfe_senden is True
    ohne = aufgabe_from_dict(basis)
    assert isinstance(ohne, SachAufgabe)
    assert ohne.hilfe_senden is False
    assert SachAufgabe(fach_id="f", frage="x", antwort="y").hilfe_senden is False
