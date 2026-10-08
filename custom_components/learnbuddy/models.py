"""Data model of the LearnBuddy integration."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time
from enum import StrEnum
from typing import TYPE_CHECKING, Any, Self
import uuid

from homeassistant.util import dt as dt_util

from .const import (
    CONF_ABFRAGEN_PRO_TAG,
    CONF_ABSENDER_KENNUNG,
    CONF_ANTWORTFRIST,
    CONF_ART,
    CONF_BILD_AKTION,
    CONF_BUNDESLAND,
    CONF_DATUM,
    CONF_FACH_ID,
    CONF_INTENSIVIERUNG,
    CONF_KALENDER_AKTIV,
    CONF_KALENDER_ENTITY,
    CONF_KALENDER_UID,
    CONF_KALENDER_UM,
    CONF_KI_ENTITY,
    CONF_KIND_ID,
    CONF_KLASSENSTUFE,
    CONF_LEKTIONEN,
    CONF_MUTTERSPRACHE,
    CONF_NAME,
    CONF_NOTIFY_DATA,
    CONF_NOTIFY_ENTITY,
    CONF_NOTIFY_SERVICE,
    CONF_NOTIFY_TARGET,
    CONF_SCHULART,
    CONF_SIMULATION_ANZAHL,
    CONF_SIMULATION_UM,
    CONF_SPRACHEN,
    CONF_START_TAGE_VORHER,
    CONF_THEMA,
    CONF_TYP,
    CONF_WERKTAG_BIS,
    CONF_WERKTAG_VON,
    CONF_WOCHENENDE_AKTIV,
    CONF_WOCHENENDE_BIS,
    CONF_WOCHENENDE_VON,
    DEFAULT_ABFRAGEN_PRO_TAG,
    DEFAULT_KALENDER_UM,
    DEFAULT_SIMULATION_ANZAHL,
    DEFAULT_START_TAGE_VORHER,
    DEFAULT_WERKTAG_BIS,
    DEFAULT_WERKTAG_VON,
    DEFAULT_WOCHENENDE_BIS,
    DEFAULT_WOCHENENDE_VON,
)

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigSubentry

RICHTUNG_TRENNER = ">"
# Math tasks have no direction, their statistics use this fixed key
MATHE_RICHTUNG = "mathe"
SACH_RICHTUNG = "sach"
MIN_SCHWIERIGKEIT = 1
MAX_SCHWIERIGKEIT = 5

_WERKTAG_VON = time.fromisoformat(DEFAULT_WERKTAG_VON)
_KALENDER_UM = time.fromisoformat(DEFAULT_KALENDER_UM)
_WERKTAG_BIS = time.fromisoformat(DEFAULT_WERKTAG_BIS)
_WOCHENENDE_VON = time.fromisoformat(DEFAULT_WOCHENENDE_VON)
_WOCHENENDE_BIS = time.fromisoformat(DEFAULT_WOCHENENDE_BIS)


class AufgabenTyp(StrEnum):
    """Type of a subject and its tasks."""

    VOKABEL = "vokabel"
    MATHE = "mathe"
    # Knowledge subjects like biology: questions about a text
    SACH = "sach"


class SachForm(StrEnum):
    """How a knowledge question is answered."""

    KURZ = "kurz"
    AUSWAHL = "auswahl"


class Quelle(StrEnum):
    """Origin of a task."""

    UPLOAD = "upload"
    GENERIERT = "generiert"
    MANUELL = "manuell"


class Verifikation(StrEnum):
    """How the solution of a math task was verified."""

    RECHNERISCH = "rechnerisch"
    KI = "ki"
    # A parent checked the solution and vouches for it
    MANUELL = "manuell"
    # Recalculating gave another result than the stored solution
    ABWEICHUNG = "abweichung"
    KEINE = "keine"


class ArbeitArt(StrEnum):
    """Kind of an exam."""

    ARBEIT = "arbeit"
    HUE = "hue"


class Ergebnis(StrEnum):
    """Result of an evaluated answer."""

    RICHTIG = "richtig"
    FAST_RICHTIG = "fast_richtig"
    # Only a part of what a knowledge question asks for was given
    TEILWEISE = "teilweise"
    FALSCH = "falsch"
    UNBEANTWORTET = "unbeantwortet"


def _parse_dt(value: str | None) -> datetime | None:
    """Parse an optional ISO timestamp."""
    if value is None:
        return None
    return dt_util.parse_datetime(value, raise_on_error=True)


def _format_dt(value: datetime | None) -> str | None:
    """Format an optional timestamp as ISO string."""
    return None if value is None else value.isoformat()


def richtung(von: str, nach: str) -> str:
    """Build the direction key for asking in one language and answering in another."""
    return f"{von}{RICHTUNG_TRENNER}{nach}"


def arbeit_titel(datum: str, fach_titel: str, thema: str) -> str:
    """Return the title of the config subentry of an exam."""
    return f"{datum} {fach_titel}: {thema}"


def richtung_teile(wert: str) -> tuple[str, str]:
    """Split a direction key into question and answer language."""
    von, _, nach = wert.partition(RICHTUNG_TRENNER)
    return von, nach


@dataclass(slots=True)
class Statistik:
    """Learning statistics of a task (for one direction)."""

    box: int = 1
    gefragt: int = 0
    richtig: int = 0
    falsch: int = 0
    # Answers that were right in part; neither right nor wrong
    teilweise: int = 0
    zuletzt_gefragt: datetime | None = None
    zuletzt_falsch: datetime | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Create statistics from stored data."""
        richtig = data.get("richtig", 0)
        falsch = data.get("falsch", 0)
        return cls(
            box=data.get("box", 1),
            # Older data did not count the questions that were asked
            gefragt=data.get("gefragt", richtig + falsch),
            richtig=richtig,
            falsch=falsch,
            teilweise=data.get("teilweise", 0),
            zuletzt_gefragt=_parse_dt(data.get("zuletzt_gefragt")),
            zuletzt_falsch=_parse_dt(data.get("zuletzt_falsch")),
        )

    def to_dict(self) -> dict[str, Any]:
        """Return the storable representation."""
        return {
            "box": self.box,
            "gefragt": self.gefragt,
            "richtig": self.richtig,
            "falsch": self.falsch,
            "teilweise": self.teilweise,
            "zuletzt_gefragt": _format_dt(self.zuletzt_gefragt),
            "zuletzt_falsch": _format_dt(self.zuletzt_falsch),
        }


