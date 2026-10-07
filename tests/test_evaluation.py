"""Tests for the local evaluation of answers."""

from __future__ import annotations

import pytest

from custom_components.learnbuddy.evaluation import (
    bewerte_vokabel,
    editierdistanz,
    normalisiere,
    varianten,
)
from custom_components.learnbuddy.models import Ergebnis


@pytest.mark.parametrize(
    ("text", "sprache", "erwartet"),
    [
        ("  Dog ", "en", "dog"),
        ("The Dog!", "en", "dog"),
        ("a house", "en", "house"),
        ("an apple", "en", "apple"),
        ("to go", "en", "go"),
        ("To  Go.", "en", "go"),
        ("der Hund", "de", "hund"),
        ("Die Katze", "de", "katze"),
        ("ein Haus", "de", "haus"),
        ("ice-cream", "en", "ice cream"),
        ("don’t", "en", "dont"),
        ("don't", "en", "dont"),
        ("l'ami", "fr", "ami"),
        ("le chien", "fr", "chien"),
        ("STRASSE", "de", "strasse"),
        ("the", "en", "the"),
        ("to", "en", "to"),
        ("", "en", ""),
        ("Hund", "xx", "hund"),
    ],
)
def test_normalisiere(text: str, sprache: str, erwartet: str) -> None:
    assert normalisiere(text, sprache) == erwartet


def test_varianten() -> None:
    assert varianten("dog", "en") == {"dog"}
    assert varianten("big / large", "en") == {"big large", "big", "large"}
    assert varianten("(to) go", "en") == {"go"}
    assert varianten("Auto (das)", "de") == {"auto", "auto das"}
    assert varianten("couch; sofa", "en") == {"couch sofa", "couch", "sofa"}
    assert varianten("", "en") == set()


@pytest.mark.parametrize(
    ("a", "b", "distanz"),
    [
        ("", "", 0),
        ("dog", "dog", 0),
        ("dog", "dig", 1),
        ("dog", "dogs", 1),
        ("dog", "do", 1),
        ("recieve", "receive", 1),
        ("abc", "", 3),
        ("", "abc", 3),
        ("kitten", "sitting", 3),
    ],
)
def test_editierdistanz(a: str, b: str, distanz: int) -> None:
    assert editierdistanz(a, b) == distanz


@pytest.mark.parametrize(
    ("antwort", "erwartet", "alternativen", "sprache", "ergebnis"),
    [
        ("dog", "dog", [], "en", Ergebnis.RICHTIG),
        ("Dog.", "dog", [], "en", Ergebnis.RICHTIG),
        ("the dog", "dog", [], "en", Ergebnis.RICHTIG),
        ("dog", "the dog", [], "en", Ergebnis.RICHTIG),
        ("hound", "dog", ["hound"], "en", Ergebnis.RICHTIG),
        ("go", "to go", [], "en", Ergebnis.RICHTIG),
        ("to go", "go", [], "en", Ergebnis.RICHTIG),
        ("Hund", "der Hund", [], "de", Ergebnis.RICHTIG),
        ("large", "big / large", [], "en", Ergebnis.RICHTIG),
        ("big, large", "big / large", [], "en", Ergebnis.RICHTIG),
        ("large, big", "big / large", [], "en", Ergebnis.RICHTIG),
        ("big, small", "big / large", [], "en", Ergebnis.FALSCH),
        ("recieve", "receive", [], "en", Ergebnis.FAST_RICHTIG),
        ("hous", "house", [], "en", Ergebnis.FAST_RICHTIG),
        ("Baer", "Bär", [], "de", Ergebnis.FAST_RICHTIG),
        ("Bar", "Bär", [], "de", Ergebnis.FAST_RICHTIG),
        ("Strasse", "Straße", [], "de", Ergebnis.RICHTIG),
        ("ecole", "école", [], "fr", Ergebnis.FAST_RICHTIG),
        ("cat", "dog", [], "en", Ergebnis.FALSCH),
        ("dig", "dog", [], "en", Ergebnis.FALSCH),
        ("", "dog", [], "en", Ergebnis.FALSCH),
        ("   ", "dog", [], "en", Ergebnis.FALSCH),
        ("?!", "dog", [], "en", Ergebnis.FALSCH),
        ("houses and more", "house", [], "en", Ergebnis.FALSCH),
    ],
)
def test_bewerte_vokabel(
    antwort: str,
    erwartet: str,
    alternativen: list[str],
    sprache: str,
    ergebnis: Ergebnis,
) -> None:
    assert bewerte_vokabel(antwort, erwartet, alternativen, sprache) is ergebnis
