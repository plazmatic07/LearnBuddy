"""Tests for importer, texts, messaging, platforms, diagnostics, translations."""

from __future__ import annotations

from datetime import timedelta
import json
from pathlib import Path
from typing import Any

from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.util import dt as dt_util
import pytest
from pytest_homeassistant_custom_component.common import (
    MockConfigEntry,
    async_mock_service,
)

from custom_components.learnbuddy.bilder import BildAblage
from custom_components.learnbuddy.const import DOMAIN
from custom_components.learnbuddy.diagnostics import (
    async_get_config_entry_diagnostics,
)
from custom_components.learnbuddy.importer import parse_vokabeln
from custom_components.learnbuddy.messaging import Messenger, notify_ziel
from custom_components.learnbuddy.models import Kind
from custom_components.learnbuddy.texte import TEXTE, sprachname, text, waehle_sprache

from .conftest import FACH_ID, KIND_ID

KOMPONENTE = Path(__file__).parents[1] / "custom_components" / "learnbuddy"


# --- importer ---------------------------------------------------------------


def test_parse_trennzeichen_automatisch() -> None:
    ergebnis = parse_vokabeln(
        "Hund;dog\nKatze\tcat\nMaus = mouse\nVogel - bird\nFisch, fish\n"
    )
    assert [(z.ausgang, z.ziel) for z in ergebnis.zeilen] == [
        ("Hund", "dog"),
        ("Katze", "cat"),
        ("Maus", "mouse"),
        ("Vogel", "bird"),
        ("Fisch", "fish"),
    ]
    assert ergebnis.fehlerzeilen == []


def test_parse_alternativen_und_hinweis() -> None:
    ergebnis = parse_vokabeln("groß|gross; big | large |; Adjektiv; häufig")
    zeile = ergebnis.zeilen[0]
    assert zeile.ausgang == "groß"
    assert zeile.ausgang_alternativen == ["gross"]
    assert zeile.ziel == "big"
    assert zeile.ziel_alternativen == ["large"]
    assert zeile.hinweis == "Adjektiv häufig"


def test_parse_fehler_und_explizites_trennzeichen() -> None:
    ergebnis = parse_vokabeln("a,b;c\nnur eins\n | ;x\n\n#kommentar", trennzeichen=";")
    assert [(z.ausgang, z.ziel) for z in ergebnis.zeilen] == [("a,b", "c")]
    assert ergebnis.fehlerzeilen == [2, 3]


# --- texts ------------------------------------------------------------------


def test_texte() -> None:
    assert waehle_sprache("de-CH") == "de"
    assert waehle_sprache("fr") == "en"
    assert sprachname("de", "en") == "Englisch"
    assert sprachname("en", "xx") == "xx"
    assert text("en", "keine_frage", name="Max").startswith(
        "Hi Max, there is no open question right now."
    )
    assert text("en", "zusatz_start", name="Max", anzahl="3") == (
        "Great, Max! 💪 3 more questions are coming."
    )
    assert TEXTE["de"].keys() == TEXTE["en"].keys()


# --- messaging --------------------------------------------------------------


async def test_senden_ueber_entity(hass: HomeAssistant) -> None:
    calls = async_mock_service(hass, "notify", "send_message")
    kind = Kind(id="k", name="Lena", notify_entity="notify.lena")
    assert notify_ziel(kind) == "notify.lena"
    assert await Messenger(hass, BildAblage(hass)).async_send(kind, "Hallo") is True
    assert calls[0].data == {"message": "Hallo", "entity_id": "notify.lena"}


async def test_senden_ueber_service_mit_daten(hass: HomeAssistant) -> None:
    calls = async_mock_service(hass, "notify", "whatsapp")
    kind = Kind(
        id="k",
        name="Lena",
        notify_service="whatsapp",
        notify_target=("49",),
        notify_data={"a": 1},
    )
    await Messenger(hass, BildAblage(hass)).async_send_or_raise(kind, "Hallo")
    assert calls[0].data == {"message": "Hallo", "target": ["49"], "data": {"a": 1}}


async def test_senden_ohne_ziel(hass: HomeAssistant) -> None:
    messenger = Messenger(hass, BildAblage(hass))
    kind = Kind(id="k", name="Lena")
    assert await messenger.async_send(kind, "Hallo") is False
    with pytest.raises(HomeAssistantError):
        await messenger.async_send_or_raise(kind, "Hallo")


async def test_wiederholung_wird_abgebrochen(hass: HomeAssistant) -> None:
    messenger = Messenger(hass, BildAblage(hass))
    kind = Kind(id="k", name="Lena", notify_service="fehlt")
    assert await messenger.async_send(kind, "Hallo", wiederholen=True) is False
    assert len(messenger._wiederholungen) == 1
    messenger.async_cancel()
    assert not messenger._wiederholungen