@dataclass(slots=True)
class Vokabel:
    """A vocabulary task."""

    fach_id: str
    frage: dict[str, str]
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    erstellt: datetime = field(default_factory=dt_util.utcnow)
    geaendert: datetime = field(default_factory=dt_util.utcnow)
    lektion: str | None = None
    quelle: Quelle = Quelle.MANUELL
    geprueft: bool = True
    alternativen: dict[str, list[str]] = field(default_factory=dict)
    hinweis: str | None = None
    # Page in the textbook's vocabulary list, used for filtering
    seite: int | None = None
    statistik: dict[str, Statistik] = field(default_factory=dict)

    typ = AufgabenTyp.VOKABEL

    def statistik_fuer(self, richtung_key: str) -> Statistik:
        """Return (and create if needed) the statistics of a direction."""
        return self.statistik.setdefault(richtung_key, Statistik())

    def fragbar(self, richtung_key: str) -> bool:
        """Return whether the task can be asked in a direction."""
        return all(self.frage.get(sprache) for sprache in richtung_teile(richtung_key))

    def frage_text(self, richtung_key: str) -> str:
        """Return what the child is asked."""
        return self.frage[richtung_teile(richtung_key)[0]]

    def loesung_text(self, richtung_key: str) -> str:
        """Return the expected answer."""
        return self.frage[richtung_teile(richtung_key)[1]]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Create a task from stored data."""
        return cls(
            id=data["id"],
            fach_id=data["fach_id"],
            erstellt=dt_util.parse_datetime(data["erstellt"], raise_on_error=True),
            geaendert=dt_util.parse_datetime(data["geaendert"], raise_on_error=True),
            lektion=data.get("lektion"),
            quelle=Quelle(data.get("quelle", Quelle.MANUELL)),
            geprueft=data.get("geprueft", True),
            frage=dict(data["frage"]),
            alternativen={
                sprache: list(werte)
                for sprache, werte in data.get("alternativen", {}).items()
            },
            hinweis=data.get("hinweis"),
            seite=data.get("seite"),
            statistik={
                key: Statistik.from_dict(wert)
                for key, wert in data.get("statistik", {}).items()
            },
        )

    def to_dict(self) -> dict[str, Any]:
        """Return the storable representation."""
        return {
            "id": self.id,
            "typ": self.typ.value,
            "fach_id": self.fach_id,
            "erstellt": self.erstellt.isoformat(),
            "geaendert": self.geaendert.isoformat(),
            "lektion": self.lektion,
            "quelle": self.quelle.value,
            "geprueft": self.geprueft,
            "frage": dict(self.frage),
            "alternativen": {k: list(v) for k, v in self.alternativen.items()},
            "hinweis": self.hinweis,
            "seite": self.seite,
            "statistik": {k: v.to_dict() for k, v in self.statistik.items()},
        }


@dataclass(slots=True)
class MatheAufgabe:
    """A math task with a single short result."""

    fach_id: str
    aufgabe: str
    loesung: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    erstellt: datetime = field(default_factory=dt_util.utcnow)
    geaendert: datetime = field(default_factory=dt_util.utcnow)
    lektion: str | None = None
    quelle: Quelle = Quelle.MANUELL
    geprueft: bool = True
    # Other spellings of the result that count as correct
    alternativen: list[str] = field(default_factory=list)
    # Steps of the solution, explained on request after a wrong answer
    rechenweg: list[str] = field(default_factory=list)
    schwierigkeit: int | None = None
    verifikation: Verifikation = Verifikation.KEINE
    # Result found when recalculating, if it differs from the solution
    vorschlag: str | None = None
    # Who found it: "lokal" (calculated) or "ki"
    vorschlag_durch: str | None = None
    # Id of the image the task is about (diagram, graph), sent with it
    bild: str | None = None
    hinweis: str | None = None
    seite: int | None = None
    statistik: dict[str, Statistik] = field(default_factory=dict)

    typ = AufgabenTyp.MATHE

    def statistik_fuer(self, richtung_key: str) -> Statistik:
        """Return (and create if needed) the statistics of the task."""
        return self.statistik.setdefault(richtung_key, Statistik())

    def fragbar(self, richtung_key: str) -> bool:
        """Return whether the task can be asked."""
        return richtung_key == MATHE_RICHTUNG and bool(self.aufgabe and self.loesung)

    def frage_text(self, richtung_key: str) -> str:
        """Return what the child is asked."""
        return self.aufgabe

    def loesung_text(self, richtung_key: str) -> str:
        """Return the expected answer."""
        return self.loesung

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Create a task from stored data."""
        return cls(
            id=data["id"],
            fach_id=data["fach_id"],
            erstellt=dt_util.parse_datetime(data["erstellt"], raise_on_error=True),
            geaendert=dt_util.parse_datetime(data["geaendert"], raise_on_error=True),
            lektion=data.get("lektion"),
            quelle=Quelle(data.get("quelle", Quelle.MANUELL)),
            geprueft=data.get("geprueft", True),
            aufgabe=data["aufgabe"],
            loesung=data["loesung"],
            alternativen=list(data.get("alternativen", [])),
            rechenweg=list(data.get("rechenweg", [])),
            schwierigkeit=data.get("schwierigkeit"),
            verifikation=Verifikation(data.get("verifikation", Verifikation.KEINE)),
            vorschlag=data.get("vorschlag"),
            vorschlag_durch=data.get("vorschlag_durch"),
            bild=data.get("bild"),
            hinweis=data.get("hinweis"),
            seite=data.get("seite"),
            statistik={
                key: Statistik.from_dict(wert)
                for key, wert in data.get("statistik", {}).items()
            },
        )

    def to_dict(self) -> dict[str, Any]:
        """Return the storable representation."""
        return {
            "id": self.id,
            "typ": self.typ.value,
            "fach_id": self.fach_id,
            "erstellt": self.erstellt.isoformat(),
            "geaendert": self.geaendert.isoformat(),
            "lektion": self.lektion,
            "quelle": self.quelle.value,
            "geprueft": self.geprueft,
            "aufgabe": self.aufgabe,
            "loesung": self.loesung,
            "alternativen": list(self.alternativen),
            "rechenweg": list(self.rechenweg),
            "schwierigkeit": self.schwierigkeit,
            "verifikation": self.verifikation.value,
            "vorschlag": self.vorschlag,
            "vorschlag_durch": self.vorschlag_durch,
            "bild": self.bild,
            "hinweis": self.hinweis,
            "seite": self.seite,
            "statistik": {k: v.to_dict() for k, v in self.statistik.items()},
        }


