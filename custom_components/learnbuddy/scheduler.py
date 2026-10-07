"""Scheduling of questions (pure logic, no Home Assistant dependency)."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import TYPE_CHECKING

from .const import MINDESTABSTAND
from .models import Ergebnis

if TYPE_CHECKING:
    from collections.abc import Collection, Iterable
    from datetime import tzinfo
    from random import Random

    from .models import Arbeit, Aufgabe, Kind, Statistik

# Leitner system: a correct answer moves a task one box up, a wrong answer
# back to the first box. Tasks in higher boxes are repeated less often.
MAX_BOX = 5
LEITNER_INTERVALLE = (
    timedelta(0),
    timedelta(days=1),
    timedelta(days=2),
    timedelta(days=4),
    timedelta(days=7),
)


def abfragen_am_tag(arbeit: Arbeit, tag: date) -> int:
    """Return how many questions an exam requests on a day.

    Questions start ``start_tage_vorher`` days before the exam and end the day
    before it. With intensification the number grows linearly up to twice the
    configured frequency on the last day.
    """
    tage_bis = (arbeit.datum - tag).days
    if tage_bis < 1 or tage_bis > arbeit.start_tage_vorher:
        return 0
    anzahl = arbeit.abfragen_pro_tag
    if arbeit.intensivierung and arbeit.start_tage_vorher > 1:
        fortschritt = (arbeit.start_tage_vorher - tage_bis) / (
            arbeit.start_tage_vorher - 1
        )
        anzahl = round(anzahl * (1 + fortschritt))
    return anzahl


def zeitpunkte(kind: Kind, tag: date, anzahl: int, zone: tzinfo) -> list[datetime]:
    """Distribute a number of questions evenly over the allowed window of a day."""
    fenster = kind.fenster(tag)
    if fenster is None or anzahl < 1:
        return []
    von = datetime.combine(tag, fenster[0], tzinfo=zone)
    bis = datetime.combine(tag, fenster[1], tzinfo=zone)
    if bis <= von:
        return []
    schritt = (bis - von) / anzahl
    return [von + schritt * (index + 0.5) for index in range(anzahl)]


def naechster_zeitpunkt(
    jetzt: datetime,
    kind: Kind,
    arbeiten: Iterable[Arbeit],
    *,
    letzte_frage: datetime | None = None,
    fruehestens: datetime | None = None,
) -> datetime | None:
    """Return the next point in time at which a question should be asked.

    ``jetzt`` must be timezone aware in the local timezone. Slots in the past
    are skipped, they are not caught up later.
    """
    arbeiten = list(arbeiten)
    if not arbeiten:
        return None
    zone = jetzt.tzinfo
    if zone is None:
        raise ValueError("jetzt must be timezone aware")
    start = jetzt
    if fruehestens is not None:
        start = max(start, fruehestens.astimezone(zone))
    if letzte_frage is not None:
        start = max(start, letzte_frage.astimezone(zone) + MINDESTABSTAND)

    tag = start.date()
    letzter_tag = max(arbeit.datum for arbeit in arbeiten)
    while tag < letzter_tag:
        anzahl = sum(abfragen_am_tag(arbeit, tag) for arbeit in arbeiten)
        for zeitpunkt in zeitpunkte(kind, tag, anzahl, zone):
            if zeitpunkt >= start:
                return zeitpunkt
        tag += timedelta(days=1)
    return None


def waehle_arbeit(arbeiten: Iterable[Arbeit], tag: date, rng: Random) -> Arbeit | None:
    """Pick the exam for the next question, weighted by today's frequency."""
    kandidaten = [(a, abfragen_am_tag(a, tag)) for a in arbeiten]
    kandidaten = [(a, gewicht) for a, gewicht in kandidaten if gewicht > 0]
    if not kandidaten:
        return None
    return rng.choices(
        [a for a, _ in kandidaten], weights=[g for _, g in kandidaten], k=1
    )[0]


def naechste_arbeit(arbeiten: Iterable[Arbeit], heute: date) -> Arbeit | None:
    """Return the upcoming exam that is closest to today."""
    kommende = [a for a in arbeiten if a.datum >= heute]
    return min(kommende, key=lambda a: a.datum, default=None)


