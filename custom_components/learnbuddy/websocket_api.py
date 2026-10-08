"""WebSocket API for the LearnBuddy panel. All commands require an admin."""

from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import TYPE_CHECKING, Any

from homeassistant.components.websocket_api import async_register_command
from homeassistant.components.websocket_api.connection import ActiveConnection
from homeassistant.components.websocket_api.decorators import (
    async_response,
    require_admin,
    websocket_command,
)
from homeassistant.core import HomeAssistant, callback
import voluptuous as vol

from .const import DOMAIN, MAX_ZUSATZAUFGABEN
from .verwaltung import Verwaltung, VerwaltungError

if TYPE_CHECKING:
    from .manager import LearnBuddyManager

type _Handler = Callable[
    [HomeAssistant, ActiveConnection, dict[str, Any], Verwaltung], Any
]

AUFGABE_SCHEMA = vol.Schema(
    {
        # Vocabulary: per language; knowledge subjects: the question itself
        vol.Optional("frage"): vol.Any({str: vol.Any(str, None)}, str, None),
        vol.Optional("antwort"): vol.Any(str, None),
        vol.Optional("form"): str,
        vol.Optional("kernpunkte"): [str],
        vol.Optional("falsche_optionen"): [str],
        vol.Optional("stelle"): vol.Any(str, None),
        # Vocabulary: per language; math: other spellings of the result
        vol.Optional("alternativen"): vol.Any({str: [str]}, [str]),
        vol.Optional("aufgabe"): vol.Any(str, None),
        vol.Optional("loesung"): vol.Any(str, None),
        vol.Optional("rechenweg"): [str],
        vol.Optional("bild"): vol.Any(str, None),
        vol.Optional("schwierigkeit"): vol.Any(int, None),
        vol.Optional("hinweis"): vol.Any(str, None),
        vol.Optional("seite"): vol.Any(int, None),
        vol.Optional("lektion"): vol.Any(str, None),
        vol.Optional("geprueft"): bool,
    }
)
ARBEIT_SCHEMA = vol.Schema(
    {
        vol.Optional("fach_id"): str,
        vol.Required("datum"): str,
        vol.Required("thema"): str,
        vol.Optional("art"): str,
        vol.Optional("lektionen"): [str],
        vol.Optional("aufgaben_ids"): [str],
        vol.Optional("abfragen_pro_tag"): vol.Coerce(int),
        vol.Optional("start_tage_vorher"): vol.Coerce(int),
        vol.Optional("intensivierung"): bool,
        vol.Optional("antwortfrist_minuten"): vol.Any(None, vol.Coerce(int)),
        vol.Optional("simulation_um"): vol.Any(None, str),
        vol.Optional("simulation_anzahl"): vol.Any(None, vol.Coerce(int)),
        vol.Optional("kalender_uid"): vol.Any(None, str),
    }
)


def _verwaltung(hass: HomeAssistant) -> Verwaltung | None:
    entries = hass.config_entries.async_loaded_entries(DOMAIN)
    if not entries:
        return None
    manager: LearnBuddyManager = entries[0].runtime_data
    return manager.verwaltung


def _befehl(
    func: Callable[[Verwaltung, dict[str, Any]], Any],
) -> Callable[[HomeAssistant, ActiveConnection, dict[str, Any]], None]:
    """Wrap a synchronous command: resolve the manager and map errors."""

    @callback
    @wraps(func)
    def wrapper(
        hass: HomeAssistant,
        connection: ActiveConnection,
        msg: dict[str, Any],
    ) -> None:
        verwaltung = _verwaltung(hass)
        if verwaltung is None:
            connection.send_error(msg["id"], "not_loaded", "nicht_geladen")
            return
        try:
            ergebnis = func(verwaltung, msg)
        except VerwaltungError as err:
            connection.send_error(msg["id"], err.code, err.schluessel)
            return
        connection.send_result(msg["id"], ergebnis)

    return wrapper