@dataclass(slots=True)
class SachAufgabe:
    """A question about the content of a text, answered from memory."""

    fach_id: str
    frage: str
    # Model answer, for a choice question the correct option
    antwort: str
    form: SachForm = SachForm.KURZ
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    erstellt: datetime = field(default_factory=dt_util.utcnow)
    geaendert: datetime = field(default_factory=dt_util.utcnow)
    lektion: str | None = None
    quelle: Quelle = Quelle.MANUELL
    geprueft: bool = True
    # What a complete answer has to contain
    kernpunkte: list[str] = field(default_factory=list)
    # Wrong options of a choice question
    falsche_optionen: list[str] = field(default_factory=list)
    # Short quote of the text that backs the answer
    stelle: str | None = None
    # Id of the image of the page the question was made from, never sent
    quelle_bild: str | None = None
    hinweis: str | None = None
    seite: int | None = None
    statistik: dict[str, Statistik] = field(default_factory=dict)

    typ = AufgabenTyp.SACH

    def statistik_fuer(self, richtung_key: str) -> Statistik:
        """Return (and create if needed) the statistics of the question."""
        return self.statistik.setdefault(richtung_key, Statistik())

    def fragbar(self, richtung_key: str) -> bool:
        """Return whether the question can be asked."""
        if richtung_key != SACH_RICHTUNG or not (self.frage and self.antwort):
            return False
        return self.form is SachForm.KURZ or len(self.falsche_optionen) >= 2

    def frage_text(self, richtung_key: str) -> str:
        """Return what the child is asked."""
        return self.frage

    def loesung_text(self, richtung_key: str) -> str:
        """Return the expected answer."""
        return self.antwort

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Create a question from stored data."""
        return cls(
            id=data["id"],
            fach_id=data["fach_id"],
            erstellt=dt_util.parse_datetime(data["erstellt"], raise_on_error=True),
            geaendert=dt_util.parse_datetime(data["geaendert"], raise_on_error=True),
            lektion=data.get("lektion"),
            quelle=Quelle(data.get("quelle", Quelle.MANUELL)),
            geprueft=data.get("geprueft", True),
            frage=data["frage"],
            antwort=data["antwort"],
            form=SachForm(data.get("form", SachForm.KURZ)),
            kernpunkte=list(data.get("kernpunkte", [])),
            falsche_optionen=list(data.get("falsche_optionen", [])),
            stelle=data.get("stelle"),
            quelle_bild=data.get("quelle_bild"),
            hinweis=data.get("hinweis"),
            seite=data.get("seite"),
            statistik={
                key: Statistik.from_dict(wert)
                for key, wert in data.get("statistik", {}).items()
            },
        )

    def to_dict(self) -> dict[str, Any]:
        """Return the storable representation."""
        return {
            "id": self.id,
            "typ": self.typ.value,
            "fach_id": self.fach_id,
            "erstellt": self.erstellt.isoformat(),
            "geaendert": self.geaendert.isoformat(),
            "lektion": self.lektion,
            "quelle": self.quelle.value,
            "geprueft": self.geprueft,
            "frage": self.frage,
            "antwort": self.antwort,
            "form": self.form.value,
            "kernpunkte": list(self.kernpunkte),
            "falsche_optionen": list(self.falsche_optionen),
            "stelle": self.stelle,
            "quelle_bild": self.quelle_bild,
            "hinweis": self.hinweis,
            "seite": self.seite,
            "statistik": {k: v.to_dict() for k, v in self.statistik.items()},
        }


type Aufgabe = Vokabel | MatheAufgabe | SachAufgabe


def aufgabe_from_dict(data: dict[str, Any]) -> Aufgabe | None:
    """Create a task of the stored type; None for an unknown type."""
    typ = data.get("typ", AufgabenTyp.VOKABEL.value)
    if typ == AufgabenTyp.VOKABEL.value:
        return Vokabel.from_dict(data)
    if typ == AufgabenTyp.MATHE.value:
        return MatheAufgabe.from_dict(data)
    if typ == AufgabenTyp.SACH.value:
        return SachAufgabe.from_dict(data)
    return None


@dataclass(slots=True, frozen=True)
class Kind:
    """A child, backed by a config subentry."""

    id: str
    name: str
    muttersprache: str | None = None
    klassenstufe: int | None = None
    schulart: str | None = None
    bundesland: str | None = None
    notify_entity: str | None = None
    notify_service: str | None = None
    notify_target: tuple[str, ...] = ()
    notify_data: dict[str, Any] | None = None
    # Actions that send an image, for messengers without built-in support
    bild_aktion: list[dict[str, Any]] | None = None
    absender_kennung: str | None = None
    # Calendar with the exam dates of the child, None if it is not used
    kalender_entity: str | None = None
    kalender_um: time = _KALENDER_UM
    werktag_von: time = _WERKTAG_VON
    werktag_bis: time = _WERKTAG_BIS
    wochenende_aktiv: bool = True
    wochenende_von: time = _WOCHENENDE_VON
    wochenende_bis: time = _WOCHENENDE_BIS

    @classmethod
    def from_subentry(cls, subentry: ConfigSubentry) -> Self:
        """Create a child from its config subentry."""
        data = subentry.data
        klassenstufe = data.get(CONF_KLASSENSTUFE)
        return cls(
            id=subentry.subentry_id,
            name=data[CONF_NAME],
            muttersprache=data.get(CONF_MUTTERSPRACHE) or None,
            klassenstufe=None if klassenstufe is None else int(klassenstufe),
            schulart=data.get(CONF_SCHULART),
            bundesland=data.get(CONF_BUNDESLAND),
            notify_entity=data.get(CONF_NOTIFY_ENTITY) or None,
            notify_service=data.get(CONF_NOTIFY_SERVICE) or None,
            notify_target=tuple(data.get(CONF_NOTIFY_TARGET) or ()),
            notify_data=data.get(CONF_NOTIFY_DATA) or None,
            bild_aktion=list(data.get(CONF_BILD_AKTION) or []) or None,
            absender_kennung=data.get(CONF_ABSENDER_KENNUNG) or None,
            kalender_entity=(
                (data.get(CONF_KALENDER_ENTITY) or None)
                if data.get(CONF_KALENDER_AKTIV)
                else None
            ),
            kalender_um=time.fromisoformat(
                data.get(CONF_KALENDER_UM) or DEFAULT_KALENDER_UM
            ),
            werktag_von=time.fromisoformat(
                data.get(CONF_WERKTAG_VON, DEFAULT_WERKTAG_VON)
            ),
            werktag_bis=time.fromisoformat(
                data.get(CONF_WERKTAG_BIS, DEFAULT_WERKTAG_BIS)
            ),
            wochenende_aktiv=data.get(CONF_WOCHENENDE_AKTIV, True),
            wochenende_von=time.fromisoformat(
                data.get(CONF_WOCHENENDE_VON, DEFAULT_WOCHENENDE_VON)
            ),
            wochenende_bis=time.fromisoformat(
                data.get(CONF_WOCHENENDE_BIS, DEFAULT_WOCHENENDE_BIS)
            ),
        )

    def fenster(self, tag: date) -> tuple[time, time] | None:
        """Return the time window in which questions are allowed on a day."""
        if tag.weekday() >= 5:
            if not self.wochenende_aktiv:
                return None
            return self.wochenende_von, self.wochenende_bis
        return self.werktag_von, self.werktag_bis


@dataclass(slots=True, frozen=True)
class Fach:
    """A subject of a child, backed by a config subentry."""

    id: str
    kind_id: str
    name: str
    typ: AufgabenTyp = AufgabenTyp.VOKABEL
    sprachen: tuple[str, ...] = ()
    ki_entity: str | None = None

    @classmethod
    def from_subentry(cls, subentry: ConfigSubentry) -> Self:
        """Create a subject from its config subentry."""
        data = subentry.data
        return cls(
            id=subentry.subentry_id,
            kind_id=data[CONF_KIND_ID],
            name=data[CONF_NAME],
            typ=AufgabenTyp(data.get(CONF_TYP, AufgabenTyp.VOKABEL)),
            sprachen=tuple(data.get(CONF_SPRACHEN, ())),
            ki_entity=data.get(CONF_KI_ENTITY) or None,
        )

    @property
    def richtungen(self) -> tuple[str, ...]:
        """Return the directions in which the tasks are asked."""
        if self.typ is AufgabenTyp.MATHE:
            return (MATHE_RICHTUNG,)
        if self.typ is AufgabenTyp.SACH:
            return (SACH_RICHTUNG,)
        if len(self.sprachen) != 2:
            return ()
        erste, zweite = self.sprachen
        return richtung(erste, zweite), richtung(zweite, erste)


@dataclass(slots=True, frozen=True)
class Arbeit:
    """An exam or homework check, backed by a config subentry."""

    id: str
    fach_id: str
    datum: date
    art: ArbeitArt = ArbeitArt.ARBEIT
    thema: str = ""
    lektionen: tuple[str, ...] = ()
    abfragen_pro_tag: int = DEFAULT_ABFRAGEN_PRO_TAG
    start_tage_vorher: int = DEFAULT_START_TAGE_VORHER
    intensivierung: bool = True
    # Own time to answer, None uses the general setting
    antwortfrist_minuten: int | None = None
    # When a simulated exam is sent to the child on its own
    simulation_um: datetime | None = None
    simulation_anzahl: int = DEFAULT_SIMULATION_ANZAHL
    # Calendar event this exam was created from
    kalender_uid: str | None = None

    @classmethod
    def from_subentry(cls, subentry: ConfigSubentry) -> Self:
        """Create an exam from its config subentry."""
        data = subentry.data
        return cls(
            id=subentry.subentry_id,
            fach_id=data[CONF_FACH_ID],
            datum=date.fromisoformat(data[CONF_DATUM]),
            art=ArbeitArt(data.get(CONF_ART, ArbeitArt.ARBEIT)),
            thema=data.get(CONF_THEMA, ""),
            lektionen=tuple(data.get(CONF_LEKTIONEN, ())),
            abfragen_pro_tag=int(
                data.get(CONF_ABFRAGEN_PRO_TAG, DEFAULT_ABFRAGEN_PRO_TAG)
            ),
            start_tage_vorher=int(
                data.get(CONF_START_TAGE_VORHER, DEFAULT_START_TAGE_VORHER)
            ),
            intensivierung=data.get(CONF_INTENSIVIERUNG, True),
            antwortfrist_minuten=(
                int(frist) if (frist := data.get(CONF_ANTWORTFRIST)) else None
            ),
            simulation_um=_parse_dt(data.get(CONF_SIMULATION_UM)),
            simulation_anzahl=int(
                data.get(CONF_SIMULATION_ANZAHL) or DEFAULT_SIMULATION_ANZAHL
            ),
            kalender_uid=data.get(CONF_KALENDER_UID) or None,
        )


@dataclass(slots=True)
class OffeneFrage:
    """The single open question of a child."""

    fach_id: str
    aufgabe_id: str
    richtung: str
    gestellt_um: datetime
    timeout_um: datetime
    arbeit_id: str | None = None
    # Options of a choice question in the order they were shown
    optionen: list[str] | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Create an open question from stored data."""
        return cls(
            fach_id=data["fach_id"],
            aufgabe_id=data["aufgabe_id"],
            richtung=data["richtung"],
            gestellt_um=dt_util.parse_datetime(
                data["gestellt_um"], raise_on_error=True
            ),
            timeout_um=dt_util.parse_datetime(data["timeout_um"], raise_on_error=True),
            arbeit_id=data.get("arbeit_id"),
            optionen=(None if data.get("optionen") is None else list(data["optionen"])),
        )

    def to_dict(self) -> dict[str, Any]:
        """Return the storable representation."""
        return {
            "fach_id": self.fach_id,
            "aufgabe_id": self.aufgabe_id,
            "richtung": self.richtung,
            "gestellt_um": self.gestellt_um.isoformat(),
            "timeout_um": self.timeout_um.isoformat(),
            "arbeit_id": self.arbeit_id,
            "optionen": None if self.optionen is None else list(self.optionen),
        }


