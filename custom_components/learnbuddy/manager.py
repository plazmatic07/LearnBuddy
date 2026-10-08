"""Central orchestration: asking questions, handling answers and timeouts."""

from __future__ import annotations

import asyncio
from collections import defaultdict
from dataclasses import dataclass, field, replace
from datetime import datetime, timedelta
from enum import StrEnum
from random import Random
import time
from types import MappingProxyType
from typing import TYPE_CHECKING, Any

from homeassistant.config_entries import ConfigSubentry
from homeassistant.core import CALLBACK_TYPE, CoreState, HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import (
    async_call_later,
    async_track_point_in_time,
    async_track_time_change,
)
from homeassistant.util import dt as dt_util
import voluptuous as vol

from .ai import KiBewerter
from .bilder import BildAblage
from .blatt import Art, BlattAufgabe, BlattTexte, zeichne
from .const import (
    CONF_ABSENDER_KENNUNG,
    CONF_AUTO_FREIGABE,
    CONF_FACH_ID,
    CONF_GEAENDERT,
    CONF_KI_ENTITY,
    CONF_NAME,
    CONF_SPRACHE,
    CONF_TIMEOUT_MINUTEN,
    CONF_VERLAUF,
    CONF_WUNSCH_KI,
    DEFAULT_TIMEOUT_MINUTEN,
    DOMAIN,
    DOPPELT_SEKUNDEN,
    EVENT_ANSWER_EVALUATED,
    EVENT_QUESTION_SENT,
    EVENT_SIMULATION_FINISHED,
    KALENDER_TAGE_VORAUS,
    LOGGER,
    MAX_ZUSATZAUFGABEN,
    SENDE_WIEDERHOLUNGEN,
    SICHER_AB_BOX,
    SPRACHE_AUTO,
    SUBENTRY_ARBEIT,
    SUBENTRY_FACH,
    SUBENTRY_KIND,
    UNBEKANNTE_ABSENDER_MAX,
    UNBEKANNTE_ABSENDER_STUNDEN,
    WUNSCH_FRIST,
    signal_kind_update,
)
from .evaluation import bewerte_vokabel
from .kalender import Termin, lies_termine
from .mathe import bewerte_mathe
from .messaging import Messenger
from .models import (
    Arbeit,
    Aufgabe,
    AufgabenTyp,
    Ergebnis,
    Fach,
    Kind,
    KindZustand,
    MatheAufgabe,
    OffeneFrage,
    RechenwegAngebot,
    SachAufgabe,
    SachForm,
    SimAufgabe,
    Simulation,
    Vokabel,
    WunschAngebot,
    richtung_teile,
)
from .sach import bewerte_auswahl, formatiere, gleiche_antwort, mische
from .scheduler import (
    abfragen_am_tag,
    antwortfrist,
    aufgaben_der_arbeit,
    naechste_arbeit,
    naechste_box,
    naechster_zeitpunkt,
    verdichtung,
    waehle_arbeit,
    waehle_aufgabe,
)
from .simulation import Auswertung, punkte_text, waehle, werte_aus
from .storage import ConfigStore, TaskStore, VerlaufStore, async_remove_task_file
from .texte import sprachname, text, waehle_sprache
from .verlauf import SimErgebnis
from .verwaltung import (
    Verwaltung,
    aufgabe_aus_zeile,
    aufgabe_schluessel,
    parse_import,
)
from .wunsch import (
    Uebungswunsch,
    WunschFach,
    erkenne_anzahl,
    erkenne_ja,
    erkenne_nein,
    erkenne_uebungswunsch,
    erkenne_zusatzwunsch,
)

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path

    from homeassistant.config_entries import ConfigEntry

KEINE_OFFENE_FRAGE = "keine_offene_frage"
ZUSATZAUFGABEN = "zusatzaufgaben"
RECHENWEG = "rechenweg"
WUNSCH_NACHFRAGE = "wunsch_nachfrage"
WUNSCH_UNKLAR = "wunsch_unklar"
KEINE_AUFGABEN = "keine_aufgaben"
SIMULATION = "simulation"
# A planned simulation that was missed is still sent within this time
SIMULATION_NACHHOLEN = timedelta(hours=6)
KI_PRUEFUNG_NACH_START = timedelta(minutes=5)
# Calendar integrations need a moment after a start as well
KALENDER_NACH_START = timedelta(minutes=2)
KALENDER_NACH_RELOAD = timedelta(seconds=5)


@dataclass(slots=True)
class KalenderStand:
    """What was last read from the exam calendar of a child."""

    termine: list[Termin] = field(default_factory=list)
    geprueft_um: datetime | None = None
    # The last attempt to read the calendar failed
    fehler: bool = False


class FrageStatus(StrEnum):
    """Outcome of an attempt to ask a question."""

    GESENDET = "gesendet"
    KEINE_AUFGABEN = "keine_aufgaben"
    SENDEFEHLER = "sendefehler"


def normalisiere_absender(wert: str) -> str:
    """Normalize a phone number or chat ID for comparison."""
    kompakt = "".join(wert.split()).casefold()
    ziffern = "".join(z for z in kompakt if z.isdigit())
    # Phone numbers are compared by their digits only (+49 ..., 0049 ...)
    if ziffern and all(z.isdigit() or z in "+-()/." for z in kompakt):
        return ziffern.removeprefix("00")
    return kompakt


