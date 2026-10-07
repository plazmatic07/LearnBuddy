# LearnBuddy

<img src="assets/icon.svg" alt="LearnBuddy-Icon" width="96" align="right">

LearnBuddy ist eine Custom Integration für Home Assistant, die Kinder auf Klassenarbeiten und Hausaufgabenüberprüfungen (HÜ) vorbereitet. Sie schickt in festgelegten Zeitfenstern Übungsfragen per Messenger, bewertet die Antworten und meldet das Ergebnis zurück. Je näher der Termin rückt, desto häufiger wird gefragt.

LearnBuddy bringt weder einen eigenen Messenger noch eine eigene KI-Anbindung mit. Es nutzt die Integrationen, die in Home Assistant schon eingerichtet sind (z. B. Telegram und OpenAI, Google Gemini, Anthropic oder Ollama). Die KI ist optional.

## Funktionen

- **Drei Facharten:** Fremdsprachen (Vokabeln in beide Richtungen), Mathematik (auch Aufgaben mit Bild) und Sachfächer wie Biologie (Kurzantwort oder Auswahl A–D).
- **Arbeiten und HÜs** mit Datum, Thema und Aufgabenauswahl; die Abfragen starten einige Tage vorher und werden zum Termin hin häufiger.
- **Karteikasten-Prinzip (Leitner):** Was sitzt, kommt seltener; was falsch war, kommt bald wieder.
- **Bewertung** zuerst lokal (Tippfehler, Artikel, Schreibweisen von Zahlen, Einheiten), bei Bedarf durch die KI (Synonyme, Textantworten).
- **Rechenweg auf Nachfrage:** Nach einer falschen Mathe-Antwort kann sich das Kind die Lösung Schritt für Schritt erklären lassen.
- **Aufgaben beschaffen:** eintippen, als Text importieren, aus Fotos von Buchseiten auslesen oder von der KI erzeugen lassen – erzeugte Aufgaben werden nachgerechnet und warten auf deine Freigabe.
- **Klassenarbeit simulieren:** als druckbares Aufgabenblatt oder als Durchlauf im Messenger mit Auswertung am Ende, auch zu einem geplanten Zeitpunkt.
- **Zusatzaufgaben auf Wunsch:** Das Kind fordert mit 👍 oder „noch 5“ selbst weitere Aufgaben an.
- **Panel** in der Seitenleiste für Übersicht, Aufgaben, Lektionen und Arbeiten.
- **Entitäten, Aktionen und Events** für eigene Automationen, zum Beispiel Bildschirmzeit als Belohnung.
- **Datensparsam:** Alles liegt lokal in Home Assistant; der Name des Kindes geht nie an die KI.

## Inhalt

