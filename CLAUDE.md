# LearnBuddy – Arbeitsnotizen

Home Assistant Custom Integration (`learnbuddy`). Ursprüngliches Lastenheft: `SPEC.md`. Zielversion: HA 2026.9.x, Python ≥ 3.14.2. Stand: Version 0.6.3, Storage 1.11.

Das Projekt hieß früher „Lernhelfer“ und „Lernbuddy“. Im Code gibt es keine Migration von den alten Namen; nur der JSON-Import nimmt noch Exporte mit dem Format `lernbuddy-aufgaben` an.

## Befehle

```bash
uv sync                                   # Umgebung (.venv) aufbauen
uv run pytest --cov --cov-report=term-missing
uv run ruff check . && uv run ruff format --check .
uv run mypy
(cd frontend-src && npm run check)        # Panel: tsc + esbuild-Bundle
```

Nach jeder Änderung in `frontend-src/src` das Bundle neu bauen und mit einchecken. `hassfest` und HACS-Validierung laufen in GitHub Actions (`.github/workflows/validate.yml`).

`hassfest` lokal: Core auf dem passenden Tag klonen, eigenes venv mit `requirements.txt` + `requirements_test.txt` + `ruff`, dann im Core-Ordner:

```bash
python -m script.hassfest --action validate --integration-path <repo>/custom_components/learnbuddy
```

## Architektur

- Ein Config Entry (`single_config_entry`). Optionen: Timeout, Sprache der Nachrichten, KI-Entität, automatische Freigabe.
- Stammdaten als Config Subentries: `kind` (ein Gerät + Entitäten), `fach`, `arbeit`. Die `subentry_id` ist die ID des Objekts.
- `.storage/learnbuddy.config`: Laufzeitdaten je Kind (aktiv, pausiert_bis, offene Frage, Zusatzaufgaben, Simulation), explizite Aufgaben-Zuordnung je Arbeit, Marke für gesendete geplante Simulationen.
- `.storage/learnbuddy.<kind_id>_<fach_id>`: Aufgaben inkl. Statistik je Richtung und die verwaltete Liste der Lektionen.
- `manager.py` orchestriert (Fragen stellen, Antworten, Fristen, Timer, Simulation). Reine Logik ohne HA-Abhängigkeit: `scheduler.py` (Leitner, Auswahl), `evaluation.py` (Vokabeln), `mathe.py`, `rechnen.py` (sicherer Auswerter mit `ast` + `Fraction`), `sach.py`, `simulation.py`, `wunsch.py`, `importer.py`.
- `verwaltung.py` enthält die Datenpflege fürs Panel; `websocket_api.py` ist nur die dünne, admin-geschützte Hülle (`learnbuddy/…`). Fehler: `VerwaltungError(code, schluessel)`; den Schlüssel übersetzt das Panel (`err_<schluessel>` in `frontend-src/src/i18n.ts`).
- `ai.py`: alle KI-Aufrufe über `ai_task` mit festem Schema und Parser; nur mit ausdrücklich gewählter Entität (Optionen, Abweichung je Fach). `ai_task` wird spät importiert (`_async_generate_data`), Tests mocken diese Funktion. `KiBewerter.status`: `keine`, `nicht_verfuegbar`, `ohne_bilder`, `ok`. Repair-Issue `ki_<entity>` nach drei Fehlern in Folge oder fehlender Entität.
- `eingang.py`: nimmt Antworten direkt von den Ereignissen `telegram_text` und `whatsapp_message_received` (ha-wa-bridge) sowie einem frei einstellbaren Ereignis an; Zuordnung über `manager.kind_per_absender`. `manager.antwort_doppelt` verhindert, dass eine Nachricht doppelt zählt, wenn zusätzlich eine Automation `submit_answer` aufruft (gleicher Text vom anderen Weg binnen 5 s). Unbekannte Absender merkt sich der Manager nur im Speicher (max. 5, 1 h, nur solange ein Kind auf eine Antwort wartet); das Panel bietet sie zum Übernehmen an (`sender/assign`, `sender/dismiss`). `async_setze_absender` ändert den Subentry ohne Reload, indem es `_basis` nachzieht.
- `messaging.py`: Versand über notify-Entität oder klassische Aktion; Bilder über die eigene Aktion des Kindes, sonst automatisch über `telegram_bot.send_photo` mit signierter Loopback-URL.
- `bilder.py`: `BildAblage` in `<config>/learnbuddy/uploads`, Views `POST /api/learnbuddy/bilder` (nur Admin) und `GET …/{id}` (angemeldet oder signiert). Pillow kodiert neu, EXIF weg, max. 1600 px (`?zweck=seite`: 2400 px). Unbenutzte Uploads werden nach 24 h gelöscht. `media_source.py` löst `media-source://learnbuddy/<id>` für die KI auf.
- `blatt.py`: Aufgabenblatt mit Pillow (A4, 1240×1754) und der mitgelieferten DejaVu-Schrift in `fonts/`; die eingebaute Pillow-Schrift kennt keine Umlaute.
- Panel: `panel.py` registriert `learnbuddy-panel` (nur Admins) und liefert `frontend/` unter `/learnbuddy_static` aus. Quellen in `frontend-src/` (Lit 3, TypeScript strict, esbuild). `panel_version` (`<version>-<prüfsumme>`) aus `learnbuddy/overview` wird mit `import.meta.url` verglichen und löst den Hinweis „Seite neu laden“ aus.
- Entitäten aktualisieren sich per Dispatcher-Signal (`signal_kind_update`), kein Polling.