@websocket_command({vol.Required("type"): "learnbuddy/overview"})
@require_admin
@_befehl
def ws_overview(verwaltung: Verwaltung, msg: dict[str, Any]) -> Any:
    """Return children, subjects and exams."""
    return verwaltung.uebersicht()


@websocket_command(
    {vol.Required("type"): "learnbuddy/dashboard", vol.Required("kind_id"): str}
)
@require_admin
@_befehl
def ws_dashboard(verwaltung: Verwaltung, msg: dict[str, Any]) -> Any:
    """Return the overview of a child."""
    return verwaltung.dashboard(msg["kind_id"])


@websocket_command(
    {
        vol.Required("type"): "learnbuddy/set_active",
        vol.Required("kind_id"): str,
        vol.Required("aktiv"): bool,
    }
)
@require_admin
@_befehl
def ws_set_active(verwaltung: Verwaltung, msg: dict[str, Any]) -> Any:
    """Enable or disable the questions of a child."""
    verwaltung.setze_aktiv(msg["kind_id"], msg["aktiv"])
    return {}


_SEITE = vol.Any(None, vol.All(int, vol.Range(min=1, max=9999)))
_ABFRAGE_AUSWAHL: dict[str | vol.Marker, Any] = {
    vol.Optional("lektionen", default=list): [str],
    vol.Optional("seite_von"): _SEITE,
    vol.Optional("seite_bis"): _SEITE,
    vol.Optional("lektion_seiten", default=list): [
        {
            vol.Required("lektion"): str,
            vol.Optional("von"): _SEITE,
            vol.Optional("bis"): _SEITE,
        }
    ],
    vol.Optional("fehlerquote_ab"): vol.Any(
        None, vol.All(int, vol.Range(min=1, max=100))
    ),
}


@websocket_command(
    {
        vol.Required("type"): "learnbuddy/ask_count",
        vol.Required("kind_id"): str,
        vol.Optional("fach_id"): vol.Any(str, None),
        **_ABFRAGE_AUSWAHL,
    }
)
@require_admin
@_befehl
def ws_ask_count(verwaltung: Verwaltung, msg: dict[str, Any]) -> Any:
    """Return how many tasks a manual request could choose from."""
    return {
        "aufgaben": verwaltung.abfrage_umfang(msg["kind_id"], msg.get("fach_id"), msg)
    }


@websocket_command(
    {
        vol.Required("type"): "learnbuddy/ask",
        vol.Required("kind_id"): str,
        vol.Optional("fach_id"): vol.Any(str, None),
        **_ABFRAGE_AUSWAHL,
        vol.Optional("anzahl", default=1): vol.All(
            int, vol.Range(min=1, max=MAX_ZUSATZAUFGABEN)
        ),
    }
)
@require_admin
@async_response
async def ws_ask(
    hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]
) -> None:
    """Ask a child a question right now."""
    verwaltung = _verwaltung(hass)
    if verwaltung is None:
        connection.send_error(msg["id"], "not_loaded", "nicht_geladen")
        return
    try:
        await verwaltung.frage_stellen(
            msg["kind_id"], msg.get("fach_id"), msg, msg["anzahl"]
        )
    except VerwaltungError as err:
        connection.send_error(msg["id"], err.code, err.schluessel)
        return
    connection.send_result(msg["id"], {})


@websocket_command(
    {vol.Required("type"): "learnbuddy/tasks/list", vol.Required("fach_id"): str}
)
@require_admin
@_befehl
def ws_tasks_list(verwaltung: Verwaltung, msg: dict[str, Any]) -> Any:
    """Return the tasks of a subject."""
    return {"aufgaben": verwaltung.aufgaben(msg["fach_id"])}


@websocket_command(
    {
        vol.Required("type"): "learnbuddy/tasks/create",
        vol.Required("fach_id"): str,
        vol.Required("aufgabe"): AUFGABE_SCHEMA,
    }
)
@require_admin
@_befehl
def ws_tasks_create(verwaltung: Verwaltung, msg: dict[str, Any]) -> Any:
    """Create a task."""
    return verwaltung.aufgabe_anlegen(msg["fach_id"], msg["aufgabe"])


