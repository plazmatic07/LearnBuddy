"""Tests for the config flow, options flow and subentry flows."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import (
    SOURCE_RECONFIGURE,
    SOURCE_USER,
    ConfigEntryState,
)
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.learnbuddy.config_flow import (
    muttersprache,
    standard_muttersprache,
)
from custom_components.learnbuddy.const import DOMAIN

from .conftest import ARBEIT_ID, FACH_ID, KIND_DATEN, KIND_ID

KIND_EINGABE: dict[str, Any] = {
    "name": " Lena ",
    "muttersprache": "de",
    "klassenstufe": 4,
    "schulart": "grundschule",
    "bundesland": "rp",
    "notify_entity": "notify.lena",
    "klassisch": {},
    "absender_kennung": " 12345 ",
    "werktag_von": "14:00:00",
    "werktag_bis": "18:00:00",
    "wochenende_aktiv": True,
    "wochenende_von": "10:00:00",
    "wochenende_bis": "12:00:00",
}
_KLASSISCH = ("notify_service", "notify_target", "notify_data")


def _formular(daten: dict[str, Any]) -> dict[str, Any]:
    """Shape stored child data like the form sends it."""
    return {k: v for k, v in daten.items() if k not in _KLASSISCH} | {
        "klassisch": {k: daten[k] for k in _KLASSISCH if k in daten}
    }


ARBEIT_EINGABE: dict[str, Any] = {
    "art": "hue",
    "datum": "2026-10-20",
    "thema": " Unit 4 ",
    "lektionen": ["Unit 3"],
    "abfragen_pro_tag": 4,
    "start_tage_vorher": 5,
    "intensivierung": True,
}


async def _subentry_flow(
    hass: HomeAssistant, entry: MockConfigEntry, typ: str
) -> dict[str, Any]:
    return await hass.config_entries.subentries.async_init(
        (entry.entry_id, typ), context={"source": SOURCE_USER}
    )


async def _reconfigure_flow(
    hass: HomeAssistant, entry: MockConfigEntry, typ: str, subentry_id: str
) -> dict[str, Any]:
    return await hass.config_entries.subentries.async_init(
        (entry.entry_id, typ),
        context={"source": SOURCE_RECONFIGURE, "subentry_id": subentry_id},
    )


async def test_user_flow(hass: HomeAssistant) -> None:
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"timeout_minuten": 45, "sprache": "auto"}
    )
    await hass.async_block_till_done()
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "LearnBuddy"
    assert result["data"] == {}
    assert result["options"] == {
        "timeout_minuten": 45,
        "sprache": "auto",
        "auto_freigabe": False,
        "eingang_telegram": True,
        "eingang_whatsapp": True,
    }
    assert result["result"].state is ConfigEntryState.LOADED


async def test_user_flow_nur_eine_instanz(
    hass: HomeAssistant, config_entry: MockConfigEntry
) -> None:
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "single_instance_allowed"


async def test_options_flow(hass: HomeAssistant, setup_entry: MockConfigEntry) -> None:
    result = await hass.config_entries.options.async_init(setup_entry.entry_id)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "init"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"timeout_minuten": 30, "sprache": "en"}
    )
    await hass.async_block_till_done()
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert setup_entry.options == {
        "timeout_minuten": 30,
        "sprache": "en",
        "auto_freigabe": False,
        "eingang_telegram": True,
        "eingang_whatsapp": True,
    }
    # The entry was reloaded with the new options
    assert setup_entry.runtime_data.timeout.total_seconds() == 1800
    assert setup_entry.runtime_data.sprache == "en"


async def test_kind_anlegen(hass: HomeAssistant, setup_entry: MockConfigEntry) -> None:
    result = await _subentry_flow(hass, setup_entry, "kind")
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"], KIND_EINGABE
    )
    await hass.async_block_till_done()
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Lena"
    daten = result["data"]
    assert daten["name"] == "Lena"
    assert daten["absender_kennung"] == "12345"
    assert daten["notify_entity"] == "notify.lena"
    assert "notify_service" not in daten
    assert daten["erstellt"] == daten["geaendert"]

    # The entry is reloaded and the new child gets its entities
    assert len(setup_entry.runtime_data.kinder) == 2
    assert hass.states.get("switch.lena_abfragen_aktiv") is not None


@pytest.mark.parametrize(
    ("aenderung", "fehler"),
    [
        ({"name": "  "}, {"name": "name_leer"}),
        ({"name": "max"}, {"name": "name_vorhanden"}),
        ({"klassisch": {"notify_service": "notify.x"}}, {"base": "notify_genau_eins"}),
        ({"notify_entity": None}, {"base": "notify_genau_eins"}),
        (
            {"notify_entity": None, "klassisch": {"notify_service": "notify.foo bar"}},
            {"base": "notify_service_ungueltig"},
        ),
        ({"werktag_bis": "13:00:00"}, {"werktag_bis": "fenster_ungueltig"}),
        ({"wochenende_bis": "10:00:00"}, {"wochenende_bis": "fenster_ungueltig"}),
    ],
)
async def test_kind_fehler(
    hass: HomeAssistant,
    setup_entry: MockConfigEntry,
    aenderung: dict[str, Any],
    fehler: dict[str, str],
) -> None:
    eingabe = {**KIND_EINGABE, **aenderung}
    eingabe = {k: v for k, v in eingabe.items() if v is not None}
    result = await _subentry_flow(hass, setup_entry, "kind")
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"], eingabe
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == fehler

    # The flow recovers after the input was corrected
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"], KIND_EINGABE
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY


async def test_kind_mit_notify_service(
    hass: HomeAssistant, setup_entry: MockConfigEntry
) -> None:
    eingabe = {k: v for k, v in KIND_EINGABE.items() if k != "notify_entity"} | {
        "klassisch": {
            "notify_service": " Notify.WhatsApp ",
            "notify_target": ["4917"],
            "notify_data": {"x": 1},
        },
    }
    result = await _subentry_flow(hass, setup_entry, "kind")
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"], eingabe
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"]["notify_service"] == "whatsapp"
    assert result["data"]["notify_target"] == ["4917"]
    assert result["data"]["notify_data"] == {"x": 1}


async def test_kind_bearbeiten(
    hass: HomeAssistant, setup_entry: MockConfigEntry
) -> None:
    result = await _reconfigure_flow(hass, setup_entry, "kind", KIND_ID)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reconfigure"

    # Keeping the own name is allowed, an invalid window is not
    eingabe = {**_formular(KIND_DATEN), "werktag_bis": "10:00:00"}
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"], eingabe
    )
    assert result["errors"] == {"werktag_bis": "fenster_ungueltig"}

    eingabe = {
        **_formular(KIND_DATEN),
        "name": "Maximilian",
        "werktag_bis": "20:00:00",
    }
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"], eingabe
    )
    await hass.async_block_till_done()
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    subentry = setup_entry.subentries[KIND_ID]
    assert subentry.title == "Maximilian"
    assert subentry.data["werktag_bis"] == "20:00:00"
    assert "geaendert" in subentry.data
    assert setup_entry.runtime_data.kinder[KIND_ID].name == "Maximilian"


async def test_fach_ohne_kind(hass: HomeAssistant) -> None:
    entry = MockConfigEntry(domain=DOMAIN, options={})
    entry.add_to_hass(hass)
    result = await _subentry_flow(hass, entry, "fach")
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "keine_kinder"


async def _fach_flow(
    hass: HomeAssistant, entry: MockConfigEntry, eingabe: dict[str, Any]
) -> dict[str, Any]:
    """Run the subject flow up to the result of the language step."""
    result = await _subentry_flow(hass, entry, "fach")
    assert result["step_id"] == "user"
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"], {"kind_id": KIND_ID, "typ": "fremdsprache"}
    )
    assert result["step_id"] == "fremdsprache"
    return await hass.config_entries.subentries.async_configure(
        result["flow_id"], eingabe
    )


async def test_fach_anlegen(hass: HomeAssistant, setup_entry: MockConfigEntry) -> None:
    result = await _subentry_flow(hass, setup_entry, "fach")
    assert result["type"] is FlowResultType.FORM
    assert result["data_schema"].schema["typ"].config["options"] == [
        "fremdsprache",
        "mathe",
        "sach",
    ]
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"], {"kind_id": KIND_ID, "typ": "fremdsprache"}
    )
    assert result["step_id"] == "fremdsprache"
    assert result["description_placeholders"] == {"ausgangssprache": "Deutsch"}
    # The native language is not offered as a foreign language
    sprachen = result["data_schema"].schema["zielsprache"].config["options"]
    assert sprachen == ["en", "fr", "es", "it", "la"]

    # Englisch already exists for this child
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"], {"zielsprache": "en"}
    )
    assert result["errors"] == {"zielsprache": "name_vorhanden"}

    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"], {"zielsprache": "fr"}
    )
    await hass.async_block_till_done()
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Französisch (Max)"
    assert result["data"]["name"] == "Französisch"
    assert result["data"]["sprachen"] == ["de", "fr"]
    assert result["data"]["typ"] == "vokabel"
    assert result["data"]["kind_id"] == KIND_ID
    assert "ki_entity" not in result["data"]
    assert len(setup_entry.runtime_data.faecher) == 2


async def test_fach_mit_eigenem_namen_und_muttersprache(
    hass: HomeAssistant, setup_entry: MockConfigEntry
) -> None:
    kind = setup_entry.subentries[KIND_ID]
    hass.config_entries.async_update_subentry(
        setup_entry, kind, data={**kind.data, "muttersprache": "es"}
    )
    await hass.async_block_till_done()
    assert setup_entry.runtime_data.kinder[KIND_ID].muttersprache == "es"
    result = await _subentry_flow(hass, setup_entry, "fach")
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"], {"kind_id": KIND_ID, "typ": "fremdsprache"}
    )
    assert result["description_placeholders"] == {"ausgangssprache": "Spanisch"}
    assert "es" not in result["data_schema"].schema["zielsprache"].config["options"]
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"], {"zielsprache": "de", "name": " Alemán "}
    )
    await hass.async_block_till_done()
    assert result["title"] == "Alemán (Max)"
    assert result["data"]["sprachen"] == ["es", "de"]
    # The existing subject keeps its languages
    assert setup_entry.subentries[FACH_ID].data["sprachen"] == ["de", "en"]


async def test_fach_bearbeiten(
    hass: HomeAssistant, setup_entry: MockConfigEntry
) -> None:
    result = await _reconfigure_flow(hass, setup_entry, "fach", FACH_ID)
    assert result["step_id"] == "reconfigure"

    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"], {"name": ""}
    )
    assert result["errors"] == {"name": "name_leer"}

    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"], {"name": "English"}
    )
    await hass.async_block_till_done()
    assert result["type"] is FlowResultType.ABORT
    subentry = setup_entry.subentries[FACH_ID]
    assert subentry.title == "English (Max)"
    assert subentry.data["sprachen"] == ["de", "en"]


async def test_fach_bearbeiten_name_vorhanden(
    hass: HomeAssistant, setup_entry: MockConfigEntry
) -> None:
    result = await _fach_flow(hass, setup_entry, {"zielsprache": "la"})
    await hass.async_block_till_done()
    assert result["data"]["name"] == "Latein"
    result = await _reconfigure_flow(hass, setup_entry, "fach", FACH_ID)
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"], {"name": "latein"}
    )
    assert result["errors"] == {"name": "name_vorhanden"}


async def test_arbeit_ohne_fach(hass: HomeAssistant) -> None:
    entry = MockConfigEntry(domain=DOMAIN, options={})
    entry.add_to_hass(hass)
    result = await _subentry_flow(hass, entry, "arbeit")
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "keine_faecher"


async def test_arbeit_anlegen(
    hass: HomeAssistant, mit_vokabeln: MockConfigEntry
) -> None:
    result = await _subentry_flow(hass, mit_vokabeln, "arbeit")
    assert result["step_id"] == "user"
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"], {"fach_id": FACH_ID}
    )
    assert result["step_id"] == "details"
    # Lessons of the imported tasks are offered
    lektionen = result["data_schema"].schema["lektionen"]
    assert lektionen.config["options"] == ["Unit 3"]

    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"], {**ARBEIT_EINGABE, "datum": "2026-10-05", "thema": " "}
    )
    assert result["errors"] == {
        "thema": "thema_leer",
        "datum": "datum_vergangen",
    }

    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"], ARBEIT_EINGABE
    )
    await hass.async_block_till_done()
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "2026-10-20 Englisch (Max): Unit 4"
    daten = result["data"]
    assert daten["fach_id"] == FACH_ID
    assert daten["thema"] == "Unit 4"
    assert daten["lektionen"] == ["Unit 3"]
    assert daten["abfragen_pro_tag"] == 4
    assert len(mit_vokabeln.runtime_data.arbeiten) == 2


async def test_arbeit_anlegen_nicht_geladen(
    hass: HomeAssistant, config_entry: MockConfigEntry
) -> None:
    result = await _subentry_flow(hass, config_entry, "arbeit")
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"], {"fach_id": FACH_ID}
    )
    assert result["data_schema"].schema["lektionen"].config["options"] == []
    eingabe = {k: v for k, v in ARBEIT_EINGABE.items() if k != "lektionen"}
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"], eingabe
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"]["lektionen"] == []


async def test_arbeit_bearbeiten(
    hass: HomeAssistant, mit_vokabeln: MockConfigEntry
) -> None:
    result = await _reconfigure_flow(hass, mit_vokabeln, "arbeit", ARBEIT_ID)
    assert result["step_id"] == "reconfigure"

    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"], {**ARBEIT_EINGABE, "datum": "2026-01-01"}
    )
    assert result["errors"] == {"datum": "datum_vergangen"}

    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"], ARBEIT_EINGABE
    )
    await hass.async_block_till_done()
    assert result["type"] is FlowResultType.ABORT
    subentry = mit_vokabeln.subentries[ARBEIT_ID]
    assert subentry.data["datum"] == "2026-10-20"
    assert subentry.data["fach_id"] == FACH_ID
    assert subentry.title == "2026-10-20 Englisch (Max): Unit 4"
    assert mit_vokabeln.runtime_data.arbeiten[ARBEIT_ID].art == "hue"


async def test_arbeit_formular_plant_simulation(
    hass: HomeAssistant, mit_vokabeln: MockConfigEntry
) -> None:
    result = await _reconfigure_flow(hass, mit_vokabeln, "arbeit", ARBEIT_ID)
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"],
        {
            **ARBEIT_EINGABE,
            "simulation_aktiv": True,
            "simulation_um": "2026-10-06 07:00:00",
        },
    )
    assert result["errors"] == {"simulation_um": "simulation_um_vergangen"}
    # Switched on without a time
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"], {**ARBEIT_EINGABE, "simulation_aktiv": True}
    )
    assert result["errors"] == {"simulation_um": "simulation_um_fehlt"}
    # The form takes local time
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"],
        {
            **ARBEIT_EINGABE,
            "simulation_aktiv": True,
            "simulation_um": "2026-10-08 15:00:00",
            "simulation_anzahl": 7,
        },
    )
    await hass.async_block_till_done()
    assert result["type"] is FlowResultType.ABORT
    daten = mit_vokabeln.subentries[ARBEIT_ID].data
    assert daten["simulation_um"] == "2026-10-08T13:00:00+00:00"
    assert daten["simulation_anzahl"] == 7
    manager = mit_vokabeln.runtime_data
    assert manager.simulation_geplant(manager.arbeiten[ARBEIT_ID])

    # Editing shows the stored time as local time and keeps it
    result = await _reconfigure_flow(hass, mit_vokabeln, "arbeit", ARBEIT_ID)
    vorbelegt = {
        str(schluessel): schluessel.description
        for schluessel in result["data_schema"].schema
    }
    assert vorbelegt["simulation_um"] == {"suggested_value": "2026-10-08 15:00:00"}
    assert vorbelegt["simulation_aktiv"] == {"suggested_value": True}
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"],
        {
            **ARBEIT_EINGABE,
            "simulation_aktiv": True,
            "simulation_um": "2026-10-08 15:00:00",
        },
    )
    await hass.async_block_till_done()
    daten = mit_vokabeln.subentries[ARBEIT_ID].data
    assert daten["simulation_um"] == "2026-10-08T13:00:00+00:00"
    # Without a value the default number applies
    assert daten["simulation_anzahl"] == 10
    # Switched off, the plan goes, even if the date field still holds a value
    # (Home Assistant fills an empty date field on its own)
    result = await _reconfigure_flow(hass, mit_vokabeln, "arbeit", ARBEIT_ID)
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"],
        {
            **ARBEIT_EINGABE,
            "simulation_aktiv": False,
            "simulation_um": "2026-10-08 15:00:00",
        },
    )
    await hass.async_block_till_done()
    assert mit_vokabeln.subentries[ARBEIT_ID].data["simulation_um"] is None


async def test_options_flow_mit_ki(
    hass: HomeAssistant, setup_entry: MockConfigEntry
) -> None:
    result = await hass.config_entries.options.async_init(setup_entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"],
        {"timeout_minuten": 60, "sprache": "de", "ki_entity": "ai_task.test"},
    )
    await hass.async_block_till_done()
    assert setup_entry.options["ki_entity"] == "ai_task.test"
    manager = setup_entry.runtime_data
    assert manager.ki_entity(manager.faecher[FACH_ID]) == "ai_task.test"

    # Leaving the field empty removes the AI entity again
    result = await hass.config_entries.options.async_init(setup_entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"timeout_minuten": 60, "sprache": "de"}
    )
    await hass.async_block_till_done()
    manager = setup_entry.runtime_data
    assert manager.ki_entity(manager.faecher[FACH_ID]) is None


async def test_fach_mit_ki_override(
    hass: HomeAssistant, setup_entry: MockConfigEntry
) -> None:
    result = await _fach_flow(
        hass, setup_entry, {"zielsprache": "la", "ki_entity": "ai_task.latein"}
    )
    await hass.async_block_till_done()
    assert result["data"]["ki_entity"] == "ai_task.latein"

    result = await _reconfigure_flow(hass, setup_entry, "fach", FACH_ID)
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"], {"name": "Englisch", "ki_entity": "ai_task.englisch"}
    )
    await hass.async_block_till_done()
    assert setup_entry.subentries[FACH_ID].data["ki_entity"] == "ai_task.englisch"
    manager = setup_entry.runtime_data
    assert manager.ki_entity(manager.faecher[FACH_ID]) == "ai_task.englisch"

    # Clearing the field removes the override
    result = await _reconfigure_flow(hass, setup_entry, "fach", FACH_ID)
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"], {"name": "Englisch"}
    )
    await hass.async_block_till_done()
    assert "ki_entity" not in setup_entry.subentries[FACH_ID].data


async def test_muttersprache_vorgabe(
    hass: HomeAssistant, setup_entry: MockConfigEntry
) -> None:
    hass.config.language = "es-419"
    assert standard_muttersprache(hass) == "es"
    # Languages without vocabulary support fall back to German
    hass.config.language = "ja"
    assert standard_muttersprache(hass) == "de"

    hass.config.language = "de"

    # A child from before this field existed falls back to the default
    kind = setup_entry.subentries[KIND_ID]
    hass.config_entries.async_update_subentry(
        setup_entry,
        kind,
        data={k: v for k, v in kind.data.items() if k != "muttersprache"},
    )
    await hass.async_block_till_done()
    assert muttersprache(hass, setup_entry.subentries[KIND_ID]) == "de"
    result = await _subentry_flow(hass, setup_entry, "fach")
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"], {"kind_id": KIND_ID, "typ": "fremdsprache"}
    )
    assert result["description_placeholders"] == {"ausgangssprache": "Deutsch"}

    # The form for a new child suggests the language of Home Assistant
    hass.config.language = "en-GB"
    result = await _subentry_flow(hass, setup_entry, "kind")
    feld = next(k for k in result["data_schema"].schema if k == "muttersprache")
    assert feld.description == {"suggested_value": "en"}


async def test_mathe_fach_anlegen(
    hass: HomeAssistant, setup_entry: MockConfigEntry
) -> None:
    result = await _subentry_flow(hass, setup_entry, "fach")
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"], {"kind_id": KIND_ID, "typ": "mathe"}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "mathe"

    # Englisch already exists for this child
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"], {"name": "englisch"}
    )
    assert result["errors"] == {"name": "name_vorhanden"}

    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"], {"ki_entity": "ai_task.mathe"}
    )
    await hass.async_block_till_done()
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Mathe (Max)"
    assert result["data"]["typ"] == "mathe"
    assert result["data"]["ki_entity"] == "ai_task.mathe"
    assert "sprachen" not in result["data"]
    fach = next(
        f for f in setup_entry.runtime_data.faecher.values() if f.name == "Mathe"
    )
    assert fach.richtungen == ("mathe",)


async def test_mathe_fach_englischer_name(
    hass: HomeAssistant, setup_entry: MockConfigEntry
) -> None:
    hass.config.language = "en"
    result = await _subentry_flow(hass, setup_entry, "fach")
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"], {"kind_id": KIND_ID, "typ": "mathe"}
    )
    result = await hass.config_entries.subentries.async_configure(result["flow_id"], {})
    assert result["title"] == "Math (Max)"


async def test_kind_mit_bild_aktion(
    hass: HomeAssistant, setup_entry: MockConfigEntry
) -> None:
    aktion = [{"action": "notify.bild", "data": {"url": "{{ bild_url }}"}}]
    result = await _subentry_flow(hass, setup_entry, "kind")
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"], {**KIND_EINGABE, "bild_aktion": [{"kein": "schritt"}]}
    )
    assert result["errors"] == {"bild_aktion": "bild_aktion_ungueltig"}
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"], {**KIND_EINGABE, "bild_aktion": aktion}
    )
    await hass.async_block_till_done()
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"]["bild_aktion"] == aktion
    lena = next(k for k in setup_entry.runtime_data.kinder.values() if k.name == "Lena")
    assert lena.bild_aktion == aktion
    assert setup_entry.runtime_data.messenger.kann_bilder(lena)


async def test_kind_ohne_bild_aktion(
    hass: HomeAssistant, setup_entry: MockConfigEntry
) -> None:
    result = await _subentry_flow(hass, setup_entry, "kind")
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"], {**KIND_EINGABE, "bild_aktion": []}
    )
    await hass.async_block_till_done()
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert "bild_aktion" not in result["data"]


async def test_sachfach_anlegen(
    hass: HomeAssistant, setup_entry: MockConfigEntry
) -> None:
    result = await _subentry_flow(hass, setup_entry, "fach")
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"], {"kind_id": KIND_ID, "typ": "sach"}
    )
    assert result["step_id"] == "sach"
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"], {"name": "  "}
    )
    assert result["errors"] == {"name": "name_leer"}
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"], {"name": " Biologie "}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Biologie (Max)"
    assert result["data"]["typ"] == "sach"
    assert result["data"]["name"] == "Biologie"
    assert "sprachen" not in result["data"]

    # The name is taken now
    result = await _subentry_flow(hass, setup_entry, "fach")
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"], {"kind_id": KIND_ID, "typ": "sach"}
    )
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"], {"name": "biologie"}
    )
    assert result["errors"] == {"name": "name_vorhanden"}


async def test_kind_klassische_aktion_eingeklappt(
    hass: HomeAssistant, setup_entry: MockConfigEntry
) -> None:
    """The classic action is folded away unless the child uses it."""
    result = await _subentry_flow(hass, setup_entry, "kind")
    abschnitt = result["data_schema"].schema["klassisch"]
    assert abschnitt.options == {"collapsed": True}
    assert set(abschnitt.schema.schema) == {
        "notify_service",
        "notify_target",
        "notify_data",
    }
    assert "notify_service" not in result["data_schema"].schema
    reihenfolge = [str(feld) for feld in result["data_schema"].schema]
    assert reihenfolge.index("klassisch") == reihenfolge.index("notify_entity") + 1

    # The test child uses the classic action: open, with its values
    result = await hass.config_entries.subentries.async_init(
        (setup_entry.entry_id, "kind"),
        context={"source": "reconfigure", "subentry_id": KIND_ID},
    )
    schema = result["data_schema"].schema
    assert schema["klassisch"].options == {"collapsed": False}
    vorgaben = {
        str(feld): feld.description["suggested_value"]
        for feld in schema["klassisch"].schema.schema
        if feld.description
    }
    assert vorgaben == {"notify_service": "test", "notify_target": ["491701234567"]}


async def test_kind_wechsel_zur_entitaet_raeumt_auf(
    hass: HomeAssistant, setup_entry: MockConfigEntry
) -> None:
    """Target and extra data of the classic action go when an entity is used."""
    result = await hass.config_entries.subentries.async_init(
        (setup_entry.entry_id, "kind"),
        context={"source": "reconfigure", "subentry_id": KIND_ID},
    )
    eingabe = {
        **{k: v for k, v in KIND_DATEN.items() if not k.startswith("notify_")},
        "notify_entity": "notify.max",
        "klassisch": {"notify_target": ["491701234567"], "notify_data": {"a": 1}},
    }
    result = await hass.config_entries.subentries.async_configure(
        result["flow_id"], eingabe
    )
    assert result["type"] is FlowResultType.ABORT
    daten = setup_entry.subentries[KIND_ID].data
    assert daten["notify_entity"] == "notify.max"
    assert not {"notify_service", "notify_target", "notify_data"} & set(daten)
