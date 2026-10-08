"""Tests for the WebSocket API of the panel."""

from __future__ import annotations

from typing import Any

from homeassistant.components.frontend import DATA_PANELS
from homeassistant.core import HomeAssistant, ServiceCall
import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.typing import WebSocketGenerator

from custom_components.learnbuddy.const import DOMAIN
from custom_components.learnbuddy.manager import LearnBuddyManager

from .conftest import ARBEIT_ID, FACH_ID, KIND_ID

ARBEIT: dict[str, Any] = {
    "fach_id": FACH_ID,
    "datum": "2026-10-20",
    "thema": " Unit 5 ",
    "art": "hue",
    "abfragen_pro_tag": 4,
    "start_tage_vorher": 5,
    "intensivierung": False,
}


class Client:
    """Small helper around the websocket test client."""

    def __init__(self, ws: Any) -> None:
        """Initialize the helper."""
        self._ws = ws

    async def ok(self, typ: str, **daten: Any) -> Any:
        await self._ws.send_json_auto_id({"type": f"learnbuddy/{typ}", **daten})
        antwort = await self._ws.receive_json()
        assert antwort["success"], antwort
        return antwort["result"]

    async def fehler(self, typ: str, **daten: Any) -> dict[str, str]:
        await self._ws.send_json_auto_id({"type": f"learnbuddy/{typ}", **daten})
        antwort = await self._ws.receive_json()
        assert not antwort["success"], antwort
        fehler: dict[str, str] = antwort["error"]
        return fehler


@pytest.fixture
async def client(
    hass: HomeAssistant,
    mit_vokabeln: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
) -> Client:
    """Return a websocket client of an admin."""
    return Client(await hass_ws_client(hass))


def _ids(aufgaben: list[dict[str, Any]]) -> dict[str, str]:
    """Map the German word of every task to its id."""
    return {a["frage"]["de"]: a["id"] for a in aufgaben}


@pytest.mark.parametrize(
    "nachricht",
    [
        {"type": "learnbuddy/overview"},
        {"type": "learnbuddy/tasks/list", "fach_id": FACH_ID},
        {"type": "learnbuddy/tasks/create", "fach_id": FACH_ID, "aufgabe": {}},
        {
            "type": "learnbuddy/tasks/update",
            "fach_id": FACH_ID,
            "aufgabe_id": "x",
            "aenderungen": {},
        },
        {"type": "learnbuddy/tasks/delete", "fach_id": FACH_ID, "aufgabe_ids": []},
        {"type": "learnbuddy/tasks/import_text", "fach_id": FACH_ID, "inhalt": "a;b"},
        {"type": "learnbuddy/tasks/export", "fach_id": FACH_ID},
        {"type": "learnbuddy/dashboard", "kind_id": KIND_ID},
        {"type": "learnbuddy/set_active", "kind_id": KIND_ID, "aktiv": False},
        {"type": "learnbuddy/ask", "kind_id": KIND_ID},
        {"type": "learnbuddy/lessons/add", "fach_id": FACH_ID, "name": "Neu"},
        {"type": "learnbuddy/lessons/delete", "fach_id": FACH_ID, "name": "Unit 3"},
        {"type": "learnbuddy/tasks/import_json", "fach_id": FACH_ID, "daten": {}},
        {
            "type": "learnbuddy/exams/save",
            "arbeit": {"datum": "2026-10-20", "thema": "x"},
        },
        {"type": "learnbuddy/exams/delete", "arbeit_id": ARBEIT_ID},
    ],
)
async def test_nur_fuer_admins(
    hass: HomeAssistant,
    mit_vokabeln: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
    hass_read_only_access_token: str,
    nachricht: dict[str, Any],
) -> None:
    ws = await hass_ws_client(hass, hass_read_only_access_token)
    await ws.send_json_auto_id(nachricht)
    antwort = await ws.receive_json()
    assert not antwort["success"]
    assert antwort["error"]["code"] == "unauthorized"
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    assert len(manager.task_stores[FACH_ID].aufgaben) == 2
    assert ARBEIT_ID in mit_vokabeln.subentries
    assert manager.zustand(KIND_ID).aktiv is True
    assert manager.zustand(KIND_ID).offene_frage is None


async def test_nicht_geladen(
    hass: HomeAssistant, mit_vokabeln: MockConfigEntry, client: Client
) -> None:
    assert await hass.config_entries.async_unload(mit_vokabeln.entry_id)
    assert (await client.fehler("overview"))["code"] == "not_loaded"
    fehler = await client.fehler(
        "exams/save", arbeit={"datum": "2026-10-20", "thema": "x"}
    )
    assert fehler["code"] == "not_loaded"


