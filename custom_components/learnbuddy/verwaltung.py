"""Data maintenance for the panel: tasks, exams, import and export."""

from __future__ import annotations

import asyncio
from datetime import date
import re
from types import MappingProxyType
from typing import TYPE_CHECKING, Any

from homeassistant.config_entries import ConfigSubentry
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.util import dt as dt_util

from .const import (
    CONF_ABFRAGEN_PRO_TAG,
    CONF_ANTWORTFRIST,
    CONF_ART,
    CONF_DATUM,
    CONF_ERSTELLT,
    CONF_FACH_ID,
    CONF_GEAENDERT,
    CONF_INTENSIVIERUNG,
    CONF_LEKTIONEN,
    CONF_SIMULATION_ANZAHL,
    CONF_SIMULATION_UM,
    CONF_START_TAGE_VORHER,
    CONF_THEMA,
    DEFAULT_ABFRAGEN_PRO_TAG,
    DEFAULT_SIMULATION_ANZAHL,
    DEFAULT_START_TAGE_VORHER,
    MAX_TIMEOUT_MINUTEN,
    SUBENTRY_ARBEIT,
)
from .evaluation import normalisiere
from .importer import ImportZeile, parse_mathe, parse_vokabeln
from .mathe import bewerte_mathe, zerlege
from .models import (
    MAX_SCHWIERIGKEIT,
    MIN_SCHWIERIGKEIT,
    ArbeitArt,
    AufgabenTyp,
    Ergebnis,
    MatheAufgabe,
    Quelle,
    SachAufgabe,
    SachForm,
    Statistik,
    Verifikation,
    Vokabel,
    arbeit_titel,
)
from .panel import panel_version
from .rechnen import berechne
from .scheduler import MAX_BOX, abfragen_am_tag, aufgaben_der_arbeit
from .simulation import MAX_AUFGABEN as MAX_SIM_AUFGABEN
from .texte import waehle_sprache

if TYPE_CHECKING:
    from collections.abc import Iterable
    from fractions import Fraction

    from .ai import GenerierteAufgabe
    from .manager import LearnBuddyManager
    from .models import Arbeit, Aufgabe, Fach
    from .storage import TaskStore

EXPORT_FORMAT = "learnbuddy-aufgaben"
# Files exported before the integration was renamed are still accepted
ALTE_EXPORT_FORMATE = ("lernbuddy-aufgaben",)
EXPORT_VERSION = 1

MAX_TEXT = 500
MAX_LOESUNG = 100
MAX_KERNPUNKTE = 6
MAX_SEITEN = 4
WEG_AUSDRUCK = "ausdruck"
WEG_MESSENGER = "messenger"
MAX_FOTO_ZEILEN = 200
MAX_SACHFRAGEN = 15
FORM_GEMISCHT = "gemischt"
MIN_FALSCHE_OPTIONEN = 2
MAX_FALSCHE_OPTIONEN = 3
MAX_OPTION = 200
MAX_STELLE = 300
MAX_SCHRITTE = 8
MAX_SEITE = 9999
MAX_GENERIEREN = 20
MAX_NACHRECHNEN = 100
# A task like 7 * 8 = ? is the calculation 7 * 8
_FRAGE_ENDE = re.compile(r"\s*=?\s*\??\s*$")
MAX_BEISPIELE = 10
# AI calls that verify generated tasks at the same time
PARALLEL_PRUEFEN = 4
MAX_LEKTION = 100
MAX_SCHWIERIG = 5
# From this Leitner box on a card counts as mastered in the overview
SICHER_AB_BOX = 3


class VerwaltungError(Exception):
    """Invalid request of the panel."""

    def __init__(self, code: str, schluessel: str) -> None:
        """Initialize with a websocket error code and a message key."""
        super().__init__(schluessel)
        self.code = code
        self.schluessel = schluessel


def _nicht_gefunden(was: str) -> VerwaltungError:
    return VerwaltungError("not_found", f"{was}_unbekannt")


def _ungueltig(schluessel: str) -> VerwaltungError:
    return VerwaltungError("invalid_format", schluessel)


def _text(wert: Any, schluessel: str, *, pflicht: bool = False) -> str | None:
    """Validate an optional short text."""
    if wert is None:
        wert = ""
    if not isinstance(wert, str) or len(wert) > MAX_TEXT:
        raise _ungueltig(schluessel)
    bereinigt: str = wert.strip()
    if not bereinigt:
        if pflicht:
            raise _ungueltig(schluessel)
        return None
    return bereinigt


def aufgabe_schluessel(fach: Fach, aufgabe: Aufgabe) -> tuple[str, str]:
    """Return the key by which duplicates of a task are recognized."""
    if isinstance(aufgabe, MatheAufgabe):
        return AufgabenTyp.MATHE.value, "".join(aufgabe.aufgabe.casefold().split())
    if isinstance(aufgabe, SachAufgabe):
        return AufgabenTyp.SACH.value, "".join(aufgabe.frage.casefold().split())
    ausgang, ziel = fach.sprachen
    return (
        normalisiere(aufgabe.frage.get(ausgang, ""), ausgang),
        normalisiere(aufgabe.frage.get(ziel, ""), ziel),
    )


def aufgabe_aus_zeile(
    fach: Fach, zeile: ImportZeile, *, lektion: str | None, geprueft: bool
) -> Aufgabe:
    """Create a task from a parsed line of a text import."""
    if fach.typ is AufgabenTyp.MATHE:
        return MatheAufgabe(
            fach_id=fach.id,
            aufgabe=zeile.ausgang,
            loesung=zeile.ziel,
            alternativen=list(zeile.ziel_alternativen),
            hinweis=zeile.hinweis,
            lektion=lektion,
            geprueft=geprueft,
        )
    ausgang, ziel = fach.sprachen
    return Vokabel(
        fach_id=fach.id,
        frage={ausgang: zeile.ausgang, ziel: zeile.ziel},
        alternativen={
            sprache: werte
            for sprache, werte in (
                (ausgang, zeile.ausgang_alternativen),
                (ziel, zeile.ziel_alternativen),
            )
            if werte
        },
        hinweis=zeile.hinweis,
        lektion=lektion,
        geprueft=geprueft,
    )


def parse_import(fach: Fach, inhalt: str, trennzeichen: str | None) -> Any:
    """Parse the text of an import for the type of a subject."""
    if fach.typ is AufgabenTyp.SACH:
        # Questions with model answers do not fit into lines of a list
        raise _ungueltig("import_sachfach")
    if fach.typ is AufgabenTyp.MATHE:
        return parse_mathe(inhalt, trennzeichen)
    return parse_vokabeln(inhalt, trennzeichen)


def _als_text(wert: Fraction) -> str:
    """Write an exact value the way it appears in a task."""
    return (
        str(wert.numerator)
        if wert.denominator == 1
        else f"{wert.numerator}/{wert.denominator}"
    )


def fehlerquote(aufgabe: Aufgabe) -> float | None:
    """Return the share of wrong answers of a task in percent."""
    richtig = sum(s.richtig for s in aufgabe.statistik.values())
    falsch = sum(s.falsch for s in aufgabe.statistik.values())
    if richtig + falsch == 0:
        return None
    return round(100 * falsch / (richtig + falsch), 1)