- [Voraussetzungen](#voraussetzungen)
- [Installation](#installation)
- [Einrichtung](#einrichtung)
- [Antworten entgegennehmen](#antworten-entgegennehmen)
- [Panel](#panel)
- [Vokabeln](#vokabeln)
- [Mathematik](#mathematik)
- [Sachfächer](#sachfächer)
- [Aufgaben aus Fotos importieren](#aufgaben-aus-fotos-importieren)
- [Wann und was gefragt wird](#wann-und-was-gefragt-wird)
- [Klassenarbeit oder HÜ simulieren](#klassenarbeit-oder-hü-simulieren)
- [KI](#ki)
- [Entitäten](#entitäten)
- [Aktionen](#aktionen)
- [Events](#events)
- [Datenschutz](#datenschutz)
- [Bekannte Einschränkungen](#bekannte-einschränkungen)
- [Entfernen](#entfernen)
- [Entwicklung](#entwicklung)
- [Lizenz](#lizenz)

## Voraussetzungen

- Home Assistant 2026.9 oder neuer.
- Eine eingerichtete Messenger-Integration mit `notify`-Entität oder klassischer `notify.<name>`-Aktion (z. B. Telegram, eine WhatsApp-Bridge, die Companion-App). Damit Antworten ankommen, muss die Integration eingehende Nachrichten als Event melden.
- Optional eine KI-Integration mit `ai_task`-Entität. Für Funktionen mit Fotos muss sie Bilder annehmen.

## Installation

**Über HACS**

1. In HACS unter „Benutzerdefinierte Repositories“ `https://github.com/plazmatic07/learnbuddy` als Typ „Integration“ hinzufügen.
2. „LearnBuddy“ installieren und Home Assistant neu starten.
3. Unter **Einstellungen → Geräte & Dienste → Integration hinzufügen** „LearnBuddy“ auswählen.

**Von Hand**

Den Ordner `custom_components/learnbuddy` nach `/config/custom_components/` kopieren, Home Assistant neu starten und die Integration wie oben hinzufügen.

## Einrichtung

### Allgemeine Einstellungen

Sie werden beim Hinzufügen abgefragt und lassen sich später über das Zahnrad der Integration ändern.

| Einstellung | Bedeutung |
|---|---|
| Timeout für offene Fragen | Nach dieser Zeit gilt eine Frage als unbeantwortet, nicht als falsch. |
| Sprache der Nachrichten | Deutsch, Englisch oder wie Home Assistant. |
| KI-Entität für die Bewertung | Optional. Eine `ai_task`-Entität. Je Fach lässt sich eine andere wählen. |
| Generierte Aufgaben automatisch freigeben | Standard: aus. Von der KI erzeugte Mathe-Aufgaben warten dann im Panel auf deine Freigabe. |

Danach legst du auf der Seite der Integration der Reihe nach Kind, Fach und Arbeit an. Fächer, Lektionen und Arbeiten lassen sich auch im Panel pflegen.

### Kind

| Feld | Bedeutung |
|---|---|
| Vorname | Für die Anrede in den Nachrichten. |
| Muttersprache | Ausgangssprache der Vokabeln. |
| Klassenstufe, Schulart, Bundesland | Damit die KI beim Erzeugen von Aufgaben das Niveau trifft. |
| Notify-Entität **oder** Notify-Aktion mit Ziel und Zusatzdaten | Wohin die Fragen gehen. |
| Absenderkennung | Telefonnummer oder Chat-ID, an der eingehende Antworten dem Kind zugeordnet werden. |
| Werktags ab/bis, Wochenende ab/bis | Zeitfenster, in denen gefragt werden darf; das Wochenende lässt sich ganz abschalten. |
| Aktion für Bilder | Nur für Aufgaben mit Bild bei anderen Messengern als Telegram, siehe [Aufgaben mit Bild](#aufgaben-mit-bild). |

### Fach

Du wählst das Kind und die Art des Fachs:

- **Fremdsprache:** Sprache wählen; das Fach heißt wie die Sprache, ein eigener Name ist möglich.
- **Mathematik:** nur ein Name (Vorgabe „Mathe“).
- **Sachfach:** ein Name, z. B. „Biologie“.

Je Fach kann eine abweichende KI-Entität gewählt werden. Die Sprachen eines Fachs lassen sich nachträglich nicht ändern.

### Arbeit / HÜ

| Feld | Bedeutung |
|---|---|
| Art, Datum, Thema | Klassenarbeit oder HÜ, Termin und Überschrift. |
| Lektionen / Themen | Welche Aufgaben dazugehören. Ohne Auswahl gelten alle Aufgaben des Fachs. Im Panel kannst du zusätzlich einzelne Aufgaben, „alle seit Datum X“ oder einen Seitenbereich des Buchs wählen. |
| Abfragen pro Tag | Wie oft am Tag gefragt wird. |
| Beginn (Tage vor dem Termin) | Ab wann die Abfragen laufen. |
| Frequenz zum Termin hin steigern | Erhöht die Zahl der Abfragen, je näher der Termin kommt. |
| Antwortfrist | Eigene Frist für die Aufgaben dieser Arbeit statt des allgemeinen Timeouts. Gehört eine Aufgabe zu mehreren laufenden Arbeiten, gilt die kürzeste. |
| Simulation einplanen, Aufgaben in der Simulation | Siehe [Klassenarbeit oder HÜ simulieren](#klassenarbeit-oder-hü-simulieren). |

## Antworten entgegennehmen

LearnBuddy verschickt Fragen selbst. Für den Rückweg reicht eine Automation die eingehenden Nachrichten an die Aktion `learnbuddy.submit_answer` weiter. Dafür liegen unter `blueprints/automation/learnbuddy/` zwei Blueprints:

- `telegram_antwort.yaml` – für die Telegram-Integration.
- `event_antwort.yaml` – für jede Integration, die eingehende Nachrichten als Event meldet. Event-Typ und die Felder für Absender und Text sind einstellbar.

Die Dateien nach `/config/blueprints/automation/learnbuddy/` kopieren und daraus eine Automation erstellen. Das Kind wird an der Absenderkennung erkannt.

### Telegram einrichten

1. In der Telegram-Bot-Integration den Bot auf **Polling** (oder Webhooks) stellen. Mit „Broadcast“ kann der Bot nur senden. Ein Bot-Token darf nur von einer Home-Assistant-Instanz empfangen werden.
2. Die Chat-ID des Kindes als **erlaubten Chat** beim Bot hinzufügen. Unbekannt? Das Kind schreibt dem Bot; die Chat-ID steht dann als „Unauthorized update“ im Log. Für jeden erlaubten Chat legt die Integration eine `notify`-Entität an.
3. Beim Kind in LearnBuddy diese `notify`-Entität als Messenger-Ziel und die Chat-ID als Absenderkennung eintragen.
4. Aus dem Blueprint `telegram_antwort.yaml` eine Automation erstellen, optional beschränkt auf die Chat-IDs der Kinder.

Tipp: Mit parse_mode „markdown“ lehnt Telegram Nachrichten ab, deren Text `_`, `*` oder `` ` `` enthält. „plain_text“ in den Bot-Optionen vermeidet das.

## Panel

Administratoren finden in der Seitenleiste den Eintrag **LearnBuddy**. Oben wählst du das Kind, darunter gibt es diese Bereiche:

- **Übersicht:** Status des Kindes (aktiv oder pausiert, offene Frage, nächste und letzte Abfrage, laufende Simulation) mit den Aktionen „Jetzt eine Aufgabe stellen“ und „Pausieren/Fortsetzen“. Dazu Kennzahlen (gestellt, richtig, teilweise, falsch, unbeantwortet, Trefferquote), anstehende Arbeiten mit Countdown und Lernstand, die Verteilung auf die Leitner-Boxen und die schwierigsten Aufgaben. Die Ansicht aktualisiert sich von selbst.
- **Aufgaben** (je Fach): Tabelle aller Aufgaben mit Lernstufe und Fehlerquote. Filter nach Suche, Lektion, Quelle, geprüft, Fehlerquote, Erstelldatum und Buchseite. Aufgaben lassen sich in der Zeile bearbeiten, anlegen und einzeln oder gesammelt löschen, freigeben oder einer neuen Arbeit zuordnen.
- **Lektionen/Themen:** Sie werden je Fach als Liste gepflegt und stehen überall als Auswahl bereit. Löschen lässt sich eine Lektion nur, wenn keine Aufgabe mehr dazugehört.
- **Arbeiten** (je Fach): anlegen, ändern, löschen, simulieren.

Weitere Funktionen im Panel:

| Funktion | Für | Braucht KI |
|---|---|---|
| Importieren (Text einfügen → Vorschau → Übernehmen) | Vokabeln, Mathe | nein |
| JSON exportieren / importieren | alle | nein |
| Aus Foto importieren | Vokabeln, Mathe | ja, mit Bildern |
| Fragen aus Buchseite | Sachfach | ja, mit Bildern |
| Aufgaben generieren | Mathe | ja |
| Auswahl nachrechnen | Mathe | nur bei Textaufgaben |
| Selbst nachgerechnet | Mathe | nein |
| Rechenweg erzeugen | Mathe | ja |

Der JSON-Export enthält keine Daten über das Kind; die Lernstatistik ist optional. Beim Import bleiben vorhandene Aufgaben erhalten, Doppelte werden übersprungen. Du wählst, ob die Lektionen aus der Datei übernommen werden oder alles in eine bestehende Lektion kommt.

Nach einem Update zeigt ein noch offenes Browserfenster den Hinweis „Seite neu laden“.

## Vokabeln

Vokabeln werden in beide Richtungen zwischen Muttersprache und Fremdsprache abgefragt. Jede Vokabel kann Alternativen, einen Hinweis und eine Buchseite haben. Der Hinweis ist eine Notiz für die Eltern und wird nicht mitgeschickt.

**Import als Text**, eine Vokabel pro Zeile:

```text
Hund; dog|hound; Nomen
gehen; to go
```

Format: `Ausgangssprache; Zielsprache; optionaler Hinweis`. Alternativen stehen hinter `|`. Als Trennzeichen werden `;`, Tabulator, `=`, ` - ` und `,` erkannt. Vorhandene Vokabeln werden übersprungen. Der Import geht im Panel oder über die Aktion `learnbuddy.import_tasks`.

**Bewertung:** Groß- und Kleinschreibung, Satzzeichen, Artikel und das englische „to“ werden ignoriert, Alternativen zählen als richtig. Ein einzelner Tippfehler oder fehlende Umlaute und Akzente ergeben „fast richtig“; das zählt als richtig, und das Kind bekommt die korrekte Schreibweise genannt. Mit KI-Entität prüft die KI die lokal als falsch gewerteten Antworten auf Synonyme und ungewöhnliche Tippfehler und kann eine kurze Erklärung mitgeben.

## Mathematik

Eine Mathe-Aufgabe besteht aus Aufgabe und Lösung, optional weiteren gültigen Schreibweisen, einem Rechenweg und einer Schwierigkeit von 1 bis 5. Sie kommt auf vier Wegen ins Fach:

- **Eingeben** im Panel über „Neue Aufgabe“.
- **Importieren** als Text: `Aufgabe; Lösung; optionaler Hinweis`, weitere Schreibweisen hinter `|`. Trennzeichen sind hier nur `;` und Tabulator.
- **Aus Foto importieren**, siehe [unten](#aufgaben-aus-fotos-importieren).
- **Generieren** (mit KI): Thema, Anzahl (bis 20), Schwierigkeit und eine optionale Beschreibung. Als Beispiele dienen die markierten Aufgaben, sonst die Aufgaben des Themas.

**Bewertung:** Zahlen werden unabhängig von der Schreibweise verglichen: `0,5`, `0.5`, `1/2` und `½` sind gleich, ebenso `1 1/2` und `1,5`. Ein vorangestelltes `x =` wird ignoriert, `3 m` und `3 Meter` gelten als gleich. Stimmt der Wert, fehlt aber die Einheit, ist die Antwort „fast richtig“. Ist die Lösung keine Zahl (z. B. „ungerade“), bewertet die KI; ohne KI zählt dann nur die genaue Übereinstimmung.

**Rechenweg auf Nachfrage:** Nach einer falschen Antwort bekommt das Kind die Lösung und die Frage, ob es den Rechenweg sehen möchte. Antwortet es mit „Ja“ oder 👍, kommt er in nummerierten Schritten. Ist keiner gespeichert, schreibt ihn die KI und er wird an der Aufgabe gespeichert. Über „Rechenweg erzeugen“ lässt er sich vorab erstellen, lesen und bearbeiten.

**Erzeugte Aufgaben werden geprüft:** Die KI liefert zu jeder Aufgabe die Rechnung, die LearnBuddy selbst nachrechnet. Geht das nicht (z. B. bei Textaufgaben), löst die KI die Aufgabe ein zweites Mal, ohne die Lösung zu kennen. Stimmt das Ergebnis nicht, wird die Aufgabe verworfen. Gespeicherte Aufgaben sind „nicht geprüft“ und werden erst nach deiner Freigabe abgefragt.

**Nachrechnen:** „Auswahl nachrechnen“ prüft markierte Aufgaben, auch selbst eingegebene. Reine Rechnungen (z. B. `3/4 + 1/8 = ?`) rechnet LearnBuddy selbst, sonst löst die KI. Bestätigte Aufgaben bekommen das Kennzeichen „nachgerechnet“ bzw. „von der KI gegengeprüft“. Bei einem anderen Ergebnis erscheint „Lösung weicht ab“; geändert wird nichts von selbst. Der gefundene Wert bleibt als Vorschlag stehen und lässt sich mit „Übernehmen“ als neue Lösung setzen; dabei werden Rechenweg, unpassende Schreibweisen und die Statistik der Aufgabe gelöscht. Hast du selbst nachgerechnet, markierst du die Aufgaben mit „Selbst nachgerechnet“.

### Aufgaben mit Bild

„Neue Aufgabe“ fragt bei Mathe nach der Art: **Rechenaufgabe** oder **Aufgabe mit Bild** (Diagramm, Kurve, Zeichnung). Für eine Aufgabe mit Bild lädst du das Bild einmal hoch (PNG, JPEG, WebP oder GIF, höchstens 10 MB) und trägst die Teilaufgaben mit ihren Lösungen ein. Aus jeder Zeile wird eine eigene Aufgabe mit demselben Bild.

Das Bild wird verkleinert unter `/config/learnbuddy/uploads/` gespeichert, Zusatzdaten wie der Aufnahmeort werden entfernt. Es wird gelöscht, sobald keine Aufgabe mehr darauf verweist.

Das Kind bekommt das Bild mit der Aufgabe als Bildunterschrift:

- **Telegram:** automatisch, wenn die `notify`-Entität des Kindes zur Telegram-Integration gehört.
- **Andere Messenger:** über das Feld „Aktion für Bilder“ beim Kind. Zur Verfügung stehen die Variablen `bild_url` (zehn Minuten gültige Adresse), `bild_pfad` (Datei auf dem Home-Assistant-Rechner) und `text`. Eine eingetragene Aktion hat Vorrang vor dem Telegram-Weg.
- **Ohne beides** werden Aufgaben mit Bild für dieses Kind nicht gestellt; das Panel weist darauf hin.

```yaml
# Companion-App: Bild in der Benachrichtigung (ungeprüft)
- action: notify.mobile_app_handy
  data:
    message: "{{ text }}"
    data:
      image: "{{ bild_url }}"
```

Bei der Companion-App muss das Handy die Adresse erreichen können. Für andere Messenger steht die passende Aktion in deren Dokumentation.

Die KI bekommt das Bild dazu, wenn die gewählte Entität Anhänge unterstützt. Wie zuverlässig sie Werte aus einem Diagramm abliest, hängt stark vom Modell ab; im Test löste das Standardmodell der OpenAI-Integration zwei von drei Diagramm-Fragen falsch. Prüfe KI-Vorschläge bei Bild-Aufgaben deshalb, bevor du sie übernimmst. Aufgaben mit Bild sind nicht im JSON-Export enthalten, und die KI erzeugt keine.

## Sachfächer

Ein Sachfach fragt Wissen aus Texten ab. Jede Frage hat eine Musterantwort und eine von zwei Formen:

- **Kurzantwort:** Das Kind antwortet frei in ein bis zwei Sätzen. Die KI vergleicht mit Musterantwort und Kernpunkten und urteilt „richtig“, „teilweise richtig“ oder „falsch“. Bei „teilweise richtig“ erfährt das Kind, was fehlt; die Aufgabe bleibt in ihrer Lernstufe. Kurzantworten brauchen eine KI-Entität. Fällt die KI aus, zählt die Antwort nicht und das Kind bekommt die Musterantwort zum Vergleichen.
- **Auswahl:** Die richtige und zwei bis drei falsche Antworten werden bei jeder Abfrage neu gemischt und als A, B, C, D geschickt. Das Kind antwortet mit dem Buchstaben oder dem Text. Die Bewertung läuft ohne KI.

**Fragen aus Buchseite:** Du lädst bis zu vier Fotos hoch und wählst Thema, Anzahl (bis 15) und Frageform. Die KI schlägt Fragen mit Musterantwort, Kernpunkten bzw. falschen Antworten und der Belegstelle vor. Diese Fragen warten immer auf deine Freigabe, weil sich hier nichts nachrechnen lässt. An der Frage siehst du die Seite und die Belegstelle. Die Seite geht nie ans Kind und wird gelöscht, sobald keine Frage mehr darauf verweist. Fragen lassen sich auch von Hand anlegen.

## Aufgaben aus Fotos importieren

Bei Vokabel- und Mathe-Fächern liest „Aus Foto importieren“ bis zu vier Fotos von Buchseiten oder Arbeitsblättern aus. Gespeichert wird erst, nachdem du die Vorschau geprüft, bei Bedarf korrigiert und „Übernehmen“ geklickt hast. Die Fotos werden danach gelöscht.

- **Vokabeln:** Wort, Übersetzung, gedruckte Seitenzahl und der Verweis auf die Unit-Seite. Beispielsätze und Lautschrift bleiben weg.
- **Mathe:** Aufgabentext und Lösung; fehlt die Lösung auf dem Foto, löst die KI. Jede Lösung wird nachgerechnet. Die Vorschau zeigt „nachgerechnet“, „von der KI gegengeprüft“, eine abweichende Lösung zum Übernehmen oder „Lösung nicht bestätigt“. Aufgaben, die eine Abbildung brauchen, sind abgewählt; lege sie als „Aufgabe mit Bild“ an.

Wie gut gelesen wird, hängt vom Modell und vom Foto ab; die Vorschau ist deshalb Pflicht.

## Wann und was gefragt wird

**Zeitplan:** Gefragt wird nur in den Zeitfenstern des Kindes und nur, solange eine Arbeit ansteht: ab dem eingestellten Beginn bis zum Termin, so oft am Tag wie eingestellt. Eine neue Frage kommt erst, wenn die vorige beantwortet oder abgelaufen ist. Verpasste Zeitpunkte werden nicht nachgeholt.

**Leitner-System:** Jede Aufgabe liegt in einer von fünf Boxen (Vokabeln je Abfragerichtung). Eine richtige Antwort schiebt sie eine Box weiter, eine falsche zurück in Box 1; unbeantwortete Fragen und „teilweise richtig“ ändern nichts. Wiederholt wird nach 0, 1, 2, 4 und 7 Tagen (Box 1 bis 5). Vor einer Arbeit schrumpfen die Abstände, am letzten Tag ist alles wieder fällig. Gefragt werden zuerst fällige Aufgaben aus der niedrigsten Box. Nicht freigegebene Aufgaben werden nie gestellt.

**Zusatzaufgaben auf Wunsch:** Ist gerade keine Frage offen, kann das Kind selbst weitere Aufgaben anfordern: mit 👍 als Nachricht (eine Aufgabe) oder mit einem Text wie „noch eine“, „mehr“, „noch 10 mehr“ oder „5 more“. Die Aufgaben kommen nacheinander, höchstens 20 auf einmal, auch außerhalb der Zeitfenster. Die Serie endet, wenn eine Frage unbeantwortet bleibt oder die Abfragen pausiert werden. Eine Reaktion auf die Nachricht (z. B. der Daumen als Telegram-Reaktion) funktioniert nicht, weil Home Assistant Reaktionen nicht als Ereignis meldet.

**Pausieren:** über den Schalter „Abfragen aktiv“, das Panel oder die Aktion `learnbuddy.pause`, optional bis zu einem Zeitpunkt (z. B. für Ferien).

## Klassenarbeit oder HÜ simulieren

Im Bereich „Arbeiten“ hat jede Arbeit den Knopf „Klassenarbeit simulieren“ bzw. „HÜ simulieren“. Du wählst die Anzahl der Aufgaben (bis 30) und den Weg. Die Aufgaben werden zufällig aus den freigegebenen Aufgaben der Arbeit gezogen, möglichst gleichmäßig über ihre Lektionen. Die Lernstatistik bleibt unberührt.

- **Per Ausdruck:** Es entsteht ein Aufgabenblatt im A4-Format als Bild (bei vielen Aufgaben mehrere Seiten) mit Kopf, Feldern für Name, Klasse und Datum, Punktekästchen und Platz für die Antworten. Du kannst die Seiten herunterladen oder drucken. Verschickt wird nichts; die Bilder werden nach 24 Stunden gelöscht.
- **Per Messenger:** Das Kind bekommt das Blatt als Bild (wenn es Bilder empfangen kann) und danach die Aufgaben nacheinander, ohne Rückmeldung nach jeder Antwort. Am Ende kommt die Auswertung mit Punkten und Prozent und den Lösungen zu allem, was nicht richtig war. Jede Aufgabe zählt einen Punkt, „teilweise richtig“ einen halben. Läuft die Antwortfrist einer Aufgabe ab, endet die Simulation mit der Auswertung des bis dahin Beantworteten. Währenddessen gibt es keine geplanten Abfragen. In der Übersicht steht der Fortschritt; dort lässt sich die Simulation abbrechen.

**Einplanen:** Im Dialog einer Arbeit legst du unter „Simulation einplanen“ Datum, Uhrzeit und Anzahl fest. Zu diesem Zeitpunkt startet die Simulation von selbst per Messenger. Sie wird genau einmal versucht: Ist das Kind dann pausiert, läuft schon eine Simulation, gibt es keine Aufgaben oder schlägt das Senden fehl, entfällt sie. War Home Assistant zum Zeitpunkt aus, wird sie bis zu sechs Stunden später nachgeholt.

Eine Note gibt es bewusst nicht, weil jede Schule anders bewertet.

## KI

LearnBuddy funktioniert ohne KI, nur mit weniger Funktionen. Genutzt wird sie für:

- die Bewertung von Antworten, die lokal als falsch gelten (Vokabeln, Mathe-Textantworten), und von Kurzantworten im Sachfach,
- Rechenwege,
- das Erzeugen, Nachrechnen und Auslesen von Aufgaben.

Die Antworten der KI werden nur in fester Struktur angenommen und geprüft. Ist die KI bei einer Bewertung nicht erreichbar, gilt die lokale Bewertung.

Das Panel zeigt je Fach, woran es liegt, wenn etwas nicht geht:

- **Keine KI-Entität gewählt:** Erzeugen, Rechenwege und Funktionen mit Fotos sind aus; im Sachfach werden nur Auswahlfragen gestellt.
- **KI gewählt, aber nicht verfügbar:** wie oben, mit Warnhinweis. Kurzantworten im Sachfach ruhen, bis die KI wieder da ist.
- **KI kann keine Bilder lesen:** nur die Funktionen mit Fotos sind aus.

Schlägt ein Aufruf fehl, unterscheidet die Meldung „nicht erreichbar“ (Verbindung, Konto, Guthaben) von „nichts Brauchbares geliefert“. Fehlt die gewählte Entität oder scheitern drei Aufrufe hintereinander, erscheint unter **Einstellungen → System → Reparaturen** ein Hinweis; er verschwindet, sobald die KI wieder funktioniert.

## Entitäten

Jedes Kind erscheint als Gerät mit diesen Entitäten:

| Entität | Bedeutung |
|---|---|
| Sensor „Nächste Arbeit“ | Datum der nächsten Arbeit, Thema und Fach als Attribute |
| Sensor „Trefferquote“ | Anteil richtiger Antworten in Prozent |
| Sensor „Offene Frage“ | `offen` oder `keine` |
| Schalter „Abfragen aktiv“ | Abfragen pausieren und fortsetzen |
| Taste „Jetzt abfragen“ | Sofort eine Frage senden |
| Kalender „Arbeiten“ | Alle Arbeiten und HÜs |

## Aktionen

Das Kind wird über `device_id`, `kind_id` oder (bei `submit_answer`) `absender` bestimmt.

| Aktion | Zweck | Weitere Felder |
|---|---|---|
| `learnbuddy.submit_answer` | Antwort eines Kindes bewerten | `text` |
| `learnbuddy.ask_now` | Sofort eine Frage senden | – |
| `learnbuddy.import_tasks` | Vokabeln oder Mathe-Aufgaben aus Text importieren | `fach` oder `fach_id`, `inhalt`, `lektion`, `trennzeichen`, `geprueft` |
| `learnbuddy.generate_tasks` | Mathe-Aufgaben von der KI erzeugen lassen | `fach` oder `fach_id`, `anzahl`, `lektion`, `schwierigkeit`, `beschreibung` |
| `learnbuddy.pause` | Abfragen pausieren | `bis` (optional) |
| `learnbuddy.resume` | Abfragen fortsetzen | – |

```yaml
action: learnbuddy.import_tasks
data:
  device_id: <Gerät des Kindes>
  fach: Englisch
  lektion: Unit 3
  inhalt: |
    Hund; dog|hound; Nomen
    gehen; to go
```

Eine hier angegebene Lektion, die es noch nicht gibt, wird angelegt.

## Events

| Event | Daten |
|---|---|
| `learnbuddy_question_sent` | `kind_id`, `fach_id`, `aufgabe_id`, `arbeit_id`, `richtung` |
| `learnbuddy_answer_evaluated` | wie oben, zusätzlich `ergebnis` (`richtig`, `fast_richtig`, `teilweise`, `falsch`, `unbeantwortet`) und `bewertet_von` (`lokal` oder `ki`) |
| `learnbuddy_simulation_finished` | `kind_id`, `fach_id`, `arbeit_id`, `punkte`, `moeglich`, `prozent`, `vollstaendig` |

Die Events enthalten keine Namen und keine Aufgabeninhalte. Während einer Simulation wird `learnbuddy_answer_evaluated` nicht ausgelöst. `teilweise` gibt es nur bei Kurzantworten im Sachfach.

Beispiel für eine Belohnung:

```yaml
triggers:
  - trigger: event
    event_type: learnbuddy_answer_evaluated
    event_data:
      ergebnis: richtig
actions:
  - action: counter.increment
    target:
      entity_id: counter.bildschirmzeit_bonus
```

## Datenschutz

- Alle Daten liegen lokal in Home Assistant (`.storage/learnbuddy.*`, im Config Entry und unter `/config/learnbuddy/uploads/`) und sind Teil des HA-Backups.
- Der Name des Kindes wird erst lokal in die fertige Nachricht eingesetzt. Events, Logs und Diagnosedaten enthalten keine Namen, Absenderkennungen oder Aufgabeninhalte.
- Nachrichten laufen über den von dir gewählten Messenger; dessen Bedingungen gelten zusätzlich.
- An die KI gehen zur Bewertung nur die Aufgabe, die Lösung samt Alternativen bzw. Kernpunkten, die Sprachen und die Antwort des Kindes. Name und Absenderkennung werden nie übertragen. Die Antwort ist Freitext des Kindes und geht unverändert an den gewählten KI-Dienst.
- Beim Erzeugen und Auslesen von Aufgaben gehen zusätzlich Klassenstufe, Schulart und Bundesland an die KI, dazu Thema, deine Beschreibung und bis zu zehn Beispielaufgaben.
- Bilder von Aufgaben gehen an den Messenger und, wenn die KI beteiligt ist, an den KI-Dienst. Fotos von Buchseiten gehen nur an den KI-Dienst. Metadaten werden vorher entfernt.
- Das Panel und seine Schnittstelle sind nur für Administratoren erreichbar.

## Bekannte Einschränkungen

- Eine Mathe-Aufgabe hat genau ein kurzes Ergebnis. Mehrteilige Aufgaben legst du als mehrere Aufgaben an.
- PDFs lassen sich nicht importieren, nur Fotos. Handschrift wird nicht gezielt unterstützt.
- Sachfächer kennen keinen Text-Import, und ihre Fragen werden ohne Bild gestellt.
- Auswahlfragen lassen sich erraten; die Statistik unterscheidet das nicht.
- Der JSON-Download funktioniert im Browser; in der Companion-App kann er je nach Gerät blockiert sein.
- Ferien werden nicht automatisch erkannt; nutze dafür `learnbuddy.pause` mit `bis`.
- Die Oberfläche gibt es auf Deutsch und Englisch; die Feldnamen in Aktionen und Events sind deutsch.

## Entfernen

Die Integration unter **Einstellungen → Geräte & Dienste** löschen. Dabei werden alle gespeicherten Aufgaben und Statistiken entfernt.

## Entwicklung

```bash
uv sync
uv run pytest --cov
uv run ruff check . && uv run ruff format --check .
uv run mypy

cd frontend-src        # Panel (Lit + TypeScript), braucht Node.js 24
npm ci
npm run check          # Typprüfung und Build nach custom_components/learnbuddy/frontend/
```

Das gebaute Panel wird eingecheckt, damit die Installation über HACS kein Node.js braucht. Das ursprüngliche Lastenheft steht in `SPEC.md`, Hinweise zur Architektur in `CLAUDE.md`.

## Lizenz

LearnBuddy steht unter der [MIT-Lizenz](LICENSE). Die mitgelieferte Schrift DejaVu Sans (für die Aufgabenblätter) steht unter ihrer eigenen freien Lizenz, siehe `custom_components/learnbuddy/fonts/LICENSE_DEJAVU.txt`.