async def test_overview(client: Client) -> None:
    ergebnis = await client.ok("overview")
    assert ergebnis["unbekannte_absender"] == []
    assert ergebnis["kinder"] == [
        {"id": KIND_ID, "name": "Max", "bilder": False, "absender": True}
    ]
    assert ergebnis["faecher"] == [
        {
            "id": FACH_ID,
            "kind_id": KIND_ID,
            "name": "Englisch",
            "typ": "vokabel",
            "ki": False,
            "ki_bilder": False,
            "ki_status": "keine",
            "sprachen": ["de", "en"],
            "lektionen": ["Unit 3"],
            "anzahl_aufgaben": 2,
        }
    ]
    assert ergebnis["arbeiten"] == [
        {
            "id": ARBEIT_ID,
            "fach_id": FACH_ID,
            "art": "arbeit",
            "datum": "2026-10-09",
            "thema": "Unit 3",
            "lektionen": [],
            "abfragen_pro_tag": 2,
            "start_tage_vorher": 7,
            "intensivierung": False,
            "antwortfrist_minuten": None,
            "simulation_um": None,
            "simulation_anzahl": 10,
            "simulation_geplant": False,
            "aufgaben_ids": [],
            "simulierbar": {"ausdruck": 2, "messenger": 2},
        }
    ]


async def test_tasks_list(hass: HomeAssistant, client: Client) -> None:
    await hass.services.async_call(
        DOMAIN, "ask_now", {"kind_id": KIND_ID}, blocking=True
    )
    await hass.services.async_call(
        DOMAIN, "submit_answer", {"kind_id": KIND_ID, "text": "quatsch"}, blocking=True
    )
    aufgaben = (await client.ok("tasks/list", fach_id=FACH_ID))["aufgaben"]
    assert len(aufgaben) == 2
    hund = next(a for a in aufgaben if a["frage"]["de"] == "Hund")
    assert hund["alternativen"] == {"en": ["hound"]}
    assert hund["hinweis"] == "Nomen"
    assert hund["lektion"] == "Unit 3"
    assert hund["arbeiten"] == [ARBEIT_ID]
    assert sorted(a["fehlerquote"] for a in aufgaben if a["statistik"]) == [100.0]
    assert [a["fehlerquote"] for a in aufgaben if not a["statistik"]] == [None]

    assert (await client.fehler("tasks/list", fach_id="x")) == {
        "code": "not_found",
        "message": "fach_unbekannt",
    }


async def test_tasks_create(
    hass: HomeAssistant, mit_vokabeln: MockConfigEntry, client: Client
) -> None:
    await client.ok("lessons/add", fach_id=FACH_ID, name="Unit 4")
    neu = await client.ok(
        "tasks/create",
        fach_id=FACH_ID,
        aufgabe={
            "frage": {"de": " Katze ", "en": "cat"},
            "alternativen": {"en": ["kitty", " "]},
            "hinweis": " ",
            "seite": 226,
            "lektion": "Unit 4",
            "geprueft": False,
        },
    )
    assert neu["frage"] == {"de": "Katze", "en": "cat"}
    assert neu["alternativen"] == {"en": ["kitty"]}
    assert neu["hinweis"] is None
    assert neu["seite"] == 226
    assert neu["lektion"] == "Unit 4"
    assert neu["geprueft"] is False
    assert neu["quelle"] == "manuell"
    assert neu["arbeiten"] == [ARBEIT_ID]
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    assert neu["id"] in manager.task_stores[FACH_ID].aufgaben


@pytest.mark.parametrize(
    ("aufgabe", "schluessel"),
    [
        ({}, "frage_ungueltig"),
        ({"frage": {"de": "Katze"}}, "frage_ungueltig"),
        ({"frage": {"de": "Katze", "en": " "}}, "frage_ungueltig"),
        ({"frage": {"de": "Katze", "en": None}}, "frage_ungueltig"),
        ({"frage": {"de": "Katze", "fr": "chat"}}, "frage_ungueltig"),
        ({"frage": {"de": "K" * 501, "en": "cat"}}, "frage_ungueltig"),
        (
            {"frage": {"de": "a", "en": "b"}, "alternativen": {"fr": ["c"]}},
            "alternativen_ungueltig",
        ),
        ({"frage": {"de": "a", "en": "b"}, "hinweis": "x" * 501}, "hinweis_ungueltig"),
        ({"frage": {"de": "a", "en": "b"}, "seite": 0}, "seite_ungueltig"),
        ({"frage": {"de": "a", "en": "b"}, "seite": 10000}, "seite_ungueltig"),
        ({"frage": {"de": "a", "en": "b"}, "lektion": "Unit 99"}, "lektion_unbekannt"),
    ],
)
async def test_tasks_create_ungueltig(
    client: Client, aufgabe: dict[str, Any], schluessel: str
) -> None:
    fehler = await client.fehler("tasks/create", fach_id=FACH_ID, aufgabe=aufgabe)
    assert fehler == {"code": "invalid_format", "message": schluessel}


