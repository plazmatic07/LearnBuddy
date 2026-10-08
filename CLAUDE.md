# LearnBuddy – Arbeitsnotizen

Home Assistant Custom Integration (`learnbuddy`). Ursprüngliches Lastenheft: `SPEC.md`. Zielversion: HA 2026.9.x, Python ≥ 3.14.2. Stand: Version 0.8.1, Storage 1.14.

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
- `.storage/learnbuddy.config`: Laufzeitdaten je Kind (aktiv, pausiert_bis, offene Frage, Zusatzaufgaben samt Lektion, gemerkter Übungswunsch, Simulation), explizite Aufgaben-Zuordnung je Arbeit, Marke für gesendete geplante Simulationen.
- `.storage/learnbuddy.<kind_id>_<fach_id>`: Aufgaben inkl. Statistik je Richtung und die verwaltete Liste der Lektionen.
- `manager.py` orchestriert (Fragen stellen, Antworten, Fristen, Timer, Simulation). Reine Logik ohne HA-Abhängigkeit: `scheduler.py` (Leitner, Auswahl), `evaluation.py` (Vokabeln), `mathe.py`, `rechnen.py` (sicherer Auswerter mit `ast` + `Fraction`), `sach.py`, `simulation.py`, `wunsch.py`, `importer.py`.
- `verwaltung.py` enthält die Datenpflege fürs Panel; `websocket_api.py` ist nur die dünne, admin-geschützte Hülle (`learnbuddy/…`). Fehler: `VerwaltungError(code, schluessel)`; den Schlüssel übersetzt das Panel (`err_<schluessel>` in `frontend-src/src/i18n.ts`).
- `ai.py`: alle KI-Aufrufe über `ai_task` mit festem Schema und Parser; nur mit ausdrücklich gewählter Entität (Optionen, Abweichung je Fach). `ai_task` wird spät importiert (`_async_generate_data`), Tests mocken diese Funktion. `KiBewerter.status`: `keine`, `nicht_verfuegbar`, `ohne_bilder`, `ok`. Repair-Issue `ki_<entity>` nach drei Fehlern in Folge oder fehlender Entität.
- `eingang.py`: nimmt Antworten direkt von den Ereignissen `telegram_text` und `whatsapp_message_received` (ha-wa-bridge) sowie einem frei einstellbaren Ereignis an; Zuordnung über `manager.kind_per_absender`. `manager.antwort_doppelt` verhindert, dass eine Nachricht doppelt zählt, wenn zusätzlich eine Automation `submit_answer` aufruft (gleicher Text vom anderen Weg binnen 5 s). Unbekannte Absender merkt sich der Manager nur im Speicher (max. 5, 1 h, nur solange ein Kind auf eine Antwort wartet); das Panel bietet sie zum Übernehmen an (`sender/assign`, `sender/dismiss`). `async_setze_absender` ändert den Subentry ohne Reload, indem es `_basis` nachzieht.
- Prüfungskalender (optional je Kind, Abschnitt im Kind-Formular: `kalender_aktiv`, `kalender_entity`, `kalender_um`): `kalender.py` ist reine Logik (Termin aus Event, Art-Erkennung, Fach-Vorauswahl nur bei eindeutigem Kürzel). `manager.async_kalender_pruefen` liest über die Aktion `calendar.get_events` (liefert keine uid, deshalb Kennung = Datum + Text) täglich zur Uhrzeit des Kindes, 2 min nach dem Start und auf Knopfdruck; Stand nur im Speicher (`KalenderStand`). Vorschlag = Termin, der weder ignoriert (`config_store.kalender_ignoriert`, Storage 1.12) noch über `kalender_uid` an einer Arbeit eingetragen ist. WS `calendar/refresh|ignore|restore`, Dashboard `kalender` + `vorschlaege`. Tests: die gemockte Aktion erst nach dem Setup registrieren, weil die eigene Kalender-Plattform die echte Aktion anlegt.
- Fach aus dem Panel (`subjects/create`, `manager.async_fach_anlegen`): Subentry wird ohne Reload übernommen (`_ohne_reload`, `_basis` nachziehen), damit das Panel offen bleibt.
- Verlauf (abschaltbar über die Optionen `verlauf` und `wochenreport`): `verlauf.py` ist reine Logik (Tageszähler je Kind/Fach, Lektionen, falsche Antworten je Aufgaben-ID, Lernstand-Schnappschuss, Simulationsergebnisse; 400 Tage). Eigene Datei `.storage/learnbuddy.verlauf` mit eigener Version (`VerlaufStore`), keine Migration der anderen Dateien. Gebucht wird in `manager`: Frage gesendet, `_feuere_bewertung` (Antwort und Frist), Frage abgebrochen, `_async_sim_ende`, Tageswechsel. Simulationsantworten zählen nicht. WS `progress` und `weekly_report`; Dashboard meldet `verlauf`/`wochenreport`. Panel: `fortschritt.ts` (`lh-fortschritt`, SVG-Diagramme ohne Bibliothek, Farben mit dem dataviz-Validator für hell und dunkel geprüft, Tabellenansicht als Ausweichform).
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
- Frage abbrechen (`manager.async_frage_abbrechen`, WS `cancel_question`, Aktion `cancel_question`): zählt nicht (`gefragt` wird zurückgenommen, Box bleibt, kein `answer_evaluated`), das Kind bekommt eine Nachricht, Zusatzaufgaben enden. Nicht während einer Simulation.
- Üben auf Wunsch: `wunsch.erkenne_uebungswunsch` (reine Logik: Auslöserwort + Fach/Lektion; ohne Zuordnung `fach_id=None`). Ohne offene Frage: Regeln, dann KI-Rückfall (`ai.async_deute_wunsch`, nur allgemeine KI, Option `wunsch_ki`), sonst Hinweis mit Fächern. Mit offener Frage nur eindeutige Regel-Treffer; die Frage wird über `_frage_zuruecknehmen` zurückgenommen (wie Abbrechen, ohne Nachricht). Ohne Zahl: Nachfrage, `KindZustand.wunsch_offen` 10 Minuten. Serie läuft über die Zusatzaufgaben; `zusatz_filter` gilt, bis eine normale (nicht kurze) Frage gestellt wird. Nicht bei ausgeschaltetem Kind oder Simulation.
- „Jetzt abfragen“ im Panel (nur noch je Fach, der Knopf in der Statuszeile ist entfallen): `manager.async_abfrage_starten`, WS `ask` und `ask_count` (Vorschau der Auswahl). Filter `models.AbfrageFilter` (Lektionen, Seite von/bis, Fehlerquote ab), gespeichert als `KindZustand.zusatz_filter`; er gilt für die Serie, bis eine normale (nicht kurze) Frage gestellt wird. Leerer Filter = ganzes Fach mit normaler Auswahl (Arbeiten zuerst). Ungeprüfte Aufgaben (`geprueft=False`, warten auf Freigabe) werden nie gefragt. Dashboard-Zustand `abfrage` zeigt die laufende Serie. Ohne Fach merkt sich `_serie_frei` (nur im Speicher), dass die Serie jedes Fach fragen darf. Taste und Aktion `ask_now` stellen weiter genau eine Frage.
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

- Ferien nur über manuelles Pausieren (`pause` mit `bis`).
- Warteschlange für Abfragen: Heute gibt es je Kind nur eine Serie; eine zweite über „Jetzt abfragen“ ersetzt die laufende (offene Frage zählt als unbeantwortet). Gewünscht: mehrere Abfragen einreihen (z. B. erst 5 aus Mathe, dann 5 aus Englisch), die nächste startet nach der vorherigen, alle stehen in der Statuszeile untereinander. Vor dem Bau planen (Speicherformat, Verhalten bei Zeitablauf, Abbrechen einzelner Einträge, Wünsche des Kindes dazwischen).

## Icon

Quelle ist `assets/icon.svg`. Daraus entstehen `custom_components/learnbuddy/brand/icon.png` (256 px) und `icon@2x.png` (512 px), transparent. Rendern z. B. mit `@resvg/resvg-js`.