## Fachliche Regeln

- Aufgaben einer Arbeit = gewählte Lektionen ∪ explizit zugeordnete IDs; ist beides leer, zählen alle Aufgaben des Fachs.
- Lektionen: Panel-Wege akzeptieren nur bekannte Lektionen; die Aktion `import_tasks` und der JSON-Import legen unbekannte an. Aufgaben und Arbeiten verweisen per Name, es gibt kein Umbenennen.
- `Statistik.gefragt` zählt gestellte Fragen; unbeantwortet = gefragt − richtig − falsch − teilweise − offene Frage. „Sicher“ = Karten ab Box 3.
- Antwortfrist: `manager._frist` nimmt die kürzeste Frist der heute laufenden Arbeiten, die die Aufgabe enthalten, sonst die Option Timeout.
- `manager._zustellbar` lässt aus: Bild-Aufgaben ohne Bildweg, Sach-Kurzantworten ohne verfügbare KI.
- Nachrechnen ändert nie selbst eine Lösung; eine Abweichung bleibt als `vorschlag` stehen. Geprüft wird nur gegen `loesung`, nicht gegen Alternativen.
- KI-erzeugte Mathe-Aufgaben, die sich nicht verifizieren lassen, werden verworfen. Fragen aus Buchseiten sind immer ungeprüft.
- Simulation: keine Statistik, kein `answer_evaluated`, am Ende `learnbuddy_simulation_finished`; teilweise = ½ Punkt, unbewertbar zählt nicht. Geplante Simulation: ein Timer je Arbeit, einmaliger Versuch, Nachholen bis 6 h.
- `hinweis` an einer Aufgabe ist eine Notiz für die Eltern und wird nicht verschickt.

## Konventionen

- Vollständig async; kein blockierendes I/O im Event Loop.
- Fachbegriffe im Code deutsch wie in der SPEC (`Kind`, `Fach`, `Arbeit`, `Aufgabe`), Docstrings/Kommentare englisch.
- Keine personenbezogenen Daten in KI-Prompts, Events, Logs (INFO+) oder Dateinamen.
- Keine Aufgabenlisten in Entity-Attributen.
- UI-Texte nur über `strings.json` + `translations/{de,en}.json` (`en.json` = Kopie von `strings.json`). Nachrichten ans Kind stehen in `texte.py`. Ausnahme: Das Panel bringt eigene de/en-Texte mit (`i18n.ts`), weil ein Custom-Panel die Integrations-Übersetzungen nicht laden kann.
- Storage-Änderungen: Version erhöhen, Migration + Test ergänzen.
- TDD für Logik; Notify und KI in Tests immer mocken.
- `import voluptuous as vol` verwenden; Tests prüfen keine Validierungs-Fehlertexte.

## Abweichungen von der SPEC

1. Kinder/Fächer/Arbeiten sind Subentries statt Einträge in `learnbuddy.config`.
2. IDs von Kind/Fach/Arbeit sind ULIDs (`subentry_id`); Aufgaben haben UUID4.
3. Storage-Dateinamen nutzen IDs statt Namen.
4. Zusätzliche Module gegenüber SPEC Abschnitt 6 (u. a. `manager.py`, `verwaltung.py`, `panel.py`, `texte.py`).
5. Mathe: kein eigenes Feld `thema`, das Thema ist die verwaltete Lektion. Verifikation mit eigenem Auswerter statt sympy, sonst zweiter KI-Aufruf. Der Rechenweg kommt nur auf Nachfrage des Kindes.
6. Nicht in der SPEC: Sachfach mit Ergebnis `teilweise`, Foto-Import (ohne PDF), Aufgaben mit Bild, Zusatzaufgaben auf Wunsch, Simulation, Antwortfrist je Arbeit.

## Lehren

- Blueprints: HA wandelt Template-Ergebnisse in Variablen zurück in native Typen (Chat-ID/Antwort „42“ → Zahl); immer explizit `| string` vergleichen.
- Arbeiten-Änderungen werden ohne Reload übernommen (`async_arbeiten_aktualisieren`). Ein Reload entfernt das Panel kurz, und das HA-Frontend wirft den Benutzer dann aus dem Panel.
- Das Zahnrad des Eintrags öffnet die Optionen; `config_panel_domain` nicht setzen, sonst sind sie unerreichbar.
- Das Panel registriert seine Elemente nur, wenn sie noch nicht definiert sind (offener Tab nach Update).
- Telegram-Reaktionen liefert HA nicht als Event.
- Tests: `conftest.zeit` wartet am Ende auf laufende Reloads, sonst bleiben Timer hängen. `upload_ordner` lenkt die Bildablage in ein Temp-Verzeichnis, die autouse-Fixture `ki_entitaet` legt `ai_task.test` an. Nach großen Zeitsprüngen oder einem Reload stirbt der WS-Testclient; dann `manager.verwaltung` direkt aufrufen.

## Offen

- Fortschrittsansicht und Wochenreport (aus der SPEC).
- Wunsch des Users (2026-10-07, für später): die aktuell offene Abfrage abbrechen können (Panel-Knopf, evtl. Aktion/Taste); zu klären: zählt sie dann als unbeantwortet oder gar nicht, bekommt das Kind eine Nachricht.
- Ferien nur über manuelles Pausieren (`pause` mit `bis`).

## Icon

Quelle ist `assets/icon.svg`. Daraus entstehen `custom_components/learnbuddy/brand/icon.png` (256 px) und `icon@2x.png` (512 px), transparent. Rendern z. B. mit `@resvg/resvg-js`.