async def test_tasks_update(client: Client) -> None:
    ids = _ids((await client.ok("tasks/list", fach_id=FACH_ID))["aufgaben"])
    await client.ok("lessons/add", fach_id=FACH_ID, name="Unit 9")
    fehler = await client.fehler(
        "tasks/update",
        fach_id=FACH_ID,
        aufgabe_id=ids["Hund"],
        aenderungen={"lektion": "Unit 77"},
    )
    assert fehler == {"code": "invalid_format", "message": "lektion_unbekannt"}
    geaendert = await client.ok(
        "tasks/update",
        fach_id=FACH_ID,
        aufgabe_id=ids["Hund"],
        aenderungen={
            "frage": {"en": "doggo"},
            "alternativen": {},
            "hinweis": None,
            "seite": 227,
            "lektion": "unit 9",
            "geprueft": False,
        },
    )
    assert geaendert["frage"] == {"de": "Hund", "en": "doggo"}
    assert geaendert["alternativen"] == {}
    assert geaendert["hinweis"] is None
    assert geaendert["seite"] == 227
    assert geaendert["lektion"] == "Unit 9"
    assert geaendert["geprueft"] is False
    assert geaendert["geaendert"] >= geaendert["erstellt"]

    fehler = await client.fehler(
        "tasks/update",
        fach_id=FACH_ID,
        aufgabe_id=ids["Hund"],
        aenderungen={"frage": {"en": ""}},
    )
    assert fehler["message"] == "frage_ungueltig"
    fehler = await client.fehler(
        "tasks/update", fach_id=FACH_ID, aufgabe_id="x", aenderungen={}
    )
    assert fehler == {"code": "not_found", "message": "aufgabe_unbekannt"}


async def test_tasks_delete(
    hass: HomeAssistant,
    mit_vokabeln: MockConfigEntry,
    client: Client,
    notify_calls: list[ServiceCall],
) -> None:
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    ids = _ids((await client.ok("tasks/list", fach_id=FACH_ID))["aufgaben"])
    alle = list(ids.values())
    manager.config_store.arbeit_aufgaben[ARBEIT_ID] = list(alle)
    await hass.services.async_call(
        DOMAIN, "ask_now", {"kind_id": KIND_ID}, blocking=True
    )
    assert manager.zustand(KIND_ID).offene_frage is not None

    # Tasks of an upcoming exam need a confirmation
    ergebnis = await client.ok("tasks/delete", fach_id=FACH_ID, aufgabe_ids=alle)
    assert ergebnis == {
        "geloescht": 0,
        "zugeordnet": {aufgabe_id: [ARBEIT_ID] for aufgabe_id in alle},
    }
    assert len(manager.task_stores[FACH_ID].aufgaben) == 2

    ergebnis = await client.ok(
        "tasks/delete",
        fach_id=FACH_ID,
        aufgabe_ids=[*alle, "gibtsnicht"],
        bestaetigt=True,
    )
    assert ergebnis == {"geloescht": 2, "zugeordnet": {}}
    assert manager.task_stores[FACH_ID].aufgaben == {}
    assert manager.config_store.arbeit_aufgaben[ARBEIT_ID] == []
    # The open question pointed to a deleted task
    assert manager.zustand(KIND_ID).offene_frage is None


async def test_tasks_delete_ohne_arbeit(
    hass: HomeAssistant, mit_vokabeln: MockConfigEntry, client: Client
) -> None:
    hass.config_entries.async_remove_subentry(mit_vokabeln, ARBEIT_ID)
    await hass.async_block_till_done()
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    ids = _ids((await client.ok("tasks/list", fach_id=FACH_ID))["aufgaben"])
    ergebnis = await client.ok(
        "tasks/delete", fach_id=FACH_ID, aufgabe_ids=[ids["Hund"]]
    )
    assert ergebnis == {"geloescht": 1, "zugeordnet": {}}
    assert len(manager.task_stores[FACH_ID].aufgaben) == 1


async def test_import_text(mit_vokabeln: MockConfigEntry, client: Client) -> None:
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    inhalt = "Hund;dog\nKatze;cat|kitty;Tier\nKatze;cat\nkaputt"
    vorschau = await client.ok(
        "tasks/import_text", fach_id=FACH_ID, inhalt=inhalt, vorschau=True
    )
    assert vorschau["fehlerzeilen"] == [4]
    assert [(z["frage"]["de"], z["vorhanden"]) for z in vorschau["zeilen"]] == [
        ("Hund", True),
        ("Katze", False),
        ("Katze", True),
    ]
    assert vorschau["zeilen"][1]["alternativen"] == {"en": ["kitty"]}
    assert vorschau["zeilen"][1]["hinweis"] == "Tier"
    assert len(manager.task_stores[FACH_ID].aufgaben) == 2

    fehler = await client.fehler(
        "tasks/import_text", fach_id=FACH_ID, inhalt=inhalt, lektion="Unit 4"
    )
    assert fehler == {"code": "invalid_format", "message": "lektion_unbekannt"}
    await client.ok("lessons/add", fach_id=FACH_ID, name="Unit 4")
    ergebnis = await client.ok(
        "tasks/import_text",
        fach_id=FACH_ID,
        inhalt=inhalt,
        lektion="Unit 4",
        geprueft=False,
    )
    assert ergebnis == {"importiert": 1, "uebersprungen": 2, "fehlerzeilen": [4]}
    katze = next(
        a
        for a in manager.task_stores[FACH_ID].aufgaben.values()
        if a.frage["de"] == "Katze"
    )
    assert katze.lektion == "Unit 4"
    assert katze.geprueft is False

    fehler = await client.fehler("tasks/import_text", fach_id=FACH_ID, inhalt="x")
    assert fehler == {"code": "invalid_format", "message": "import_leer"}
    fehler = await client.fehler("tasks/import_text", fach_id="x", inhalt="a;b")
    assert fehler["code"] == "not_found"