@dataclass(slots=True, frozen=True)
class RechenwegAngebot:
    """The offer to explain how a math task is solved."""

    fach_id: str
    aufgabe_id: str
    bis: datetime

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Create the offer from stored data."""
        return cls(
            fach_id=data["fach_id"],
            aufgabe_id=data["aufgabe_id"],
            bis=dt_util.parse_datetime(data["bis"], raise_on_error=True),
        )

    def to_dict(self) -> dict[str, Any]:
        """Return the storable representation."""
        return {
            "fach_id": self.fach_id,
            "aufgabe_id": self.aufgabe_id,
            "bis": self.bis.isoformat(),
        }


@dataclass(frozen=True, slots=True)
class AbfrageFilter:
    """Which tasks of a subject a series of questions is limited to."""

    lektionen: tuple[str, ...] = ()
    seite_von: int | None = None
    seite_bis: int | None = None
    # Share of wrong answers in percent a task has at least
    fehlerquote_ab: int | None = None

    @property
    def aktiv(self) -> bool:
        """Return whether the filter limits anything."""
        return self != AbfrageFilter()

    def passt(self, aufgabe: Aufgabe) -> bool:
        """Return whether a task belongs to the selection."""
        if self.lektionen and aufgabe.lektion not in self.lektionen:
            return False
        if self.seite_von is not None or self.seite_bis is not None:
            if aufgabe.seite is None:
                return False
            if self.seite_von is not None and aufgabe.seite < self.seite_von:
                return False
            if self.seite_bis is not None and aufgabe.seite > self.seite_bis:
                return False
        if self.fehlerquote_ab is not None:
            richtig = sum(s.richtig for s in aufgabe.statistik.values())
            falsch = sum(s.falsch for s in aufgabe.statistik.values())
            if richtig + falsch == 0:
                return False
            if 100 * falsch / (richtig + falsch) < self.fehlerquote_ab:
                return False
        return True

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Create the filter from stored data."""
        return cls(
            lektionen=tuple(data.get("lektionen", ())),
            seite_von=data.get("seite_von"),
            seite_bis=data.get("seite_bis"),
            fehlerquote_ab=data.get("fehlerquote_ab"),
        )

    def to_dict(self) -> dict[str, Any]:
        """Return the storable representation."""
        return {
            "lektionen": list(self.lektionen),
            "seite_von": self.seite_von,
            "seite_bis": self.seite_bis,
            "fehlerquote_ab": self.fehlerquote_ab,
        }