class Verwaltung:
    """Maintenance operations on the data of a manager."""

    def __init__(self, manager: LearnBuddyManager) -> None:
        """Initialize the maintenance helper."""
        self._manager = manager

    # ------------------------------------------------------------------
    # Lookups
    # ------------------------------------------------------------------

    def _fach(self, fach_id: str) -> tuple[Fach, TaskStore]:
        fach = self._manager.faecher.get(fach_id)
        if fach is None:
            raise _nicht_gefunden("fach")
        return fach, self._manager.task_stores[fach_id]

    def _aufgabe(self, store: TaskStore, aufgabe_id: str) -> Aufgabe:
        aufgabe = store.aufgaben.get(aufgabe_id)
        if aufgabe is None:
            raise _nicht_gefunden("aufgabe")
        return aufgabe

    def _arbeiten_mit(self, fach_id: str) -> dict[str, list[str]]:
        """Return for every task the upcoming exams it belongs to."""
        manager = self._manager
        heute = dt_util.now().date()
        ergebnis: dict[str, list[str]] = {}
        aufgaben = list(manager.task_stores[fach_id].aufgaben.values())
        for arbeit in manager.arbeiten.values():
            if arbeit.fach_id != fach_id or arbeit.datum < heute:
                continue
            explizit = manager.config_store.arbeit_aufgaben.get(arbeit.id, ())
            for aufgabe in aufgaben_der_arbeit(arbeit, aufgaben, explizit):
                ergebnis.setdefault(aufgabe.id, []).append(arbeit.id)
        return ergebnis

    # ------------------------------------------------------------------
    # Overview
    # ------------------------------------------------------------------

    def uebersicht(self) -> dict[str, Any]:
        """Return children, subjects and exams for the panel."""
        manager = self._manager
        return {
            "panel_version": panel_version(manager.hass),
            "kinder": [
                {
                    "id": k.id,
                    "name": k.name,
                    "bilder": manager.messenger.kann_bilder(k),
                }
                for k in manager.kinder.values()
            ],
            "faecher": [
                {
                    "id": f.id,
                    "kind_id": f.kind_id,
                    "name": f.name,
                    "typ": f.typ.value,
                    "ki": manager.ki_entity(f) is not None,
                    # Whether the AI can read photos of pages
                    "ki_bilder": manager.ki.status(manager.ki_entity(f)) == "ok",
                    # keine | nicht_verfuegbar | ohne_bilder | ok
                    "ki_status": manager.ki.status(manager.ki_entity(f)),
                    "sprachen": list(f.sprachen),
                    "lektionen": manager.lektionen(f.id),
                    "anzahl_aufgaben": len(manager.task_stores[f.id].aufgaben),
                }
                for f in manager.faecher.values()
            ],
            "arbeiten": [
                {
                    "id": a.id,
                    "fach_id": a.fach_id,
                    "art": a.art.value,
                    "datum": a.datum.isoformat(),
                    "thema": a.thema,
                    "lektionen": list(a.lektionen),
                    "abfragen_pro_tag": a.abfragen_pro_tag,
                    "start_tage_vorher": a.start_tage_vorher,
                    "intensivierung": a.intensivierung,
                    "antwortfrist_minuten": a.antwortfrist_minuten,
                    "simulation_um": None
                    if a.simulation_um is None
                    else a.simulation_um.isoformat(),
                    "simulation_anzahl": a.simulation_anzahl,
                    # False once the planned simulation was sent or skipped
                    "simulation_geplant": manager.simulation_geplant(a),
                    "aufgaben_ids": list(
                        manager.config_store.arbeit_aufgaben.get(a.id, [])
                    ),
                    # How many tasks a simulation could use, per way
                    "simulierbar": {
                        weg: len(
                            manager.simulation_auswahl(
                                a, MAX_SIM_AUFGABEN, messenger=weg == WEG_MESSENGER
                            )
                        )
                        for weg in (WEG_AUSDRUCK, WEG_MESSENGER)
                    },
                }
                for a in manager.arbeiten.values()
            ],
        }

    # ------------------------------------------------------------------
    # Dashboard
    # ------------------------------------------------------------------

    @staticmethod
    def _kennzahlen(
        aufgaben: list[Aufgabe], richtungen: tuple[str, ...]
    ) -> dict[str, Any]:
        """Return counters and the Leitner distribution of approved tasks."""
        gefragt = richtig = falsch = 0
        boxen = [0] * MAX_BOX
        for aufgabe in aufgaben:
            for stat in aufgabe.statistik.values():
                gefragt += stat.gefragt
                richtig += stat.richtig
                falsch += stat.falsch
            if not aufgabe.geprueft:
                continue
            for richtung_key in richtungen:
                stat_r = aufgabe.statistik.get(richtung_key)
                box = 1 if stat_r is None else min(max(stat_r.box, 1), MAX_BOX)
                boxen[box - 1] += 1
        bewertet = richtig + falsch
        karten = sum(boxen)
        return {
            "gefragt": gefragt,
            "richtig": richtig,
            "falsch": falsch,
            "trefferquote": None
            if not bewertet
            else round(100 * richtig / bewertet, 1),
            "boxen": boxen,
            # Share of cards that reached the upper boxes
            "sicher": None
            if not karten
            else round(100 * sum(boxen[SICHER_AB_BOX - 1 :]) / karten),
        }

    def dashboard(self, kind_id: str) -> dict[str, Any]:
        """Return the overview of a child: state, subjects, exams, statistics."""
        manager = self._manager
        if kind_id not in manager.kinder:
            raise _nicht_gefunden("kind")
        zustand = manager.zustand(kind_id)
        heute = dt_util.now().date()
        jetzt = dt_util.utcnow()
        faecher = manager.faecher_von(kind_id)

        fach_daten = []
        alle: list[Aufgabe] = []
        schwierig: list[dict[str, Any]] = []
        gesamt_boxen = [0] * MAX_BOX
        for fach in faecher:
            store = manager.task_stores[fach.id]
            aufgaben = list(store.aufgaben.values())
            alle.extend(aufgaben)
            kennzahlen = self._kennzahlen(aufgaben, fach.richtungen)
            gesamt_boxen = [
                a + b for a, b in zip(gesamt_boxen, kennzahlen["boxen"], strict=True)
            ]
            fach_daten.append(
                {
                    "id": fach.id,
                    "name": fach.name,
                    "typ": fach.typ.value,
                    "sprachen": list(fach.sprachen),
                    "ki": manager.ki_entity(fach) is not None,
                    "aufgaben": len(aufgaben),
                    "ungeprueft": sum(1 for a in aufgaben if not a.geprueft),
                    "lektionen": len(store.lektionen),
                    **kennzahlen,
                }
            )
            for aufgabe in aufgaben:
                quote = fehlerquote(aufgabe)
                if quote:
                    schwierig.append(
                        {
                            "fach_id": fach.id,
                            "fach": fach.name,
                            "frage": (
                                dict(aufgabe.frage)
                                if isinstance(aufgabe, Vokabel)
                                else None
                            ),
                            "aufgabe": (
                                None
                                if isinstance(aufgabe, Vokabel)
                                else aufgabe.frage_text(fach.richtungen[0])
                            ),
                            "fehlerquote": quote,
                            "falsch": sum(s.falsch for s in aufgabe.statistik.values()),
                        }
                    )
        schwierig.sort(key=lambda e: (-e["fehlerquote"], -e["falsch"]))

        arbeiten = []
        for arbeit in sorted(manager.arbeiten_von(kind_id), key=lambda a: a.datum):
            if arbeit.datum < heute:
                continue
            fach = manager.faecher[arbeit.fach_id]
            aufgaben = aufgaben_der_arbeit(
                arbeit,
                manager.task_stores[fach.id].aufgaben.values(),
                manager.config_store.arbeit_aufgaben.get(arbeit.id, ()),
            )
            kennzahlen = self._kennzahlen(aufgaben, fach.richtungen)
            arbeiten.append(
                {
                    "id": arbeit.id,
                    "fach_id": fach.id,
                    "fach": fach.name,
                    "art": arbeit.art.value,
                    "thema": arbeit.thema,
                    "datum": arbeit.datum.isoformat(),
                    "tage_bis": (arbeit.datum - heute).days,
                    "aufgaben": len(aufgaben),
                    "abfragen_heute": abfragen_am_tag(arbeit, heute),
                    "boxen": kennzahlen["boxen"],
                    "sicher": kennzahlen["sicher"],
                }
            )

        gefragt = sum(f["gefragt"] for f in fach_daten)
        richtig = sum(f["richtig"] for f in fach_daten)
        falsch = sum(f["falsch"] for f in fach_daten)
        teilweise = sum(s.teilweise for a in alle for s in a.statistik.values())
        offen = zustand.offene_frage
        naechste = manager.naechste_abfrage.get(kind_id)
        return {
            "kind_id": kind_id,
            "zustand": {
                "aktiv": zustand.aktiv,
                "pausiert": zustand.ist_pausiert(jetzt),
                "pausiert_bis": None
                if zustand.pausiert_bis is None or zustand.pausiert_bis <= jetzt
                else zustand.pausiert_bis.isoformat(),
                "offene_frage": None
                if offen is None
                else {
                    "fach_id": offen.fach_id,
                    "fach": manager.faecher[offen.fach_id].name,
                    "gestellt_um": offen.gestellt_um.isoformat(),
                    "timeout_um": offen.timeout_um.isoformat(),
                },
                "simulation": None
                if zustand.simulation is None
                else {
                    "arbeit_id": zustand.simulation.arbeit_id,
                    "nummer": zustand.simulation.index + 1,
                    "anzahl": len(zustand.simulation.aufgaben),
                },
                "letzte_frage_um": None
                if zustand.letzte_frage_um is None
                else zustand.letzte_frage_um.isoformat(),
                "naechste_abfrage": None if naechste is None else naechste.isoformat(),
            },
            "statistik": {
                "aufgaben": len(alle),
                "gefragt": gefragt,
                "richtig": richtig,
                "falsch": falsch,
                "teilweise": teilweise,
                "unbeantwortet": max(
                    0,
                    gefragt
                    - richtig
                    - falsch
                    - teilweise
                    - (0 if offen is None else 1),
                ),
                "trefferquote": None
                if not richtig + falsch
                else round(100 * richtig / (richtig + falsch), 1),
                "boxen": gesamt_boxen,
            },
            "faecher": fach_daten,
            "arbeiten": arbeiten,
            "schwierig": schwierig[:MAX_SCHWIERIG],
        }

    async def frage_stellen(self, kind_id: str, fach_id: str | None) -> None:
        """Ask a child a question right now, optionally of one subject."""
        manager = self._manager
        if kind_id not in manager.kinder:
            raise _nicht_gefunden("kind")
        if fach_id is not None:
            fach = manager.faecher.get(fach_id)
            if fach is None or fach.kind_id != kind_id:
                raise _nicht_gefunden("fach")
        try:
            await manager.async_frage_stellen(kind_id, fach_id)
        except ServiceValidationError as err:
            raise _ungueltig(err.translation_key or "keine_aufgaben") from err
        except HomeAssistantError as err:
            raise VerwaltungError("send_failed", "senden_fehlgeschlagen") from err

    def setze_aktiv(self, kind_id: str, aktiv: bool) -> None:
        """Enable or disable the questions of a child."""
        if kind_id not in self._manager.kinder:
            raise _nicht_gefunden("kind")
        self._manager.async_set_aktiv(kind_id, aktiv=aktiv)

    # ------------------------------------------------------------------
    # Tasks
    # ------------------------------------------------------------------

    def _aufgabe_dict(self, aufgabe: Aufgabe, arbeiten: list[str]) -> dict[str, Any]:
        return {
            **aufgabe.to_dict(),
            "fehlerquote": fehlerquote(aufgabe),
            "arbeiten": arbeiten,
        }

    def aufgaben(self, fach_id: str) -> list[dict[str, Any]]:
        """Return all tasks of a subject including statistics."""
        _, store = self._fach(fach_id)
        arbeiten = self._arbeiten_mit(fach_id)
        return [
            self._aufgabe_dict(aufgabe, arbeiten.get(aufgabe.id, []))
            for aufgabe in store.aufgaben.values()
        ]

    def _pruefe_felder(
        self,
        fach: Fach,
        daten: dict[str, Any],
        *,
        vollstaendig: bool,
        lektionen: TaskStore | None = None,
    ) -> dict[str, Any]:
        """Validate the editable fields of a task of the subject's type."""
        ergebnis: dict[str, Any] = {}
        if fach.typ is AufgabenTyp.MATHE:
            self._pruefe_mathe(daten, ergebnis, vollstaendig=vollstaendig)
        elif fach.typ is AufgabenTyp.SACH:
            self._pruefe_sach(daten, ergebnis, vollstaendig=vollstaendig)
        else:
            self._pruefe_vokabel(fach, daten, ergebnis, vollstaendig=vollstaendig)
        for feld in ("hinweis", "lektion"):
            if feld in daten:
                ergebnis[feld] = _text(daten[feld], f"{feld}_ungueltig")
        if "seite" in daten:
            seite = daten["seite"]
            if seite is not None and (
                isinstance(seite, bool)
                or not isinstance(seite, int)
                or not 1 <= seite <= MAX_SEITE
            ):
                raise _ungueltig("seite_ungueltig")
            ergebnis["seite"] = seite
        if lektionen is not None and ergebnis.get("lektion"):
            # The panel may only use lessons that were created before
            bekannt = lektionen.lektion_finden(ergebnis["lektion"])
            if bekannt is None:
                raise _ungueltig("lektion_unbekannt")
            ergebnis["lektion"] = bekannt
        if "geprueft" in daten:
            if not isinstance(daten["geprueft"], bool):
                raise _ungueltig("geprueft_ungueltig")
            ergebnis["geprueft"] = daten["geprueft"]
        return ergebnis

    def _pruefe_mathe(
        self, daten: dict[str, Any], ergebnis: dict[str, Any], *, vollstaendig: bool
    ) -> None:
        """Validate the fields that only math tasks have."""
        for feld, laenge in (("aufgabe", MAX_TEXT), ("loesung", MAX_LOESUNG)):
            if feld in daten or vollstaendig:
                wert = daten.get(feld)
                if isinstance(wert, str) and len(wert.strip()) > laenge:
                    raise _ungueltig(f"{feld}_ungueltig")
                ergebnis[feld] = _text(wert, f"{feld}_ungueltig", pflicht=True)
        for feld, anzahl, laenge in (
            ("alternativen", MAX_SCHRITTE, MAX_LOESUNG),
            ("rechenweg", MAX_SCHRITTE, MAX_TEXT),
        ):
            if feld not in daten:
                continue
            roh = daten[feld]
            if not isinstance(roh, list) or len(roh) > anzahl:
                raise _ungueltig(f"{feld}_ungueltig")
            werte = [_text(w, f"{feld}_ungueltig") for w in roh]
            if any(w is not None and len(w) > laenge for w in werte):
                raise _ungueltig(f"{feld}_ungueltig")
            ergebnis[feld] = [w for w in werte if w]
        if "bild" in daten:
            bild = daten["bild"]
            if bild is not None and self._manager.bilder.pfad(str(bild)) is None:
                raise _ungueltig("bild_unbekannt")
            ergebnis["bild"] = bild
        if "schwierigkeit" in daten:
            stufe = daten["schwierigkeit"]
            if stufe is not None and (
                isinstance(stufe, bool)
                or not isinstance(stufe, int)
                or not MIN_SCHWIERIGKEIT <= stufe <= MAX_SCHWIERIGKEIT
            ):
                raise _ungueltig("schwierigkeit_ungueltig")
            ergebnis["schwierigkeit"] = stufe

    @staticmethod
    def _pruefe_sach(
        daten: dict[str, Any], ergebnis: dict[str, Any], *, vollstaendig: bool
    ) -> None:
        """Validate the fields that only knowledge questions have."""
        for feld in ("frage", "antwort"):
            if feld in daten or vollstaendig:
                ergebnis[feld] = _text(
                    daten.get(feld), f"sach_{feld}_ungueltig", pflicht=True
                )
        if "form" in daten:
            try:
                ergebnis["form"] = SachForm(daten["form"])
            except ValueError as err:
                raise _ungueltig("form_ungueltig") from err
        for feld, anzahl in (
            ("kernpunkte", MAX_KERNPUNKTE),
            ("falsche_optionen", MAX_FALSCHE_OPTIONEN),
        ):
            if feld not in daten:
                continue
            roh = daten[feld]
            if not isinstance(roh, list) or len(roh) > anzahl:
                raise _ungueltig(f"{feld}_ungueltig")
            werte = [_text(w, f"{feld}_ungueltig") for w in roh]
            if any(w is not None and len(w) > MAX_OPTION for w in werte):
                raise _ungueltig(f"{feld}_ungueltig")
            ergebnis[feld] = [w for w in werte if w]
        if "stelle" in daten:
            stelle = _text(daten["stelle"], "stelle_ungueltig")
            if stelle is not None and len(stelle) > MAX_STELLE:
                raise _ungueltig("stelle_ungueltig")
            ergebnis["stelle"] = stelle

    @staticmethod
    def _pruefe_auswahl(form: SachForm, antwort: str, falsche: list[str]) -> None:
        """Check that a choice question has usable options."""
        if form is not SachForm.AUSWAHL:
            return
        gesehen = {antwort.casefold()}
        for option in falsche:
            if option.casefold() in gesehen:
                raise _ungueltig("falsche_optionen_ungueltig")
            gesehen.add(option.casefold())
        if len(falsche) < MIN_FALSCHE_OPTIONEN:
            raise _ungueltig("falsche_optionen_ungueltig")

    @staticmethod
    def _pruefe_vokabel(
        fach: Fach,
        daten: dict[str, Any],
        ergebnis: dict[str, Any],
        *,
        vollstaendig: bool,
    ) -> None:
        """Validate the fields that only vocabulary tasks have."""
        sprachen = fach.sprachen
        if "frage" in daten or vollstaendig:
            frage = daten.get("frage")
            if not isinstance(frage, dict) or set(frage) - set(sprachen):
                raise _ungueltig("frage_ungueltig")
            werte = {
                sprache: _text(frage.get(sprache), "frage_ungueltig", pflicht=True)
                for sprache in sprachen
                if vollstaendig or sprache in frage
            }
            ergebnis["frage"] = werte
        if "alternativen" in daten:
            alternativen = daten["alternativen"]
            if not isinstance(alternativen, dict) or set(alternativen) - set(sprachen):
                raise _ungueltig("alternativen_ungueltig")
            bereinigt: dict[str, list[str]] = {}
            for sprache, werte_roh in alternativen.items():
                if not isinstance(werte_roh, list):
                    raise _ungueltig("alternativen_ungueltig")
                werte_liste = [
                    wert
                    for wert in (_text(w, "alternativen_ungueltig") for w in werte_roh)
                    if wert
                ]
                if werte_liste:
                    bereinigt[sprache] = werte_liste
            ergebnis["alternativen"] = bereinigt

    def aufgabe_anlegen(self, fach_id: str, daten: dict[str, Any]) -> dict[str, Any]:
        """Create a single task."""
        fach, store = self._fach(fach_id)
        felder = self._pruefe_felder(fach, daten, vollstaendig=True, lektionen=store)
        aufgabe: Aufgabe
        if fach.typ is AufgabenTyp.MATHE:
            aufgabe = MatheAufgabe(fach_id=fach_id, quelle=Quelle.MANUELL, **felder)
        elif fach.typ is AufgabenTyp.SACH:
            aufgabe = SachAufgabe(fach_id=fach_id, quelle=Quelle.MANUELL, **felder)
            self._pruefe_auswahl(
                aufgabe.form, aufgabe.antwort, aufgabe.falsche_optionen
            )
        else:
            aufgabe = Vokabel(fach_id=fach_id, quelle=Quelle.MANUELL, **felder)
        store.add(aufgabe)
        self._gespeichert(fach, store)
        return self._aufgabe_dict(
            aufgabe, self._arbeiten_mit(fach_id).get(aufgabe.id, [])
        )

    def aufgabe_aendern(
        self, fach_id: str, aufgabe_id: str, daten: dict[str, Any]
    ) -> dict[str, Any]:
        """Change fields of a task."""
        fach, store = self._fach(fach_id)
        aufgabe = self._aufgabe(store, aufgabe_id)
        felder = self._pruefe_felder(fach, daten, vollstaendig=False, lektionen=store)
        if isinstance(aufgabe, Vokabel):
            if "frage" in felder:
                aufgabe.frage = {**aufgabe.frage, **felder.pop("frage")}
        elif isinstance(aufgabe, SachAufgabe):
            self._pruefe_auswahl(
                felder.get("form", aufgabe.form),
                felder.get("antwort", aufgabe.antwort),
                felder.get("falsche_optionen", aufgabe.falsche_optionen),
            )
        elif "aufgabe" in felder or "loesung" in felder:
            # A changed task is no longer the one that was verified
            aufgabe.verifikation = Verifikation.KEINE
            aufgabe.vorschlag = None
            aufgabe.vorschlag_durch = None
        for feld, wert in felder.items():
            setattr(aufgabe, feld, wert)
        aufgabe.geaendert = dt_util.utcnow()
        self._gespeichert(fach, store)
        self._bilder_aufraeumen()
        return self._aufgabe_dict(
            aufgabe, self._arbeiten_mit(fach_id).get(aufgabe.id, [])
        )

    def aufgaben_loeschen(
        self, fach_id: str, aufgabe_ids: list[str], *, bestaetigt: bool
    ) -> dict[str, Any]:
        """Delete tasks.

        If a task belongs to an upcoming exam nothing is deleted unless the
        request is confirmed; the affected exams are returned instead.
        """
        fach, store = self._fach(fach_id)
        manager = self._manager
        ids = [i for i in aufgabe_ids if i in store.aufgaben]
        arbeiten = self._arbeiten_mit(fach_id)
        zugeordnet = {i: arbeiten[i] for i in ids if i in arbeiten}
        if zugeordnet and not bestaetigt:
            return {"geloescht": 0, "zugeordnet": zugeordnet}

        for aufgabe_id in ids:
            store.remove(aufgabe_id)
        entfernt = set(ids)
        for arbeit_id, explizit in manager.config_store.arbeit_aufgaben.items():
            manager.config_store.arbeit_aufgaben[arbeit_id] = [
                i for i in explizit if i not in entfernt
            ]
        manager.async_frage_verwerfen(fach.kind_id, entfernt)
        manager.config_store.async_schedule_save()
        self._gespeichert(fach, store)
        self._bilder_aufraeumen()
        return {"geloescht": len(ids), "zugeordnet": {}}

    def _bilder_aufraeumen(self, sofort: Iterable[str] = ()) -> None:
        """Delete images that no task refers to any more.

        Fresh uploads are spared for a while, except the ones given in
        ``sofort``: they were only needed for a single run of the AI.
        """
        manager = self._manager
        verwendet = manager.verwendete_bilder()
        ungenutzt = [bild for bild in sofort if bild not in verwendet]
        if ungenutzt:
            manager.hass.async_create_task(
                manager.bilder.async_loesche(ungenutzt),
                "learnbuddy image removal",
            )
        manager.hass.async_create_task(
            manager.bilder.async_raeume_auf(verwendet),
            "learnbuddy image cleanup",
        )

    def _gespeichert(self, fach: Fach, store: TaskStore) -> None:
        store.async_schedule_save()
        self._manager.async_benachrichtige(fach.kind_id)

    # ------------------------------------------------------------------
    # Lessons
    # ------------------------------------------------------------------

    def lektion_hinzufuegen(self, fach_id: str, name: Any) -> list[str]:
        """Create a lesson (or topic) of a subject."""
        fach, store = self._fach(fach_id)
        bereinigt = _text(name, "lektion_leer", pflicht=True)
        if bereinigt is None or len(bereinigt) > MAX_LEKTION:
            raise _ungueltig("lektion_ungueltig")
        if not store.lektion_hinzufuegen(bereinigt):
            raise _ungueltig("lektion_vorhanden")
        self._gespeichert(fach, store)
        return list(store.lektionen)

    def lektion_loeschen(self, fach_id: str, name: str) -> list[str]:
        """Delete a lesson that no task uses any more."""
        fach, store = self._fach(fach_id)
        bekannt = store.lektion_finden(name)
        if bekannt is None:
            raise _nicht_gefunden("lektion")
        if store.lektion_verwendet(bekannt):
            raise _ungueltig("lektion_verwendet")
        store.lektion_entfernen(bekannt)
        self._gespeichert(fach, store)
        # Exams must not keep pointing to the deleted lesson
        entry = self._manager.entry
        for subentry in list(entry.subentries.values()):
            if (
                subentry.subentry_type == SUBENTRY_ARBEIT
                and subentry.data[CONF_FACH_ID] == fach_id
                and bekannt in subentry.data.get(CONF_LEKTIONEN, [])
            ):
                self._manager.hass.config_entries.async_update_subentry(
                    entry,
                    subentry,
                    data={
                        **subentry.data,
                        CONF_LEKTIONEN: [
                            x for x in subentry.data[CONF_LEKTIONEN] if x != bekannt
                        ],
                    },
                )
        return list(store.lektionen)

    # ------------------------------------------------------------------
    # Import and export
    # ------------------------------------------------------------------

    def import_text(
        self,
        fach_id: str,
        inhalt: str,
        *,
        lektion: str | None,
        trennzeichen: str | None,
        geprueft: bool,
        vorschau: bool,
    ) -> dict[str, Any]:
        """Preview a list of tasks or import it."""
        _, store = self._fach(fach_id)
        if vorschau:
            return self.import_vorschau(fach_id, inhalt, trennzeichen)
        if lektion and lektion.strip():
            lektion = store.lektion_finden(lektion)
            if lektion is None:
                raise _ungueltig("lektion_unbekannt")
        try:
            return self._manager.async_importiere(
                fach_id,
                inhalt,
                lektion=lektion,
                trennzeichen=trennzeichen,
                geprueft=geprueft,
            )
        except ServiceValidationError as err:
            raise _ungueltig(err.translation_key or "import_leer") from err

    def import_vorschau(
        self, fach_id: str, inhalt: str, trennzeichen: str | None
    ) -> dict[str, Any]:
        """Parse a list of tasks without storing anything."""
        fach, store = self._fach(fach_id)
        vorhanden = self._schluessel_menge(fach, store)
        geparst = parse_import(fach, inhalt, trennzeichen)
        zeilen = []
        for zeile in geparst.zeilen:
            aufgabe = aufgabe_aus_zeile(fach, zeile, lektion=None, geprueft=True)
            schluessel = aufgabe_schluessel(fach, aufgabe)
            daten = aufgabe.to_dict()
            felder = (
                ("aufgabe", "loesung", "alternativen", "hinweis")
                if isinstance(aufgabe, MatheAufgabe)
                else ("frage", "alternativen", "hinweis")
            )
            zeilen.append(
                {
                    **{feld: daten[feld] for feld in felder},
                    "vorhanden": schluessel in vorhanden,
                }
            )
            vorhanden.add(schluessel)
        return {"zeilen": zeilen, "fehlerzeilen": geparst.fehlerzeilen}

    @staticmethod
    def _schluessel_menge(fach: Fach, store: TaskStore) -> set[tuple[str, str]]:
        return {aufgabe_schluessel(fach, a) for a in store.aufgaben.values()}

    def export(self, fach_id: str, *, mit_statistik: bool) -> dict[str, Any]:
        """Export the tasks of a subject without any data about the child."""
        fach, store = self._fach(fach_id)
        aufgaben = []
        ohne_bild = 0
        for aufgabe in store.aufgaben.values():
            if isinstance(aufgabe, MatheAufgabe) and aufgabe.bild:
                # The image file is not part of the export
                ohne_bild += 1
                continue
            daten = aufgabe.to_dict()
            del daten["fach_id"]
            daten.pop("bild", None)
            daten.pop("quelle_bild", None)
            daten.pop("vorschlag", None)
            daten.pop("vorschlag_durch", None)
            if not mit_statistik:
                del daten["statistik"]
            aufgaben.append(daten)
        return {
            "format": EXPORT_FORMAT,
            "version": EXPORT_VERSION,
            "fach": fach.name,
            "typ": fach.typ.value,
            "sprachen": list(fach.sprachen),
            "exportiert": dt_util.utcnow().isoformat(),
            "ausgelassen_mit_bild": ohne_bild,
            "aufgaben": aufgaben,
        }

    def import_json(
        self,
        fach_id: str,
        daten: Any,
        *,
        mit_statistik: bool,
        lektion: str | None = None,
    ) -> dict[str, Any]:
        """Import tasks from an export; existing tasks are kept.

        Without ``lektion`` every task keeps the lesson from the file. With it
        all imported tasks are assigned to that existing lesson.
        """
        fach, store = self._fach(fach_id)
        ziel_lektion: str | None = None
        if lektion and lektion.strip():
            ziel_lektion = store.lektion_finden(lektion)
            if ziel_lektion is None:
                raise _ungueltig("lektion_unbekannt")
        if (
            not isinstance(daten, dict)
            or daten.get("format") not in (EXPORT_FORMAT, *ALTE_EXPORT_FORMATE)
            or not isinstance(daten.get("aufgaben"), list)
        ):
            raise _ungueltig("export_ungueltig")
        if daten.get("version") != EXPORT_VERSION:
            raise _ungueltig("export_version")
        mathe = fach.typ is AufgabenTyp.MATHE
        if daten.get("typ", AufgabenTyp.VOKABEL.value) != fach.typ.value:
            raise _ungueltig("export_typ")
        sach = fach.typ is AufgabenTyp.SACH
        if (
            not mathe
            and not sach
            and sorted(daten.get("sprachen") or []) != sorted(fach.sprachen)
        ):
            raise _ungueltig("export_sprachen")

        erlaubt = (
            (
                "aufgabe",
                "loesung",
                "alternativen",
                "rechenweg",
                "schwierigkeit",
                "hinweis",
                "seite",
                "lektion",
                "geprueft",
            )
            if mathe
            else (
                "frage",
                "antwort",
                "form",
                "kernpunkte",
                "falsche_optionen",
                "stelle",
                "hinweis",
                "seite",
                "lektion",
                "geprueft",
            )
            if sach
            else ("frage", "alternativen", "hinweis", "seite", "lektion", "geprueft")
        )
        vorhanden = self._schluessel_menge(fach, store)
        importiert = uebersprungen = 0
        fehler: list[int] = []
        for index, roh in enumerate(daten["aufgaben"]):
            try:
                if not isinstance(roh, dict):
                    raise _ungueltig("export_ungueltig")
                felder = self._pruefe_felder(
                    fach, {k: roh[k] for k in erlaubt if k in roh}, vollstaendig=True
                )
                statistik = (
                    {
                        key: Statistik.from_dict(wert)
                        for key, wert in roh.get("statistik", {}).items()
                        if key in fach.richtungen
                    }
                    if mit_statistik
                    else {}
                )
                quelle = Quelle(roh.get("quelle", Quelle.MANUELL))
                if ziel_lektion is not None:
                    felder["lektion"] = ziel_lektion
                aufgabe: Aufgabe
                if mathe:
                    aufgabe = MatheAufgabe(
                        fach_id=fach_id,
                        quelle=quelle,
                        statistik=statistik,
                        verifikation=Verifikation(
                            roh.get("verifikation", Verifikation.KEINE)
                        ),
                        **felder,
                    )
                elif sach:
                    aufgabe = SachAufgabe(
                        fach_id=fach_id, quelle=quelle, statistik=statistik, **felder
                    )
                    self._pruefe_auswahl(
                        aufgabe.form, aufgabe.antwort, aufgabe.falsche_optionen
                    )
                else:
                    aufgabe = Vokabel(
                        fach_id=fach_id, quelle=quelle, statistik=statistik, **felder
                    )
            except VerwaltungError, ValueError, TypeError, AttributeError:
                fehler.append(index)
                continue
            schluessel = aufgabe_schluessel(fach, aufgabe)
            if schluessel in vorhanden:
                uebersprungen += 1
                continue
            vorhanden.add(schluessel)
            store.add(aufgabe)
            importiert += 1
        if importiert:
            self._gespeichert(fach, store)
        return {
            "importiert": importiert,
            "uebersprungen": uebersprungen,
            "fehler": fehler,
        }

    # ------------------------------------------------------------------
    # Generating math tasks
    # ------------------------------------------------------------------

    async def generiere(
        self,
        fach_id: str,
        *,
        anzahl: int,
        lektion: str | None = None,
        schwierigkeit: int | None = None,
        beschreibung: str | None = None,
        beispiel_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        """Let the AI create math tasks similar to existing ones.

        Only tasks whose solution could be verified are stored. They wait for
        approval unless the user chose otherwise.
        """
        manager = self._manager
        fach, store = self._fach(fach_id)
        if fach.typ is not AufgabenTyp.MATHE:
            raise _ungueltig("generieren_nur_mathe")
        ki_entity = self._ki(fach)
        if not 1 <= anzahl <= MAX_GENERIEREN:
            raise _ungueltig("anzahl_ungueltig")
        if schwierigkeit is not None and not (
            MIN_SCHWIERIGKEIT <= schwierigkeit <= MAX_SCHWIERIGKEIT
        ):
            raise _ungueltig("schwierigkeit_ungueltig")
        beschreibung = _text(beschreibung, "beschreibung_ungueltig")
        thema: str | None = None
        if lektion and lektion.strip():
            thema = store.lektion_finden(lektion)
            if thema is None:
                raise _ungueltig("lektion_unbekannt")

        # Tasks about an image make no sense as examples without it
        mathe = [
            a
            for a in store.aufgaben.values()
            if isinstance(a, MatheAufgabe) and not a.bild
        ]
        gewaehlt = set(beispiel_ids or ())
        beispiele = [a for a in mathe if a.id in gewaehlt]
        if not beispiele:
            beispiele = [a for a in mathe if thema is None or a.lektion == thema]
        if not beispiele and not thema and not beschreibung:
            raise _ungueltig("generieren_ohne_vorgabe")

        # Lazy import: the AI module is only needed here
        from .ai import baue_generieren_prompt  # noqa: PLC0415

        kind = manager.kinder[fach.kind_id]
        prompt = baue_generieren_prompt(
            thema=thema,
            anzahl=anzahl,
            schwierigkeit=schwierigkeit,
            beschreibung=beschreibung,
            beispiele=[(a.aufgabe, a.loesung) for a in beispiele[:MAX_BEISPIELE]],
            klassenstufe=kind.klassenstufe,
            schulart=kind.schulart,
            bundesland=kind.bundesland,
            sprache=manager.sprache,
        )
        vorschlaege = await manager.ki.async_generiere(ki_entity, prompt)
        if vorschlaege is None:
            raise VerwaltungError("home_assistant_error", manager.ki.fehler_schluessel)

        sperre = asyncio.Semaphore(PARALLEL_PRUEFEN)

        async def _pruefe(vorschlag: GenerierteAufgabe) -> Verifikation | None:
            async with sperre:
                return await self._verifiziere(ki_entity, vorschlag)

        ergebnisse = await asyncio.gather(*(_pruefe(v) for v in vorschlaege[:anzahl]))

        return self._speichere_generierte(
            fach_id,
            list(zip(vorschlaege[:anzahl], ergebnisse, strict=True)),
            thema=thema,
            schwierigkeit=schwierigkeit,
        )

    def _ki(self, fach: Fach, *, bilder: bool = False) -> str:
        """Return the AI entity of a subject or say why it cannot be used."""
        manager = self._manager
        ki_entity = manager.ki_entity(fach)
        if not ki_entity:
            raise _ungueltig("ki_fehlt")
        if not manager.ki.verfuegbar(ki_entity):
            raise _ungueltig("ki_nicht_verfuegbar")
        if bilder and not manager.ki.kann_bilder(ki_entity):
            raise _ungueltig("ki_ohne_bilder")
        return ki_entity

    def _pruefe_seiten(self, fach: Fach, seiten: list[str]) -> str:
        """Check that the AI of a subject can read the given pages."""
        manager = self._manager
        ki_entity = self._ki(fach, bilder=True)
        if (
            not 1 <= len(seiten) <= MAX_SEITEN
            or len(set(seiten)) != len(seiten)
            or any(manager.bilder.pfad(seite) is None for seite in seiten)
        ):
            raise _ungueltig("seiten_ungueltig")
        return ki_entity

    async def foto_auslesen(self, fach_id: str, seiten: list[str]) -> dict[str, Any]:
        """Read tasks from photos of book pages; nothing is stored.

        Returns a preview the user checks before taking the tasks over. The
        photos are deleted afterwards.
        """
        manager = self._manager
        fach, store = self._fach(fach_id)
        try:
            if fach.typ is AufgabenTyp.SACH:
                raise _ungueltig("foto_sachfach")
            ki_entity = self._pruefe_seiten(fach, seiten)

            # Lazy import: the AI module is only needed here
            from .ai import (  # noqa: PLC0415
                baue_foto_mathe_prompt,
                baue_foto_vokabeln_prompt,
            )

            vorhanden = self._schluessel_menge(fach, store)
            zeilen: list[dict[str, Any]] = []
            if fach.typ is AufgabenTyp.MATHE:
                gelesen = await manager.ki.async_lies_mathe(
                    ki_entity, baue_foto_mathe_prompt(), seiten
                )
                if gelesen is None:
                    raise VerwaltungError(
                        "home_assistant_error", manager.ki.fehler_schluessel
                    )
                aufgaben = [
                    MatheAufgabe(fach_id=fach_id, aufgabe=g.aufgabe, loesung=g.loesung)
                    for g in gelesen
                ]
                sperre = asyncio.Semaphore(PARALLEL_PRUEFEN)

                async def _pruefe(
                    aufgabe: MatheAufgabe, braucht_bild: bool
                ) -> tuple[Verifikation, str | None, str]:
                    if braucht_bild:
                        # Without the figure nobody can check the result
                        return Verifikation.KEINE, None, "lokal"
                    async with sperre:
                        return await self._rechne_nach(ki_entity, aufgabe)

                ergebnisse = await asyncio.gather(
                    *(
                        _pruefe(a, g.braucht_bild)
                        for a, g in zip(aufgaben, gelesen, strict=True)
                    )
                )
                for mathe, g, (verifikation, berechnet, durch) in zip(
                    aufgaben, gelesen, ergebnisse, strict=True
                ):
                    schluessel = aufgabe_schluessel(fach, mathe)
                    zeilen.append(
                        {
                            "aufgabe": g.aufgabe,
                            "loesung": g.loesung,
                            "seite": g.seite,
                            "braucht_bild": g.braucht_bild,
                            "verifikation": verifikation.value,
                            "vorschlag": berechnet,
                            "vorschlag_durch": durch if berechnet else None,
                            "vorhanden": schluessel in vorhanden,
                        }
                    )
                    vorhanden.add(schluessel)
            else:
                ausgang, ziel = fach.sprachen
                vokabeln = await manager.ki.async_lies_vokabeln(
                    ki_entity,
                    baue_foto_vokabeln_prompt(ausgang=ausgang, ziel=ziel),
                    seiten,
                )
                if vokabeln is None:
                    raise VerwaltungError(
                        "home_assistant_error", manager.ki.fehler_schluessel
                    )
                for v in vokabeln:
                    vokabel = Vokabel(
                        fach_id=fach_id, frage={ausgang: v.ausgang, ziel: v.ziel}
                    )
                    schluessel = aufgabe_schluessel(fach, vokabel)
                    zeilen.append(
                        {
                            "frage": dict(vokabel.frage),
                            "alternativen": {
                                sprache: werte
                                for sprache, werte in (
                                    (ausgang, v.ausgang_weitere),
                                    (ziel, v.ziel_weitere),
                                )
                                if werte
                            },
                            "hinweis": v.hinweis,
                            "seite": v.seite,
                            "vorhanden": schluessel in vorhanden,
                        }
                    )
                    vorhanden.add(schluessel)
            return {"typ": fach.typ.value, "zeilen": zeilen}
        finally:
            self._bilder_aufraeumen(sofort=seiten)

    def foto_uebernehmen(
        self, fach_id: str, zeilen: list[Any], *, lektion: str | None = None
    ) -> dict[str, Any]:
        """Store the tasks the user took over from the preview of a photo."""
        fach, store = self._fach(fach_id)
        if fach.typ is AufgabenTyp.SACH:
            raise _ungueltig("foto_sachfach")
        if not zeilen or len(zeilen) > MAX_FOTO_ZEILEN:
            raise _ungueltig("auswahl_ungueltig")
        ziel_lektion: str | None = None
        if lektion and lektion.strip():
            ziel_lektion = store.lektion_finden(lektion)
            if ziel_lektion is None:
                raise _ungueltig("lektion_unbekannt")
        mathe = fach.typ is AufgabenTyp.MATHE
        erlaubt = (
            ("aufgabe", "loesung", "seite")
            if mathe
            else ("frage", "alternativen", "hinweis", "seite")
        )
        vorhanden = self._schluessel_menge(fach, store)
        importiert = uebersprungen = 0
        fehler: list[int] = []
        for index, roh in enumerate(zeilen):
            try:
                if not isinstance(roh, dict):
                    raise _ungueltig("auswahl_ungueltig")
                felder = self._pruefe_felder(
                    fach, {k: roh[k] for k in erlaubt if k in roh}, vollstaendig=True
                )
                aufgabe: Aufgabe
                if mathe:
                    bestaetigt = roh.get("verifikation")
                    aufgabe = MatheAufgabe(
                        fach_id=fach_id,
                        quelle=Quelle.UPLOAD,
                        lektion=ziel_lektion,
                        verifikation=(
                            Verifikation(bestaetigt)
                            if bestaetigt in (Verifikation.RECHNERISCH, Verifikation.KI)
                            else Verifikation.KEINE
                        ),
                        **felder,
                    )
                else:
                    aufgabe = Vokabel(
                        fach_id=fach_id,
                        quelle=Quelle.UPLOAD,
                        lektion=ziel_lektion,
                        **felder,
                    )
            except VerwaltungError, ValueError, TypeError, AttributeError:
                fehler.append(index)
                continue
            schluessel = aufgabe_schluessel(fach, aufgabe)
            if schluessel in vorhanden:
                uebersprungen += 1
                continue
            vorhanden.add(schluessel)
            store.add(aufgabe)
            importiert += 1
        if importiert:
            self._gespeichert(fach, store)
        return {
            "importiert": importiert,
            "uebersprungen": uebersprungen,
            "fehler": fehler,
        }

    async def fragen_aus_seiten(
        self,
        fach_id: str,
        *,
        seiten: list[str],
        anzahl: int,
        form: str | None = None,
        lektion: str | None = None,
        schwerpunkt: str | None = None,
    ) -> dict[str, Any]:
        """Let the AI create questions about photographed pages of a book.

        The questions always wait for approval: nothing can verify them.
        """
        manager = self._manager
        fach, store = self._fach(fach_id)
        try:
            if fach.typ is not AufgabenTyp.SACH:
                raise _ungueltig("seiten_nur_sachfach")
            ki_entity = self._pruefe_seiten(fach, seiten)
            if not 1 <= anzahl <= MAX_SACHFRAGEN:
                raise _ungueltig("anzahl_ungueltig")
            if form not in (None, FORM_GEMISCHT, *(f.value for f in SachForm)):
                raise _ungueltig("form_ungueltig")
            schwerpunkt = _text(schwerpunkt, "beschreibung_ungueltig")
            thema: str | None = None
            if lektion and lektion.strip():
                thema = store.lektion_finden(lektion)
                if thema is None:
                    raise _ungueltig("lektion_unbekannt")

            # Lazy import: the AI module is only needed here
            from .ai import baue_sachfragen_prompt  # noqa: PLC0415

            kind = manager.kinder[fach.kind_id]
            prompt = baue_sachfragen_prompt(
                anzahl=anzahl,
                form=form or FORM_GEMISCHT,
                thema=thema,
                schwerpunkt=schwerpunkt,
                klassenstufe=kind.klassenstufe,
                schulart=kind.schulart,
                sprache=manager.sprache,
            )
            vorschlaege = await manager.ki.async_erzeuge_sachfragen(
                ki_entity, prompt, seiten
            )
            if vorschlaege is None:
                raise VerwaltungError(
                    "home_assistant_error", manager.ki.fehler_schluessel
                )

            # The subject may have been removed while the AI was working
            fach, store = self._fach(fach_id)
            vorhanden = self._schluessel_menge(fach, store)
            erzeugt: list[str] = []
            uebersprungen = 0
            for vorschlag in vorschlaege[:anzahl]:
                aufgabe = SachAufgabe(
                    fach_id=fach_id,
                    frage=vorschlag.frage,
                    antwort=vorschlag.antwort,
                    form=vorschlag.form,
                    kernpunkte=list(vorschlag.kernpunkte),
                    falsche_optionen=list(vorschlag.falsche_optionen),
                    stelle=vorschlag.stelle,
                    quelle_bild=seiten[
                        (vorschlag.seite or 1) - 1
                        if (vorschlag.seite or 1) <= len(seiten)
                        else 0
                    ],
                    lektion=thema,
                    quelle=Quelle.GENERIERT,
                    geprueft=False,
                )
                schluessel = aufgabe_schluessel(fach, aufgabe)
                if schluessel in vorhanden:
                    uebersprungen += 1
                    continue
                vorhanden.add(schluessel)
                store.add(aufgabe)
                erzeugt.append(aufgabe.id)
            if erzeugt:
                self._gespeichert(fach, store)
            return {
                "erzeugt": len(erzeugt),
                # What the AI returned but could not be used
                "verworfen": max(0, anzahl - len(vorschlaege)),
                "uebersprungen": uebersprungen,
                "aufgabe_ids": erzeugt,
            }
        finally:
            # Pages no question refers to are not kept
            self._bilder_aufraeumen(sofort=seiten)

    def _speichere_generierte(
        self,
        fach_id: str,
        geprueft: list[tuple[GenerierteAufgabe, Verifikation | None]],
        *,
        thema: str | None,
        schwierigkeit: int | None,
    ) -> dict[str, Any]:
        """Store the generated tasks whose solution was verified."""
        # The subject may have been removed while the AI was working
        fach, store = self._fach(fach_id)
        vorhanden = self._schluessel_menge(fach, store)
        erzeugt: list[str] = []
        verworfen = uebersprungen = 0
        for vorschlag, verifikation in geprueft:
            if verifikation is None:
                verworfen += 1
                continue
            aufgabe = MatheAufgabe(
                fach_id=fach_id,
                aufgabe=vorschlag.aufgabe,
                loesung=vorschlag.loesung,
                rechenweg=list(vorschlag.rechenweg),
                schwierigkeit=vorschlag.schwierigkeit or schwierigkeit,
                verifikation=verifikation,
                lektion=thema,
                quelle=Quelle.GENERIERT,
                geprueft=self._manager.auto_freigabe,
            )
            schluessel = aufgabe_schluessel(fach, aufgabe)
            if schluessel in vorhanden:
                uebersprungen += 1
                continue
            vorhanden.add(schluessel)
            store.add(aufgabe)
            erzeugt.append(aufgabe.id)
        if erzeugt:
            self._gespeichert(fach, store)
        return {
            "erzeugt": len(erzeugt),
            "verworfen": verworfen,
            "uebersprungen": uebersprungen,
            "aufgabe_ids": erzeugt,
        }

    async def _verifiziere(
        self, ki_entity: str, vorschlag: GenerierteAufgabe
    ) -> Verifikation | None:
        """Verify the solution of a generated task; None if it does not hold.

        The calculation given by the AI is evaluated locally. If that is not
        possible, the AI solves the task again without knowing the solution.
        """
        soll = zerlege(vorschlag.loesung)
        if soll is not None and vorschlag.rechnung:
            wert = berechne(vorschlag.rechnung)
            if wert is not None:
                return Verifikation.RECHNERISCH if wert == soll[0] else None
        zweite = await self._manager.ki.async_loese(
            ki_entity, aufgabe=vorschlag.aufgabe
        )
        if zweite is None:
            return None
        gleich = (Ergebnis.RICHTIG, Ergebnis.FAST_RICHTIG)
        if (
            bewerte_mathe(zweite, vorschlag.loesung) in gleich
            or bewerte_mathe(vorschlag.loesung, zweite) in gleich
        ):
            return Verifikation.KI
        return None

    async def nachrechnen(self, fach_id: str, aufgabe_ids: list[str]) -> dict[str, Any]:
        """Check the stored solutions of math tasks.

        A task that is a plain calculation is evaluated locally. Otherwise
        the AI solves it without knowing the solution. Deviations are marked
        at the task and returned, nothing else is changed.
        """
        manager = self._manager
        fach, store = self._fach(fach_id)
        if fach.typ is not AufgabenTyp.MATHE:
            raise _ungueltig("nachrechnen_nur_mathe")
        if not aufgabe_ids or len(aufgabe_ids) > MAX_NACHRECHNEN:
            raise _ungueltig("auswahl_ungueltig")
        gewaehlt = set(aufgabe_ids)
        aufgaben = [
            a
            for a in store.aufgaben.values()
            if a.id in gewaehlt and isinstance(a, MatheAufgabe)
        ]
        ki_entity = manager.ki_entity(fach)
        sperre = asyncio.Semaphore(PARALLEL_PRUEFEN)

        async def _pruefe(
            aufgabe: MatheAufgabe,
        ) -> tuple[Verifikation, str | None, str]:
            async with sperre:
                return await self._rechne_nach(ki_entity, aufgabe)

        ergebnisse = await asyncio.gather(*(_pruefe(a) for a in aufgaben))

        bestaetigt = offen = 0
        abweichend: list[dict[str, Any]] = []
        for aufgabe, (verifikation, berechnet, durch) in zip(
            aufgaben, ergebnisse, strict=True
        ):
            if aufgabe.id not in store.aufgaben:
                # Deleted while the AI was working
                continue
            if verifikation is Verifikation.KEINE:
                offen += 1
                continue
            aufgabe.verifikation = verifikation
            abweichung = verifikation is Verifikation.ABWEICHUNG
            # The result that was found can be taken over later
            aufgabe.vorschlag = berechnet if abweichung else None
            aufgabe.vorschlag_durch = durch if abweichung else None
            if abweichung:
                abweichend.append(
                    {
                        "id": aufgabe.id,
                        "aufgabe": aufgabe.aufgabe,
                        "loesung": aufgabe.loesung,
                        "berechnet": berechnet,
                        # The AI can be wrong, a local calculation cannot
                        "durch": durch,
                    }
                )
            else:
                bestaetigt += 1
        if bestaetigt or abweichend:
            self._gespeichert(fach, store)
        return {
            "bestaetigt": bestaetigt,
            "abweichend": abweichend,
            "nicht_pruefbar": offen,
        }

    async def rechenwege_erzeugen(
        self, fach_id: str, aufgabe_ids: list[str]
    ) -> dict[str, Any]:
        """Let the AI write the solution steps of math tasks that have none.

        Tasks whose solution was found to deviate are left out: the steps
        would lead to a result that is probably wrong.
        """
        manager = self._manager
        fach, store = self._fach(fach_id)
        if fach.typ is not AufgabenTyp.MATHE:
            raise _ungueltig("rechenweg_nur_mathe")
        if not aufgabe_ids or len(aufgabe_ids) > MAX_NACHRECHNEN:
            raise _ungueltig("auswahl_ungueltig")
        ki_entity = self._ki(fach)
        gewaehlt = set(aufgabe_ids)
        mathe = [
            a
            for a in store.aufgaben.values()
            if a.id in gewaehlt and isinstance(a, MatheAufgabe)
        ]
        vorhanden = sum(1 for a in mathe if a.rechenweg)
        abweichend = sum(
            1
            for a in mathe
            if not a.rechenweg and a.verifikation is Verifikation.ABWEICHUNG
        )
        offen = [
            a
            for a in mathe
            if not a.rechenweg and a.verifikation is not Verifikation.ABWEICHUNG
        ]
        sperre = asyncio.Semaphore(PARALLEL_PRUEFEN)
        sprache = waehle_sprache(manager.sprache)

        async def _erzeuge(aufgabe: MatheAufgabe) -> list[str] | None:
            async with sperre:
                return await manager.ki.async_rechenweg(
                    ki_entity,
                    aufgabe=aufgabe.aufgabe,
                    loesung=aufgabe.loesung,
                    sprache=sprache,
                    bild=aufgabe.bild,
                )

        # The solution may change while the AI is working
        loesungen = {a.id: a.loesung for a in offen}
        ergebnisse = await asyncio.gather(*(_erzeuge(a) for a in offen))
        erzeugt = fehlgeschlagen = 0
        for aufgabe, schritte in zip(offen, ergebnisse, strict=True):
            if (
                not schritte
                or aufgabe.id not in store.aufgaben
                or aufgabe.loesung != loesungen[aufgabe.id]
            ):
                fehlgeschlagen += 1
                continue
            aufgabe.rechenweg = schritte
            erzeugt += 1
        if erzeugt:
            self._gespeichert(fach, store)
        return {
            "erzeugt": erzeugt,
            "vorhanden": vorhanden,
            "abweichend": abweichend,
            "fehlgeschlagen": fehlgeschlagen,
        }

    def vorschlag_uebernehmen(
        self, fach_id: str, aufgabe_ids: list[str]
    ) -> dict[str, Any]:
        """Replace the solution of tasks by the result found when recalculating.

        Everything that belonged to the old solution goes with it: other
        spellings that do not match, the solution steps and the statistics,
        because the answers so far were judged against a wrong solution.
        """
        fach, store = self._fach(fach_id)
        gewaehlt = set(aufgabe_ids)
        gleich = (Ergebnis.RICHTIG, Ergebnis.FAST_RICHTIG)
        uebernommen = 0
        for aufgabe in store.aufgaben.values():
            if (
                aufgabe.id not in gewaehlt
                or not isinstance(aufgabe, MatheAufgabe)
                or not aufgabe.vorschlag
            ):
                continue
            neu = aufgabe.vorschlag
            aufgabe.alternativen = [
                a for a in aufgabe.alternativen if bewerte_mathe(a, neu) in gleich
            ]
            aufgabe.loesung = neu
            aufgabe.rechenweg = []
            aufgabe.statistik = {}
            aufgabe.verifikation = (
                Verifikation.KI
                if aufgabe.vorschlag_durch == "ki"
                else Verifikation.RECHNERISCH
            )
            aufgabe.vorschlag = None
            aufgabe.vorschlag_durch = None
            aufgabe.geaendert = dt_util.utcnow()
            uebernommen += 1
        if uebernommen:
            self._gespeichert(fach, store)
        return {"uebernommen": uebernommen}

    def als_geprueft_markieren(
        self, fach_id: str, aufgabe_ids: list[str]
    ) -> dict[str, Any]:
        """Mark the solution of math tasks as checked by a parent.

        The stored solution stays as it is; a result found when recalculating
        is dropped, because the parent decided against it.
        """
        fach, store = self._fach(fach_id)
        if fach.typ is not AufgabenTyp.MATHE:
            raise _ungueltig("nachrechnen_nur_mathe")
        gewaehlt = set(aufgabe_ids)
        markiert = 0
        for aufgabe in store.aufgaben.values():
            if aufgabe.id not in gewaehlt or not isinstance(aufgabe, MatheAufgabe):
                continue
            if aufgabe.verifikation is Verifikation.MANUELL:
                continue
            aufgabe.verifikation = Verifikation.MANUELL
            aufgabe.vorschlag = None
            aufgabe.vorschlag_durch = None
            aufgabe.geaendert = dt_util.utcnow()
            markiert += 1
        if markiert:
            self._gespeichert(fach, store)
        return {"markiert": markiert}

    async def _rechne_nach(
        self, ki_entity: str | None, aufgabe: MatheAufgabe
    ) -> tuple[Verifikation, str | None, str]:
        """Return how the stored solution of a task holds up.

        The second value is the result that was found instead, the third one
        who found it ("lokal" or "ki"). KEINE means that the task could not be
        checked. Only the solution itself counts, it is what the child is told.
        """
        # A task about an image cannot be calculated from its text alone
        wert = None if aufgabe.bild else berechne(_FRAGE_ENDE.sub("", aufgabe.aufgabe))
        soll = zerlege(aufgabe.loesung)
        if wert is not None and soll is not None:
            if wert == soll[0]:
                return Verifikation.RECHNERISCH, None, "lokal"
            return Verifikation.ABWEICHUNG, _als_text(wert), "lokal"
        if not ki_entity:
            return Verifikation.KEINE, None, "lokal"
        zweite = await self._manager.ki.async_loese(
            ki_entity, aufgabe=aufgabe.aufgabe, bild=aufgabe.bild
        )
        if zweite is None:
            return Verifikation.KEINE, None, "ki"
        gleich = (Ergebnis.RICHTIG, Ergebnis.FAST_RICHTIG)
        lokal = bewerte_mathe(zweite, aufgabe.loesung)
        if lokal in gleich or bewerte_mathe(aufgabe.loesung, zweite) in gleich:
            return Verifikation.KI, None, "ki"
        if lokal is None:
            # Results in words can only be compared by their meaning
            urteil = await self._manager.ki.async_bewerte_mathe(
                ki_entity,
                aufgabe=aufgabe.aufgabe,
                loesung=aufgabe.loesung,
                alternativen=aufgabe.alternativen,
                antwort=zweite,
            )
            if urteil is None:
                return Verifikation.KEINE, None, "ki"
            if urteil.ergebnis in gleich:
                return Verifikation.KI, None, "ki"
        return Verifikation.ABWEICHUNG, zweite, "ki"

    # ------------------------------------------------------------------
    # Exams
    # ------------------------------------------------------------------

    async def arbeit_speichern(
        self, arbeit_id: str | None, daten: dict[str, Any]
    ) -> str:
        """Create or change an exam including its explicit task selection.

        The exam itself is a config subentry; the update listener of the entry
        applies the change to the running manager.
        """
        manager = self._manager
        entry = manager.entry
        if arbeit_id is None:
            fach, store = self._fach(daten.get("fach_id", ""))
            alt = None
        else:
            alt = entry.subentries.get(arbeit_id)
            if alt is None or alt.subentry_type != SUBENTRY_ARBEIT:
                raise _nicht_gefunden("arbeit")
            fach, store = self._fach(alt.data[CONF_FACH_ID])

        thema = _text(daten.get("thema"), "thema_leer", pflicht=True)
        try:
            datum = date.fromisoformat(daten.get("datum") or "")
            art = ArbeitArt(daten.get("art", ArbeitArt.ARBEIT))
            abfragen = int(daten.get("abfragen_pro_tag", DEFAULT_ABFRAGEN_PRO_TAG))
            start = int(daten.get("start_tage_vorher", DEFAULT_START_TAGE_VORHER))
            frist_roh = daten.get("antwortfrist_minuten")
            frist = None if frist_roh is None else int(frist_roh)
            sim_anzahl = int(
                daten.get("simulation_anzahl") or DEFAULT_SIMULATION_ANZAHL
            )
        except (ValueError, TypeError) as err:
            raise _ungueltig("arbeit_ungueltig") from err
        if not 1 <= abfragen <= 24 or not 1 <= start <= 90:
            raise _ungueltig("arbeit_ungueltig")
        if frist is not None and not 1 <= frist <= MAX_TIMEOUT_MINUTEN:
            raise _ungueltig("arbeit_ungueltig")
        if datum < dt_util.now().date():
            raise _ungueltig("datum_vergangen")
        if not 1 <= sim_anzahl <= MAX_SIM_AUFGABEN:
            raise _ungueltig("anzahl_ungueltig")
        sim_um = self._pruefe_simulation_um(
            daten.get("simulation_um"),
            None if alt is None else alt.data.get(CONF_SIMULATION_UM),
        )
        lektionen_roh = daten.get("lektionen") or []
        ids_roh = daten.get("aufgaben_ids") or []
        if not isinstance(lektionen_roh, list) or not isinstance(ids_roh, list):
            raise _ungueltig("arbeit_ungueltig")
        lektionen = [
            w for w in (_text(x, "arbeit_ungueltig") for x in lektionen_roh) if w
        ]
        aufgaben_ids = [i for i in ids_roh if i in store.aufgaben]

        jetzt = dt_util.utcnow().isoformat()
        subentry_daten = {
            CONF_FACH_ID: fach.id,
            CONF_ART: art.value,
            CONF_DATUM: datum.isoformat(),
            CONF_THEMA: thema,
            CONF_LEKTIONEN: lektionen,
            CONF_ABFRAGEN_PRO_TAG: abfragen,
            CONF_START_TAGE_VORHER: start,
            CONF_INTENSIVIERUNG: bool(daten.get("intensivierung", True)),
            CONF_ANTWORTFRIST: frist,
            CONF_SIMULATION_UM: sim_um,
            CONF_SIMULATION_ANZAHL: sim_anzahl,
            CONF_ERSTELLT: alt.data.get(CONF_ERSTELLT, jetzt) if alt else jetzt,
            CONF_GEAENDERT: jetzt,
        }
        fach_subentry = entry.subentries[fach.id]
        titel = arbeit_titel(datum.isoformat(), fach_subentry.title, thema or "")

        # The selection is stored first so that it survives a restart or reload
        if alt is not None:
            manager.config_store.arbeit_aufgaben[alt.subentry_id] = aufgaben_ids
            await manager.config_store.async_save()
            manager.hass.config_entries.async_update_subentry(
                entry, alt, data=subentry_daten, title=titel
            )
            return alt.subentry_id
        neu = ConfigSubentry(
            data=MappingProxyType(subentry_daten),
            subentry_type=SUBENTRY_ARBEIT,
            title=titel,
            unique_id=None,
        )
        manager.config_store.arbeit_aufgaben[neu.subentry_id] = aufgaben_ids
        await manager.config_store.async_save()
        manager.hass.config_entries.async_add_subentry(entry, neu)
        return neu.subentry_id

    @staticmethod
    def _pruefe_simulation_um(wert: Any, bisher: str | None) -> str | None:
        """Validate the time of a planned simulation; returns it as ISO text.

        A time without a zone is local time. A new time has to be in the
        future; one that was stored before may stay as it is.
        """
        if wert in (None, ""):
            return None
        zeitpunkt = dt_util.parse_datetime(wert) if isinstance(wert, str) else None
        if zeitpunkt is None:
            raise _ungueltig("simulation_um_ungueltig")
        if zeitpunkt.tzinfo is None:
            zeitpunkt = zeitpunkt.replace(tzinfo=dt_util.DEFAULT_TIME_ZONE)
        text = dt_util.as_utc(zeitpunkt).isoformat()
        if text != bisher and zeitpunkt <= dt_util.utcnow():
            raise _ungueltig("simulation_um_vergangen")
        return text

    def _arbeit(self, arbeit_id: str) -> Arbeit:
        arbeit = self._manager.arbeiten.get(arbeit_id)
        if arbeit is None:
            raise _nicht_gefunden("arbeit")
        return arbeit

    async def simulieren(self, arbeit_id: str, anzahl: int, weg: str) -> dict[str, Any]:
        """Simulate an exam as a sheet to print or in the messenger."""
        manager = self._manager
        arbeit = self._arbeit(arbeit_id)
        if not 1 <= anzahl <= MAX_SIM_AUFGABEN:
            raise _ungueltig("anzahl_ungueltig")
        if weg == WEG_AUSDRUCK:
            eintraege = manager.simulation_auswahl(arbeit, anzahl, messenger=False)
            if not eintraege:
                raise _ungueltig("keine_aufgaben")
            seiten = await manager.async_simulation_blatt(arbeit, eintraege)
            return {"weg": weg, "anzahl": len(eintraege), "bilder": seiten}
        if weg != WEG_MESSENGER:
            raise _ungueltig("weg_ungueltig")
        try:
            gestellt = await manager.async_simulation_starten(arbeit_id, anzahl)
        except ServiceValidationError as err:
            raise _ungueltig(err.translation_key or "keine_aufgaben") from err
        except HomeAssistantError as err:
            raise VerwaltungError("send_failed", "senden_fehlgeschlagen") from err
        return {"weg": weg, "anzahl": gestellt, "bilder": []}

    async def simulation_abbrechen(self, kind_id: str) -> dict[str, Any]:
        """Stop the simulated exam of a child."""
        if kind_id not in self._manager.kinder:
            raise _nicht_gefunden("kind")
        return {"abgebrochen": await self._manager.async_simulation_abbrechen(kind_id)}

    def arbeit_loeschen(self, arbeit_id: str) -> None:
        """Delete an exam."""
        entry = self._manager.entry
        subentry = entry.subentries.get(arbeit_id)
        if subentry is None or subentry.subentry_type != SUBENTRY_ARBEIT:
            raise _nicht_gefunden("arbeit")
        self._manager.hass.config_entries.async_remove_subentry(entry, arbeit_id)