async def test_export_und_import_json(
    hass: HomeAssistant, mit_vokabeln: MockConfigEntry, client: Client
) -> None:
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    await hass.services.async_call(
        DOMAIN, "ask_now", {"kind_id": KIND_ID}, blocking=True
    )
    await hass.services.async_call(
        DOMAIN, "submit_answer", {"kind_id": KIND_ID, "text": "quatsch"}, blocking=True
    )

    ohne = await client.ok("tasks/export", fach_id=FACH_ID)
    assert ohne["format"] == "learnbuddy-aufgaben"
    assert ohne["version"] == 1
    assert ohne["sprachen"] == ["de", "en"]
    assert len(ohne["aufgaben"]) == 2
    assert all("statistik" not in a and "fach_id" not in a for a in ohne["aufgaben"])
    # Nothing about the child is exported
    assert "Max" not in str(ohne)
    assert KIND_ID not in str(ohne)

    mit = await client.ok("tasks/export", fach_id=FACH_ID, mit_statistik=True)
    assert sum(1 for a in mit["aufgaben"] if a["statistik"]) == 1

    # The page of the textbook is part of the export
    assert all(a["seite"] is None for a in ohne["aufgaben"])
    mit["aufgaben"][0]["seite"] = 226

    # Importing into the same subject skips everything
    ergebnis = await client.ok("tasks/import_json", fach_id=FACH_ID, daten=mit)
    assert ergebnis == {"importiert": 0, "uebersprungen": 2, "fehler": []}
    # A file exported under the former name of the integration still works
    alt = await client.ok(
        "tasks/import_json",
        fach_id=FACH_ID,
        daten={**mit, "format": "lernbuddy-aufgaben"},
    )
    assert alt == {"importiert": 0, "uebersprungen": 2, "fehler": []}

    alle = list(manager.task_stores[FACH_ID].aufgaben)
    await client.ok("tasks/delete", fach_id=FACH_ID, aufgabe_ids=alle, bestaetigt=True)
    mit["aufgaben"].extend(["kaputt", {"frage": {"de": "nur deutsch"}}])
    mit["aufgaben"][0]["statistik"]["xx>yy"] = {"richtig": 9}
    ergebnis = await client.ok(
        "tasks/import_json", fach_id=FACH_ID, daten=mit, mit_statistik=True
    )
    assert ergebnis == {"importiert": 2, "uebersprungen": 0, "fehler": [2, 3]}
    neu = list(manager.task_stores[FACH_ID].aufgaben.values())
    assert {a.frage["de"] for a in neu} == {"Hund", "gehen"}
    assert not set(alle) & {a.id for a in neu}
    assert sum(s.falsch for a in neu for s in a.statistik.values()) == 1
    assert all("xx>yy" not in a.statistik for a in neu)
    assert {a.lektion for a in neu} == {"Unit 3"}
    assert sorted(a.seite or 0 for a in neu) == [0, 226]


@pytest.mark.parametrize(
    ("aenderung", "schluessel"),
    [
        ({"format": "anderes"}, "export_ungueltig"),
        ({"aufgaben": "x"}, "export_ungueltig"),
        ({"version": 2}, "export_version"),
        ({"sprachen": ["de", "fr"]}, "export_sprachen"),
        ({"sprachen": None}, "export_sprachen"),
    ],
)
async def test_import_json_ungueltig(
    client: Client, aenderung: dict[str, Any], schluessel: str
) -> None:
    daten = await client.ok("tasks/export", fach_id=FACH_ID)
    fehler = await client.fehler(
        "tasks/import_json", fach_id=FACH_ID, daten={**daten, **aenderung}
    )
    assert fehler == {"code": "invalid_format", "message": schluessel}


async def test_import_json_ohne_statistik(
    mit_vokabeln: MockConfigEntry, client: Client
) -> None:
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    daten = await client.ok("tasks/export", fach_id=FACH_ID)
    daten["aufgaben"] = [
        {
            "frage": {"de": "Maus", "en": "mouse"},
            "quelle": "generiert",
            "statistik": {"de>en": {"richtig": 5}},
        },
        {"frage": {"de": "Vogel", "en": "bird"}, "quelle": "unbekannt"},
    ]
    ergebnis = await client.ok("tasks/import_json", fach_id=FACH_ID, daten=daten)
    assert ergebnis == {"importiert": 1, "uebersprungen": 0, "fehler": [1]}
    maus = next(
        a
        for a in manager.task_stores[FACH_ID].aufgaben.values()
        if a.frage["de"] == "Maus"
    )
    assert maus.quelle == "generiert"
    assert maus.statistik == {}