@websocket_command(
    {
        vol.Required("type"): "learnbuddy/tasks/update",
        vol.Required("fach_id"): str,
        vol.Required("aufgabe_id"): str,
        vol.Required("aenderungen"): AUFGABE_SCHEMA,
    }
)
@require_admin
@_befehl
def ws_tasks_update(verwaltung: Verwaltung, msg: dict[str, Any]) -> Any:
    """Change a task."""
    return verwaltung.aufgabe_aendern(
        msg["fach_id"], msg["aufgabe_id"], msg["aenderungen"]
    )


@websocket_command(
    {
        vol.Required("type"): "learnbuddy/tasks/delete",
        vol.Required("fach_id"): str,
        vol.Required("aufgabe_ids"): [str],
        vol.Optional("bestaetigt", default=False): bool,
    }
)
@require_admin
@_befehl
def ws_tasks_delete(verwaltung: Verwaltung, msg: dict[str, Any]) -> Any:
    """Delete tasks, asking for confirmation if exams are affected."""
    return verwaltung.aufgaben_loeschen(
        msg["fach_id"], msg["aufgabe_ids"], bestaetigt=msg["bestaetigt"]
    )


@websocket_command(
    {
        vol.Required("type"): "learnbuddy/lessons/add",
        vol.Required("fach_id"): str,
        vol.Required("name"): str,
    }
)
@require_admin
@_befehl
def ws_lessons_add(verwaltung: Verwaltung, msg: dict[str, Any]) -> Any:
    """Create a lesson of a subject."""
    return {"lektionen": verwaltung.lektion_hinzufuegen(msg["fach_id"], msg["name"])}


@websocket_command(
    {
        vol.Required("type"): "learnbuddy/lessons/delete",
        vol.Required("fach_id"): str,
        vol.Required("name"): str,
    }
)
@require_admin
@_befehl
def ws_lessons_delete(verwaltung: Verwaltung, msg: dict[str, Any]) -> Any:
    """Delete an unused lesson of a subject."""
    return {"lektionen": verwaltung.lektion_loeschen(msg["fach_id"], msg["name"])}


@websocket_command(
    {
        vol.Required("type"): "learnbuddy/tasks/import_text",
        vol.Required("fach_id"): str,
        vol.Required("inhalt"): str,
        vol.Optional("lektion"): vol.Any(str, None),
        vol.Optional("trennzeichen"): vol.Any(str, None),
        vol.Optional("geprueft", default=True): bool,
        vol.Optional("vorschau", default=False): bool,
    }
)
@require_admin
@_befehl
def ws_tasks_import_text(verwaltung: Verwaltung, msg: dict[str, Any]) -> Any:
    """Preview or import a vocabulary list."""
    return verwaltung.import_text(
        msg["fach_id"],
        msg["inhalt"],
        lektion=msg.get("lektion"),
        trennzeichen=msg.get("trennzeichen") or None,
        geprueft=msg["geprueft"],
        vorschau=msg["vorschau"],
    )


@websocket_command(
    {
        vol.Required("type"): "learnbuddy/tasks/export",
        vol.Required("fach_id"): str,
        vol.Optional("mit_statistik", default=False): bool,
    }
)
@require_admin
@_befehl
def ws_tasks_export(verwaltung: Verwaltung, msg: dict[str, Any]) -> Any:
    """Export the tasks of a subject."""
    return verwaltung.export(msg["fach_id"], mit_statistik=msg["mit_statistik"])