def antwortfrist(arbeiten: Iterable[Arbeit], standard: int) -> int:
    """Return the minutes a child has to answer a question.

    The shortest own time of the given exams wins, without one the general
    setting applies.
    """
    return min(
        (a.antwortfrist_minuten for a in arbeiten if a.antwortfrist_minuten),
        default=standard,
    )


def aufgaben_der_arbeit(
    arbeit: Arbeit, aufgaben: Iterable[Aufgabe], explizit: Collection[str] = ()
) -> list[Aufgabe]:
    """Return the tasks that belong to an exam.

    These are the tasks of the selected lessons plus the explicitly assigned
    ones. Without any selection all tasks of the subject belong to the exam.
    """
    if not arbeit.lektionen and not explizit:
        return list(aufgaben)
    return [
        aufgabe
        for aufgabe in aufgaben
        if aufgabe.lektion in arbeit.lektionen or aufgabe.id in explizit
    ]


def naechste_box(box: int, ergebnis: Ergebnis) -> int:
    """Return the Leitner box of a task after an answer."""
    if ergebnis is Ergebnis.FALSCH:
        return 1
    if ergebnis in (Ergebnis.RICHTIG, Ergebnis.FAST_RICHTIG):
        return min(max(box, 1) + 1, MAX_BOX)
    return min(max(box, 1), MAX_BOX)


def verdichtung(arbeit: Arbeit | None, tag: date) -> float:
    """Return the factor by which the repetition intervals shrink before an exam.

    1.0 at the start of the question period, 0.0 on the last day before the
    exam, so that everything is due again right before it.
    """
    if arbeit is None or arbeit.start_tage_vorher < 1:
        return 1.0
    tage_bis = (arbeit.datum - tag).days
    return min(1.0, max(0.0, (tage_bis - 1) / arbeit.start_tage_vorher))


def faellig_ab(stat: Statistik, faktor: float = 1.0) -> datetime | None:
    """Return when a task is due again; None if it was never asked."""
    if stat.zuletzt_gefragt is None:
        return None
    box = min(max(stat.box, 1), MAX_BOX)
    return stat.zuletzt_gefragt + LEITNER_INTERVALLE[box - 1] * faktor


def _rang(
    aufgabe: Aufgabe, richtung_key: str, jetzt: datetime, faktor: float
) -> tuple[int, int, float]:
    """Return the priority of a task: lower values are asked first."""
    stat = aufgabe.statistik.get(richtung_key)
    if stat is None or stat.zuletzt_gefragt is None:
        return 0, 1, 0.0
    faellig = faellig_ab(stat, faktor)
    ist_faellig = faellig is None or faellig <= jetzt
    return (0 if ist_faellig else 1, stat.box, stat.zuletzt_gefragt.timestamp())


def waehle_aufgabe(
    aufgaben: Iterable[Aufgabe],
    richtungen: Iterable[str],
    rng: Random,
    *,
    jetzt: datetime,
    faktor: float = 1.0,
    vermeide: str | None = None,
) -> tuple[Aufgabe, str] | None:
    """Pick the next task and direction according to the Leitner system.

    Due tasks come first, ordered by box (lowest first) and then by the time
    they were asked last. If nothing is due, the same order applies to the
    tasks that are not due yet.
    """
    richtungen = list(richtungen)
    kandidaten = [
        (aufgabe, richtung_key)
        for aufgabe in aufgaben
        if aufgabe.geprueft
        for richtung_key in richtungen
        if aufgabe.fragbar(richtung_key)
    ]
    if not kandidaten:
        return None
    andere = [k for k in kandidaten if k[0].id != vermeide]
    if andere:
        kandidaten = andere
    raenge = [_rang(aufgabe, key, jetzt, faktor) for aufgabe, key in kandidaten]
    bester_rang = min(raenge)
    beste = [
        k for k, rang in zip(kandidaten, raenge, strict=True) if rang == bester_rang
    ]
    return rng.choice(beste)
