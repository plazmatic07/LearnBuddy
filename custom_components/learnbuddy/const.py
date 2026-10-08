"""Constants for the LearnBuddy integration."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Final

from homeassistant.const import Platform

DOMAIN: Final = "learnbuddy"
LOGGER: Final = logging.getLogger(__package__)

PLATFORMS: Final = [
    Platform.BUTTON,
    Platform.CALENDAR,
    Platform.SENSOR,
    Platform.SWITCH,
]

SUBENTRY_KIND: Final = "kind"
SUBENTRY_FACH: Final = "fach"
SUBENTRY_ARBEIT: Final = "arbeit"

# Options of the main config entry
CONF_TIMEOUT_MINUTEN: Final = "timeout_minuten"
CONF_SPRACHE: Final = "sprache"
CONF_KI_ENTITY: Final = "ki_entity"
CONF_AUTO_FREIGABE: Final = "auto_freigabe"
CONF_VERLAUF: Final = "verlauf"
CONF_WOCHENREPORT: Final = "wochenreport"
CONF_EINGANG_TELEGRAM: Final = "eingang_telegram"
CONF_EINGANG_WHATSAPP: Final = "eingang_whatsapp"
CONF_EINGANG_EVENT: Final = "eingang_event"
CONF_EINGANG_ABSENDER_FELD: Final = "eingang_absender_feld"
CONF_EINGANG_TEXT_FELD: Final = "eingang_text_feld"

# Subentry "kind"
CONF_NAME: Final = "name"
CONF_MUTTERSPRACHE: Final = "muttersprache"
CONF_KLASSENSTUFE: Final = "klassenstufe"
CONF_SCHULART: Final = "schulart"
CONF_BUNDESLAND: Final = "bundesland"
CONF_NOTIFY_ENTITY: Final = "notify_entity"
CONF_NOTIFY_SERVICE: Final = "notify_service"
CONF_NOTIFY_TARGET: Final = "notify_target"
CONF_NOTIFY_DATA: Final = "notify_data"
CONF_BILD_AKTION: Final = "bild_aktion"
CONF_ABSENDER_KENNUNG: Final = "absender_kennung"
CONF_KALENDER_AKTIV: Final = "kalender_aktiv"
CONF_KALENDER_ENTITY: Final = "kalender_entity"
CONF_KALENDER_UM: Final = "kalender_um"
# Calendar event an exam was created from
CONF_KALENDER_UID: Final = "kalender_uid"
CONF_WERKTAG_VON: Final = "werktag_von"
CONF_WERKTAG_BIS: Final = "werktag_bis"
CONF_WOCHENENDE_AKTIV: Final = "wochenende_aktiv"
CONF_WOCHENENDE_VON: Final = "wochenende_von"
CONF_WOCHENENDE_BIS: Final = "wochenende_bis"

# Subentry "fach"
CONF_KIND_ID: Final = "kind_id"
CONF_TYP: Final = "typ"
CONF_SPRACHEN: Final = "sprachen"
CONF_AUSGANGSSPRACHE: Final = "ausgangssprache"
CONF_ZIELSPRACHE: Final = "zielsprache"

# Subentry "arbeit"
CONF_FACH_ID: Final = "fach_id"
CONF_ART: Final = "art"
CONF_DATUM: Final = "datum"
CONF_THEMA: Final = "thema"
CONF_LEKTIONEN: Final = "lektionen"
CONF_ABFRAGEN_PRO_TAG: Final = "abfragen_pro_tag"
CONF_START_TAGE_VORHER: Final = "start_tage_vorher"
CONF_INTENSIVIERUNG: Final = "intensivierung"
CONF_ANTWORTFRIST: Final = "antwortfrist_minuten"
CONF_SIMULATION_UM: Final = "simulation_um"
CONF_SIMULATION_ANZAHL: Final = "simulation_anzahl"

CONF_ERSTELLT: Final = "erstellt"
CONF_GEAENDERT: Final = "geaendert"

DEFAULT_TIMEOUT_MINUTEN: Final = 60
DEFAULT_KALENDER_UM: Final = "20:00:00"
# How far ahead exam dates are read from a calendar
KALENDER_TAGE_VORAUS: Final = 120
DEFAULT_EINGANG_ABSENDER_FELD: Final = "sender"
DEFAULT_EINGANG_TEXT_FELD: Final = "text"
# Events fired by other integrations for incoming messages
EVENT_TELEGRAM_TEXT: Final = "telegram_text"
EVENT_WHATSAPP_NACHRICHT: Final = "whatsapp_message_received"
# Two paths (built-in listener and an automation) may deliver the same message
DOPPELT_SEKUNDEN: Final = 5.0
# Unknown senders are remembered in memory only, for the hint in the panel
UNBEKANNTE_ABSENDER_MAX: Final = 5
UNBEKANNTE_ABSENDER_STUNDEN: Final = 1
DEFAULT_SIMULATION_ANZAHL: Final = 10
MAX_TIMEOUT_MINUTEN: Final = 1440
DEFAULT_ABFRAGEN_PRO_TAG: Final = 3
DEFAULT_START_TAGE_VORHER: Final = 7
DEFAULT_WERKTAG_VON: Final = "15:00:00"
DEFAULT_WERKTAG_BIS: Final = "19:00:00"
DEFAULT_WOCHENENDE_VON: Final = "10:00:00"
DEFAULT_WOCHENENDE_BIS: Final = "18:00:00"
SPRACHE_AUTO: Final = "auto"

SCHULARTEN: Final = [
    "grundschule",
    "hauptschule",
    "realschule",
    "gymnasium",
    "gesamtschule",
    "sonstige",
]
BUNDESLAENDER: Final = [
    "bw",
    "by",
    "be",
    "bb",
    "hb",
    "hh",
    "he",
    "mv",
    "ni",
    "nw",
    "rp",
    "sl",
    "sn",
    "st",
    "sh",
    "th",
]
SPRACH_CODES: Final = ["de", "en", "fr", "es", "it", "la"]

# Minimum distance between two questions for the same child
MINDESTABSTAND: Final = timedelta(minutes=10)
# Delays between the retries of a failed notification
SENDE_WIEDERHOLUNGEN: Final = (
    timedelta(seconds=30),
    timedelta(minutes=2),
    timedelta(minutes=10),
)

EVENT_QUESTION_SENT: Final = "learnbuddy_question_sent"
EVENT_ANSWER_EVALUATED: Final = "learnbuddy_answer_evaluated"
EVENT_SIMULATION_FINISHED: Final = "learnbuddy_simulation_finished"

SERVICE_SUBMIT_ANSWER: Final = "submit_answer"
SERVICE_ASK_NOW: Final = "ask_now"
SERVICE_IMPORT_TASKS: Final = "import_tasks"
SERVICE_GENERATE_TASKS: Final = "generate_tasks"
SERVICE_PAUSE: Final = "pause"
SERVICE_RESUME: Final = "resume"
SERVICE_CANCEL_QUESTION: Final = "cancel_question"

ATTR_KIND_ID: Final = "kind_id"
ATTR_DEVICE_ID: Final = "device_id"
ATTR_ABSENDER: Final = "absender"
ATTR_TEXT: Final = "text"
ATTR_FACH_ID: Final = "fach_id"
ATTR_FACH: Final = "fach"
ATTR_INHALT: Final = "inhalt"
ATTR_LEKTION: Final = "lektion"
ATTR_TRENNZEICHEN: Final = "trennzeichen"
ATTR_GEPRUEFT: Final = "geprueft"
ATTR_ANZAHL: Final = "anzahl"
ATTR_SCHWIERIGKEIT: Final = "schwierigkeit"
ATTR_BESCHREIBUNG: Final = "beschreibung"
ATTR_BIS: Final = "bis"

STORAGE_VERSION: Final = 1
STORAGE_MINOR_VERSION: Final = 12

# Most extra questions a child can ask for at once
MAX_ZUSATZAUFGABEN: Final = 20
STORAGE_KEY_CONFIG: Final = f"{DOMAIN}.config"
# The daily log is a file of its own with its own version
STORAGE_KEY_VERLAUF: Final = f"{DOMAIN}.verlauf"
VERLAUF_VERSION: Final = 1
# A card counts as safe from this Leitner box on
SICHER_AB_BOX: Final = 3


def signal_kind_update(kind_id: str) -> str:
    """Return the dispatcher signal that is sent when a child changes."""
    return f"{DOMAIN}_update_{kind_id}"
