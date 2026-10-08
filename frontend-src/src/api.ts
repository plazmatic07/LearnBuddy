import type {
  AbfrageAuswahl,
  ArbeitEingabe,
  Dashboard,
  GenerierEingabe,
  SeitenEingabe,
  SimulationsErgebnis,
  SimulationsWeg,
  FotoVorschau,
  GenerierErgebnis,
  NachrechnenErgebnis,
  Aufgabe,
  AufgabeEingabe,
  Hass,
  ImportErgebnis,
  ImportVorschau,
  JsonImportErgebnis,
  LoeschErgebnis,
  Uebersicht,
  Fachart,
  Fortschritt,
  Wochenreport,
} from "./types";

/** Thin typed wrapper around the admin-only WebSocket API of the integration. */
export class Api {
  constructor(private readonly hass: Hass) {}

  private call<T>(typ: string, daten: Record<string, unknown> = {}): Promise<T> {
    return this.hass.callWS<T>({ type: `learnbuddy/${typ}`, ...daten });
  }

  uebersicht(): Promise<Uebersicht> {
    return this.call("overview");
  }

  dashboard(kindId: string): Promise<Dashboard> {
    return this.call("dashboard", { kind_id: kindId });
  }

  frageStellen(
    kindId: string,
    fachId: string | null,
    auswahl: AbfrageAuswahl = {},
    anzahl = 1,
  ): Promise<void> {
    return this.call("ask", {
      kind_id: kindId,
      fach_id: fachId,
      ...auswahl,
      anzahl,
    });
  }

  /** How many tasks a manual request could choose from. */
  async abfrageUmfang(
    kindId: string,
    fachId: string | null,
    auswahl: AbfrageAuswahl,
  ): Promise<number> {
    const antwort = await this.call<{ aufgaben: number }>("ask_count", {
      kind_id: kindId,
      fach_id: fachId,
      ...auswahl,
    });
    return antwort.aufgaben;
  }

  async frageAbbrechen(kindId: string): Promise<boolean> {
    const antwort = await this.call<{ abgebrochen: boolean }>("cancel_question", {
      kind_id: kindId,
    });
    return antwort.abgebrochen;
  }

  setzeAktiv(kindId: string, aktiv: boolean): Promise<void> {
    return this.call("set_active", { kind_id: kindId, aktiv });
  }

  fortschritt(kindId: string, tage: number): Promise<Fortschritt> {
    return this.call("progress", { kind_id: kindId, tage });
  }

  wochenreport(kindId: string, versatz: number): Promise<Wochenreport> {
    return this.call("weekly_report", { kind_id: kindId, versatz });
  }

  async kalenderPruefen(kindId: string): Promise<boolean> {
    const antwort = await this.call<{ gelesen: boolean }>("calendar/refresh", {
      kind_id: kindId,
    });
    return antwort.gelesen;
  }

  kalenderIgnorieren(kindId: string, uid: string): Promise<void> {
    return this.call("calendar/ignore", { kind_id: kindId, uid });
  }

  kalenderWiederherstellen(kindId: string): Promise<void> {
    return this.call("calendar/restore", { kind_id: kindId });
  }

  async fachAnlegen(
    kindId: string,
    typ: Fachart,
    name: string,
    sprache: string | null,
  ): Promise<string> {
    const antwort = await this.call<{ fach_id: string }>("subjects/create", {
      kind_id: kindId,
      typ,
      name: name || null,
      sprache,
    });
    return antwort.fach_id;
  }

  absenderZuordnen(kindId: string, kennung: string): Promise<void> {
    return this.call("sender/assign", { kind_id: kindId, kennung });
  }

  absenderVerwerfen(kennung: string): Promise<void> {
    return this.call("sender/dismiss", { kennung });
  }

  async aufgaben(fachId: string): Promise<Aufgabe[]> {
    const antwort = await this.call<{ aufgaben: Aufgabe[] }>("tasks/list", {
      fach_id: fachId,
    });
    return antwort.aufgaben;
  }

  aufgabeAnlegen(fachId: string, aufgabe: AufgabeEingabe): Promise<Aufgabe> {
    return this.call("tasks/create", { fach_id: fachId, aufgabe });
  }

  aufgabeAendern(
    fachId: string,
    aufgabeId: string,
    aenderungen: AufgabeEingabe,
  ): Promise<Aufgabe> {
    return this.call("tasks/update", {
      fach_id: fachId,
      aufgabe_id: aufgabeId,
      aenderungen,
    });
  }

  aufgabenLoeschen(
    fachId: string,
    aufgabeIds: string[],
    bestaetigt: boolean,
  ): Promise<LoeschErgebnis> {
    return this.call("tasks/delete", {
      fach_id: fachId,
      aufgabe_ids: aufgabeIds,
      bestaetigt,
    });
  }

  async lektionHinzufuegen(fachId: string, name: string): Promise<string[]> {
    const antwort = await this.call<{ lektionen: string[] }>("lessons/add", {
      fach_id: fachId,
      name,
    });
    return antwort.lektionen;
  }

  async lektionLoeschen(fachId: string, name: string): Promise<string[]> {
    const antwort = await this.call<{ lektionen: string[] }>("lessons/delete", {
      fach_id: fachId,
      name,
    });
    return antwort.lektionen;
  }

