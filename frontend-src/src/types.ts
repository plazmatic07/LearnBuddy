export interface Hass {
  language: string;
  themes?: { darkMode?: boolean };
  connection?: {
    subscribeEvents(
      callback: (event: unknown) => void,
      eventType: string,
    ): Promise<() => void>;
  };
  callWS<T>(msg: Record<string, unknown>): Promise<T>;
  fetchWithAuth(path: string, init?: RequestInit): Promise<Response>;
}

export interface WsError {
  code: string;
  message: string;
}

export interface Kind {
  id: string;
  name: string;
  // Whether tasks with an image can be sent to the child
  bilder: boolean;
  // Whether a sender ID is set; missing on older servers
  absender?: boolean;
}

export interface Fach {
  id: string;
  kind_id: string;
  name: string;
  typ: "vokabel" | "mathe" | "sach";
  ki: boolean;
  ki_bilder?: boolean;
  ki_status?: KiStatus;
  sprachen: string[];
  lektionen: string[];
  anzahl_aufgaben: number;
}

export interface Arbeit {
  id: string;
  fach_id: string;
  art: "arbeit" | "hue";
  datum: string;
  thema: string;
  lektionen: string[];
  abfragen_pro_tag: number;
  start_tage_vorher: number;
  intensivierung: boolean;
  antwortfrist_minuten: number | null;
  aufgaben_ids: string[];
  simulierbar?: { ausdruck: number; messenger: number };
  simulation_um?: string | null;
  simulation_anzahl?: number;
  simulation_geplant?: boolean;
}

/** What the AI of a subject can do right now. */
export type KiStatus = "keine" | "nicht_verfuegbar" | "ohne_bilder" | "ok";

export interface UnbekannterAbsender {
  kennung: string;
  quelle: "telegram" | "whatsapp" | "event";
  zuletzt: string;
}

export interface Uebersicht {
  panel_version?: string | null;
  // Missing on older servers
  unbekannte_absender?: UnbekannterAbsender[];
  kinder: Kind[];
  faecher: Fach[];
  arbeiten: Arbeit[];
}

export interface Statistik {
  box: number;
  gefragt: number;
  richtig: number;
  falsch: number;
  teilweise?: number;
  zuletzt_gefragt: string | null;
  zuletzt_falsch: string | null;
}

export type Quelle = "upload" | "generiert" | "manuell";

interface AufgabeBasis {
  id: string;
  fach_id: string;
  erstellt: string;
  geaendert: string;
  lektion: string | null;
  quelle: Quelle;
  geprueft: boolean;
  hinweis: string | null;
  seite: number | null;
  statistik: Record<string, Statistik>;
  fehlerquote: number | null;
  arbeiten: string[];
}

export interface Vokabel extends AufgabeBasis {
  typ: "vokabel";
  frage: Record<string, string>;
  alternativen: Record<string, string[]>;
}

export type Verifikation = "rechnerisch" | "ki" | "manuell" | "abweichung" | "keine";

export interface MatheAufgabe extends AufgabeBasis {
  typ: "mathe";
  aufgabe: string;
  loesung: string;
  alternativen: string[];
  rechenweg: string[];
  schwierigkeit: number | null;
  verifikation: Verifikation;
  vorschlag: string | null;
  vorschlag_durch: "lokal" | "ki" | null;
  bild: string | null;
}

export type SachForm = "kurz" | "auswahl";

export interface SachAufgabe extends AufgabeBasis {
  typ: "sach";
  frage: string;
  antwort: string;
  form: SachForm;
  kernpunkte: string[];
  falsche_optionen: string[];
  stelle: string | null;
  quelle_bild: string | null;
}

export type Aufgabe = Vokabel | MatheAufgabe | SachAufgabe;

export interface AufgabeEingabe {
  frage?: Record<string, string> | string;
  antwort?: string;
  form?: SachForm;
  kernpunkte?: string[];
  falsche_optionen?: string[];
  stelle?: string | null;
  alternativen?: Record<string, string[]> | string[];
  aufgabe?: string;
  loesung?: string;
  rechenweg?: string[];
  schwierigkeit?: number | null;
  bild?: string | null;
  hinweis?: string | null;
  seite?: number | null;
  lektion?: string | null;
  geprueft?: boolean;
}

export interface ArbeitEingabe {
  fach_id?: string;
  datum: string;
  thema: string;
  art: "arbeit" | "hue";
  lektionen: string[];
  aufgaben_ids: string[];
  abfragen_pro_tag: number;
  start_tage_vorher: number;
  intensivierung: boolean;
  antwortfrist_minuten: number | null;
  simulation_um: string | null;
  simulation_anzahl: number;
  kalender_uid?: string | null;
}

/** An exam date of the calendar that is not entered yet. */
export interface Vorschlag {
  uid: string;
  datum: string;
  art: "arbeit" | "hue";
  text: string;
  // A guess of the server, only if exactly one subject fits
  fach_id: string | null;
  // Exams entered by hand for the same day
  gleicher_tag: string[];
}

export type Fachart = "fremdsprache" | "mathe" | "sach";

export interface VorschauZeile {
  frage?: Record<string, string>;
  aufgabe?: string;
  loesung?: string;
  hinweis: string | null;
  vorhanden: boolean;
}

export interface ImportVorschau {
  zeilen: VorschauZeile[];
  fehlerzeilen: number[];
}

export interface ImportErgebnis {
  importiert: number;
  uebersprungen: number;
  fehlerzeilen: number[];
}

export interface JsonImportErgebnis {
  importiert: number;
  uebersprungen: number;
  fehler: number[];
}

export interface GenerierErgebnis {
  erzeugt: number;
  verworfen: number;
  uebersprungen: number;
  aufgabe_ids: string[];
}