@dataclass(slots=True)
class WunschAngebot:
    """A wish to practise that waits for the amount of questions."""

    fach_id: str
    lektion: str | None
    bis: datetime

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Create the wish from stored data."""
        return cls(
            fach_id=data["fach_id"],
            lektion=data.get("lektion"),
            bis=dt_util.parse_datetime(data["bis"], raise_on_error=True),
        )

    def to_dict(self) -> dict[str, Any]:
        """Return the storable representation."""
        return {
            "fach_id": self.fach_id,
            "lektion": self.lektion,
            "bis": self.bis.isoformat(),
        }


@dataclass(slots=True)
class SimAufgabe:
    """A task of a simulated exam and how it was answered."""

    aufgabe_id: str
    richtung: str
    # Options of a choice question in the order they are shown
    optionen: list[str] | None = None
    # None until the task was answered
    ergebnis: Ergebnis | None = None
    erklaerung: str | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Create the task from stored data."""
        ergebnis = data.get("ergebnis")
        return cls(
            aufgabe_id=data["aufgabe_id"],
            richtung=data["richtung"],
            optionen=None if data.get("optionen") is None else list(data["optionen"]),
            ergebnis=None if ergebnis is None else Ergebnis(ergebnis),
            erklaerung=data.get("erklaerung"),
        )

    def to_dict(self) -> dict[str, Any]:
        """Return the storable representation."""
        return {
            "aufgabe_id": self.aufgabe_id,
            "richtung": self.richtung,
            "optionen": None if self.optionen is None else list(self.optionen),
            "ergebnis": None if self.ergebnis is None else self.ergebnis.value,
            "erklaerung": self.erklaerung,
        }