async def test_exams_save_neu(
    hass: HomeAssistant, mit_vokabeln: MockConfigEntry, client: Client
) -> None:
    vorher: LearnBuddyManager = mit_vokabeln.runtime_data
    ids = _ids((await client.ok("tasks/list", fach_id=FACH_ID))["aufgaben"])
    ergebnis = await client.ok(
        "exams/save",
        arbeit={**ARBEIT, "aufgaben_ids": [ids["Hund"], "gibtsnicht"]},
    )
    await hass.async_block_till_done()
    arbeit_id = ergebnis["arbeit_id"]

    subentry = mit_vokabeln.subentries[arbeit_id]
    assert subentry.subentry_type == "arbeit"
    assert subentry.title == "2026-10-20 Englisch (Max): Unit 5"
    assert subentry.data["thema"] == "Unit 5"
    assert subentry.data["art"] == "hue"
    assert subentry.data["lektionen"] == []
    assert subentry.data["erstellt"] == subentry.data["geaendert"]

    # The exam is applied in place: no reload, the panel stays registered
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    assert manager is vorher
    assert "learnbuddy" in hass.data[DATA_PANELS]
    assert manager.arbeiten[arbeit_id].abfragen_pro_tag == 4
    assert manager.config_store.arbeit_aufgaben[arbeit_id] == [ids["Hund"]]
    arbeiten = (await client.ok("overview"))["arbeiten"]
    neu = next(a for a in arbeiten if a["id"] == arbeit_id)
    assert neu["aufgaben_ids"] == [ids["Hund"]]
    aufgaben = (await client.ok("tasks/list", fach_id=FACH_ID))["aufgaben"]
    hund = next(a for a in aufgaben if a["frage"]["de"] == "Hund")
    gehen = next(a for a in aufgaben if a["frage"]["de"] == "gehen")
    assert hund["arbeiten"] == [ARBEIT_ID, arbeit_id]
    assert gehen["arbeiten"] == [ARBEIT_ID]


async def test_exams_save_aendern(
    hass: HomeAssistant, mit_vokabeln: MockConfigEntry, client: Client
) -> None:
    erstellt_vorher = mit_vokabeln.subentries[ARBEIT_ID].data.get("erstellt")
    ergebnis = await client.ok(
        "exams/save",
        arbeit_id=ARBEIT_ID,
        arbeit={
            "datum": "2026-10-12",
            "thema": "Unit 3+4",
            "lektionen": ["Unit 3", " "],
        },
    )
    await hass.async_block_till_done()
    assert ergebnis == {"arbeit_id": ARBEIT_ID}
    subentry = mit_vokabeln.subentries[ARBEIT_ID]
    assert subentry.data["datum"] == "2026-10-12"
    assert subentry.data["lektionen"] == ["Unit 3"]
    assert subentry.data["fach_id"] == FACH_ID
    assert subentry.data["abfragen_pro_tag"] == 3
    assert subentry.data.get("erstellt") != erstellt_vorher or erstellt_vorher is None
    assert subentry.title == "2026-10-12 Englisch (Max): Unit 3+4"
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    assert manager.arbeiten[ARBEIT_ID].thema == "Unit 3+4"


@pytest.mark.parametrize(
    ("arbeit_id", "aenderung", "fehler"),
    [
        (None, {"fach_id": "x"}, {"code": "not_found", "message": "fach_unbekannt"}),
        ("x", {}, {"code": "not_found", "message": "arbeit_unbekannt"}),
        (KIND_ID, {}, {"code": "not_found", "message": "arbeit_unbekannt"}),
        (None, {"thema": " "}, {"code": "invalid_format", "message": "thema_leer"}),
        (
            None,
            {"datum": "morgen"},
            {"code": "invalid_format", "message": "arbeit_ungueltig"},
        ),
        (
            None,
            {"datum": "2026-10-01"},
            {"code": "invalid_format", "message": "datum_vergangen"},
        ),
        (
            None,
            {"art": "test"},
            {"code": "invalid_format", "message": "arbeit_ungueltig"},
        ),
        (
            None,
            {"abfragen_pro_tag": 99},
            {"code": "invalid_format", "message": "arbeit_ungueltig"},
        ),
        (
            None,
            {"start_tage_vorher": 0},
            {"code": "invalid_format", "message": "arbeit_ungueltig"},
        ),
    ],
)
async def test_exams_save_fehler(
    mit_vokabeln: MockConfigEntry,
    client: Client,
    arbeit_id: str | None,
    aenderung: dict[str, Any],
    fehler: dict[str, str],
) -> None:
    daten: dict[str, Any] = {"arbeit": {**ARBEIT, **aenderung}}
    if arbeit_id is not None:
        daten["arbeit_id"] = arbeit_id
    assert await client.fehler("exams/save", **daten) == fehler
    assert len(mit_vokabeln.subentries) == 3


