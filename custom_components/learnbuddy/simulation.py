"""Pure logic for simulating an exam: picking tasks and scoring answers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .models import Ergebnis

if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence
    from random import Random

    from .models import Aufgabe

MAX_AUFGABEN = 30
DEFAULT_AUFGABEN = 10

_PUNKTE = {
    Ergebnis.RICHTIG: 1.0,
    Ergebnis.FAST_RICHTIG: 1.0,
    Ergebnis.TEILWEISE: 0.5,
    Ergebnis.FALSCH: 0.0,
}


def waehle(
    aufgaben: Iterable[Aufgabe],
    richtungen: Sequence[str],
    anzahl: int,
    rng: Random,
) -> list[tuple[Aufgabe, str]]:
    """Pick tasks for a simulated exam, spread evenly over the lessons.

    Only approved tasks that can be asked take part. Every task comes with
    the direction it is asked in.
    """
    gruppen: dict[str | None, list[tuple[Aufgabe, list[str]]]] = {}
    for aufgabe in aufgaben:
        moeglich = [r for r in richtungen if aufgabe.fragbar(r)]
        if aufgabe.geprueft and moeglich:
            gruppen.setdefault(aufgabe.lektion, []).append((aufgabe, moeglich))
    stapel = list(gruppen.values())
    for gruppe in stapel:
        rng.shuffle(gruppe)
    rng.shuffle(stapel)

    gewaehlt: list[tuple[Aufgabe, str]] = []
    grenze = min(max(anzahl, 0), MAX_AUFGABEN)
    while stapel and len(gewaehlt) < grenze:
        # One task of every lesson in turn
        for gruppe in list(stapel):
            if len(gewaehlt) >= grenze:
                break
            aufgabe, moeglich = gruppe.pop()
            gewaehlt.append((aufgabe, rng.choice(moeglich)))
            if not gruppe:
                stapel.remove(gruppe)
    rng.shuffle(gewaehlt)
    return gewaehlt


@dataclass(frozen=True, slots=True)
class Auswertung:
    """Score of a simulated exam."""

    punkte: float
    moeglich: int
    # Answers that could not be judged; they do not count
    unbewertet: int

    @property
    def prozent(self) -> int | None:
        """Return the share of points in percent."""
        if not self.moeglich:
            return None
        return round(100 * self.punkte / self.moeglich)


def werte_aus(ergebnisse: Iterable[Ergebnis | None]) -> Auswertung:
    """Score the answers of a simulated exam.

    A task without an answer gives no point. An answer nobody could judge is
    left out of the score.
    """
    punkte = 0.0
    moeglich = unbewertet = 0
    for ergebnis in ergebnisse:
        if ergebnis is Ergebnis.UNBEANTWORTET:
            unbewertet += 1
            continue
        moeglich += 1
        if ergebnis is not None:
            punkte += _PUNKTE[ergebnis]
    return Auswertung(punkte=punkte, moeglich=moeglich, unbewertet=unbewertet)


def punkte_text(punkte: float, sprache: str) -> str:
    """Write points the way the language does: 7 or 7,5."""
    if punkte == int(punkte):
        return str(int(punkte))
    text = f"{punkte:.1f}"
    return text.replace(".", ",") if sprache.startswith("de") else text