# --- platforms --------------------------------------------------------------


async def test_sensoren(hass: HomeAssistant, mit_vokabeln: MockConfigEntry) -> None:
    arbeit = hass.states.get("sensor.max_nachste_arbeit")
    assert arbeit.state == "2026-10-09"
    assert arbeit.attributes["thema"] == "Unit 3"
    assert arbeit.attributes["fach"] == "Englisch"
    assert arbeit.attributes["art"] == "arbeit"
    assert hass.states.get("sensor.max_trefferquote").state == "unknown"
    offen = hass.states.get("sensor.max_offene_frage")
    assert offen.state == "keine"
    assert "gestellt_um" not in offen.attributes


async def test_button_und_offene_frage(
    hass: HomeAssistant,
    mit_vokabeln: MockConfigEntry,
    notify_calls: list[ServiceCall],
) -> None:
    await hass.services.async_call(
        "button",
        "press",
        {"entity_id": "button.max_jetzt_abfragen"},
        blocking=True,
    )
    assert len(notify_calls) == 1
    offen = hass.states.get("sensor.max_offene_frage")
    assert offen.state == "offen"
    assert offen.attributes["fach"] == "Englisch"
    assert set(offen.attributes) >= {"gestellt_um", "timeout_um"}
    # No task content in attributes
    assert "dog" not in json.dumps(dict(offen.attributes))


async def test_switch(hass: HomeAssistant, setup_entry: MockConfigEntry) -> None:
    entity_id = "switch.max_abfragen_aktiv"
    await hass.services.async_call(
        "switch", "turn_off", {"entity_id": entity_id}, blocking=True
    )
    assert hass.states.get(entity_id).state == "off"
    assert setup_entry.runtime_data.zustand(KIND_ID).aktiv is False
    await hass.services.async_call(
        "switch", "turn_on", {"entity_id": entity_id}, blocking=True
    )
    assert hass.states.get(entity_id).state == "on"


async def test_kalender(hass: HomeAssistant, setup_entry: MockConfigEntry) -> None:
    entity_id = "calendar.max_arbeiten"
    zustand = hass.states.get(entity_id)
    assert zustand.state == "off"
    assert zustand.attributes["message"] == "Englisch: Unit 3"

    jetzt = dt_util.now()
    ergebnis = await hass.services.async_call(
        "calendar",
        "get_events",
        {
            "entity_id": entity_id,
            "start_date_time": jetzt.isoformat(),
            "end_date_time": (jetzt + timedelta(days=10)).isoformat(),
        },
        blocking=True,
        return_response=True,
    )
    assert ergebnis is not None
    events: Any = ergebnis[entity_id]["events"]
    assert len(events) == 1
    assert events[0]["summary"] == "Englisch: Unit 3"
    assert events[0]["start"] == "2026-10-09"

    ergebnis = await hass.services.async_call(
        "calendar",
        "get_events",
        {
            "entity_id": entity_id,
            "start_date_time": jetzt.isoformat(),
            "end_date_time": (jetzt + timedelta(days=1)).isoformat(),
        },
        blocking=True,
        return_response=True,
    )
    assert ergebnis is not None
    assert ergebnis[entity_id]["events"] == []


# --- diagnostics ------------------------------------------------------------


async def test_diagnostics(hass: HomeAssistant, mit_vokabeln: MockConfigEntry) -> None:
    await hass.services.async_call(
        DOMAIN, "ask_now", {"kind_id": KIND_ID}, blocking=True
    )
    daten = await async_get_config_entry_diagnostics(hass, mit_vokabeln)
    roh = json.dumps(daten, default=str)
    for geheim in ("Max", "1234567", "Unit 3", "dog", "Hund"):
        assert geheim not in roh
    assert daten["kinder"][KIND_ID]["offene_frage"] is True
    assert daten["kinder"][KIND_ID]["faecher"] == 1
    assert daten["faecher"][FACH_ID] == {
        "typ": "vokabel",
        "sprachen": ["de", "en"],
        "aufgaben": 2,
        "geprueft": 2,
        "lektionen": 1,
    }


# --- translations -----------------------------------------------------------


def _schluessel(daten: Any, pfad: str = "") -> set[str]:
    if not isinstance(daten, dict):
        return {pfad}
    return {
        eintrag
        for key, wert in daten.items()
        for eintrag in _schluessel(wert, f"{pfad}.{key}")
    }


def test_uebersetzungen_vollstaendig() -> None:
    strings = json.loads((KOMPONENTE / "strings.json").read_text())
    en = json.loads((KOMPONENTE / "translations" / "en.json").read_text())
    de = json.loads((KOMPONENTE / "translations" / "de.json").read_text())
    assert en == strings
    assert _schluessel(de) == _schluessel(en)