async def test_exams_delete(
    hass: HomeAssistant, mit_vokabeln: MockConfigEntry, client: Client
) -> None:
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    manager.config_store.arbeit_aufgaben[ARBEIT_ID] = ["x"]
    assert manager.naechste_abfrage[KIND_ID] is not None
    assert await client.ok("exams/delete", arbeit_id=ARBEIT_ID) == {}
    await hass.async_block_till_done()
    assert ARBEIT_ID not in mit_vokabeln.subentries
    assert mit_vokabeln.runtime_data is manager
    assert manager.arbeiten == {}
    assert ARBEIT_ID not in manager.config_store.arbeit_aufgaben
    # Without an exam nothing is scheduled any more
    assert manager.naechste_abfrage[KIND_ID] is None
    assert hass.states.get("sensor.max_nachste_arbeit").state == "unknown"
    for arbeit_id in (ARBEIT_ID, FACH_ID):
        fehler = await client.fehler("exams/delete", arbeit_id=arbeit_id)
        assert fehler == {"code": "not_found", "message": "arbeit_unbekannt"}


async def test_lessons(
    hass: HomeAssistant, mit_vokabeln: MockConfigEntry, client: Client
) -> None:
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    ergebnis = await client.ok("lessons/add", fach_id=FACH_ID, name="  Tiere ")
    assert ergebnis == {"lektionen": ["Unit 3", "Tiere"]}
    uebersicht = await client.ok("overview")
    assert uebersicht["faecher"][0]["lektionen"] == ["Unit 3", "Tiere"]

    for name, schluessel in (
        ("tiere", "lektion_vorhanden"),
        ("  ", "lektion_leer"),
        ("x" * 101, "lektion_ungueltig"),
    ):
        fehler = await client.fehler("lessons/add", fach_id=FACH_ID, name=name)
        assert fehler == {"code": "invalid_format", "message": schluessel}
    assert (await client.fehler("lessons/add", fach_id="x", name="A"))["code"] == (
        "not_found"
    )

    # A lesson with tasks cannot be deleted
    fehler = await client.fehler("lessons/delete", fach_id=FACH_ID, name="Unit 3")
    assert fehler == {"code": "invalid_format", "message": "lektion_verwendet"}
    fehler = await client.fehler("lessons/delete", fach_id=FACH_ID, name="Unit 8")
    assert fehler == {"code": "not_found", "message": "lektion_unbekannt"}

    # Deleting an unused lesson also removes it from the exams
    await client.ok(
        "exams/save",
        arbeit_id=ARBEIT_ID,
        arbeit={"datum": "2026-10-12", "thema": "x", "lektionen": ["Unit 3", "Tiere"]},
    )
    await hass.async_block_till_done()
    ergebnis = await client.ok("lessons/delete", fach_id=FACH_ID, name="TIERE")
    await hass.async_block_till_done()
    assert ergebnis == {"lektionen": ["Unit 3"]}
    assert mit_vokabeln.subentries[ARBEIT_ID].data["lektionen"] == ["Unit 3"]
    assert manager.arbeiten[ARBEIT_ID].lektionen == ("Unit 3",)
    assert mit_vokabeln.runtime_data is manager


async def test_import_json_in_lektion(
    mit_vokabeln: MockConfigEntry, client: Client
) -> None:
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    daten = await client.ok("tasks/export", fach_id=FACH_ID)
    daten["aufgaben"] = [
        {"frage": {"de": "Maus", "en": "mouse"}, "lektion": "Aus der Datei"},
        {"frage": {"de": "Vogel", "en": "bird"}},
    ]
    fehler = await client.fehler(
        "tasks/import_json", fach_id=FACH_ID, daten=daten, lektion="Gibt es nicht"
    )
    assert fehler == {"code": "invalid_format", "message": "lektion_unbekannt"}
    assert len(manager.task_stores[FACH_ID].aufgaben) == 2

    # All imported tasks go into the selected lesson
    ergebnis = await client.ok(
        "tasks/import_json", fach_id=FACH_ID, daten=daten, lektion="unit 3"
    )
    assert ergebnis == {"importiert": 2, "uebersprungen": 0, "fehler": []}
    store = manager.task_stores[FACH_ID]
    assert {a.lektion for a in store.aufgaben.values()} == {"Unit 3"}
    assert store.lektionen == ["Unit 3"]

    # Without a selection the lessons of the file are used and created
    daten["aufgaben"] = [
        {"frage": {"de": "Fisch", "en": "fish"}, "lektion": "Aus der Datei"},
        {"frage": {"de": "Pferd", "en": "horse"}},
    ]
    await client.ok("tasks/import_json", fach_id=FACH_ID, daten=daten, lektion=None)
    nach_wort = {a.frage["de"]: a.lektion for a in store.aufgaben.values()}
    assert nach_wort["Fisch"] == "Aus der Datei"
    assert nach_wort["Pferd"] is None
    assert store.lektionen == ["Unit 3", "Aus der Datei"]


