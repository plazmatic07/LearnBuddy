"""Texts of the messages that are sent to the children.

These are not UI texts of Home Assistant, therefore they are not part of the
translation files. The name of the child is inserted locally only.
"""

from __future__ import annotations

from typing import Final

FALLBACK_SPRACHE: Final = "en"

TEXTE: Final[dict[str, dict[str, str]]] = {
    "de": {
        "frage": "Hallo {name}! 📚 {fach}: Was heißt „{wort}“ auf {zielsprache}?",
        "frage_kurz": "Was heißt „{wort}“ auf {zielsprache}?",
        "frage_mathe": "Hallo {name}! 🔢 {fach}: {aufgabe}",
        "frage_mathe_kurz": "{aufgabe}",
        "richtig_mathe": "Richtig, {name}! 🎉 Die Lösung ist {loesung}.",
        "fast_richtig_mathe": (
            "Fast richtig, {name}! 👍 Denk an die Einheit: {loesung}."
        ),
        "falsch_mathe": "Leider nicht richtig, {name}. Die Lösung ist {loesung}. 💪",
        "unbeantwortet_mathe": "Die Zeit ist um, {name}. Die Lösung ist {loesung}.",
        "rechenweg_angebot": (
            "\n\nSoll ich dir den Rechenweg erklären? Antworte mit Ja."
        ),
        "rechenweg": "So geht es, {name}:",
        "rechenweg_fehlt": (
            "{name}, den Rechenweg kann ich dir gerade leider nicht erklären."
        ),
        "rechenweg_nein": "Alles klar, {name}!",
        "frage_sach": "Hallo {name}! 📖 {fach}: {frage}",
        "frage_sach_kurz": "{frage}",
        "frage_optionen": "\n{optionen}\nAntworte mit dem Buchstaben.",
        "richtig_sach": "Richtig, {name}! 🎉",
        "teilweise_sach": ("Teilweise richtig, {name}. 👍 Vollständig wäre: {loesung}"),
        "falsch_sach": "Leider nicht richtig, {name}. Richtig ist: {loesung} 💪",
        "unbeantwortet_sach": "Die Zeit ist um, {name}. Richtig ist: {loesung}",
        "unbewertet_sach": (
            "{name}, ich kann deine Antwort gerade nicht bewerten. "
            "Vergleiche selbst: {loesung}"
        ),
        "sim_titel_arbeit": "Klassenarbeit",
        "sim_titel_hue": "Hausaufgabenüberprüfung",
        "sim_start": (
            "Hallo {name}! 📝 Wir üben für die {titel} in {fach}: {thema}\n"
            "Es sind {anzahl} Aufgaben. Ich stelle sie nacheinander, "
            "die Auswertung bekommst du am Ende. Viel Erfolg! 🍀"
        ),
        "sim_seite": "Seite {nr}",
        "sim_aufgabe": "Aufgabe {nr} von {anzahl}: {frage}",
        "sim_ende": (
            "Geschafft, {name}! 🎓 Du hast {punkte} von {moeglich} Punkten "
            "({prozent} %)."
        ),
        "sim_zeit": (
            "Die Zeit ist um, {name}. Die Übungsarbeit endet hier: "
            "{punkte} von {moeglich} Punkten ({prozent} %)."
        ),
        "sim_ende_leer": (
            "Die Übungsarbeit ist zu Ende, {name}. "
            "Leider konnte ich keine Antwort bewerten."
        ),
        "sim_alles_richtig": "\n\nAlles richtig – super! 🎉",
        "sim_fehler": "\n\nDas schauen wir uns noch einmal an:",
        "sim_fehler_zeile": "\n{nr}. {frage} → {loesung}",
        "sim_unbewertet": (
            "\n\nNicht bewertbare Antworten: {anzahl}. Sie zählen nicht mit."
        ),
        "sim_abbruch": "Die Übungsarbeit wurde beendet, {name}.",
        "blatt_name": "Name:",
        "blatt_klasse": "Klasse:",
        "blatt_datum": "Datum:",
        "blatt_punkte": "Punkte",
        "blatt_punkt_kurz": "P.",
        "blatt_antwort": "Antwort:",
        "blatt_unterschrift": "Unterschrift:",
        "blatt_seite": "Seite",
        "blatt_uebersetze": "Übersetze ins {zielsprache}e: {wort}",
        "richtig": "Richtig, {name}! 🎉 „{wort}“ heißt „{loesung}“.",
        "fast_richtig": (
            "Fast richtig, {name}! 👍 Achte auf die Schreibweise: „{loesung}“."
        ),
        "falsch": "Leider nicht richtig, {name}. „{wort}“ heißt „{loesung}“. 💪",
        "unbeantwortet": "Die Zeit ist um, {name}. „{wort}“ heißt „{loesung}“.",
        "frage_abgebrochen": (
            "{name}, die letzte Frage wurde zurückgezogen. "
            "Du musst sie nicht mehr beantworten."
        ),
        "keine_frage": (
            "Hallo {name}, im Moment ist keine Frage offen. "
            "Schick 👍 für eine weitere Aufgabe oder zum Beispiel „noch 5“."
        ),
        "zusatz_tipp": (
            "\n\nLust auf mehr? Schick 👍 für eine weitere Aufgabe "
            "oder zum Beispiel „noch 5“."
        ),
        "zusatz_start": "Super, {name}! 💪 Es kommen {anzahl} weitere Aufgaben.",
        "zusatz_gekuerzt": (
            "Super, {name}! 💪 Mehr als {anzahl} auf einmal gehen nicht, "
            "es kommen {anzahl} weitere Aufgaben."
        ),
        "zusatz_keine": "{name}, im Moment gibt es keine Aufgaben für dich.",
        "erklaerung": " 💡 {erklaerung}",
    },
    "en": {
        "frage": "Hi {name}! 📚 {fach}: What is “{wort}” in {zielsprache}?",
        "frage_kurz": "What is “{wort}” in {zielsprache}?",
        "frage_mathe": "Hi {name}! 🔢 {fach}: {aufgabe}",
        "frage_mathe_kurz": "{aufgabe}",
        "richtig_mathe": "Correct, {name}! 🎉 The result is {loesung}.",
        "fast_richtig_mathe": "Almost, {name}! 👍 Mind the unit: {loesung}.",
        "falsch_mathe": "Not quite, {name}. The result is {loesung}. 💪",
        "unbeantwortet_mathe": "Time is up, {name}. The result is {loesung}.",
        "rechenweg_angebot": ("\n\nShall I explain how to solve it? Answer with yes."),
        "rechenweg": "This is how it works, {name}:",
        "rechenweg_fehlt": "{name}, I cannot explain the solution right now.",
        "rechenweg_nein": "All right, {name}!",
        "frage_sach": "Hi {name}! 📖 {fach}: {frage}",
        "frage_sach_kurz": "{frage}",
        "frage_optionen": "\n{optionen}\nAnswer with the letter.",
        "richtig_sach": "Correct, {name}! 🎉",
        "teilweise_sach": "Partly right, {name}. 👍 The complete answer: {loesung}",
        "falsch_sach": "Not quite, {name}. The answer is: {loesung} 💪",
        "unbeantwortet_sach": "Time is up, {name}. The answer is: {loesung}",
        "unbewertet_sach": (
            "{name}, I cannot judge your answer right now. "
            "Compare it yourself: {loesung}"
        ),
        "sim_titel_arbeit": "Class test",
        "sim_titel_hue": "Homework check",
        "sim_start": (
            "Hi {name}! 📝 Let us practise for the {titel} in {fach}: {thema}\n"
            "There are {anzahl} tasks. I ask them one after the other, "
            "you get the result at the end. Good luck! 🍀"
        ),
        "sim_seite": "Page {nr}",
        "sim_aufgabe": "Task {nr} of {anzahl}: {frage}",
        "sim_ende": (
            "Done, {name}! 🎓 You scored {punkte} of {moeglich} points ({prozent} %)."
        ),
        "sim_zeit": (
            "Time is up, {name}. The practice test ends here: "
            "{punkte} of {moeglich} points ({prozent} %)."
        ),
        "sim_ende_leer": (
            "The practice test is over, {name}. "
            "Unfortunately I could not judge any answer."
        ),
        "sim_alles_richtig": "\n\nAll correct – great! 🎉",
        "sim_fehler": "\n\nLet us look at these again:",
        "sim_fehler_zeile": "\n{nr}. {frage} → {loesung}",
        "sim_unbewertet": (
            "\n\nAnswers I could not judge: {anzahl}. They do not count."
        ),
        "sim_abbruch": "The practice test was stopped, {name}.",
        "blatt_name": "Name:",
        "blatt_klasse": "Class:",
        "blatt_datum": "Date:",
        "blatt_punkte": "Points",
        "blatt_punkt_kurz": "pt.",
        "blatt_antwort": "Answer:",
        "blatt_unterschrift": "Signature:",
        "blatt_seite": "Page",
        "blatt_uebersetze": "Translate into {zielsprache}: {wort}",
        "richtig": "Correct, {name}! 🎉 “{wort}” means “{loesung}”.",
        "fast_richtig": "Almost, {name}! 👍 Mind the spelling: “{loesung}”.",
        "falsch": "Not quite, {name}. “{wort}” means “{loesung}”. 💪",
        "unbeantwortet": "Time is up, {name}. “{wort}” means “{loesung}”.",
        "frage_abgebrochen": (
            "{name}, the last question was withdrawn. "
            "You do not need to answer it any more."
        ),
        "keine_frage": (
            "Hi {name}, there is no open question right now. "
            "Send 👍 for one more question or for example “5 more”."
        ),
        "zusatz_tipp": (
            "\n\nWant more? Send 👍 for one more question or for example “5 more”."
        ),
        "zusatz_start": "Great, {name}! 💪 {anzahl} more questions are coming.",
        "zusatz_gekuerzt": (
            "Great, {name}! 💪 {anzahl} at once is the limit, "
            "{anzahl} more questions are coming."
        ),
        "zusatz_keine": "{name}, there are no tasks for you right now.",
        "erklaerung": " 💡 {erklaerung}",
    },
}

SPRACHNAMEN: Final[dict[str, dict[str, str]]] = {
    "de": {
        "de": "Deutsch",
        "en": "Englisch",
        "fr": "Französisch",
        "es": "Spanisch",
        "it": "Italienisch",
        "la": "Latein",
    },
    "en": {
        "de": "German",
        "en": "English",
        "fr": "French",
        "es": "Spanish",
        "it": "Italian",
        "la": "Latin",
    },
}


def waehle_sprache(sprache: str) -> str:
    """Return a supported message language for a language tag."""
    kurz = sprache.split("-", maxsplit=1)[0].lower()
    return kurz if kurz in TEXTE else FALLBACK_SPRACHE


def text(sprache: str, schluessel: str, **werte: str) -> str:
    """Return a formatted message text."""
    return TEXTE[waehle_sprache(sprache)][schluessel].format(**werte)


def sprachname(sprache: str, code: str) -> str:
    """Return the name of a language in the message language."""
    return SPRACHNAMEN[waehle_sprache(sprache)].get(code, code)