@websocket_command(
    {
        vol.Required("type"): "learnbuddy/tasks/import_json",
        vol.Required("fach_id"): str,
        vol.Required("daten"): dict,
        vol.Optional("mit_statistik", default=False): bool,
        vol.Optional("lektion"): vol.Any(str, None),
    }
)
@require_admin
@_befehl
def ws_tasks_import_json(verwaltung: Verwaltung, msg: dict[str, Any]) -> Any:
    """Import tasks from an export."""
    return verwaltung.import_json(
        msg["fach_id"],
        msg["daten"],
        mit_statistik=msg["mit_statistik"],
        lektion=msg.get("lektion"),
    )


@websocket_command(
    {
        vol.Required("type"): "learnbuddy/tasks/generate",
        vol.Required("fach_id"): str,
        vol.Required("anzahl"): int,
        vol.Optional("lektion"): vol.Any(str, None),
        vol.Optional("schwierigkeit"): vol.Any(int, None),
        vol.Optional("beschreibung"): vol.Any(str, None),
        vol.Optional("beispiel_ids"): [str],
    }
)
@require_admin
@async_response
async def ws_tasks_generate(
    hass: HomeAssistant,
    connection: ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Let the AI create math tasks."""
    verwaltung = _verwaltung(hass)
    if verwaltung is None:
        connection.send_error(msg["id"], "not_loaded", "nicht_geladen")
        return
    try:
        ergebnis = await verwaltung.generiere(
            msg["fach_id"],
            anzahl=msg["anzahl"],
            lektion=msg.get("lektion"),
            schwierigkeit=msg.get("schwierigkeit"),
            beschreibung=msg.get("beschreibung"),
            beispiel_ids=msg.get("beispiel_ids"),
        )
    except VerwaltungError as err:
        connection.send_error(msg["id"], err.code, err.schluessel)
        return
    connection.send_result(msg["id"], ergebnis)


@websocket_command(
    {
        vol.Required("type"): "learnbuddy/tasks/generate_from_pages",
        vol.Required("fach_id"): str,
        vol.Required("seiten"): [str],
        vol.Required("anzahl"): int,
        vol.Optional("form"): vol.Any(str, None),
        vol.Optional("lektion"): vol.Any(str, None),
        vol.Optional("schwerpunkt"): vol.Any(str, None),
    }
)
@require_admin
@async_response
async def ws_tasks_generate_from_pages(
    hass: HomeAssistant,
    connection: ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Let the AI create questions about photographed pages."""
    verwaltung = _verwaltung(hass)
    if verwaltung is None:
        connection.send_error(msg["id"], "not_loaded", "nicht_geladen")
        return
    try:
        ergebnis = await verwaltung.fragen_aus_seiten(
            msg["fach_id"],
            seiten=msg["seiten"],
            anzahl=msg["anzahl"],
            form=msg.get("form"),
            lektion=msg.get("lektion"),
            schwerpunkt=msg.get("schwerpunkt"),
        )
    except VerwaltungError as err:
        connection.send_error(msg["id"], err.code, err.schluessel)
        return
    connection.send_result(msg["id"], ergebnis)


@websocket_command(
    {
        vol.Required("type"): "learnbuddy/tasks/photo_extract",
        vol.Required("fach_id"): str,
        vol.Required("seiten"): [str],
    }
)
@require_admin
@async_response
async def ws_tasks_photo_extract(
    hass: HomeAssistant,
    connection: ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Let the AI read tasks from photos and return a preview."""
    verwaltung = _verwaltung(hass)
    if verwaltung is None:
        connection.send_error(msg["id"], "not_loaded", "nicht_geladen")
        return
    try:
        ergebnis = await verwaltung.foto_auslesen(msg["fach_id"], msg["seiten"])
    except VerwaltungError as err:
        connection.send_error(msg["id"], err.code, err.schluessel)
        return
    connection.send_result(msg["id"], ergebnis)


@websocket_command(
    {
        vol.Required("type"): "learnbuddy/tasks/photo_accept",
        vol.Required("fach_id"): str,
        vol.Required("zeilen"): [dict],
        vol.Optional("lektion"): vol.Any(str, None),
    }
)
@require_admin
@_befehl
def ws_tasks_photo_accept(verwaltung: Verwaltung, msg: dict[str, Any]) -> Any:
    """Store the tasks taken over from the preview of a photo."""
    return verwaltung.foto_uebernehmen(
        msg["fach_id"], msg["zeilen"], lektion=msg.get("lektion")
    )


@websocket_command(
    {
        vol.Required("type"): "learnbuddy/tasks/verify",
        vol.Required("fach_id"): str,
        vol.Required("aufgabe_ids"): [str],
    }
)
@require_admin
@async_response
async def ws_tasks_verify(
    hass: HomeAssistant,
    connection: ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Check the solutions of math tasks."""
    verwaltung = _verwaltung(hass)
    if verwaltung is None:
        connection.send_error(msg["id"], "not_loaded", "nicht_geladen")
        return
    try:
        ergebnis = await verwaltung.nachrechnen(msg["fach_id"], msg["aufgabe_ids"])
    except VerwaltungError as err:
        connection.send_error(msg["id"], err.code, err.schluessel)
        return
    connection.send_result(msg["id"], ergebnis)


@websocket_command(
    {
        vol.Required("type"): "learnbuddy/tasks/accept_suggestion",
        vol.Required("fach_id"): str,
        vol.Required("aufgabe_ids"): [str],
    }
)
@require_admin
@_befehl
def ws_tasks_accept_suggestion(verwaltung: Verwaltung, msg: dict[str, Any]) -> Any:
    """Take over the results found when recalculating."""
    return verwaltung.vorschlag_uebernehmen(msg["fach_id"], msg["aufgabe_ids"])


@websocket_command(
    {
        vol.Required("type"): "learnbuddy/tasks/mark_verified",
        vol.Required("fach_id"): str,
        vol.Required("aufgabe_ids"): [str],
    }
)
@require_admin
@_befehl
def ws_tasks_mark_verified(verwaltung: Verwaltung, msg: dict[str, Any]) -> Any:
    """Mark the solutions as checked by a parent."""
    return verwaltung.als_geprueft_markieren(msg["fach_id"], msg["aufgabe_ids"])


@websocket_command(
    {
        vol.Required("type"): "learnbuddy/tasks/generate_steps",
        vol.Required("fach_id"): str,
        vol.Required("aufgabe_ids"): [str],
    }
)
@require_admin
@async_response
async def ws_tasks_generate_steps(
    hass: HomeAssistant,
    connection: ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Let the AI write missing solution steps."""
    verwaltung = _verwaltung(hass)
    if verwaltung is None:
        connection.send_error(msg["id"], "not_loaded", "nicht_geladen")
        return
    try:
        ergebnis = await verwaltung.rechenwege_erzeugen(
            msg["fach_id"], msg["aufgabe_ids"]
        )
    except VerwaltungError as err:
        connection.send_error(msg["id"], err.code, err.schluessel)
        return
    connection.send_result(msg["id"], ergebnis)


@websocket_command(
    {
        vol.Required("type"): "learnbuddy/exams/save",
        vol.Optional("arbeit_id"): vol.Any(str, None),
        vol.Required("arbeit"): ARBEIT_SCHEMA,
    }
)
@require_admin
@async_response
async def ws_exams_save(
    hass: HomeAssistant,
    connection: ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Create or change an exam."""
    verwaltung = _verwaltung(hass)
    if verwaltung is None:
        connection.send_error(msg["id"], "not_loaded", "nicht_geladen")
        return
    try:
        arbeit_id = await verwaltung.arbeit_speichern(
            msg.get("arbeit_id"), msg["arbeit"]
        )
    except VerwaltungError as err:
        connection.send_error(msg["id"], err.code, err.schluessel)
        return
    connection.send_result(msg["id"], {"arbeit_id": arbeit_id})


@websocket_command(
    {
        vol.Required("type"): "learnbuddy/exams/simulate",
        vol.Required("arbeit_id"): str,
        vol.Required("anzahl"): int,
        vol.Required("weg"): str,
    }
)
@require_admin
@async_response
async def ws_exams_simulate(
    hass: HomeAssistant,
    connection: ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Simulate an exam as a sheet to print or in the messenger."""
    verwaltung = _verwaltung(hass)
    if verwaltung is None:
        connection.send_error(msg["id"], "not_loaded", "nicht_geladen")
        return
    try:
        ergebnis = await verwaltung.simulieren(
            msg["arbeit_id"], msg["anzahl"], msg["weg"]
        )
    except VerwaltungError as err:
        connection.send_error(msg["id"], err.code, err.schluessel)
        return
    connection.send_result(msg["id"], ergebnis)


@websocket_command(
    {
        vol.Required("type"): "learnbuddy/cancel_question",
        vol.Required("kind_id"): str,
    }
)
@require_admin
@async_response
async def ws_cancel_question(
    hass: HomeAssistant,
    connection: ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Withdraw the open question of a child."""
    verwaltung = _verwaltung(hass)
    if verwaltung is None:
        connection.send_error(msg["id"], "not_loaded", "nicht_geladen")
        return
    try:
        ergebnis = await verwaltung.frage_abbrechen(msg["kind_id"])
    except VerwaltungError as err:
        connection.send_error(msg["id"], err.code, err.schluessel)
        return
    connection.send_result(msg["id"], ergebnis)


@websocket_command(
    {
        vol.Required("type"): "learnbuddy/exams/simulate_stop",
        vol.Required("kind_id"): str,
    }
)
@require_admin
@async_response
async def ws_exams_simulate_stop(
    hass: HomeAssistant,
    connection: ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Stop the simulated exam of a child."""
    verwaltung = _verwaltung(hass)
    if verwaltung is None:
        connection.send_error(msg["id"], "not_loaded", "nicht_geladen")
        return
    try:
        ergebnis = await verwaltung.simulation_abbrechen(msg["kind_id"])
    except VerwaltungError as err:
        connection.send_error(msg["id"], err.code, err.schluessel)
        return
    connection.send_result(msg["id"], ergebnis)


@websocket_command(
    {vol.Required("type"): "learnbuddy/exams/delete", vol.Required("arbeit_id"): str}
)
@require_admin
@_befehl
def ws_exams_delete(verwaltung: Verwaltung, msg: dict[str, Any]) -> Any:
    """Delete an exam."""
    verwaltung.arbeit_loeschen(msg["arbeit_id"])
    return {}


@websocket_command(
    {
        vol.Required("type"): "learnbuddy/progress",
        vol.Required("kind_id"): str,
        vol.Optional("tage", default=30): int,
    }
)
@require_admin
@_befehl
def ws_progress(verwaltung: Verwaltung, msg: dict[str, Any]) -> Any:
    """Return the progress of a child over the last days."""
    return verwaltung.fortschritt(msg["kind_id"], msg["tage"])


@websocket_command(
    {
        vol.Required("type"): "learnbuddy/weekly_report",
        vol.Required("kind_id"): str,
        vol.Optional("versatz", default=-1): int,
    }
)
@require_admin
@_befehl
def ws_weekly_report(verwaltung: Verwaltung, msg: dict[str, Any]) -> Any:
    """Return the summary of a week of a child."""
    return verwaltung.wochenreport(msg["kind_id"], msg["versatz"])


@websocket_command(
    {vol.Required("type"): "learnbuddy/calendar/refresh", vol.Required("kind_id"): str}
)
@require_admin
@async_response
async def ws_calendar_refresh(
    hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]
) -> None:
    """Read the exam calendar of a child right now."""
    verwaltung = _verwaltung(hass)
    if verwaltung is None:
        connection.send_error(msg["id"], "not_loaded", "nicht_geladen")
        return
    try:
        ergebnis = await verwaltung.kalender_pruefen(msg["kind_id"])
    except VerwaltungError as err:
        connection.send_error(msg["id"], err.code, err.schluessel)
        return
    connection.send_result(msg["id"], ergebnis)


@websocket_command(
    {
        vol.Required("type"): "learnbuddy/calendar/ignore",
        vol.Required("kind_id"): str,
        vol.Required("uid"): str,
    }
)
@require_admin
@_befehl
def ws_calendar_ignore(verwaltung: Verwaltung, msg: dict[str, Any]) -> Any:
    """Stop suggesting an exam date of the calendar."""
    verwaltung.kalender_ignorieren(msg["kind_id"], msg["uid"])
    return {}


@websocket_command(
    {vol.Required("type"): "learnbuddy/calendar/restore", vol.Required("kind_id"): str}
)
@require_admin
@_befehl
def ws_calendar_restore(verwaltung: Verwaltung, msg: dict[str, Any]) -> Any:
    """Suggest all ignored exam dates of a child again."""
    verwaltung.kalender_wiederherstellen(msg["kind_id"])
    return {}


@websocket_command(
    {
        vol.Required("type"): "learnbuddy/subjects/create",
        vol.Required("kind_id"): str,
        vol.Required("typ"): str,
        vol.Optional("name"): vol.Any(None, str),
        vol.Optional("sprache"): vol.Any(None, str),
    }
)
@require_admin
@async_response
async def ws_subjects_create(
    hass: HomeAssistant, connection: ActiveConnection, msg: dict[str, Any]
) -> None:
    """Add a subject of a child."""
    verwaltung = _verwaltung(hass)
    if verwaltung is None:
        connection.send_error(msg["id"], "not_loaded", "nicht_geladen")
        return
    try:
        fach_id = await verwaltung.fach_anlegen(msg["kind_id"], msg)
    except VerwaltungError as err:
        connection.send_error(msg["id"], err.code, err.schluessel)
        return
    connection.send_result(msg["id"], {"fach_id": fach_id})


@websocket_command(
    {
        vol.Required("type"): "learnbuddy/sender/assign",
        vol.Required("kind_id"): str,
        vol.Required("kennung"): str,
    }
)
@require_admin
@_befehl
def ws_sender_assign(verwaltung: Verwaltung, msg: dict[str, Any]) -> Any:
    """Set an unknown sender as the sender ID of a child."""
    verwaltung.absender_zuordnen(msg["kind_id"], msg["kennung"])
    return {}


@websocket_command(
    {vol.Required("type"): "learnbuddy/sender/dismiss", vol.Required("kennung"): str}
)
@require_admin
@_befehl
def ws_sender_dismiss(verwaltung: Verwaltung, msg: dict[str, Any]) -> Any:
    """Dismiss the hint about an unknown sender."""
    verwaltung.absender_verwerfen(msg["kennung"])
    return {}


@callback
def async_setup_websocket_api(hass: HomeAssistant) -> None:
    """Register the commands of the panel."""
    for befehl in (
        ws_overview,
        ws_dashboard,
        ws_set_active,
        ws_ask,
        ws_ask_count,
        ws_cancel_question,
        ws_tasks_list,
        ws_tasks_create,
        ws_tasks_update,
        ws_tasks_delete,
        ws_lessons_add,
        ws_lessons_delete,
        ws_tasks_import_text,
        ws_tasks_export,
        ws_tasks_import_json,
        ws_tasks_generate,
        ws_tasks_verify,
        ws_tasks_photo_extract,
        ws_tasks_photo_accept,
        ws_tasks_generate_from_pages,
        ws_tasks_generate_steps,
        ws_tasks_accept_suggestion,
        ws_tasks_mark_verified,
        ws_exams_save,
        ws_exams_delete,
        ws_exams_simulate,
        ws_exams_simulate_stop,
        ws_sender_assign,
        ws_sender_dismiss,
        ws_progress,
        ws_weekly_report,
        ws_calendar_refresh,
        ws_calendar_ignore,
        ws_calendar_restore,
        ws_subjects_create,
    ):
        async_register_command(hass, befehl)
