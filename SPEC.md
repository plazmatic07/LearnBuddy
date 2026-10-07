# LearnBuddy – Home Assistant Custom Integration

## Lastenheft / Spezifikation

**Domain:** `learnbuddy`
**Ziel:** Kinder bei der Vorbereitung auf Klassenarbeiten und Hausaufgabenüberprüfungen (HÜ) unterstützen. Die Integration stellt regelmäßig Übungsaufgaben per Messenger, nimmt Antworten entgegen, bewertet sie und erklärt bei Fehlern den Lösungsweg. KI und Messenger werden **nicht** selbst implementiert, sondern über bestehende HA-Integrationen genutzt.

---

## 1. Grundprinzipien

1. **Messenger-agnostisch:** Der Anwender wählt pro Kind eine vorhandene `notify`-Entität bzw. einen Notify-Service (WhatsApp Business, Telegram, Companion App …). Die Integration enthält keinen Messenger-Code.
2. **KI-agnostisch:** Generierung und Bewertung laufen über vorhandene HA-KI-Integrationen (Gemini, Claude, ChatGPT, Ollama) via `ai_task.generate_data` (strukturierte Ausgabe) bzw. `conversation.process`. Der Anwender wählt die Entität aus.
3. **Datensparsamkeit:** An KI-Dienste werden keine personenbezogenen Daten gesendet. Der Name des Kindes wird erst lokal in die fertige Nachricht eingesetzt.
4. **Alles im HA-Backup:** Persistenz ausschließlich über den HA-Storage bzw. unter `/config/`.

---

## 2. Begriffe & Datenmodell

Alle Objekte haben eine UUID `id`, `erstellt` und `geaendert` (ISO-8601-Zeitstempel).

### 2.1 Kind
| Feld | Beschreibung |
|---|---|
| `name` | Vorname (Ansprache) |
| `klassenstufe`, `schulart`, `bundesland` | Kontext für KI-Generierung (Lehrplan, Niveau) |
| `notify_target` | Gewählte notify-Entität / Service |
| `absender_kennung` | Telefonnummer / Chat-ID zur Zuordnung eingehender Antworten |
| `ruhezeiten` | Zeitfenster ohne Abfragen (Schule, Schlafenszeit), Wochenend-/Ferienregel |
| `aktiv` | Pausieren möglich |

### 2.2 Fach
`kind_id`, `name`, `typ` (`vokabel` | `mathe`, erweiterbar), `sprachen` (bei Vokabeln, z. B. `de`/`en`).

### 2.3 Aufgabe (eine Storage-Datei pro Kind und Fach)
Gemeinsame Felder:
`fach_id`, `lektion` (z. B. „Unit 3“), `quelle` (`upload` | `generiert` | `manuell`), `geprueft` (bool), `statistik` {`box` (Leitner 1–5), `richtig`, `falsch`, `zuletzt_gefragt`, `zuletzt_falsch`}.

**Typ `vokabel`:**
```json
{"frage": {"de": "Hund", "en": "dog"},
 "alternativen": {"de": [], "en": ["hound"]},
 "hinweis": "optional, z. B. Wortart"}
```
Abfrage in beide Richtungen (DE→EN, EN→DE); Statistik je Richtung.

**Typ `mathe`:**
```json
{"aufgabe": "…", "loesung": "…", "rechenweg": ["Schritt 1", "…"],
 "thema": "Bruchrechnen", "schwierigkeit": 1-5}
```

### 2.4 Arbeit / HÜ
`fach_id`, `art` (`arbeit` | `hue`), `datum`, `thema`, `aufgaben_ids` (Referenzen, keine Kopien), `frequenz` (Abfragen pro Tag, Start-Zeitraum vor Termin), `intensivierung` (Frequenz steigt zum Termin).

### 2.5 Sitzung / offene Frage
Pro Kind max. eine offene Frage: `aufgabe_id`, `richtung`, `gestellt_um`, `timeout`. Persistent, damit ein HA-Neustart den Zustand nicht verliert.

### 2.6 Ablage
- `.storage/learnbuddy.config` (Kinder, Fächer, Arbeiten)
- `.storage/learnbuddy.<kind>_<fach>` (Aufgaben inkl. Statistik)
- Originaldateien (Fotos/PDFs): `/config/learnbuddy/uploads/` – **nicht** `/config/www`
- Storage-Versionierung mit Migrationen von Anfang an.

---

## 3. Funktionen

### 3.1 Einrichtung (Config Flow / Options Flow)
- Kind anlegen/bearbeiten inkl. Messenger-Ziel, Absenderkennung, Ruhezeiten
- KI-Entität wählen (global, optional pro Fach überschreibbar)
- Fächer anlegen