async def test_dashboard(
    hass: HomeAssistant,
    mit_vokabeln: MockConfigEntry,
    client: Client,
    notify_calls: list[ServiceCall],
) -> None:
    leer = await client.ok("dashboard", kind_id=KIND_ID)
    assert leer["zustand"] == {
        "aktiv": True,
        "pausiert": False,
        "pausiert_bis": None,
        "offene_frage": None,
        "simulation": None,
        "letzte_frage_um": None,
        "naechste_abfrage": "2026-10-06T16:00:00+02:00",
    }
    assert leer["statistik"] == {
        "aufgaben": 2,
        "gefragt": 0,
        "richtig": 0,
        "falsch": 0,
        "teilweise": 0,
        "unbeantwortet": 0,
        "trefferquote": None,
        "boxen": [4, 0, 0, 0, 0],
    }
    assert leer["schwierig"] == []
    assert leer["faecher"] == [
        {
            "id": FACH_ID,
            "name": "Englisch",
            "typ": "vokabel",
            "sprachen": ["de", "en"],
            "ki": False,
            "aufgaben": 2,
            "ungeprueft": 0,
            "lektionen": 1,
            "lektionsliste": [{"name": "Unit 3", "aufgaben": 2}],
            "ohne_lektion": 0,
            "gefragt": 0,
            "richtig": 0,
            "falsch": 0,
            "trefferquote": None,
            "boxen": [4, 0, 0, 0, 0],
            "sicher": 0,
        }
    ]
    assert leer["arbeiten"] == [
        {
            "id": ARBEIT_ID,
            "fach_id": FACH_ID,
            "fach": "Englisch",
            "art": "arbeit",
            "thema": "Unit 3",
            "datum": "2026-10-09",
            "tage_bis": 3,
            "aufgaben": 2,
            "abfragen_heute": 2,
            "boxen": [4, 0, 0, 0, 0],
            "sicher": 0,
        }
    ]

    # One wrong answer, one right answer, one open question
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    await client.ok("ask", kind_id=KIND_ID, fach_id=FACH_ID)
    await hass.services.async_call(
        DOMAIN, "submit_answer", {"kind_id": KIND_ID, "text": "quatsch"}, blocking=True
    )
    await client.ok("ask", kind_id=KIND_ID)
    frage = manager.zustand(KIND_ID).offene_frage
    assert frage is not None
    aufgabe = manager.task_stores[FACH_ID].aufgaben[frage.aufgabe_id]
    await hass.services.async_call(
        DOMAIN,
        "submit_answer",
        {"kind_id": KIND_ID, "text": aufgabe.frage[frage.richtung.split(">")[1]]},
        blocking=True,
    )
    await client.ok("ask", kind_id=KIND_ID)

    daten = await client.ok("dashboard", kind_id=KIND_ID)
    assert daten["statistik"] == {
        "aufgaben": 2,
        "gefragt": 3,
        "richtig": 1,
        "falsch": 1,
        "teilweise": 0,
        "unbeantwortet": 0,
        "trefferquote": 50.0,
        "boxen": [3, 1, 0, 0, 0],
    }
    assert daten["zustand"]["offene_frage"]["fach"] == "Englisch"
    assert daten["zustand"]["letzte_frage_um"] is not None
    assert daten["faecher"][0]["boxen"] == [3, 1, 0, 0, 0]
    assert len(daten["schwierig"]) == 1
    schwierig = daten["schwierig"][0]
    assert schwierig["fach"] == "Englisch"
    assert schwierig["falsch"] == 1
    assert schwierig["fehlerquote"] in (50.0, 100.0)
    # Nothing about the task content of the open question is exposed
    assert "aufgabe_id" not in daten["zustand"]["offene_frage"]

    # An expired question counts as unanswered
    await manager.async_timeout(KIND_ID)
    daten = await client.ok("dashboard", kind_id=KIND_ID)
    assert daten["statistik"]["unbeantwortet"] == 1
    assert daten["zustand"]["offene_frage"] is None

    fehler = await client.fehler("dashboard", kind_id="x")
    assert fehler == {"code": "not_found", "message": "kind_unbekannt"}


async def test_dashboard_lernstand_und_vergangene_arbeit(
    hass: HomeAssistant,
    freezer: Any,
    mit_vokabeln: MockConfigEntry,
    client: Client,
) -> None:
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    aufgaben = list(manager.task_stores[FACH_ID].aufgaben.values())
    aufgaben[0].statistik_fuer("de>en").box = 3
    aufgaben[0].statistik_fuer("en>de").box = 9
    aufgaben[1].geprueft = False
    daten = await client.ok("dashboard", kind_id=KIND_ID)
    assert daten["faecher"][0]["boxen"] == [0, 0, 1, 0, 1]
    assert daten["faecher"][0]["sicher"] == 100
    assert daten["faecher"][0]["ungeprueft"] == 1
    assert daten["arbeiten"][0]["sicher"] == 100

    freezer.move_to("2026-10-10 08:00:00+02:00")
    daten = await client.ok("dashboard", kind_id=KIND_ID)
    assert daten["arbeiten"] == []


