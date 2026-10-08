"""Daily log of answers: pure logic without Home Assistant.

The tasks themselves only keep totals. Progress over time and weekly figures
need to know when something was answered, so every day is counted per child
and subject. The log holds numbers and IDs only: no names, no task texts and
no answers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import TYPE_CHECKING, Any, Self

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping

AUFBEWAHRUNG_TAGE = 400
MAX_SIMULATIONEN = 100
# A lesson needs a few answers before its error rate says anything
MIN_ANTWORTEN_LEKTION = 3
GLAETTUNG_TAGE = 7

RICHTIG = "richtig"
TEILWEISE = "teilweise"
FALSCH = "falsch"
UNBEANTWORTET = "unbeantwortet"
# How the results of the evaluation are counted
_ZAEHLER = {
    "richtig": RICHTIG,
    "fast_richtig": RICHTIG,
    "teilweise": TEILWEISE,
    "falsch": FALSCH,
    "unbeantwortet": UNBEANTWORTET,
}


@dataclass(slots=True)
class FachTag:
    """What happened in one subject on one day."""

    gefragt: int = 0
    richtig: int = 0
    teilweise: int = 0
    falsch: int = 0
    unbeantwortet: int = 0
    # Right and wrong answers per lesson
    lektionen: dict[str, list[int]] = field(default_factory=dict)
    # Wrong answers per task
    aufgaben_falsch: dict[str, int] = field(default_factory=dict)
    # Cards of the subject and how many of them are safe, last seen that day
    karten: int | None = None
    sicher: int | None = None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Self:
        """Create the day of a subject from stored data."""
        return cls(
            gefragt=int(data.get("gefragt", 0)),
            richtig=int(data.get("richtig", 0)),
            teilweise=int(data.get("teilweise", 0)),
            falsch=int(data.get("falsch", 0)),
            unbeantwortet=int(data.get("unbeantwortet", 0)),
            lektionen={
                str(name): [int(wert[0]), int(wert[1])]
                for name, wert in (data.get("lektionen") or {}).items()
            },
            aufgaben_falsch={
                str(aufgabe_id): int(anzahl)
                for aufgabe_id, anzahl in (data.get("aufgaben_falsch") or {}).items()
            },
            karten=data.get("karten"),
            sicher=data.get("sicher"),
        )

    def to_dict(self) -> dict[str, Any]:
        """Return the day of a subject for storage."""
        return {
            "gefragt": self.gefragt,
            "richtig": self.richtig,
            "teilweise": self.teilweise,
            "falsch": self.falsch,
            "unbeantwortet": self.unbeantwortet,
            "lektionen": {name: list(wert) for name, wert in self.lektionen.items()},
            "aufgaben_falsch": dict(self.aufgaben_falsch),
            "karten": self.karten,
            "sicher": self.sicher,
        }


@dataclass(slots=True, frozen=True)
class SimErgebnis:
    """Result of a simulated exam."""

    tag: date
    arbeit_id: str
    fach_id: str
    punkte: float
    moeglich: int
    # False if it ended because a task was not answered in time
    vollstaendig: bool = True

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Self:
        """Create a result from stored data."""
        return cls(
            tag=date.fromisoformat(data["tag"]),
            arbeit_id=data["arbeit_id"],
            fach_id=data["fach_id"],
            punkte=float(data["punkte"]),
            moeglich=int(data["moeglich"]),
            vollstaendig=bool(data.get("vollstaendig", True)),
        )

    def to_dict(self) -> dict[str, Any]:
        """Return the result for storage and for the panel."""
        return {
            "tag": self.tag.isoformat(),
            "arbeit_id": self.arbeit_id,
            "fach_id": self.fach_id,
            "punkte": self.punkte,
            "moeglich": self.moeglich,
            "vollstaendig": self.vollstaendig,
        }

    @property
    def prozent(self) -> int | None:
        """Return the share of points reached."""
        return None if not self.moeglich else round(100 * self.punkte / self.moeglich)


@dataclass(slots=True)
class KindVerlauf:
    """The log of one child."""

    # Day -> subject -> counters
    tage: dict[date, dict[str, FachTag]] = field(default_factory=dict)
    simulationen: list[SimErgebnis] = field(default_factory=list)
    # First day anything was logged; nothing is known about the time before
    seit: date | None = None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Self:
        """Create the log of a child from stored data."""
        seit = data.get("seit")
        return cls(
            tage={
                date.fromisoformat(tag): {
                    fach_id: FachTag.from_dict(wert)
                    for fach_id, wert in faecher.items()
                }
                for tag, faecher in (data.get("tage") or {}).items()
            },
            simulationen=[
                SimErgebnis.from_dict(wert) for wert in data.get("simulationen") or []
            ],
            seit=None if not seit else date.fromisoformat(seit),
        )

    def to_dict(self) -> dict[str, Any]:
        """Return the log of a child for storage."""
        return {
            "tage": {
                tag.isoformat(): {
                    fach_id: wert.to_dict() for fach_id, wert in faecher.items()
                }
                for tag, faecher in sorted(self.tage.items())
            },
            "simulationen": [ergebnis.to_dict() for ergebnis in self.simulationen],
            "seit": None if self.seit is None else self.seit.isoformat(),
        }

    def _fach_tag(self, tag: date, fach_id: str) -> FachTag:
        if self.seit is None or tag < self.seit:
            self.seit = tag
        return self.tage.setdefault(tag, {}).setdefault(fach_id, FachTag())

    # -------------------------------------------------------------- logging

    def frage(self, tag: date, fach_id: str) -> None:
        """Count a question that was sent."""
        self._fach_tag(tag, fach_id).gefragt += 1

    def frage_zurueck(self, tag: date, fach_id: str) -> None:
        """Take back a question that was withdrawn."""
        eintrag = self.tage.get(tag, {}).get(fach_id)
        if eintrag is not None and eintrag.gefragt > 0:
            eintrag.gefragt -= 1

    def ergebnis(
        self,
        tag: date,
        fach_id: str,
        ergebnis: str,
        *,
        lektion: str | None = None,
        aufgabe_id: str | None = None,
    ) -> None:
        """Count the result of an answer or of a question that ran out."""
        zaehler = _ZAEHLER.get(ergebnis)
        if zaehler is None:
            return
        eintrag = self._fach_tag(tag, fach_id)
        setattr(eintrag, zaehler, getattr(eintrag, zaehler) + 1)
        if zaehler not in (RICHTIG, FALSCH):
            return
        if lektion:
            paar = eintrag.lektionen.setdefault(lektion, [0, 0])
            paar[0 if zaehler == RICHTIG else 1] += 1
        if zaehler == FALSCH and aufgabe_id:
            eintrag.aufgaben_falsch[aufgabe_id] = (
                eintrag.aufgaben_falsch.get(aufgabe_id, 0) + 1
            )

    def lernstand(self, tag: date, fach_id: str, karten: int, sicher: int) -> None:
        """Note how many cards of a subject are safe."""
        eintrag = self._fach_tag(tag, fach_id)
        eintrag.karten = karten
        eintrag.sicher = sicher

    def simulation(self, ergebnis: SimErgebnis) -> None:
        """Keep the result of a simulated exam."""
        if self.seit is None or ergebnis.tag < self.seit:
            self.seit = ergebnis.tag
        self.simulationen.append(ergebnis)
        del self.simulationen[:-MAX_SIMULATIONEN]

    def bereinige(self, fach_ids: Iterable[str], heute: date) -> bool:
        """Drop old days and subjects that no longer exist."""
        faecher = set(fach_ids)
        grenze = heute - timedelta(days=AUFBEWAHRUNG_TAGE)
        geaendert = False
        for tag in list(self.tage):
            if tag < grenze:
                del self.tage[tag]
                geaendert = True
                continue
            for fach_id in self.tage[tag].keys() - faecher:
                del self.tage[tag][fach_id]
                geaendert = True
            if not self.tage[tag]:
                del self.tage[tag]
                geaendert = True
        behalten = [s for s in self.simulationen if s.fach_id in faecher]
        if len(behalten) != len(self.simulationen):
            self.simulationen = behalten
            geaendert = True
        return geaendert

    # -------------------------------------------------------------- reading

    def summe(self, von: date, bis: date) -> dict[str, Any]:
        """Add up the counters of a period, both days included."""
        summe = {"gefragt": 0, RICHTIG: 0, TEILWEISE: 0, FALSCH: 0, UNBEANTWORTET: 0}
        tage_aktiv = 0
        for tag, faecher in self.tage.items():
            if not von <= tag <= bis:
                continue
            beantwortet = 0
            for eintrag in faecher.values():
                summe["gefragt"] += eintrag.gefragt
                summe[RICHTIG] += eintrag.richtig
                summe[TEILWEISE] += eintrag.teilweise
                summe[FALSCH] += eintrag.falsch
                summe[UNBEANTWORTET] += eintrag.unbeantwortet
                beantwortet += eintrag.richtig + eintrag.teilweise + eintrag.falsch
            tage_aktiv += bool(beantwortet)
        return {
            **summe,
            "trefferquote": trefferquote(summe[RICHTIG], summe[FALSCH]),
            # Days on which the child answered at least once
            "tage_aktiv": tage_aktiv,
        }

    def reihe(self, von: date, bis: date) -> list[dict[str, Any]]:
        """Return the counters of every day of a period, days without data too."""
        reihe = []
        richtig: list[int] = []
        falsch: list[int] = []
        # The smoothed rate of the first days looks back before the period
        for tag in tage_von_bis(von - timedelta(days=GLAETTUNG_TAGE - 1), bis):
            tagessumme = self.summe(tag, tag)
            richtig.append(tagessumme[RICHTIG])
            falsch.append(tagessumme[FALSCH])
            if tag < von:
                continue
            reihe.append(
                {
                    "tag": tag.isoformat(),
                    "gefragt": tagessumme["gefragt"],
                    RICHTIG: tagessumme[RICHTIG],
                    TEILWEISE: tagessumme[TEILWEISE],
                    FALSCH: tagessumme[FALSCH],
                    UNBEANTWORTET: tagessumme[UNBEANTWORTET],
                    # Over the last days, so that a day with one answer does
                    # not jump to 0 or 100 percent
                    "trefferquote": trefferquote(
                        sum(richtig[-GLAETTUNG_TAGE:]), sum(falsch[-GLAETTUNG_TAGE:])
                    ),
                }
            )
        return reihe

    def lernstand_am(self, fach_id: str, tag: date) -> int | None:
        """Return the share of safe cards of a subject at the end of a day."""
        for frueher in sorted((t for t in self.tage if t <= tag), reverse=True):
            eintrag = self.tage[frueher].get(fach_id)
            if eintrag is not None and eintrag.karten:
                return round(100 * (eintrag.sicher or 0) / eintrag.karten)
        return None

    def lernstand_reihe(self, fach_id: str, von: date, bis: date) -> list[int | None]:
        """Return the share of safe cards for every day; the last value carries on."""
        wert = self.lernstand_am(fach_id, von - timedelta(days=1))
        reihe: list[int | None] = []
        for tag in tage_von_bis(von, bis):
            eintrag = self.tage.get(tag, {}).get(fach_id)
            if eintrag is not None and eintrag.karten:
                wert = round(100 * (eintrag.sicher or 0) / eintrag.karten)
            reihe.append(wert)
        return reihe

    def schwache_lektionen(
        self, von: date, bis: date, anzahl: int = 5
    ) -> list[dict[str, Any]]:
        """Return the lessons with the highest error rate of a period."""
        summen: dict[tuple[str, str], list[int]] = {}
        for tag, faecher in self.tage.items():
            if not von <= tag <= bis:
                continue
            for fach_id, eintrag in faecher.items():
                for lektion, (richtig, falsch) in eintrag.lektionen.items():
                    paar = summen.setdefault((fach_id, lektion), [0, 0])
                    paar[0] += richtig
                    paar[1] += falsch
        schwach = sorted(
            (
                (round(100 * falsch / (richtig + falsch)), falsch, fach_id, lektion)
                for (fach_id, lektion), (richtig, falsch) in summen.items()
                if falsch and richtig + falsch >= MIN_ANTWORTEN_LEKTION
            ),
            key=lambda e: (-e[0], -e[1], e[2], e[3]),
        )
        return [
            {
                "fach_id": fach_id,
                "lektion": lektion,
                RICHTIG: summen[fach_id, lektion][0],
                FALSCH: falsch,
                "fehlerquote": quote,
            }
            for quote, falsch, fach_id, lektion in schwach[:anzahl]
        ]

    def schwierige_aufgaben(self, von: date, bis: date) -> list[tuple[str, str, int]]:
        """Return subject, task and number of wrong answers, most wrong first."""
        summen: dict[tuple[str, str], int] = {}
        for tag, faecher in self.tage.items():
            if not von <= tag <= bis:
                continue
            for fach_id, eintrag in faecher.items():
                for aufgabe_id, anzahl in eintrag.aufgaben_falsch.items():
                    schluessel = (fach_id, aufgabe_id)
                    summen[schluessel] = summen.get(schluessel, 0) + anzahl
        return sorted(
            ((fach_id, aufgabe_id, n) for (fach_id, aufgabe_id), n in summen.items()),
            key=lambda e: (-e[2], e[0], e[1]),
        )

    def simulationen_im(self, von: date, bis: date) -> list[SimErgebnis]:
        """Return the simulated exams of a period, newest first."""
        return sorted(
            (s for s in self.simulationen if von <= s.tag <= bis),
            key=lambda s: s.tag,
            reverse=True,
        )


def trefferquote(richtig: int, falsch: int) -> int | None:
    """Return the share of right answers among the judged ones."""
    return None if not richtig + falsch else round(100 * richtig / (richtig + falsch))


def tage_von_bis(von: date, bis: date) -> list[date]:
    """Return every day of a period, both ends included."""
    return [von + timedelta(days=n) for n in range((bis - von).days + 1)]


def woche(tag: date, versatz: int = 0) -> tuple[date, date]:
    """Return Monday and Sunday of the week of a day, shifted by whole weeks."""
    montag = tag - timedelta(days=tag.weekday()) + timedelta(weeks=versatz)
    return montag, montag + timedelta(days=6)