### 3.2 Datenpflege (eigenes Seitenleisten-Panel)
- Tabelle aller Aufgaben je Kind/Fach mit Filter (Zeitraum `erstellt`, Lektion, Fehlerquote, Quelle, geprüft)
- Inline-Bearbeitung, Einzel- und Mehrfachlöschung (Warnung, wenn einer Arbeit zugeordnet)
- Arbeit/HÜ anlegen: Datum, Thema, Frequenz; Aufgaben per Mehrfachauswahl oder Schnellauswahl („alle aus Unit 3“, „alle seit Datum X“) zuordnen
- Import: CSV/Text (Vokabellisten), Foto/PDF (Extraktion per KI-Vision → Vorschau → Übernehmen)
- „Weitere Aufgaben generieren“ (KI, auf Basis vorhandener Beispiele) → Ergebnisse als `geprueft: false`, Freigabe in der UI
- Export/Import als JSON
- Fortschrittsansicht: Trefferquote, Schwachstellen, Verlauf
- Kommunikation Panel ↔ Backend über eigene WebSocket-API mit Admin-Berechtigungsprüfung

### 3.3 Abfrage-Logik
- Scheduler wählt basierend auf anstehenden Arbeiten, Frequenz, Intensivierung und Ruhezeiten den nächsten Abfragezeitpunkt
- Aufgabenauswahl nach Leitner-System (falsche Antworten kommen häufiger)
- Personalisierte Nachricht mit Namen (lokal eingesetzt)
- Timeout für offene Fragen; danach gilt die Frage als unbeantwortet (nicht falsch)

### 3.4 Antwortverarbeitung
- Service `learnbuddy.submit_answer` (`kind_id` oder `absender`, `text`)
- Mitgelieferte **Blueprints** verbinden Messenger-Events (z. B. WhatsApp-Business-Webhook, `telegram_text`) mit dem Service
- Bewertung:
  - Vokabeln: erst lokal (Normalisierung: Groß/Klein, Artikel, „to “, Satzzeichen; Alternativen), bei Unklarheit KI (Tippfehler, Synonyme). Ergebnis: richtig / fast richtig / falsch
  - Mathe: KI vergleicht mit Musterlösung; bei Falsch → Rechenweg erklären, kindgerecht
- Feedback-Nachricht ans Kind; Statistik aktualisieren

### 3.5 Qualitätssicherung KI
- Ausschließlich strukturierte KI-Ausgabe (JSON-Schema), Validierung vor Speicherung
- Mathe: Musterlösung wird verifiziert (wo möglich rechnerisch per Python/sympy, sonst zweiter KI-Aufruf)
- Generierte Aufgaben erst nach Freigabe aktiv (konfigurierbar)
- Darstellung messengertauglich: kein LaTeX, Unicode für Brüche/Potenzen (½, x², √)

### 3.6 Entitäten
Pro Kind: `sensor` nächste Arbeit, `sensor` Trefferquote, `sensor` offene Frage; `switch` Abfragen aktiv; `button` jetzt abfragen; `calendar` mit Arbeiten/HÜs. **Keine Aufgabenlisten als Attribute.**

### 3.7 Services
`submit_answer`, `ask_now`, `generate_tasks`, `import_tasks`, `pause`/`resume`.

### 3.8 Events
`learnbuddy_question_sent`, `learnbuddy_answer_evaluated` (für Belohnungs-Automationen, z. B. Bildschirmzeit).

---

## 4. Ausbaustufen

| Phase | Inhalt |
|---|---|
| **1 – MVP** | Datenmodell + Storage, Config Flow, Vokabeln (manuell/CSV), Scheduler, Senden, `submit_answer`, lokale Bewertung, Entitäten, Blueprints |
| **2** | Panel (Tabelle, Bearbeiten, Arbeit anlegen mit Auswahl), KI-Bewertung, Leitner |
| **3** | Mathe inkl. Rechenweg-Erklärung und Verifikation, KI-Generierung mit Freigabe |
| **4** | Foto/PDF-Import per KI-Vision, Fortschrittsansicht, Wochenreport an Eltern |

---

## 5. Qualitätsanforderungen

- Ziel: HA **Integration Quality Scale** mindestens Silber, Gold anstreben
- Vollständig async, keine blockierenden Aufrufe im Event Loop
- Typisierung (mypy strict), Linting/Format mit `ruff`
- Tests mit `pytest-homeassistant-custom-component`, Testabdeckung ≥ 90 % für Logik (Scheduler, Bewertung, Leitner, Storage-Migration, Config Flow)
- KI- und Notify-Aufrufe in Tests gemockt
- `hassfest` und HACS-Validierung grün (GitHub Actions)
- Übersetzungen `de` und `en` (`strings.json`, `translations/`)
- Diagnostics-Support mit Schwärzung personenbezogener Daten
- Saubere Fehlerbehandlung: KI/Messenger nicht erreichbar → Logging, Retry, kein Absturz
- Dokumentation: README (Installation via HACS, Einrichtung, Blueprints, Datenschutzhinweise)

---

## 6. Repository-Struktur

```
custom_components/learnbuddy/
  __init__.py  manifest.json  const.py  config_flow.py
  storage.py  models.py  scheduler.py  evaluation.py  ai.py  messaging.py
  websocket_api.py  services.py  services.yaml  diagnostics.py
  sensor.py  switch.py  button.py  calendar.py
  strings.json  translations/de.json  translations/en.json
  frontend/            (Panel, gebautes JS)
blueprints/automation/learnbuddy/
frontend-src/          (Panel-Quellcode, Lit + TypeScript)
tests/
.github/workflows/
hacs.json  README.md  CLAUDE.md
```