async def test_ask_und_set_active(
    hass: HomeAssistant,
    mit_vokabeln: MockConfigEntry,
    client: Client,
    notify_calls: list[ServiceCall],
) -> None:
    manager: LearnBuddyManager = mit_vokabeln.runtime_data
    for daten, fehler in (
        ({"kind_id": "x"}, {"code": "not_found", "message": "kind_unbekannt"}),
        (
            {"kind_id": KIND_ID, "fach_id": "x"},
            {"code": "not_found", "message": "fach_unbekannt"},
        ),
    ):
        assert await client.fehler("ask", **daten) == fehler
    assert not notify_calls

    assert await client.ok("ask", kind_id=KIND_ID, fach_id=FACH_ID) == {}
    assert len(notify_calls) == 1
    frage = manager.zustand(KIND_ID).offene_frage
    assert frage is not None
    assert frage.fach_id == FACH_ID
    stat = (
        manager.task_stores[FACH_ID]
        .aufgaben[frage.aufgabe_id]
        .statistik[frage.richtung]
    )
    assert stat.gefragt == 1

    assert await client.ok("set_active", kind_id=KIND_ID, aktiv=False) == {}
    assert manager.zustand(KIND_ID).aktiv is False
    assert hass.states.get("switch.max_abfragen_aktiv").state == "off"
    assert (await client.ok("dashboard", kind_id=KIND_ID))["zustand"]["pausiert"]
    await client.ok("set_active", kind_id=KIND_ID, aktiv=True)
    assert manager.zustand(KIND_ID).aktiv is True
    fehler = await client.fehler("set_active", kind_id="x", aktiv=True)
    assert fehler["code"] == "not_found"


async def test_ask_fehler(
    hass: HomeAssistant,
    setup_entry: MockConfigEntry,
    hass_ws_client: WebSocketGenerator,
) -> None:
    client = Client(await hass_ws_client(hass))
    # No tasks yet
    fehler = await client.fehler("ask", kind_id=KIND_ID)
    assert fehler == {"code": "invalid_format", "message": "keine_aufgaben"}

    # The notify action fails
    hass.services.async_remove("notify", "test")
    await hass.services.async_call(
        DOMAIN,
        "import_tasks",
        {"fach_id": FACH_ID, "inhalt": "Hund;dog"},
        blocking=True,
    )
    fehler = await client.fehler("ask", kind_id=KIND_ID)
    assert fehler == {"code": "send_failed", "message": "senden_fehlgeschlagen"}

    assert await hass.config_entries.async_unload(setup_entry.entry_id)
    assert (await client.fehler("ask", kind_id=KIND_ID))["code"] == "not_loaded"


async def test_antwortfrist_der_arbeit(
    hass: HomeAssistant, mit_vokabeln: MockConfigEntry, client: Client
) -> None:
    def _frist() -> float:
        frage = mit_vokabeln.runtime_data.zustand(KIND_ID).offene_frage
        assert frage is not None
        return (frage.timeout_um - frage.gestellt_um).total_seconds() / 60

    async def _frage() -> None:
        await hass.services.async_call(
            DOMAIN, "ask_now", {"kind_id": KIND_ID}, blocking=True
        )

    arbeit = {
        "datum": "2026-10-09",
        "thema": "Unit 3",
        "abfragen_pro_tag": 2,
        "start_tage_vorher": 7,
        "intensivierung": False,
    }
    # Without an own value the general setting applies
    await _frage()
    assert _frist() == 60

    await client.ok(
        "exams/save", arbeit_id=ARBEIT_ID, arbeit={**arbeit, "antwortfrist_minuten": 15}
    )
    await hass.async_block_till_done()
    uebersicht = await client.ok("overview")
    assert uebersicht["arbeiten"][0]["antwortfrist_minuten"] == 15
    await _frage()
    assert _frist() == 15

    # A second running exam with the same tasks: the shortest time wins
    await client.ok(
        "exams/save",
        arbeit={
            **arbeit,
            "fach_id": FACH_ID,
            "thema": "HÜ",
            "antwortfrist_minuten": 5,
        },
    )
    await hass.async_block_till_done()
    await _frage()
    assert _frist() == 5

    for falsch in (0, 1441):
        assert await client.fehler(
            "exams/save",
            arbeit_id=ARBEIT_ID,
            arbeit={**arbeit, "antwortfrist_minuten": falsch},
        ) == {"code": "invalid_format", "message": "arbeit_ungueltig"}

    # An empty field removes the own value again
    await client.ok(
        "exams/save",
        arbeit_id=ARBEIT_ID,
        arbeit={**arbeit, "antwortfrist_minuten": None},
    )
    await hass.async_block_till_done()
    uebersicht = await client.ok("overview")
    eigene = {a["thema"]: a["antwortfrist_minuten"] for a in uebersicht["arbeiten"]}
    assert eigene == {"Unit 3": None, "HÜ": 5}


async def test_sender_befehle(hass: HomeAssistant, client: Client) -> None:
    await client.ok("ask", kind_id=KIND_ID, fach_id=None)
    hass.bus.async_fire("telegram_text", {"chat_id": 4711, "text": "x"})
    hass.bus.async_fire("telegram_text", {"chat_id": 4712, "text": "x"})
    await hass.async_block_till_done()
    ergebnis = await client.ok("overview")
    assert [e["kennung"] for e in ergebnis["unbekannte_absender"]] == ["4712", "4711"]

    await client.ok("sender/dismiss", kennung="4712")
    fehler = await client.fehler("sender/assign", kind_id="x", kennung="4711")
    assert fehler["message"] == "kind_unbekannt"
    await client.ok("sender/assign", kind_id=KIND_ID, kennung="4711")
    ergebnis = await client.ok("overview")
    assert ergebnis["unbekannte_absender"] == []