class LearnBuddyManager:
    """Hold the runtime data of the integration and drive the question cycle."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the manager."""
        self.hass = hass
        self.entry = entry
        self.config_store = ConfigStore(hass)
        self.verlauf_store = VerlaufStore(hass)
        # Whether answers are logged per day; what was logged stays either way
        self.verlauf_aktiv: bool = entry.options.get(CONF_VERLAUF, True)
        self.task_stores: dict[str, TaskStore] = {}
        self.bilder = BildAblage(hass)
        self.messenger = Messenger(hass, self.bilder)
        self.ki = KiBewerter(hass)
        self.verwaltung = Verwaltung(self)
        self.kinder: dict[str, Kind] = {}
        self.faecher: dict[str, Fach] = {}
        self.arbeiten: dict[str, Arbeit] = {}
        self.naechste_abfrage: dict[str, datetime | None] = {}
        self._timer: dict[str, CALLBACK_TYPE] = {}
        self._sendeversuche: dict[str, int] = {}
        self._wiederholung_um: dict[str, datetime] = {}
        self._letzte_aufgabe: dict[str, str] = {}
        self._letztes_fach: dict[str, str] = {}
        self._tagesuhr: CALLBACK_TYPE | None = None
        self._ki_pruefung: CALLBACK_TYPE | None = None
        self._basis: tuple[dict[str, Any], dict[str, Any]] = ({}, {})
        # Set while the manager itself changes a subentry it applies in place
        self._ohne_reload = False
        self._sperren: defaultdict[str, asyncio.Lock] = defaultdict(asyncio.Lock)
        # Last incoming answer per child: text, monotonic time, path it came on
        self._letzte_antwort: dict[str, tuple[str, float, str]] = {}
        # Senders nobody is assigned to, kept in memory only: source and time
        self._unbekannte_absender: dict[str, tuple[str, datetime]] = {}
        # Exam dates read from calendars, in memory only
        self._kalender: dict[str, KalenderStand] = {}
        self._kalender_uhren: list[CALLBACK_TYPE] = []
        self._rng = Random()  # noqa: S311 - not used for cryptography
        # Timers of planned simulations, per exam
        self._sim_timer: dict[str, CALLBACK_TYPE] = {}

    # ------------------------------------------------------------------
    # Setup and teardown
    # ------------------------------------------------------------------

    async def async_setup(self) -> None:
        """Read the subentries and load all stores."""
        for subentry in self.entry.subentries.values():
            if subentry.subentry_type == SUBENTRY_KIND:
                self.kinder[subentry.subentry_id] = Kind.from_subentry(subentry)
            elif subentry.subentry_type == SUBENTRY_FACH:
                self.faecher[subentry.subentry_id] = Fach.from_subentry(subentry)
            elif subentry.subentry_type == SUBENTRY_ARBEIT:
                self.arbeiten[subentry.subentry_id] = Arbeit.from_subentry(subentry)

        self._basis = self._signatur()

        await self.config_store.async_load()
        geaendert = self.config_store.bereinige(self.kinder, self.arbeiten)
        await self.verlauf_store.async_load()
        if self.verlauf_store.bereinige(
            {
                kind_id: [f.id for f in self.faecher_von(kind_id)]
                for kind_id in self.kinder
            },
            dt_util.now().date(),
        ):
            self.verlauf_store.async_schedule_save()

        for fach in self.faecher.values():
            store = TaskStore(self.hass, fach.kind_id, fach.id)
            await store.async_load()
            self.task_stores[fach.id] = store

        await self.bilder.async_load()
        await self.bilder.async_raeume_auf(self.verwendete_bilder())

        aktuelle_dateien = {store.key for store in self.task_stores.values()}
        for key in self.config_store.aufgaben_dateien - aktuelle_dateien:
            await async_remove_task_file(self.hass, key)
        if self.config_store.aufgaben_dateien != aktuelle_dateien:
            self.config_store.aufgaben_dateien = aktuelle_dateien
            geaendert = True

        for kind_id in self.kinder:
            zustand = self.config_store.zustand(kind_id)
            frage = zustand.offene_frage
            if frage is not None and self._aufgabe(frage) is None:
                zustand.offene_frage = None
                geaendert = True
            simulation = zustand.simulation
            if simulation is not None and (
                simulation.arbeit_id not in self.arbeiten
                or simulation.fach_id not in self.task_stores
            ):
                zustand.simulation = None
                geaendert = True
        if geaendert:
            await self.config_store.async_save()

    def _signatur(self) -> tuple[dict[str, Any], dict[str, Any]]:
        """Return everything of the entry that requires a reload when it changes."""
        return (
            dict(self.entry.options),
            {
                subentry.subentry_id: (dict(subentry.data), subentry.title)
                for subentry in self.entry.subentries.values()
                if subentry.subentry_type != SUBENTRY_ARBEIT
            },
        )

    @callback
    def async_nur_arbeiten_geaendert(self) -> bool:
        """Return whether the entry only differs in its exams since setup."""
        return self._ohne_reload or self._signatur() == self._basis

    @callback
    def async_arbeiten_aktualisieren(self) -> None:
        """Apply added, changed or removed exams without reloading the entry."""
        self.arbeiten = {
            subentry.subentry_id: Arbeit.from_subentry(subentry)
            for subentry in self.entry.subentries.values()
            if subentry.subentry_type == SUBENTRY_ARBEIT
            and subentry.data[CONF_FACH_ID] in self.faecher
        }
        if self.config_store.bereinige(self.kinder, self.arbeiten):
            self.config_store.async_schedule_save()
        self._plane_simulationen()
        for kind_id in self.kinder:
            zustand = self.zustand(kind_id)
            simulation = zustand.simulation
            if simulation is not None and simulation.arbeit_id not in self.arbeiten:
                # The exam that was simulated is gone
                zustand.simulation = None
                self.config_store.async_schedule_save()
                self._plane(kind_id)
            self._benachrichtige(kind_id)
            if zustand.offene_frage is None and zustand.simulation is None:
                self._plane(kind_id)

    @callback
    def async_start(self) -> None:
        """Start the timers of all children."""
        if self.hass.is_stopping:
            # A reload that finishes during shutdown must not leave timers
            return
        for kind_id in self.kinder:
            self._plane(kind_id)
        self._plane_simulationen()
        # AI integrations need a moment after a start before their entity exists
        self._ki_pruefung = async_call_later(
            self.hass, KI_PRUEFUNG_NACH_START, self.async_pruefe_ki
        )
        self._tagesuhr = async_track_time_change(
            self.hass, self._neuer_tag, hour=0, minute=0, second=10
        )
        self._starte_kalender()
        self._verlauf_lernstand()

    @callback
    def _neuer_tag(self, _jetzt: datetime) -> None:
        """Refresh date dependent data once a day."""
        self.async_pruefe_ki()
        self._verlauf_lernstand()
        for kind_id in self.kinder:
            self._benachrichtige(kind_id)
            if kind_id not in self._timer:
                self._plane(kind_id)

    @callback
    def async_stop(self) -> None:
        """Cancel all timers and pending retries."""
        for abbrechen in (*self._timer.values(), *self._sim_timer.values()):
            abbrechen()
        self._timer.clear()
        self._sim_timer.clear()
        if self._tagesuhr is not None:
            self._tagesuhr()
            self._tagesuhr = None
        if self._ki_pruefung is not None:
            self._ki_pruefung()
            self._ki_pruefung = None
        for abmelden in self._kalender_uhren:
            abmelden()
        self._kalender_uhren.clear()
        self.messenger.async_cancel()

    async def async_flush(self) -> None:
        """Write all stores to disk immediately."""
        await self.config_store.async_save()
        if self.verlauf_aktiv:
            await self.verlauf_store.async_save()
        for store in self.task_stores.values():
            await store.async_save()

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    @property
    def sprache(self) -> str:
        """Return the language of the messages."""
        sprache: str = self.entry.options.get(CONF_SPRACHE, SPRACHE_AUTO)
        if sprache == SPRACHE_AUTO:
            return self.hass.config.language
        return sprache

    @property
    def timeout(self) -> timedelta:
        """Return the time after which an open question expires."""
        return timedelta(
            minutes=int(
                self.entry.options.get(CONF_TIMEOUT_MINUTEN, DEFAULT_TIMEOUT_MINUTEN)
            )
        )

    def _frist(
        self, kind_id: str, aufgabe: Aufgabe, gewaehlt: Arbeit | None = None
    ) -> timedelta:
        """Return the time to answer a task.

        Exams that are running today and contain the task may shorten or
        extend the general setting, as may the exam the task was picked for.
        """
        heute = dt_util.now().date()
        arbeiten = [
            a
            for a in self.arbeiten_von(kind_id)
            if a.antwortfrist_minuten
            and (a is gewaehlt or abfragen_am_tag(a, heute) > 0)
            and self.task_stores[a.fach_id].aufgaben.get(aufgabe.id) is aufgabe
            and aufgaben_der_arbeit(
                a, [aufgabe], self.config_store.arbeit_aufgaben.get(a.id, ())
            )
        ]
        minuten = antwortfrist(arbeiten, int(self.timeout.total_seconds() // 60))
        return timedelta(minutes=minuten)

    def _ki_bereit(self, fach: Fach) -> bool:
        """Return whether the AI of a subject could judge an answer right now."""
        ki_entity = self.ki_entity(fach)
        return ki_entity is not None and self.ki.verfuegbar(ki_entity)

    @callback
    def async_pruefe_ki(self, _jetzt: datetime | None = None) -> None:
        """Check that the selected AI entities still exist."""
        self.ki.pruefe_entitaeten(
            {e for fach in self.faecher.values() if (e := self.ki_entity(fach))}
        )

    def ki_entity(self, fach: Fach) -> str | None:
        """Return the AI task entity for a subject, if the user selected one."""
        return fach.ki_entity or self.entry.options.get(CONF_KI_ENTITY) or None

    @property
    def wunsch_ki(self) -> bool:
        """Return whether the AI may interpret what a child asks to practise."""
        return bool(self.entry.options.get(CONF_WUNSCH_KI, True))

    @property
    def auto_freigabe(self) -> bool:
        """Return whether generated tasks are active without approval."""
        return bool(self.entry.options.get(CONF_AUTO_FREIGABE, False))

    def verwendete_bilder(self) -> set[str]:
        """Return the ids of all images that tasks refer to."""
        bilder: set[str] = set()
        for store in self.task_stores.values():
            for aufgabe in store.aufgaben.values():
                if isinstance(aufgabe, MatheAufgabe) and aufgabe.bild:
                    bilder.add(aufgabe.bild)
                elif isinstance(aufgabe, SachAufgabe) and aufgabe.quelle_bild:
                    bilder.add(aufgabe.quelle_bild)
        return bilder

    def zustand(self, kind_id: str) -> KindZustand:
        """Return the runtime state of a child."""
        return self.config_store.zustand(kind_id)

    def faecher_von(self, kind_id: str) -> list[Fach]:
        """Return the subjects of a child."""
        return [f for f in self.faecher.values() if f.kind_id == kind_id]

    def arbeiten_von(self, kind_id: str) -> list[Arbeit]:
        """Return the exams of a child."""
        fach_ids = {f.id for f in self.faecher_von(kind_id)}
        return [a for a in self.arbeiten.values() if a.fach_id in fach_ids]

    def naechste_arbeit(self, kind_id: str) -> Arbeit | None:
        """Return the next upcoming exam of a child."""
        return naechste_arbeit(self.arbeiten_von(kind_id), dt_util.now().date())

    def trefferquote(self, kind_id: str) -> float | None:
        """Return the share of correct answers of a child in percent."""
        richtig = falsch = 0
        for fach in self.faecher_von(kind_id):
            for aufgabe in self.task_stores[fach.id].aufgaben.values():
                for stat in aufgabe.statistik.values():
                    richtig += stat.richtig
                    falsch += stat.falsch
        if richtig + falsch == 0:
            return None
        return 100 * richtig / (richtig + falsch)

    def lektionen(self, fach_id: str) -> list[str]:
        """Return the lessons that exist in the tasks of a subject."""
        store = self.task_stores.get(fach_id)
        return [] if store is None else store.lektionen

    def kind_per_absender(self, absender: str) -> Kind | None:
        """Find a child by the sender of an incoming message."""
        gesucht = normalisiere_absender(absender)
        if not gesucht:
            return None
        for kind in self.kinder.values():
            if (
                kind.absender_kennung
                and normalisiere_absender(kind.absender_kennung) == gesucht
            ):
                return kind
        return None

    # ------------------------------------------------------------------
    # Exam calendar
    # ------------------------------------------------------------------

    @callback
    def _starte_kalender(self) -> None:
        """Read the exam calendars once a day and shortly after the start."""
        mit_kalender = [k for k in self.kinder.values() if k.kalender_entity]
        for kind in mit_kalender:

            @callback
            def _uhr(_jetzt: datetime, kind_id: str = kind.id) -> None:
                self.hass.async_create_task(
                    self.async_kalender_pruefen(kind_id), "learnbuddy_kalender"
                )

            self._kalender_uhren.append(
                async_track_time_change(
                    self.hass,
                    _uhr,
                    hour=kind.kalender_um.hour,
                    minute=kind.kalender_um.minute,
                    second=0,
                )
            )
        if not mit_kalender:
            return

        async def _nach_start(_jetzt: datetime) -> None:
            for kind in mit_kalender:
                await self.async_kalender_pruefen(kind.id)

        # After a restart the calendar integration needs a moment; when only
        # the settings were saved, the dates should show up right away
        laeuft = self.hass.state is CoreState.running
        warten = KALENDER_NACH_RELOAD if laeuft else KALENDER_NACH_START
        self._kalender_uhren.append(async_call_later(self.hass, warten, _nach_start))

    def kalender_stand(self, kind_id: str) -> KalenderStand | None:
        """Return what was read from the calendar, None if the child has none."""
        if not self.kinder[kind_id].kalender_entity:
            return None
        return self._kalender.setdefault(kind_id, KalenderStand())

    async def async_kalender_pruefen(self, kind_id: str) -> bool:
        """Read the upcoming exam dates of a child from its calendar.

        The events are fetched with the action of the calendar integration.
        If that fails, the dates read last stay. Nothing is logged: the texts
        of the events are private.
        """
        kind = self.kinder.get(kind_id)
        if kind is None or not kind.kalender_entity:
            return False
        stand = self._kalender.setdefault(kind_id, KalenderStand())
        heute = dt_util.start_of_local_day()
        stand.geprueft_um = dt_util.utcnow()
        try:
            antwort = await self.hass.services.async_call(
                "calendar",
                "get_events",
                {
                    "entity_id": kind.kalender_entity,
                    "start_date_time": heute,
                    "end_date_time": heute + timedelta(days=KALENDER_TAGE_VORAUS),
                },
                blocking=True,
                return_response=True,
            )
        except HomeAssistantError, vol.Invalid:
            stand.fehler = True
            return False
        eintrag = (antwort or {}).get(kind.kalender_entity)
        rohe = eintrag.get("events") if isinstance(eintrag, dict) else None
        if not isinstance(rohe, list):
            stand.fehler = True
            return False
        stand.termine = lies_termine(
            [roh for roh in rohe if isinstance(roh, dict)],
            dt_util.get_default_time_zone(),
            heute.date(),
        )
        stand.fehler = False
        # Ignored dates of the past are of no use any more
        ignoriert = self.config_store.kalender_ignoriert.get(kind_id, {})
        vorbei = [
            uid for uid, tag in ignoriert.items() if tag < heute.date().isoformat()
        ]
        for uid in vorbei:
            del ignoriert[uid]
        if vorbei:
            self.config_store.async_schedule_save()
        return True

    async def async_fach_anlegen(self, kind_id: str, daten: dict[str, Any]) -> str:
        """Add a subject without reloading the entry, so the panel stays open."""
        kind_subentry = self.entry.subentries[kind_id]
        neu = ConfigSubentry(
            data=MappingProxyType(daten),
            subentry_type=SUBENTRY_FACH,
            title=f"{daten[CONF_NAME]} ({kind_subentry.title})",
            unique_id=None,
        )
        store = TaskStore(self.hass, kind_id, neu.subentry_id)
        await store.async_load()
        # The update listener may run during the call or later; in both cases
        # it must not see a difference that needs a reload
        self._ohne_reload = True
        try:
            self.hass.config_entries.async_add_subentry(self.entry, neu)
        finally:
            self._ohne_reload = False
        self.faecher[neu.subentry_id] = Fach.from_subentry(neu)
        self.task_stores[neu.subentry_id] = store
        self.config_store.aufgaben_dateien.add(store.key)
        self.config_store.async_schedule_save()
        self._basis = self._signatur()
        self._benachrichtige(kind_id)
        return neu.subentry_id

    @callback
    def merke_unbekannten_absender(self, absender: str, quelle: str) -> None:
        """Remember a sender no child is assigned to, for the hint in the panel.

        Only while a child waits for an answer, so that unrelated messages to
        the same messenger account are not collected. Nothing is written to
        disk or to the log.
        """
        kennung = normalisiere_absender(absender)
        if not kennung or not any(
            zustand.offene_frage is not None or zustand.simulation is not None
            for zustand in map(self.zustand, self.kinder)
        ):
            return
        self._unbekannte_absender.pop(kennung, None)
        self._unbekannte_absender[kennung] = (quelle, dt_util.utcnow())
        while len(self._unbekannte_absender) > UNBEKANNTE_ABSENDER_MAX:
            del self._unbekannte_absender[next(iter(self._unbekannte_absender))]

    def unbekannte_absender(self) -> list[dict[str, str]]:
        """Return the recently seen unknown senders, newest first."""
        grenze = dt_util.utcnow() - timedelta(hours=UNBEKANNTE_ABSENDER_STUNDEN)
        self._unbekannte_absender = {
            kennung: wert
            for kennung, wert in self._unbekannte_absender.items()
            if wert[1] >= grenze
        }
        return [
            {"kennung": kennung, "quelle": quelle, "zuletzt": zeit.isoformat()}
            for kennung, (quelle, zeit) in reversed(self._unbekannte_absender.items())
        ]

    @callback
    def vergiss_absender(self, absender: str) -> None:
        """Drop an unknown sender from the hint."""
        self._unbekannte_absender.pop(normalisiere_absender(absender), None)

    @callback
    def async_setze_absender(self, kind_id: str, absender: str) -> None:
        """Set the sender ID of a child without reloading the entry."""
        subentry = self.entry.subentries[kind_id]
        # The update listener may run during the call or later; in both cases
        # it must not see a difference that needs a reload
        self._ohne_reload = True
        try:
            self.hass.config_entries.async_update_subentry(
                self.entry,
                subentry,
                data={
                    **subentry.data,
                    CONF_ABSENDER_KENNUNG: absender,
                    CONF_GEAENDERT: dt_util.utcnow().isoformat(),
                },
            )
        finally:
            self._ohne_reload = False
        self.kinder[kind_id] = Kind.from_subentry(self.entry.subentries[kind_id])
        self._basis = self._signatur()
        self.vergiss_absender(absender)

    def antwort_doppelt(self, kind_id: str, antwort: str, quelle: str) -> bool:
        """Tell whether the same message just arrived on the other path.

        The built-in listener and an automation calling the action may both
        deliver one message; only the first one counts.
        """
        jetzt = time.monotonic()
        letzte = self._letzte_antwort.get(kind_id)
        if (
            letzte is not None
            and letzte[0] == antwort
            and letzte[2] != quelle
            and jetzt - letzte[1] < DOPPELT_SEKUNDEN
        ):
            return True
        self._letzte_antwort[kind_id] = (antwort, jetzt, quelle)
        return False

    def fach_per_name(self, kind_id: str, name: str) -> Fach | None:
        """Find a subject of a child by its name."""
        for fach in self.faecher_von(kind_id):
            if fach.name.casefold() == name.strip().casefold():
                return fach
        return None

    def _aufgabe(self, frage: OffeneFrage) -> Aufgabe | None:
        store = self.task_stores.get(frage.fach_id)
        return None if store is None else store.aufgaben.get(frage.aufgabe_id)

    # ------------------------------------------------------------------
    # Scheduling
    # ------------------------------------------------------------------

    @callback
    def _plane(self, kind_id: str) -> None:
        """(Re)start the timer of a child for its next question or timeout."""
        if abbrechen := self._timer.pop(kind_id, None):
            abbrechen()
        self.naechste_abfrage[kind_id] = None
        if self.hass.is_stopping:
            return
        zustand = self.zustand(kind_id)
        jetzt = dt_util.now()

        simulation = zustand.simulation
        if simulation is not None:
            # Nothing else is asked while an exam is simulated
            if simulation.timeout_um is not None:

                async def _sim_timeout(_jetzt: datetime) -> None:
                    self._timer.pop(kind_id, None)
                    await self.async_simulation_timeout(kind_id)

                self._timer[kind_id] = async_track_point_in_time(
                    self.hass, _sim_timeout, simulation.timeout_um
                )
            return

        if zustand.offene_frage is not None:

            async def _timeout(_jetzt: datetime) -> None:
                self._timer.pop(kind_id, None)
                await self.async_timeout(kind_id)

            self._timer[kind_id] = async_track_point_in_time(
                self.hass, _timeout, zustand.offene_frage.timeout_um
            )
            return

        if not zustand.aktiv:
            return

        zeitpunkt = self._wiederholung_um.get(kind_id) or naechster_zeitpunkt(
            jetzt,
            self.kinder[kind_id],
            self.arbeiten_von(kind_id),
            letzte_frage=zustand.letzte_frage_um,
            fruehestens=zustand.pausiert_bis,
        )
        self.naechste_abfrage[kind_id] = zeitpunkt
        if zeitpunkt is None:
            return

        async def _frage(_jetzt: datetime) -> None:
            self._timer.pop(kind_id, None)
            await self._async_geplante_frage(kind_id)

        self._timer[kind_id] = async_track_point_in_time(self.hass, _frage, zeitpunkt)

    async def _async_geplante_frage(self, kind_id: str) -> None:
        """Ask a scheduled question and plan the next step."""
        async with self._sperren[kind_id]:
            self._wiederholung_um.pop(kind_id, None)
            zustand = self.zustand(kind_id)
            if zustand.rechenweg_angebot is not None:
                # The offer was not taken; a series waiting for it is over
                zustand.rechenweg_angebot = None
                zustand.zusatz_offen = 0
            if zustand.offene_frage is None and not zustand.ist_pausiert(dt_util.now()):
                status = await self._async_frage(kind_id, manuell=False)
                versuch = self._sendeversuche.get(kind_id, 0)
                if status is FrageStatus.SENDEFEHLER and versuch < len(
                    SENDE_WIEDERHOLUNGEN
                ):
                    self._sendeversuche[kind_id] = versuch + 1
                    self._wiederholung_um[kind_id] = (
                        dt_util.now() + SENDE_WIEDERHOLUNGEN[versuch]
                    )
                else:
                    self._sendeversuche.pop(kind_id, None)
                    if status is not FrageStatus.GESENDET:
                        # Skip this slot, otherwise it would be picked again
                        zustand.letzte_frage_um = dt_util.utcnow()
                        self.config_store.async_schedule_save()
            self._plane(kind_id)

    # ------------------------------------------------------------------
    # Asking
    # ------------------------------------------------------------------

    def _waehle(
        self,
        kind_id: str,
        *,
        manuell: bool,
        fach_id: str | None = None,
        lektion: str | None = None,
    ) -> tuple[Fach, Aufgabe, str, Arbeit | None] | None:
        """Pick the subject, task and direction of the next question.

        A manual request may be limited to one subject or to one of its
        lessons.
        """
        if fach_id is not None and lektion is not None:
            fach = self.faecher[fach_id]
            auswahl = waehle_aufgabe(
                self._zustellbar(
                    kind_id,
                    [
                        a
                        for a in self.task_stores[fach.id].aufgaben.values()
                        if a.lektion == lektion
                    ],
                ),
                fach.richtungen,
                self._rng,
                jetzt=dt_util.utcnow(),
                vermeide=self._letzte_aufgabe.get(kind_id),
            )
            return None if auswahl is None else (fach, auswahl[0], auswahl[1], None)
        heute = dt_util.now().date()
        arbeiten = [
            a
            for a in self.arbeiten_von(kind_id)
            if fach_id is None or a.fach_id == fach_id
        ]
        vermeide = self._letzte_aufgabe.get(kind_id)

        arbeit = waehle_arbeit(arbeiten, heute, self._rng)
        if arbeit is None and manuell:
            arbeit = naechste_arbeit(arbeiten, heute)
        if arbeit is not None:
            fach = self.faecher[arbeit.fach_id]
            aufgaben = aufgaben_der_arbeit(
                arbeit,
                self.task_stores[fach.id].aufgaben.values(),
                self.config_store.arbeit_aufgaben.get(arbeit.id, ()),
            )
            auswahl = waehle_aufgabe(
                self._zustellbar(kind_id, aufgaben),
                fach.richtungen,
                self._rng,
                jetzt=dt_util.utcnow(),
                faktor=verdichtung(arbeit, heute),
                vermeide=vermeide,
            )
            if auswahl is not None:
                return fach, auswahl[0], auswahl[1], arbeit
        if not manuell:
            return None

        # Manual request without a usable exam: ask anything the child has
        faecher = [
            f for f in self.faecher_von(kind_id) if fach_id is None or f.id == fach_id
        ]
        self._rng.shuffle(faecher)
        for fach in faecher:
            auswahl = waehle_aufgabe(
                self._zustellbar(kind_id, self.task_stores[fach.id].aufgaben.values()),
                fach.richtungen,
                self._rng,
                jetzt=dt_util.utcnow(),
                vermeide=vermeide,
            )
            if auswahl is not None:
                return fach, auswahl[0], auswahl[1], None
        return None

    def _zustellbar(self, kind_id: str, aufgaben: Iterable[Aufgabe]) -> list[Aufgabe]:
        """Leave out tasks that cannot be asked or judged right now.

        Tasks with an image need a messenger that can send images, free
        answers to knowledge questions need an AI that judges them.
        """
        bilder = self.messenger.kann_bilder(self.kinder[kind_id])
        return [
            a
            for a in aufgaben
            if (bilder or not (isinstance(a, MatheAufgabe) and a.bild))
            and not (
                isinstance(a, SachAufgabe)
                and a.form is SachForm.KURZ
                and not self._ki_bereit(self.faecher[a.fach_id])
            )
        ]

    async def async_frage_stellen(
        self, kind_id: str, fach_id: str | None = None
    ) -> None:
        """Ask a question right now (manual request), optionally of one subject.

        Raises a translated error if there is no task or sending fails.
        """
        async with self._sperren[kind_id]:
            if self.zustand(kind_id).simulation is not None:
                raise ServiceValidationError(
                    translation_domain=DOMAIN, translation_key="simulation_laeuft"
                )
            await self._async_frage(kind_id, manuell=True, fach_id=fach_id)
            self._plane(kind_id)

    def _frage_text(
        self,
        kind: Kind,
        fach: Fach,
        aufgabe: Aufgabe,
        richtung_key: str,
        *,
        kurz: bool,
        optionen: list[str] | None = None,
    ) -> str:
        """Return the message that asks a task.

        Follow-up questions of a running conversation need no greeting.
        """
        if isinstance(aufgabe, SachAufgabe):
            nachricht = text(
                self.sprache,
                "frage_sach_kurz" if kurz else "frage_sach",
                name=kind.name,
                fach=fach.name,
                frage=aufgabe.frage,
            )
            if optionen:
                nachricht += text(
                    self.sprache, "frage_optionen", optionen=formatiere(optionen)
                )
            return nachricht
        if isinstance(aufgabe, MatheAufgabe):
            return text(
                self.sprache,
                "frage_mathe_kurz" if kurz else "frage_mathe",
                name=kind.name,
                fach=fach.name,
                aufgabe=aufgabe.aufgabe,
            )
        von, nach = richtung_teile(richtung_key)
        return text(
            self.sprache,
            "frage_kurz" if kurz else "frage",
            name=kind.name,
            fach=fach.name,
            wort=aufgabe.frage[von],
            zielsprache=sprachname(self.sprache, nach),
        )

    async def _async_frage(
        self,
        kind_id: str,
        *,
        manuell: bool,
        fach_id: str | None = None,
        lektion: str | None = None,
        kurz: bool = False,
    ) -> FrageStatus:
        kind = self.kinder[kind_id]
        zustand = self.zustand(kind_id)
        auswahl = self._waehle(
            kind_id, manuell=manuell, fach_id=fach_id, lektion=lektion
        )
        if auswahl is None:
            if manuell:
                raise ServiceValidationError(
                    translation_domain=DOMAIN, translation_key="keine_aufgaben"
                )
            LOGGER.debug("No task available for scheduled question of %s", kind_id)
            return FrageStatus.KEINE_AUFGABEN
        fach, aufgabe, richtung_key, arbeit = auswahl
        optionen = (
            mische(aufgabe.antwort, aufgabe.falsche_optionen, self._rng)
            if isinstance(aufgabe, SachAufgabe) and aufgabe.form is SachForm.AUSWAHL
            else None
        )
        nachricht = self._frage_text(
            kind, fach, aufgabe, richtung_key, kurz=kurz, optionen=optionen
        )

        bild = aufgabe.bild if isinstance(aufgabe, MatheAufgabe) else None
        if manuell:
            await self.messenger.async_send_or_raise(kind, nachricht, bild=bild)
        elif not await self.messenger.async_send(kind, nachricht, bild=bild):
            return FrageStatus.SENDEFEHLER

        if zustand.offene_frage is not None:
            # A manual request replaces the open question
            self._feuere_bewertung(
                kind_id, zustand.offene_frage, Ergebnis.UNBEANTWORTET
            )

        jetzt = dt_util.utcnow()
        stat = aufgabe.statistik_fuer(richtung_key)
        stat.zuletzt_gefragt = jetzt
        stat.gefragt += 1
        zustand.offene_frage = OffeneFrage(
            fach_id=fach.id,
            aufgabe_id=aufgabe.id,
            richtung=richtung_key,
            gestellt_um=jetzt,
            timeout_um=jetzt + self._frist(kind_id, aufgabe, arbeit),
            arbeit_id=None if arbeit is None else arbeit.id,
            optionen=optionen,
        )
        zustand.letzte_frage_um = jetzt
        # A new question ends the offer to explain the previous one
        zustand.rechenweg_angebot = None
        zustand.wunsch_offen = None
        if not kurz:
            # Only the questions a child asked for stay within a lesson
            zustand.zusatz_lektion = None
        self._letzte_aufgabe[kind_id] = aufgabe.id
        self._letztes_fach[kind_id] = fach.id
        self.task_stores[fach.id].async_schedule_save()
        self.config_store.async_schedule_save()
        if self.verlauf_aktiv:
            self.verlauf_store.kind(kind_id).frage(dt_util.now().date(), fach.id)
            self.verlauf_store.async_schedule_save()
        self.hass.bus.async_fire(
            EVENT_QUESTION_SENT,
            self._event_daten(kind_id, zustand.offene_frage),
        )
        self._benachrichtige(kind_id)
        return FrageStatus.GESENDET

    # ------------------------------------------------------------------
    # Answers and timeouts
    # ------------------------------------------------------------------

    async def async_antwort(self, kind_id: str, antwort: str) -> dict[str, Any]:
        """Evaluate the answer of a child to its open question."""
        async with self._sperren[kind_id]:
            kind = self.kinder[kind_id]
            zustand = self.zustand(kind_id)
            if zustand.simulation is not None:
                return await self._async_sim_antwort(kind_id, antwort)
            frage = zustand.offene_frage
            aufgabe = None if frage is None else self._aufgabe(frage)
            if frage is None or aufgabe is None:
                return await self._async_ohne_frage(kind_id, antwort)

            gewuenscht = await self._async_wunsch_statt_antwort(kind_id, antwort)
            if gewuenscht is not None:
                return gewuenscht

            fach = self.faecher[frage.fach_id]
            loesung = aufgabe.loesung_text(frage.richtung)
            ergebnis, bewertet_von, erklaerung = await self._async_bewerte(
                fach, aufgabe, frage.richtung, antwort, frage.optionen
            )

            jetzt = dt_util.utcnow()
            stat = aufgabe.statistik_fuer(frage.richtung)
            if ergebnis is Ergebnis.FALSCH:
                stat.falsch += 1
                stat.zuletzt_falsch = jetzt
            elif ergebnis is Ergebnis.TEILWEISE:
                stat.teilweise += 1
            elif ergebnis is not Ergebnis.UNBEANTWORTET:
                stat.richtig += 1
            stat.box = naechste_box(stat.box, ergebnis)
            zustand.offene_frage = None
            self.task_stores[frage.fach_id].async_schedule_save()
            self.config_store.async_schedule_save()

            if ergebnis is Ergebnis.UNBEANTWORTET:
                # Only a free answer that could not be judged ends up here
                nachricht = text(
                    self.sprache, "unbewertet_sach", name=kind.name, loesung=loesung
                )
            else:
                nachricht = self._ergebnis_text(kind, aufgabe, frage.richtung, ergebnis)
            if erklaerung:
                nachricht += text(self.sprache, "erklaerung", erklaerung=erklaerung)
            angebot = (
                isinstance(aufgabe, MatheAufgabe)
                and ergebnis is Ergebnis.FALSCH
                and (bool(aufgabe.rechenweg) or self._ki_kann_erklaeren(fach, aufgabe))
            )
            if angebot:
                # The child may ask how the task is solved; a running series
                # of extra questions waits for that reply
                zustand.rechenweg_angebot = RechenwegAngebot(
                    fach_id=fach.id,
                    aufgabe_id=aufgabe.id,
                    bis=jetzt + self._frist(kind_id, aufgabe),
                )
                nachricht += text(self.sprache, "rechenweg_angebot")
            elif zustand.zusatz_offen == 0 and zustand.aktiv:
                # No further question follows, tell how to get one
                nachricht += text(self.sprache, "zusatz_tipp")
            await self.messenger.async_send(kind, nachricht, wiederholen=True)
            self._feuere_bewertung(kind_id, frage, ergebnis, bewertet_von)
            self._benachrichtige(kind_id)
            if not angebot:
                await self._async_serie_fortsetzen(kind_id, frage.fach_id)
            self._plane(kind_id)
            antwort_daten = {
                "ergebnis": ergebnis.value,
                "loesung": loesung,
                "bewertet_von": bewertet_von,
            }
            if erklaerung:
                antwort_daten["erklaerung"] = erklaerung
            return antwort_daten

    def _ki_kann_erklaeren(self, fach: Fach, aufgabe: MatheAufgabe) -> bool:
        """Return whether the AI could write the solution steps of a task.

        A task with an image needs an AI that can see it.
        """
        ki_entity = self.ki_entity(fach)
        if not ki_entity:
            return False
        return not aufgabe.bild or self.ki.kann_bilder(ki_entity)

    async def _async_bewerte(
        self,
        fach: Fach,
        aufgabe: Aufgabe,
        richtung_key: str,
        antwort: str,
        optionen: list[str] | None = None,
    ) -> tuple[Ergebnis, str, str | None]:
        """Evaluate an answer locally and, if that is not enough, with the AI.

        Returns the result, who evaluated it and an optional explanation.
        """
        ki_entity = self.ki_entity(fach)
        loesung = aufgabe.loesung_text(richtung_key)
        if isinstance(aufgabe, SachAufgabe):
            if aufgabe.form is SachForm.AUSWAHL:
                gezeigt = optionen or [aufgabe.antwort, *aufgabe.falsche_optionen]
                return bewerte_auswahl(antwort, gezeigt, loesung), "lokal", None
            if gleiche_antwort(antwort, loesung):
                return Ergebnis.RICHTIG, "lokal", None
            if ki_entity and antwort.strip():
                bewertung = await self.ki.async_bewerte_sach(
                    ki_entity,
                    frage=aufgabe.frage,
                    musterantwort=loesung,
                    kernpunkte=aufgabe.kernpunkte,
                    antwort=antwort,
                    sprache=waehle_sprache(self.sprache),
                )
                if bewertung is not None:
                    return bewertung.ergebnis, "ki", bewertung.erklaerung
            # A free answer cannot be judged without the AI: it does not count
            return Ergebnis.UNBEANTWORTET, "lokal", None
        if isinstance(aufgabe, MatheAufgabe):
            lokal = bewerte_mathe(antwort, loesung, aufgabe.alternativen)
            if lokal is not None:
                return lokal, "lokal", None
            if ki_entity:
                # Results that are no plain numbers can only be judged by the AI
                bewertung = await self.ki.async_bewerte_mathe(
                    ki_entity,
                    aufgabe=aufgabe.aufgabe,
                    loesung=loesung,
                    alternativen=aufgabe.alternativen,
                    antwort=antwort,
                    bild=aufgabe.bild,
                )
                if bewertung is not None:
                    return bewertung.ergebnis, "ki", None
            return Ergebnis.FALSCH, "lokal", None

        von, nach = richtung_teile(richtung_key)
        alternativen = aufgabe.alternativen.get(nach, ())
        ergebnis = bewerte_vokabel(antwort, loesung, alternativen, nach)
        if ergebnis is Ergebnis.FALSCH and ki_entity and antwort.strip():
            # Synonyms and unusual typos can only be judged by the AI
            bewertung = await self.ki.async_bewerte_vokabel(
                ki_entity,
                wort=aufgabe.frage[von],
                loesung=loesung,
                alternativen=alternativen,
                antwort=antwort,
                von=von,
                nach=nach,
                erklaersprache=waehle_sprache(self.sprache),
            )
            if bewertung is not None:
                return bewertung.ergebnis, "ki", bewertung.erklaerung
        return ergebnis, "lokal", None

    def _ergebnis_text(
        self, kind: Kind, aufgabe: Aufgabe, richtung_key: str, ergebnis: Ergebnis
    ) -> str:
        """Return the message that tells the child the result."""
        endung = (
            "_mathe"
            if isinstance(aufgabe, MatheAufgabe)
            else "_sach"
            if isinstance(aufgabe, SachAufgabe)
            else ""
        )
        return text(
            self.sprache,
            f"{ergebnis.value}{endung}",
            name=kind.name,
            wort=aufgabe.frage_text(richtung_key),
            loesung=aufgabe.loesung_text(richtung_key),
        )

    async def _async_serie_fortsetzen(self, kind_id: str, fach_id: str | None) -> bool:
        """Ask the next extra question of a running series, if there is one."""
        zustand = self.zustand(kind_id)
        if zustand.zusatz_offen <= 0:
            return False
        zustand.zusatz_offen -= 1
        await self._async_zusatzfrage(kind_id, fach_id)
        return True

    async def _async_ohne_frage(self, kind_id: str, antwort: str) -> dict[str, Any]:
        """Handle a message that does not answer a question.

        It may accept the offer to explain a solution or ask for more
        questions.
        """
        kind = self.kinder[kind_id]
        zustand = self.zustand(kind_id)
        if zustand.offene_frage is not None:
            # The task of the open question was deleted in the meantime
            zustand.offene_frage = None
            self.config_store.async_schedule_save()
            self._benachrichtige(kind_id)
            self._plane(kind_id)

        offen = zustand.wunsch_offen
        if offen is not None:
            zustand.wunsch_offen = None
            self.config_store.async_schedule_save()
            anzahl = erkenne_anzahl(antwort)
            if (
                anzahl is not None
                and offen.bis >= dt_util.utcnow()
                and offen.fach_id in self.faecher
                and zustand.aktiv
            ):
                return await self._async_wunsch_starten(
                    kind_id, offen.fach_id, offen.lektion, anzahl
                )

        angebot = zustand.rechenweg_angebot
        if angebot is not None:
            zustand.rechenweg_angebot = None
            self.config_store.async_schedule_save()
            if angebot.bis < dt_util.utcnow():
                # Too late, a waiting series ended with it
                zustand.zusatz_offen = 0
                angebot = None
        if angebot is not None and erkenne_ja(antwort):
            await self._async_rechenweg_senden(kind_id, angebot)
            if await self._async_serie_fortsetzen(kind_id, angebot.fach_id):
                self._plane(kind_id)
            return {"ergebnis": RECHENWEG}

        wunsch = erkenne_zusatzwunsch(antwort) if zustand.aktiv else None
        if wunsch is not None:
            return await self._async_zusatz_starten(kind_id, wunsch)
        uebung = self._uebungswunsch(kind_id, antwort)
        if uebung is not None and not uebung.eindeutig:
            uebung = await self._async_ki_wunsch(kind_id, antwort, uebung)
        if uebung is not None:
            return await self._async_wunsch(kind_id, uebung)
        if angebot is not None:
            # Anything else declines the offer; a waiting series goes on
            if await self._async_serie_fortsetzen(kind_id, angebot.fach_id):
                self._plane(kind_id)
                return {"ergebnis": ZUSATZAUFGABEN, "anzahl": zustand.zusatz_offen + 1}
            if erkenne_nein(antwort):
                nachricht = text(self.sprache, "rechenweg_nein", name=kind.name)
                if zustand.aktiv:
                    nachricht += text(self.sprache, "zusatz_tipp")
                await self.messenger.async_send(kind, nachricht)
                return {"ergebnis": KEINE_OFFENE_FRAGE}
        await self.messenger.async_send(
            kind, text(self.sprache, "keine_frage", name=kind.name)
        )
        return {"ergebnis": KEINE_OFFENE_FRAGE}

    async def _async_rechenweg_senden(
        self, kind_id: str, angebot: RechenwegAngebot
    ) -> None:
        """Send the steps of a solution; the AI creates them if needed."""
        kind = self.kinder[kind_id]
        store = self.task_stores.get(angebot.fach_id)
        aufgabe = None if store is None else store.aufgaben.get(angebot.aufgabe_id)
        schritte: list[str] | None = None
        if store is not None and isinstance(aufgabe, MatheAufgabe):
            schritte = aufgabe.rechenweg or None
            ki_entity = self.ki_entity(self.faecher[angebot.fach_id])
            if schritte is None and ki_entity:
                schritte = await self.ki.async_rechenweg(
                    ki_entity,
                    aufgabe=aufgabe.aufgabe,
                    loesung=aufgabe.loesung,
                    sprache=waehle_sprache(self.sprache),
                    bild=aufgabe.bild,
                )
                if schritte:
                    # Keep them, so they are created only once
                    aufgabe.rechenweg = schritte
                    store.async_schedule_save()
        if not schritte:
            await self.messenger.async_send(
                kind, text(self.sprache, "rechenweg_fehlt", name=kind.name)
            )
            return
        zeilen = [text(self.sprache, "rechenweg", name=kind.name)]
        zeilen.extend(
            f"{nummer}. {schritt}" for nummer, schritt in enumerate(schritte, 1)
        )
        await self.messenger.async_send(kind, "\n".join(zeilen), wiederholen=True)

    async def _async_zusatz_starten(self, kind_id: str, wunsch: int) -> dict[str, Any]:
        """Start the extra questions a child asked for."""
        kind = self.kinder[kind_id]
        zustand = self.zustand(kind_id)
        anzahl = min(wunsch, MAX_ZUSATZAUFGABEN)
        if anzahl > 1:
            await self.messenger.async_send(
                kind,
                text(
                    self.sprache,
                    "zusatz_gekuerzt" if wunsch > anzahl else "zusatz_start",
                    name=kind.name,
                    anzahl=str(anzahl),
                ),
            )
        zustand.zusatz_offen = anzahl - 1
        await self._async_zusatzfrage(kind_id, self._letztes_fach.get(kind_id))
        self._plane(kind_id)
        return {"ergebnis": ZUSATZAUFGABEN, "anzahl": anzahl}

    def _wunsch_faecher(self, kind_id: str) -> list[WunschFach]:
        """Return what is needed to find the subjects of a child in a message."""
        return [
            WunschFach(
                id=fach.id,
                name=fach.name,
                vokabeln=fach.typ is AufgabenTyp.VOKABEL,
                lektionen=tuple(self.task_stores[fach.id].lektionen),
            )
            for fach in self.faecher_von(kind_id)
        ]

    def _uebungswunsch(self, kind_id: str, nachricht: str) -> Uebungswunsch | None:
        """Return what the child asks to practise, if it does."""
        if not self.zustand(kind_id).aktiv:
            return None
        return erkenne_uebungswunsch(nachricht, self._wunsch_faecher(kind_id))

    async def _async_ki_wunsch(
        self, kind_id: str, nachricht: str, wunsch: Uebungswunsch
    ) -> Uebungswunsch:
        """Let the AI assign a wish the rules could not assign."""
        ki_entity = self.entry.options.get(CONF_KI_ENTITY)
        faecher = self._wunsch_faecher(kind_id)
        if not ki_entity or not faecher or not self.wunsch_ki:
            return wunsch
        gedeutet = await self.ki.async_deute_wunsch(
            ki_entity, nachricht=nachricht, faecher=faecher
        )
        if gedeutet is None or not gedeutet.eindeutig:
            return wunsch
        if gedeutet.anzahl is None and wunsch.anzahl is not None:
            gedeutet = replace(gedeutet, anzahl=wunsch.anzahl)
        return gedeutet

    async def _async_wunsch_statt_antwort(
        self, kind_id: str, nachricht: str
    ) -> dict[str, Any] | None:
        """React to a clear wish that arrives while a question is open.

        The wish wins: the open question is taken back and does not count.
        Only the rules decide here, so that an answer never costs an AI call.
        """
        wunsch = self._uebungswunsch(kind_id, nachricht)
        if wunsch is None or not wunsch.eindeutig:
            return None
        self._frage_zuruecknehmen(kind_id)
        self._benachrichtige(kind_id)
        ergebnis = await self._async_wunsch(kind_id, wunsch)
        self._plane(kind_id)
        return ergebnis

    def _wunsch_ort(self, fach_id: str, lektion: str | None) -> str:
        name = self.faecher[fach_id].name
        return name if lektion is None else f"{name}, {lektion}"

    async def _async_wunsch(
        self, kind_id: str, wunsch: Uebungswunsch
    ) -> dict[str, Any]:
        """React to the wish of a child to practise something."""
        kind = self.kinder[kind_id]
        zustand = self.zustand(kind_id)
        zustand.zusatz_offen = 0
        if wunsch.fach_id is None:
            faecher = ", ".join(sorted(f.name for f in self.faecher_von(kind_id)))
            await self.messenger.async_send(
                kind,
                text(
                    self.sprache,
                    "wunsch_unklar" if faecher else "zusatz_keine",
                    name=kind.name,
                    faecher=faecher,
                ),
            )
            self.config_store.async_schedule_save()
            return {"ergebnis": WUNSCH_UNKLAR}
        ort = self._wunsch_ort(wunsch.fach_id, wunsch.lektion)
        if (
            self._waehle(
                kind_id, manuell=True, fach_id=wunsch.fach_id, lektion=wunsch.lektion
            )
            is None
        ):
            await self.messenger.async_send(
                kind, text(self.sprache, "wunsch_keine", name=kind.name, ort=ort)
            )
            self.config_store.async_schedule_save()
            return {"ergebnis": KEINE_AUFGABEN}
        if wunsch.anzahl is None:
            zustand.wunsch_offen = WunschAngebot(
                fach_id=wunsch.fach_id,
                lektion=wunsch.lektion,
                bis=dt_util.utcnow() + WUNSCH_FRIST,
            )
            zustand.rechenweg_angebot = None
            self.config_store.async_schedule_save()
            await self.messenger.async_send(
                kind, text(self.sprache, "wunsch_anzahl", name=kind.name, ort=ort)
            )
            return {"ergebnis": WUNSCH_NACHFRAGE}
        return await self._async_wunsch_starten(
            kind_id, wunsch.fach_id, wunsch.lektion, wunsch.anzahl
        )

    async def _async_wunsch_starten(
        self, kind_id: str, fach_id: str, lektion: str | None, wunsch: int
    ) -> dict[str, Any]:
        """Start the questions of a subject or a lesson a child asked for."""
        kind = self.kinder[kind_id]
        zustand = self.zustand(kind_id)
        anzahl = min(wunsch, MAX_ZUSATZAUFGABEN)
        await self.messenger.async_send(
            kind,
            text(
                self.sprache,
                "wunsch_gekuerzt" if wunsch > anzahl else "wunsch_start",
                name=kind.name,
                anzahl=str(anzahl),
                ort=self._wunsch_ort(fach_id, lektion),
            ),
        )
        zustand.rechenweg_angebot = None
        zustand.zusatz_lektion = lektion
        zustand.zusatz_offen = anzahl - 1
        await self._async_zusatzfrage(kind_id, fach_id)
        self._plane(kind_id)
        return {"ergebnis": ZUSATZAUFGABEN, "anzahl": anzahl}

    async def _async_zusatzfrage(self, kind_id: str, fach_id: str | None) -> None:
        """Ask one extra question; end the series if that is not possible."""
        zustand = self.zustand(kind_id)
        if fach_id not in self.faecher:
            fach_id = None
        try:
            await self._async_frage(
                kind_id,
                manuell=True,
                fach_id=fach_id,
                lektion=None if fach_id is None else zustand.zusatz_lektion,
                kurz=True,
            )
        except ServiceValidationError:
            # Nothing to ask
            zustand.zusatz_offen = 0
            kind = self.kinder[kind_id]
            await self.messenger.async_send(
                kind, text(self.sprache, "zusatz_keine", name=kind.name)
            )
        except HomeAssistantError:
            zustand.zusatz_offen = 0
        self.config_store.async_schedule_save()

    async def async_timeout(self, kind_id: str) -> None:
        """Close the open question of a child as unanswered."""
        async with self._sperren[kind_id]:
            kind = self.kinder[kind_id]
            zustand = self.zustand(kind_id)
            frage = zustand.offene_frage
            if frage is None:
                return
            zustand.offene_frage = None
            # Without an answer the extra questions end as well
            zustand.zusatz_offen = 0
            self.config_store.async_schedule_save()
            aufgabe = self._aufgabe(frage)
            if aufgabe is not None:
                await self.messenger.async_send(
                    kind,
                    self._ergebnis_text(
                        kind, aufgabe, frage.richtung, Ergebnis.UNBEANTWORTET
                    ),
                )
            self._feuere_bewertung(kind_id, frage, Ergebnis.UNBEANTWORTET)
            self._benachrichtige(kind_id)
            self._plane(kind_id)

    def _frage_zuruecknehmen(self, kind_id: str) -> None:
        """Take the open question of a child back as if it was never asked."""
        zustand = self.zustand(kind_id)
        frage = zustand.offene_frage
        if frage is None:
            return
        zustand.offene_frage = None
        # The extra questions the child asked for end as well
        zustand.zusatz_offen = 0
        aufgabe = self._aufgabe(frage)
        if aufgabe is not None:
            stat = aufgabe.statistik_fuer(frage.richtung)
            stat.gefragt = max(0, stat.gefragt - 1)
            self.task_stores[frage.fach_id].async_schedule_save()
        if self.verlauf_aktiv:
            # Taken back on the day the question was asked
            self.verlauf_store.kind(kind_id).frage_zurueck(
                dt_util.as_local(frage.gestellt_um).date(), frage.fach_id
            )
            self.verlauf_store.async_schedule_save()
        self.config_store.async_schedule_save()

    async def async_frage_abbrechen(self, kind_id: str) -> bool:
        """Withdraw the open question of a child.

        It does not count: the question counter is taken back and the level
        of the task stays as it is. The child is told that the question is
        gone. A simulated exam is stopped with its own command.
        """
        async with self._sperren[kind_id]:
            kind = self.kinder[kind_id]
            zustand = self.zustand(kind_id)
            if zustand.offene_frage is None or zustand.simulation is not None:
                return False
            self._frage_zuruecknehmen(kind_id)
            await self.messenger.async_send(
                kind, text(self.sprache, "frage_abgebrochen", name=kind.name)
            )
            self._benachrichtige(kind_id)
            self._plane(kind_id)
            return True

    # ------------------------------------------------------------------
    # Simulated exams
    # ------------------------------------------------------------------

    def simulation_auswahl(
        self, arbeit: Arbeit, anzahl: int, *, messenger: bool
    ) -> list[SimAufgabe]:
        """Pick the tasks of a simulated exam.

        In the messenger only tasks take part that can be delivered and
        judged there.
        """
        fach = self.faecher[arbeit.fach_id]
        store = self.task_stores[fach.id]
        aufgaben: Iterable[Aufgabe] = aufgaben_der_arbeit(
            arbeit,
            store.aufgaben.values(),
            self.config_store.arbeit_aufgaben.get(arbeit.id, ()),
        )
        if messenger:
            aufgaben = self._zustellbar(fach.kind_id, aufgaben)
        gewaehlt = waehle(aufgaben, fach.richtungen, anzahl, self._rng)
        # Tasks about the same image stand together, like parts a), b), c)
        bilder = [
            aufgabe.bild if isinstance(aufgabe, MatheAufgabe) else None
            for aufgabe, _ in gewaehlt
        ]
        reihenfolge = sorted(
            range(len(gewaehlt)),
            key=lambda i: bilder.index(bilder[i]) if bilder[i] else i,
        )
        return [
            SimAufgabe(
                aufgabe_id=aufgabe.id,
                richtung=richtung_key,
                optionen=(
                    mische(aufgabe.antwort, aufgabe.falsche_optionen, self._rng)
                    if isinstance(aufgabe, SachAufgabe)
                    and aufgabe.form is SachForm.AUSWAHL
                    else None
                ),
            )
            for aufgabe, richtung_key in (gewaehlt[i] for i in reihenfolge)
        ]

    def _blatt_aufgabe(self, aufgabe: Aufgabe, eintrag: SimAufgabe) -> BlattAufgabe:
        """Return a task the way it is printed on the sheet."""
        if isinstance(aufgabe, Vokabel):
            von, nach = richtung_teile(eintrag.richtung)
            return BlattAufgabe(
                text(
                    self.sprache,
                    "blatt_uebersetze",
                    zielsprache=sprachname(self.sprache, nach),
                    wort=aufgabe.frage[von],
                ),
                Art.LINIE,
            )
        if isinstance(aufgabe, MatheAufgabe):
            return BlattAufgabe(
                aufgabe.aufgabe,
                Art.RECHNEN,
                bild=self.bilder.pfad(aufgabe.bild) if aufgabe.bild else None,
            )
        if aufgabe.form is SachForm.AUSWAHL:
            return BlattAufgabe(
                aufgabe.frage, Art.AUSWAHL, optionen=tuple(eintrag.optionen or ())
            )
        return BlattAufgabe(aufgabe.frage, Art.ZEILEN)

    def _sim_titel(self, arbeit: Arbeit) -> str:
        return text(self.sprache, f"sim_titel_{arbeit.art.value}")

    async def async_simulation_blatt(
        self, arbeit: Arbeit, eintraege: list[SimAufgabe]
    ) -> list[str]:
        """Render the sheet of a simulated exam and return the ids of its pages."""
        store = self.task_stores[arbeit.fach_id]
        sprache = self.sprache
        texte = BlattTexte(
            titel=self._sim_titel(arbeit),
            fach=self.faecher[arbeit.fach_id].name,
            thema=arbeit.thema,
            name=text(sprache, "blatt_name"),
            klasse=text(sprache, "blatt_klasse"),
            datum=text(sprache, "blatt_datum"),
            punkte=text(sprache, "blatt_punkte"),
            punkt_kurz=text(sprache, "blatt_punkt_kurz"),
            antwort=text(sprache, "blatt_antwort"),
            unterschrift=text(sprache, "blatt_unterschrift"),
            seite=text(sprache, "blatt_seite"),
        )
        aufgaben: list[BlattAufgabe] = []
        zuletzt: Path | None = None
        for eintrag in eintraege:
            blatt = self._blatt_aufgabe(store.aufgaben[eintrag.aufgabe_id], eintrag)
            if blatt.bild is not None and blatt.bild == zuletzt:
                # The image is printed once above the tasks that share it
                blatt = replace(blatt, bild=None)
            else:
                zuletzt = blatt.bild
            aufgaben.append(blatt)
        seiten = await self.hass.async_add_executor_job(zeichne, texte, aufgaben)
        return [await self.bilder.async_speichere_fertig(seite) for seite in seiten]

    def simulation_geplant(self, arbeit: Arbeit) -> bool:
        """Return whether the planned simulation of an exam is still to come."""
        return (
            arbeit.simulation_um is not None
            and self.config_store.simulation_gesendet.get(arbeit.id)
            != arbeit.simulation_um.isoformat()
        )

    def _plane_simulationen(self) -> None:
        """(Re)start the timers of all planned simulations."""
        for abbrechen in self._sim_timer.values():
            abbrechen()
        self._sim_timer.clear()
        if self.hass.is_stopping:
            return
        jetzt = dt_util.utcnow()
        for arbeit in self.arbeiten.values():
            if arbeit.simulation_um is None or not self.simulation_geplant(arbeit):
                continue
            zeitpunkt = arbeit.simulation_um
            if zeitpunkt <= jetzt:
                if jetzt - zeitpunkt > SIMULATION_NACHHOLEN:
                    # Missed long ago, for example while Home Assistant was off
                    continue
                zeitpunkt = jetzt + timedelta(seconds=30)

            async def _start(_jetzt: datetime, arbeit_id: str = arbeit.id) -> None:
                self._sim_timer.pop(arbeit_id, None)
                await self.async_geplante_simulation(arbeit_id)

            self._sim_timer[arbeit.id] = async_track_point_in_time(
                self.hass, _start, zeitpunkt
            )

    async def async_geplante_simulation(self, arbeit_id: str) -> bool:
        """Start the simulation that was planned for an exam.

        It is tried once: if the child is paused, busy with another
        simulation or cannot be reached, the simulation is skipped.
        """
        arbeit = self.arbeiten.get(arbeit_id)
        if arbeit is None or arbeit.simulation_um is None:
            return False
        self.config_store.simulation_gesendet[arbeit_id] = (
            arbeit.simulation_um.isoformat()
        )
        self.config_store.async_schedule_save()
        kind_id = self.faecher[arbeit.fach_id].kind_id
        if self.zustand(kind_id).ist_pausiert(dt_util.utcnow()):
            LOGGER.info("Planned simulation of exam %s skipped: paused", arbeit_id)
            self._benachrichtige(kind_id)
            return False
        try:
            await self.async_simulation_starten(arbeit_id, arbeit.simulation_anzahl)
        except HomeAssistantError as err:
            LOGGER.warning(
                "Planned simulation of exam %s could not start: %s",
                arbeit_id,
                getattr(err, "translation_key", None) or type(err).__name__,
            )
            self._benachrichtige(kind_id)
            return False
        return True

    async def async_simulation_starten(self, arbeit_id: str, anzahl: int) -> int:
        """Start a simulated exam in the messenger of the child.

        Returns the number of tasks. Raises a translated error if there is
        no task, a simulation is running or sending fails.
        """
        arbeit = self.arbeiten[arbeit_id]
        fach = self.faecher[arbeit.fach_id]
        kind_id = fach.kind_id
        async with self._sperren[kind_id]:
            kind = self.kinder[kind_id]
            zustand = self.zustand(kind_id)
            if zustand.simulation is not None:
                raise ServiceValidationError(
                    translation_domain=DOMAIN, translation_key="simulation_laeuft"
                )
            eintraege = self.simulation_auswahl(arbeit, anzahl, messenger=True)
            if not eintraege:
                raise ServiceValidationError(
                    translation_domain=DOMAIN, translation_key="keine_aufgaben"
                )
            seiten = (
                await self.async_simulation_blatt(arbeit, eintraege)
                if self.messenger.kann_bilder(kind)
                else []
            )
            einleitung = text(
                self.sprache,
                "sim_start",
                name=kind.name,
                titel=self._sim_titel(arbeit),
                fach=fach.name,
                thema=arbeit.thema,
                anzahl=str(len(eintraege)),
            )
            await self.messenger.async_send_or_raise(
                kind, einleitung, bild=seiten[0] if seiten else None
            )
            for nummer, seite in enumerate(seiten[1:], start=2):
                await self.messenger.async_send(
                    kind, text(self.sprache, "sim_seite", nr=str(nummer)), bild=seite
                )

            if zustand.offene_frage is not None:
                # The simulation replaces the open question
                self._feuere_bewertung(
                    kind_id, zustand.offene_frage, Ergebnis.UNBEANTWORTET
                )
                zustand.offene_frage = None
            zustand.zusatz_offen = 0
            zustand.rechenweg_angebot = None
            self._wiederholung_um.pop(kind_id, None)
            zustand.simulation = Simulation(
                arbeit_id=arbeit_id, fach_id=fach.id, aufgaben=eintraege
            )
            await self._async_sim_frage(kind_id)
            self.config_store.async_schedule_save()
            self._benachrichtige(kind_id)
            self._plane(kind_id)
            return len(eintraege)

    async def _async_sim_frage(self, kind_id: str) -> None:
        """Send the task of a simulated exam that is next, or finish it."""
        kind = self.kinder[kind_id]
        simulation = self.zustand(kind_id).simulation
        if simulation is None:
            return
        fach = self.faecher[simulation.fach_id]
        store = self.task_stores[fach.id]
        while simulation.index < len(simulation.aufgaben):
            eintrag = simulation.aufgaben[simulation.index]
            aufgabe = store.aufgaben.get(eintrag.aufgabe_id)
            if aufgabe is None:
                # Deleted in the meantime: it does not count
                eintrag.ergebnis = Ergebnis.UNBEANTWORTET
                simulation.index += 1
                continue
            frage = self._frage_text(
                kind,
                fach,
                aufgabe,
                eintrag.richtung,
                kurz=True,
                optionen=eintrag.optionen,
            )
            await self.messenger.async_send(
                kind,
                text(
                    self.sprache,
                    "sim_aufgabe",
                    nr=str(simulation.index + 1),
                    anzahl=str(len(simulation.aufgaben)),
                    frage=frage,
                ),
                bild=aufgabe.bild if isinstance(aufgabe, MatheAufgabe) else None,
                wiederholen=True,
            )
            simulation.timeout_um = dt_util.utcnow() + self._frist(
                kind_id, aufgabe, self.arbeiten.get(simulation.arbeit_id)
            )
            return
        await self._async_sim_ende(kind_id)

    async def _async_sim_antwort(self, kind_id: str, antwort: str) -> dict[str, Any]:
        """Judge the answer to a task of a simulated exam without feedback."""
        simulation = self.zustand(kind_id).simulation
        if simulation is None or simulation.index >= len(simulation.aufgaben):
            await self._async_sim_ende(kind_id)
            return {"ergebnis": SIMULATION}
        fach = self.faecher[simulation.fach_id]
        eintrag = simulation.aufgaben[simulation.index]
        aufgabe = self.task_stores[fach.id].aufgaben.get(eintrag.aufgabe_id)
        if aufgabe is None:
            eintrag.ergebnis = Ergebnis.UNBEANTWORTET
        else:
            eintrag.ergebnis, _, eintrag.erklaerung = await self._async_bewerte(
                fach, aufgabe, eintrag.richtung, antwort, eintrag.optionen
            )
        simulation.index += 1
        anzahl = len(simulation.aufgaben)
        nummer = simulation.index
        await self._async_sim_frage(kind_id)
        self.config_store.async_schedule_save()
        self._benachrichtige(kind_id)
        self._plane(kind_id)
        return {"ergebnis": SIMULATION, "nummer": nummer, "anzahl": anzahl}

    def _sim_auswertung(
        self, kind: Kind, simulation: Simulation, *, zeit: bool
    ) -> tuple[Auswertung, str]:
        """Score a simulated exam and write the message that tells the result."""
        sprache = self.sprache
        auswertung = werte_aus(e.ergebnis for e in simulation.aufgaben)
        if auswertung.prozent is None:
            nachricht = text(sprache, "sim_ende_leer", name=kind.name)
        else:
            nachricht = text(
                sprache,
                "sim_zeit" if zeit else "sim_ende",
                name=kind.name,
                punkte=punkte_text(auswertung.punkte, waehle_sprache(sprache)),
                moeglich=str(auswertung.moeglich),
                prozent=str(auswertung.prozent),
            )
        store = self.task_stores[simulation.fach_id]
        zeilen = ""
        for nummer, eintrag in enumerate(simulation.aufgaben, start=1):
            aufgabe = store.aufgaben.get(eintrag.aufgabe_id)
            if aufgabe is None or eintrag.ergebnis in (
                Ergebnis.RICHTIG,
                Ergebnis.FAST_RICHTIG,
                Ergebnis.UNBEANTWORTET,
            ):
                continue
            zeilen += text(
                sprache,
                "sim_fehler_zeile",
                nr=str(nummer),
                frage=aufgabe.frage_text(eintrag.richtung),
                loesung=aufgabe.loesung_text(eintrag.richtung),
            )
            if eintrag.erklaerung:
                zeilen += text(sprache, "erklaerung", erklaerung=eintrag.erklaerung)
        if zeilen:
            nachricht += text(sprache, "sim_fehler") + zeilen
        elif auswertung.moeglich:
            nachricht += text(sprache, "sim_alles_richtig")
        if auswertung.unbewertet:
            nachricht += text(
                sprache, "sim_unbewertet", anzahl=str(auswertung.unbewertet)
            )
        return auswertung, nachricht

    async def _async_sim_ende(self, kind_id: str, *, zeit: bool = False) -> None:
        """Finish a simulated exam: send the result and fire the event."""
        kind = self.kinder[kind_id]
        zustand = self.zustand(kind_id)
        simulation = zustand.simulation
        if simulation is None:
            return
        zustand.simulation = None
        self.config_store.async_schedule_save()
        auswertung, nachricht = self._sim_auswertung(kind, simulation, zeit=zeit)
        if self.verlauf_aktiv:
            self.verlauf_store.kind(kind_id).simulation(
                SimErgebnis(
                    tag=dt_util.now().date(),
                    arbeit_id=simulation.arbeit_id,
                    fach_id=simulation.fach_id,
                    punkte=auswertung.punkte,
                    moeglich=auswertung.moeglich,
                    vollstaendig=not zeit,
                )
            )
            self.verlauf_store.async_schedule_save()
        await self.messenger.async_send(kind, nachricht, wiederholen=True)
        self.hass.bus.async_fire(
            EVENT_SIMULATION_FINISHED,
            {
                "kind_id": kind_id,
                "fach_id": simulation.fach_id,
                "arbeit_id": simulation.arbeit_id,
                "punkte": auswertung.punkte,
                "moeglich": auswertung.moeglich,
                "prozent": auswertung.prozent,
                "vollstaendig": not zeit,
            },
        )
        self._benachrichtige(kind_id)

    async def async_simulation_timeout(self, kind_id: str) -> None:
        """End a simulated exam whose task was not answered in time."""
        async with self._sperren[kind_id]:
            await self._async_sim_ende(kind_id, zeit=True)
            self._plane(kind_id)

    async def async_simulation_abbrechen(self, kind_id: str) -> bool:
        """Stop a simulated exam without a result."""
        async with self._sperren[kind_id]:
            kind = self.kinder[kind_id]
            zustand = self.zustand(kind_id)
            if zustand.simulation is None:
                return False
            zustand.simulation = None
            self.config_store.async_schedule_save()
            await self.messenger.async_send(
                kind, text(self.sprache, "sim_abbruch", name=kind.name)
            )
            self._benachrichtige(kind_id)
            self._plane(kind_id)
            return True

    # ------------------------------------------------------------------
    # Pause and import
    # ------------------------------------------------------------------

    @callback
    def async_set_aktiv(
        self, kind_id: str, aktiv: bool, bis: datetime | None = None
    ) -> None:
        """Enable, disable or pause the questions of a child."""
        zustand = self.zustand(kind_id)
        if bis is not None:
            zustand.aktiv = True
            zustand.pausiert_bis = dt_util.as_utc(bis)
        else:
            zustand.aktiv = aktiv
            zustand.pausiert_bis = None
        if bis is not None or not aktiv:
            zustand.zusatz_offen = 0
            # A simulated exam ends without a result
            zustand.simulation = None
        self.config_store.async_schedule_save()
        self._benachrichtige(kind_id)
        self._plane(kind_id)

    @callback
    def async_importiere(
        self,
        fach_id: str,
        inhalt: str,
        *,
        lektion: str | None = None,
        trennzeichen: str | None = None,
        geprueft: bool = True,
    ) -> dict[str, Any]:
        """Import tasks from text into a subject."""
        fach = self.faecher[fach_id]
        store = self.task_stores[fach_id]
        if fach.typ is AufgabenTyp.SACH:
            raise ServiceValidationError(
                translation_domain=DOMAIN, translation_key="import_sachfach"
            )
        geparst = parse_import(fach, inhalt, trennzeichen)
        if not geparst.zeilen:
            raise ServiceValidationError(
                translation_domain=DOMAIN, translation_key="import_leer"
            )

        vorhanden = {aufgabe_schluessel(fach, a) for a in store.aufgaben.values()}
        importiert = uebersprungen = 0
        for zeile in geparst.zeilen:
            aufgabe = aufgabe_aus_zeile(
                fach,
                zeile,
                lektion=lektion.strip() if lektion and lektion.strip() else None,
                geprueft=geprueft,
            )
            schluessel = aufgabe_schluessel(fach, aufgabe)
            if schluessel in vorhanden:
                uebersprungen += 1
                continue
            vorhanden.add(schluessel)
            store.add(aufgabe)
            importiert += 1
        if importiert:
            store.async_schedule_save()
            self._benachrichtige(fach.kind_id)
        return {
            "importiert": importiert,
            "uebersprungen": uebersprungen,
            "fehlerzeilen": geparst.fehlerzeilen,
        }

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _event_daten(kind_id: str, frage: OffeneFrage) -> dict[str, Any]:
        """Return the event payload of a question (without personal data)."""
        return {
            "kind_id": kind_id,
            "fach_id": frage.fach_id,
            "aufgabe_id": frage.aufgabe_id,
            "arbeit_id": frage.arbeit_id,
            "richtung": frage.richtung,
        }

    def _feuere_bewertung(
        self,
        kind_id: str,
        frage: OffeneFrage,
        ergebnis: Ergebnis,
        bewertet_von: str = "lokal",
    ) -> None:
        self._verlauf_ergebnis(kind_id, frage, ergebnis)
        self.hass.bus.async_fire(
            EVENT_ANSWER_EVALUATED,
            {
                **self._event_daten(kind_id, frage),
                "ergebnis": ergebnis.value,
                "bewertet_von": bewertet_von,
            },
        )

    # ------------------------------------------------------------------
    # Daily log
    # ------------------------------------------------------------------

    def lernstand(self, fach: Fach) -> tuple[int, int]:
        """Return the cards of a subject and how many of them are safe."""
        karten = sicher = 0
        for aufgabe in self.task_stores[fach.id].aufgaben.values():
            if not aufgabe.geprueft:
                continue
            for richtung in fach.richtungen:
                stat = aufgabe.statistik.get(richtung)
                karten += 1
                sicher += stat is not None and stat.box >= SICHER_AB_BOX
        return karten, sicher

    def _verlauf_ergebnis(
        self, kind_id: str, frage: OffeneFrage, ergebnis: Ergebnis
    ) -> None:
        """Log the result of a question and the level of its subject."""
        if not self.verlauf_aktiv:
            return
        heute = dt_util.now().date()
        verlauf = self.verlauf_store.kind(kind_id)
        aufgabe = self._aufgabe(frage)
        verlauf.ergebnis(
            heute,
            frage.fach_id,
            ergebnis.value,
            lektion=None if aufgabe is None else aufgabe.lektion,
            aufgabe_id=frage.aufgabe_id,
        )
        fach = self.faecher.get(frage.fach_id)
        if fach is not None:
            verlauf.lernstand(heute, fach.id, *self.lernstand(fach))
        self.verlauf_store.async_schedule_save()

    @callback
    def _verlauf_lernstand(self) -> None:
        """Note the level of every subject, once a day and at the start."""
        if not self.verlauf_aktiv:
            return
        heute = dt_util.now().date()
        for fach in self.faecher.values():
            karten, sicher = self.lernstand(fach)
            if karten:
                self.verlauf_store.kind(fach.kind_id).lernstand(
                    heute, fach.id, karten, sicher
                )
        self.verlauf_store.async_schedule_save()

    def _benachrichtige(self, kind_id: str) -> None:
        """Tell the entities of a child to update."""
        async_dispatcher_send(self.hass, signal_kind_update(kind_id))

    @callback
    def async_benachrichtige(self, kind_id: str) -> None:
        """Tell the entities of a child to update after its data was edited."""
        self._benachrichtige(kind_id)

    @callback
    def async_frage_verwerfen(self, kind_id: str, aufgabe_ids: set[str]) -> None:
        """Drop the open question of a child if its task was deleted."""
        zustand = self.zustand(kind_id)
        frage = zustand.offene_frage
        if frage is None or frage.aufgabe_id not in aufgabe_ids:
            return
        zustand.offene_frage = None
        self.config_store.async_schedule_save()
        self._plane(kind_id)