export interface NachrechnenErgebnis {
  bestaetigt: number;
  abweichend: {
    id: string;
    aufgabe: string;
    loesung: string;
    berechnet: string | null;
    durch: "lokal" | "ki";
  }[];
  nicht_pruefbar: number;
}

/** A line of the preview of tasks read from photos. */
export interface FotoZeile {
  frage?: Record<string, string>;
  alternativen?: Record<string, string[]>;
  hinweis?: string | null;
  aufgabe?: string;
  loesung?: string;
  seite: number | null;
  braucht_bild?: boolean;
  verifikation?: Verifikation;
  vorschlag?: string | null;
  vorschlag_durch?: "lokal" | "ki" | null;
  vorhanden: boolean;
}

export interface FotoVorschau {
  typ: "vokabel" | "mathe";
  zeilen: FotoZeile[];
}

export type SimulationsWeg = "ausdruck" | "messenger";

export interface SimulationsErgebnis {
  weg: SimulationsWeg;
  anzahl: number;
  bilder: string[];
}

export interface SeitenEingabe {
  seiten: string[];
  anzahl: number;
  form: SachForm | "gemischt";
  lektion: string | null;
  schwerpunkt: string | null;
}

export interface GenerierEingabe {
  anzahl: number;
  lektion: string | null;
  schwierigkeit: number | null;
  beschreibung: string | null;
  beispiel_ids: string[];
}

export interface LoeschErgebnis {
  geloescht: number;
  zugeordnet: Record<string, string[]>;
}

export interface Kennzahlen {
  gefragt: number;
  richtig: number;
  falsch: number;
  trefferquote: number | null;
  boxen: number[];
  sicher: number | null;
}

export interface DashboardFach extends Kennzahlen {
  id: string;
  name: string;
  typ: "vokabel" | "mathe" | "sach";
  ki: boolean;
  sprachen: string[];
  aufgaben: number;
  ungeprueft: number;
  lektionen: number;
  lektionsliste: { name: string; aufgaben: number }[];
  ohne_lektion: number;
}

/** What a manual request is limited to (only with a subject). */
export interface AbfrageAuswahl {
  lektionen?: string[];
  seite_von?: number | null;
  seite_bis?: number | null;
  fehlerquote_ab?: number | null;
}

export interface DashboardArbeit {
  id: string;
  fach_id: string;
  fach: string;
  art: "arbeit" | "hue";
  thema: string;
  datum: string;
  tage_bis: number;
  aufgaben: number;
  abfragen_heute: number;
  boxen: number[];
  sicher: number | null;
}

export interface Dashboard {
  kind_id: string;
  zustand: {
    aktiv: boolean;
    pausiert: boolean;
    pausiert_bis: string | null;
    offene_frage: {
      fach_id: string;
      fach: string;
      gestellt_um: string;
      timeout_um: string;
    } | null;
    simulation?: { arbeit_id: string; nummer: number; anzahl: number } | null;
    // Series of questions that goes on after the open one
    abfrage?: (AbfrageAuswahl & { weitere: number }) | null;
    letzte_frage_um: string | null;
    naechste_abfrage: string | null;
  };
  statistik: {
    aufgaben: number;
    gefragt: number;
    richtig: number;
    falsch: number;
    teilweise?: number;
    unbeantwortet: number;
    trefferquote: number | null;
    boxen: number[];
  };
  faecher: DashboardFach[];
  arbeiten: DashboardArbeit[];
  // Optional parts of the overview; missing on older servers
  verlauf?: boolean;
  wochenreport?: boolean;
  // Missing on older servers; null if the child uses no exam calendar
  kalender?: { geprueft_um: string | null; fehler: boolean; ignoriert: number } | null;
  vorschlaege?: Vorschlag[];
  schwierig: {
    fach_id: string;
    fach: string;
    frage: Record<string, string> | null;
    aufgabe: string | null;
    fehlerquote: number;
    falsch: number;
  }[];
}

/** Counters of one day or of a period. */
export interface Tageszahlen {
  gefragt: number;
  richtig: number;
  teilweise: number;
  falsch: number;
  unbeantwortet: number;
  // Share of right answers; per day smoothed over the last days
  trefferquote: number | null;
}

export interface SchwacheLektion {
  fach: string;
  lektion: string;
  richtig: number;
  falsch: number;
  fehlerquote: number;
}

export interface FehlerAufgabe {
  fach: string;
  aufgabe: string;
  loesung: string;
  falsch: number;
}

export interface SimulationsEintrag {
  tag: string;
  fach: string | null;
  thema: string | null;
  punkte: number;
  moeglich: number;
  prozent: number | null;
  vollstaendig: boolean;
}

export interface Fortschritt {
  // First day anything was recorded, null if nothing yet
  seit: string | null;
  von: string;
  bis: string;
  reihe: (Tageszahlen & { tag: string })[];
  faecher: { id: string; name: string; lernstand: (number | null)[] }[];
  lektionen: SchwacheLektion[];
  aufgaben: FehlerAufgabe[];
  simulationen: SimulationsEintrag[];
}

export interface Wochenreport {
  von: string;
  bis: string;
  laufend: boolean;
  seit: string | null;
  kennzahlen: Tageszahlen & { tage_aktiv: number };
  vorwoche: Tageszahlen & { tage_aktiv: number };
  faecher: { name: string; lernstand: number | null; vorher: number | null }[];
  lektionen: SchwacheLektion[];
  aufgaben: FehlerAufgabe[];
  arbeiten: {
    fach: string;
    thema: string;
    art: "arbeit" | "hue";
    datum: string;
    tage_bis: number;
    sicher: number | null;
  }[];
  vorschlaege: { datum: string; art: "arbeit" | "hue"; text: string }[];
  simulationen: SimulationsEintrag[];
}