  importVorschau(
    fachId: string,
    inhalt: string,
    trennzeichen: string | null,
  ): Promise<ImportVorschau> {
    return this.call("tasks/import_text", {
      fach_id: fachId,
      inhalt,
      trennzeichen,
      vorschau: true,
    });
  }

  importText(
    fachId: string,
    inhalt: string,
    lektion: string | null,
    trennzeichen: string | null,
    geprueft: boolean,
  ): Promise<ImportErgebnis> {
    return this.call("tasks/import_text", {
      fach_id: fachId,
      inhalt,
      lektion,
      trennzeichen,
      geprueft,
    });
  }

  generieren(fachId: string, eingabe: GenerierEingabe): Promise<GenerierErgebnis> {
    return this.call("tasks/generate", { fach_id: fachId, ...eingabe });
  }

  fragenAusSeiten(fachId: string, eingabe: SeitenEingabe): Promise<GenerierErgebnis> {
    return this.call("tasks/generate_from_pages", { fach_id: fachId, ...eingabe });
  }

  fotoAuslesen(fachId: string, seiten: string[]): Promise<FotoVorschau> {
    return this.call("tasks/photo_extract", { fach_id: fachId, seiten });
  }

  fotoUebernehmen(
    fachId: string,
    zeilen: Record<string, unknown>[],
    lektion: string | null,
  ): Promise<{ importiert: number; uebersprungen: number; fehler: number[] }> {
    return this.call("tasks/photo_accept", { fach_id: fachId, zeilen, lektion });
  }

  nachrechnen(fachId: string, aufgabeIds: string[]): Promise<NachrechnenErgebnis> {
    return this.call("tasks/verify", { fach_id: fachId, aufgabe_ids: aufgabeIds });
  }

  rechenwegeErzeugen(
    fachId: string,
    aufgabeIds: string[],
  ): Promise<{ erzeugt: number; vorhanden: number; abweichend: number; fehlgeschlagen: number }> {
    return this.call("tasks/generate_steps", { fach_id: fachId, aufgabe_ids: aufgabeIds });
  }

  /** Upload an image; the server re-encodes it and returns its id. */
  async bildHochladen(datei: File, seite = false): Promise<string> {
    const formular = new FormData();
    formular.append("file", datei);
    // The photo of a page is stored larger so that small print stays legible
    const adresse = `/api/learnbuddy/bilder${seite ? "?zweck=seite" : ""}`;
    const antwort = await this.hass.fetchWithAuth(adresse, {
      method: "POST",
      body: formular,
    });
    const daten = (await antwort.json().catch(() => ({}))) as {
      bild?: string;
      message?: string;
    };
    if (!antwort.ok || !daten.bild) {
      // Same shape as an error of the WebSocket API
      throw { code: String(antwort.status), message: daten.message ?? "bild_ungueltig" };
    }
    return daten.bild;
  }

  /** Return an address of an image that works in an img element for an hour. */
  async bildAdresse(bildId: string): Promise<string> {
    const antwort = await this.hass.callWS<{ path: string }>({
      type: "auth/sign_path",
      path: `/api/learnbuddy/bilder/${bildId}`,
      expires: 3600,
    });
    return antwort.path;
  }

  async vorschlagUebernehmen(fachId: string, aufgabeIds: string[]): Promise<number> {
    const antwort = await this.call<{ uebernommen: number }>("tasks/accept_suggestion", {
      fach_id: fachId,
      aufgabe_ids: aufgabeIds,
    });
    return antwort.uebernommen;
  }

  async alsGeprueftMarkieren(fachId: string, aufgabeIds: string[]): Promise<number> {
    const antwort = await this.call<{ markiert: number }>("tasks/mark_verified", {
      fach_id: fachId,
      aufgabe_ids: aufgabeIds,
    });
    return antwort.markiert;
  }

  export(fachId: string, mitStatistik: boolean): Promise<Record<string, unknown>> {
    return this.call("tasks/export", {
      fach_id: fachId,
      mit_statistik: mitStatistik,
    });
  }

  importJson(
    fachId: string,
    daten: Record<string, unknown>,
    mitStatistik: boolean,
    lektion: string | null,
  ): Promise<JsonImportErgebnis> {
    return this.call("tasks/import_json", {
      fach_id: fachId,
      daten,
      mit_statistik: mitStatistik,
      lektion,
    });
  }

  async arbeitSpeichern(
    arbeitId: string | null,
    arbeit: ArbeitEingabe,
  ): Promise<string> {
    const antwort = await this.call<{ arbeit_id: string }>("exams/save", {
      arbeit_id: arbeitId,
      arbeit,
    });
    return antwort.arbeit_id;
  }

  simulieren(
    arbeitId: string,
    anzahl: number,
    weg: SimulationsWeg,
  ): Promise<SimulationsErgebnis> {
    return this.call("exams/simulate", { arbeit_id: arbeitId, anzahl, weg });
  }

  async simulationAbbrechen(kindId: string): Promise<boolean> {
    const antwort = await this.call<{ abgebrochen: boolean }>("exams/simulate_stop", {
      kind_id: kindId,
    });
    return antwort.abgebrochen;
  }

  arbeitLoeschen(arbeitId: string): Promise<void> {
    return this.call("exams/delete", { arbeit_id: arbeitId });
  }
}