@dataclass(slots=True)
class Simulation:
    """A simulated exam that runs in the messenger of a child."""

    arbeit_id: str
    fach_id: str
    aufgaben: list[SimAufgabe]
    # Position of the task that waits for its answer
    index: int = 0
    timeout_um: datetime | None = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Create the simulation from stored data."""
        return cls(
            arbeit_id=data["arbeit_id"],
            fach_id=data["fach_id"],
            aufgaben=[SimAufgabe.from_dict(a) for a in data.get("aufgaben", [])],
            index=data.get("index", 0),
            timeout_um=_parse_dt(data.get("timeout_um")),
        )

    def to_dict(self) -> dict[str, Any]:
        """Return the storable representation."""
        return {
            "arbeit_id": self.arbeit_id,
            "fach_id": self.fach_id,
            "aufgaben": [a.to_dict() for a in self.aufgaben],
            "index": self.index,
            "timeout_um": _format_dt(self.timeout_um),
        }


@dataclass(slots=True)
class KindZustand:
    """Runtime state of a child that is persisted across restarts."""

    aktiv: bool = True
    pausiert_bis: datetime | None = None
    offene_frage: OffeneFrage | None = None
    letzte_frage_um: datetime | None = None
    # Extra questions the child asked for that are still to come
    zusatz_offen: int = 0
    # Offer to explain the solution of the last wrong math answer
    rechenweg_angebot: RechenwegAngebot | None = None
    # Simulated exam that is running in the messenger
    simulation: Simulation | None = None
    # Wish to practise that waits for the amount of questions
    wunsch_offen: WunschAngebot | None = None
    # Tasks the extra questions are limited to
    zusatz_filter: AbfrageFilter = AbfrageFilter()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        """Create the state from stored data."""
        offene = data.get("offene_frage")
        angebot = data.get("rechenweg_angebot")
        simulation = data.get("simulation")
        wunsch = data.get("wunsch_offen")
        return cls(
            aktiv=data.get("aktiv", True),
            pausiert_bis=_parse_dt(data.get("pausiert_bis")),
            offene_frage=None if offene is None else OffeneFrage.from_dict(offene),
            letzte_frage_um=_parse_dt(data.get("letzte_frage_um")),
            zusatz_offen=data.get("zusatz_offen", 0),
            rechenweg_angebot=(
                None if angebot is None else RechenwegAngebot.from_dict(angebot)
            ),
            simulation=(
                None if simulation is None else Simulation.from_dict(simulation)
            ),
            wunsch_offen=None if wunsch is None else WunschAngebot.from_dict(wunsch),
            zusatz_filter=AbfrageFilter.from_dict(data.get("zusatz_filter") or {}),
        )

    def to_dict(self) -> dict[str, Any]:
        """Return the storable representation."""
        return {
            "aktiv": self.aktiv,
            "pausiert_bis": _format_dt(self.pausiert_bis),
            "offene_frage": (
                None if self.offene_frage is None else self.offene_frage.to_dict()
            ),
            "letzte_frage_um": _format_dt(self.letzte_frage_um),
            "zusatz_offen": self.zusatz_offen,
            "rechenweg_angebot": (
                None
                if self.rechenweg_angebot is None
                else self.rechenweg_angebot.to_dict()
            ),
            "simulation": (
                None if self.simulation is None else self.simulation.to_dict()
            ),
            "wunsch_offen": (
                None if self.wunsch_offen is None else self.wunsch_offen.to_dict()
            ),
            "zusatz_filter": self.zusatz_filter.to_dict(),
        }

    def ist_pausiert(self, jetzt: datetime) -> bool:
        """Return whether asking is paused right now."""
        if not self.aktiv:
            return True
        return self.pausiert_bis is not None and self.pausiert_bis > jetzt
