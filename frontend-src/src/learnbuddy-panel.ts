import { LitElement, html, nothing, type PropertyValues, type TemplateResult } from "lit";
import { property, state } from "lit/decorators.js";

import { Api } from "./api";
import "./uebersicht";
import { fehlertext, sprachname, uebersetzer, type Uebersetzer } from "./i18n";
import { styles } from "./styles";
import type {
  Arbeit,
  ArbeitEingabe,
  Aufgabe,
  AufgabeEingabe,
  Fach,
  FotoZeile,
  Hass,
  ImportVorschau,
  KiStatus,
  MatheAufgabe,
  NachrechnenErgebnis,
  Quelle,
  SachAufgabe,
  SachForm,
  SimulationsWeg,
  Uebersicht,
} from "./types";

type Tab = "uebersicht" | "aufgaben" | "arbeiten";
type Dialog =
  | "import"
  | "export"
  | "importJson"
  | "arbeit"
  | "lektion"
  | "generieren"
  | "nachrechnen"
  | "aufgabenart"
  | "bildaufgabe"
  | "bild"
  | "seiten"
  | "foto"
  | "simulation"
  | null;

interface Filter {
  suche: string;
  lektion: string;
  quelle: "" | Quelle;
  geprueft: "" | "ja" | "nein";
  fehlerquote: string;
  von: string;
  bis: string;
  seiteVon: string;
  seiteBis: string;
}

interface AufgabeEntwurf {
  id: string | null;
  a: string;
  b: string;
  altA: string;
  altB: string;
  hinweis: string;
  seite: string;
  lektion: string;
  geprueft: boolean;
  // Math only
  rechenweg: string;
  schwierigkeit: string;
  // Knowledge subjects only; lists with one entry per line
  form: SachForm;
  kernpunkte: string;
  falsche: string;
}

interface SeitenEntwurf {
  dateien: File[];
  vorschauen: string[];
  lektion: string;
  anzahl: number;
  form: SachForm | "gemischt";
  schwerpunkt: string;
}

/** An editable line of the preview of a photo import. */
interface FotoEntwurfZeile {
  an: boolean;
  // Vocabulary: both words; math: task and result
  a: string;
  b: string;
  hinweis: string;
  seite: string;
  geaendert: boolean;
  roh: FotoZeile;
}

interface FotoEntwurf {
  dateien: File[];
  vorschauen: string[];
  lektion: string;
  zeilen: FotoEntwurfZeile[] | null;
}

interface SimulationsEntwurf {
  arbeit: Arbeit;
  anzahl: number;
  weg: SimulationsWeg;
  // Addresses of the pages of the sheet once it was made
  seiten: string[] | null;
}

const MAX_SIM_AUFGABEN = 30;
const MAX_SEITEN = 4;

/** Turn a stored time into the value of a datetime-local field. */
function lokaleZeit(iso: string | null): string {
  if (!iso) {
    return "";
  }
  const zeit = new Date(iso);
  if (Number.isNaN(zeit.getTime())) {
    return "";
  }
  const zwei = (zahl: number): string => String(zahl).padStart(2, "0");
  return (
    `${zeit.getFullYear()}-${zwei(zeit.getMonth() + 1)}-${zwei(zeit.getDate())}` +
    `T${zwei(zeit.getHours())}:${zwei(zeit.getMinutes())}`
  );
}

/** Split a text field into its non-empty lines. */
function zeilen(text: string): string[] {
  return text
    .split("\n")
    .map((zeile) => zeile.trim())
    .filter((zeile) => zeile.length > 0);
}

interface Teilaufgabe {
  aufgabe: string;
  loesung: string;
  alternativen: string;
}

interface BildEntwurf {
  datei: File | null;
  vorschau: string;
  einleitung: string;
  lektion: string;
  seite: string;
  teile: Teilaufgabe[];
}

const LEERER_TEIL: Teilaufgabe = { aufgabe: "", loesung: "", alternativen: "" };

interface GenerierEntwurf {
  lektion: string;
  anzahl: number;
  schwierigkeit: string;
  beschreibung: string;
}

interface ArbeitEntwurf {
  id: string | null;
  art: "arbeit" | "hue";
  datum: string;
  thema: string;
  abfragen: number;
  start: number;
  intensivierung: boolean;
  frist: number | null;
  // Planned simulation: local date and time as in a datetime-local field
  simUm: string;
  simAnzahl: number;
  modus: "alle" | "auswahl";
  lektionen: Set<string>;
  ids: Set<string>;
  seit: string;
  seiteVon: string;
  seiteBis: string;
}

const OHNE_LEKTION = "\u0000ohne";
const LEERER_FILTER: Filter = {
  suche: "",
  lektion: "",
  quelle: "",
  geprueft: "",
  fehlerquote: "",
  von: "",
  bis: "",
  seiteVon: "",
  seiteBis: "",
};

/** Whether a page lies in a range; an empty bound is open. */
function inSeiten(seite: number | null, von: string, bis: string): boolean {
  const untere = von.trim() === "" ? null : Number(von);
  const obere = bis.trim() === "" ? null : Number(bis);
  if (untere === null && obere === null) {
    return true;
  }
  if (seite === null) {
    return false;
  }
  return (untere === null || seite >= untere) && (obere === null || seite <= obere);
}

/** Short text that identifies a task in lists. */
function kurztext(aufgabe: Aufgabe, a: string, b: string): string {
  if (aufgabe.typ === "mathe") {
    return `${aufgabe.aufgabe} = ${aufgabe.loesung}`;
  }
  if (aufgabe.typ === "sach") {
    return `${aufgabe.frage} – ${aufgabe.antwort}`;
  }
  return `${aufgabe.frage[a] ?? ""} – ${aufgabe.frage[b] ?? ""}`;
}

function wert(ereignis: Event): string {
  return (ereignis.target as HTMLInputElement | HTMLSelectElement).value;
}

function angehakt(ereignis: Event): boolean {
  return (ereignis.target as HTMLInputElement).checked;
}

function teile(text: string): string[] {
  return text
    .split("|")
    .map((teil) => teil.trim())
    .filter((teil) => teil.length > 0);
}

/** Version of this bundle, taken from the address it was loaded from. */
const GELADENE_VERSION = ((): string | null => {
  try {
    return new URL(import.meta.url).searchParams.get("v");
  } catch {
    return null;
  }
})();

function pause(ms: number): Promise<void> {
  return new Promise((fertig) => setTimeout(fertig, ms));
}

export class LearnBuddyPanel extends LitElement {
  static styles = styles;

  @property({ attribute: false }) hass?: Hass;

  @property({ type: Boolean, reflect: true }) narrow = false;

  @state() private _uebersicht?: Uebersicht;

  @state() private _kindId = "";

  @state() private _fachId = "";

  @state() private _aufgaben: Aufgabe[] = [];

  @state() private _tab: Tab = "uebersicht";

  @state() private _filter: Filter = { ...LEERER_FILTER };

  @state() private _auswahl = new Set<string>();

  @state() private _entwurf: AufgabeEntwurf | null = null;

  @state() private _dialog: Dialog = null;

  @state() private _generieren: GenerierEntwurf | null = null;

  @state() private _bildEntwurf: BildEntwurf | null = null;

  // Signed addresses of the task images, by image id
  @state() private _bildAdressen: Record<string, string> = {};

  // Image shown large
  @state() private _grossbild = "";

  /** Text shown below the large image, e.g. the passage a question is based on. */
  @state() private _bildText = "";

  @state() private _seiten: SeitenEntwurf | null = null;

  @state() private _foto: FotoEntwurf | null = null;

  @state() private _sim: SimulationsEntwurf | null = null;

  /** The server serves a newer panel than the one that is running here. */
  @state() private _veraltet = false;

  @state() private _nachgerechnet: NachrechnenErgebnis | null = null;

  // Only these tasks are listed (after recalculating)
  @state() private _nurIds: Set<string> | null = null;

  @state() private _meldung: { text: string; fehler: boolean } | null = null;

  @state() private _laedt = true;

  @state() private _beschaeftigt = false;

  @state() private _importText = "";

  @state() private _importLektion = "";

  @state() private _importTrenner = "";

  @state() private _importGeprueft = true;

  @state() private _vorschau: ImportVorschau | null = null;

  @state() private _mitStatistik = false;

  @state() private _jsonDaten: Record<string, unknown> | null = null;

  @state() private _arbeit: ArbeitEntwurf | null = null;

  @state() private _dialogFehler = "";

  @state() private _lektionName = "";

  @state() private _jsonLektion = "";

  private _gestartet = false;

  private get _t(): Uebersetzer {
    return uebersetzer(this.hass?.language ?? "en");
  }

  private get _api(): Api {
    return new Api(this.hass as Hass);
  }

  private get _fach(): Fach | undefined {
    return this._uebersicht?.faecher.find((fach) => fach.id === this._fachId);
  }

  private get _faecherDesKindes(): Fach[] {
    return (this._uebersicht?.faecher ?? []).filter(
      (fach) => fach.kind_id === this._kindId,
    );
  }

  private get _arbeitenDesFachs(): Arbeit[] {
    return (this._uebersicht?.arbeiten ?? [])
      .filter((arbeit) => arbeit.fach_id === this._fachId)
      .sort((a, b) => a.datum.localeCompare(b.datum));
  }

  connectedCallback(): void {
    super.connectedCallback();
    window.addEventListener("keydown", this._taste);
  }

  disconnectedCallback(): void {
    super.disconnectedCallback();
    window.removeEventListener("keydown", this._taste);
  }

  protected updated(geaendert: PropertyValues): void {
    if (geaendert.has("hass") && this.hass && !this._gestartet) {
      this._gestartet = true;
      void this._ladeUebersicht();
    }
  }

  private _taste = (ereignis: KeyboardEvent): void => {
    if (ereignis.key !== "Escape") {
      return;
    }
    if (this._dialog) {
      this._schliesseDialog();
    } else if (this._entwurf) {
      this._entwurf = null;
    }
  };

  // ---------------------------------------------------------------- data

  private async _ladeUebersicht(wiederholungen = 0): Promise<void> {
    let versuch = 0;
    for (;;) {
      try {
        this._uebersicht = await this._api.uebersicht();
        break;
      } catch (fehler) {
        const code = (fehler as { code?: string }).code;
        // The integration may be reloading for a moment, e.g. after a config change
        if (code === "not_loaded" && versuch < wiederholungen) {
          versuch += 1;
          await pause(500);
          continue;
        }
        this._zeigeFehler(fehler);
        this._laedt = false;
        return;
      }
    }
    const uebersicht = this._uebersicht;
    this._veraltet = Boolean(
      GELADENE_VERSION &&
        uebersicht.panel_version &&
        uebersicht.panel_version !== GELADENE_VERSION,
    );
    if (!uebersicht.kinder.some((kind) => kind.id === this._kindId)) {
      this._kindId = uebersicht.kinder[0]?.id ?? "";
    }
    if (!this._faecherDesKindes.some((fach) => fach.id === this._fachId)) {
      this._fachId = this._faecherDesKindes[0]?.id ?? "";
    }
    await this._ladeAufgaben();
    this._laedt = false;
  }

  private async _ladeAufgaben(): Promise<void> {
    if (!this._fachId) {
      this._aufgaben = [];
      return;
    }
    try {
      this._aufgaben = await this._api.aufgaben(this._fachId);
    } catch (fehler) {
      this._aufgaben = [];
      this._zeigeFehler(fehler);
    }
    const vorhanden = new Set(this._aufgaben.map((aufgabe) => aufgabe.id));
    this._auswahl = new Set([...this._auswahl].filter((id) => vorhanden.has(id)));
    void this._ladeBildAdressen();
  }

  /** Get addresses for the images of the tasks that an img element can load. */
  private async _ladeBildAdressen(): Promise<void> {
    const ids = new Set<string>();
    for (const aufgabe of this._aufgaben) {
      const bild =
        aufgabe.typ === "mathe"
          ? aufgabe.bild
          : aufgabe.typ === "sach"
            ? aufgabe.quelle_bild
            : null;
      if (bild && !(bild in this._bildAdressen)) {
        ids.add(bild);
      }
    }
    for (const id of ids) {
      try {
        const adresse = await this._api.bildAdresse(id);
        this._bildAdressen = { ...this._bildAdressen, [id]: adresse };
      } catch {
        // The row simply shows no preview
      }
    }
  }

  private async _neuLaden(wiederholungen = 0): Promise<void> {
    await this._ladeUebersicht(wiederholungen);
  }

  private _zeigeFehler(fehler: unknown): void {
    this._meldung = { text: fehlertext(this._t, fehler), fehler: true };
  }

  private _zeigeErfolg(text: string): void {
    this._meldung = { text, fehler: false };
  }

  private _gefiltert(): Aufgabe[] {
    const filter = this._filter;
    const suche = filter.suche.trim().toLowerCase();
    const schwelle = filter.fehlerquote === "" ? null : Number(filter.fehlerquote);
    // The restriction only applies to the subject it was made for
    const nur =
      this._nurIds && this._aufgaben.some((aufgabe) => this._nurIds?.has(aufgabe.id))
        ? this._nurIds
        : null;
    return this._aufgaben.filter((aufgabe) => {
      if (nur && !nur.has(aufgabe.id)) {
        return false;
      }
      if (suche) {
        const text = [
          ...(aufgabe.typ === "mathe"
            ? [aufgabe.aufgabe, aufgabe.loesung, ...aufgabe.alternativen]
            : aufgabe.typ === "sach"
              ? [
                  aufgabe.frage,
                  aufgabe.antwort,
                  ...aufgabe.kernpunkte,
                  ...aufgabe.falsche_optionen,
                ]
              : [
                ...Object.values(aufgabe.frage),
                ...Object.values(aufgabe.alternativen).flat(),
              ]),
          aufgabe.hinweis ?? "",
        ]
          .join(" ")
          .toLowerCase();
        if (!text.includes(suche)) {
          return false;
        }
      }
      if (filter.lektion === OHNE_LEKTION && aufgabe.lektion) {
        return false;
      }
      if (
        filter.lektion &&
        filter.lektion !== OHNE_LEKTION &&
        aufgabe.lektion !== filter.lektion
      ) {
        return false;
      }
      if (filter.quelle && aufgabe.quelle !== filter.quelle) {
        return false;
      }
      if (filter.geprueft && aufgabe.geprueft !== (filter.geprueft === "ja")) {
        return false;
      }
      if (
        schwelle !== null &&
        !Number.isNaN(schwelle) &&
        (aufgabe.fehlerquote === null || aufgabe.fehlerquote < schwelle)
      ) {
        return false;
      }
      const tag = aufgabe.erstellt.slice(0, 10);
      if (filter.von && tag < filter.von) {
        return false;
      }
      if (filter.bis && tag > filter.bis) {
        return false;
      }
      if (!inSeiten(aufgabe.seite, filter.seiteVon, filter.seiteBis)) {
        return false;
      }
      return true;
    });
  }

  // ------------------------------------------------------------- actions

  private async _waehleKind(kindId: string): Promise<void> {
    if (kindId === this._kindId) {
      return;
    }
    this._kindId = kindId;
    this._fachId = this._faecherDesKindes[0]?.id ?? "";
    this._zuruecksetzen();
    await this._ladeAufgaben();
  }

  private async _waehleFach(fachId: string): Promise<void> {
    this._fachId = fachId;
    this._zuruecksetzen();
    await this._ladeAufgaben();
  }

  private _zuruecksetzen(): void {
    this._auswahl = new Set();
    this._entwurf = null;
    this._filter = { ...LEERER_FILTER };
  }

  private _setzeFilter(feld: keyof Filter, neu: string): void {
    this._filter = { ...this._filter, [feld]: neu };
    this._nurIds = null;
  }

  private _umschalten(id: string, an: boolean): void {
    const auswahl = new Set(this._auswahl);
    if (an) {
      auswahl.add(id);
    } else {
      auswahl.delete(id);
    }
    this._auswahl = auswahl;
  }

  private _alleUmschalten(sichtbar: Aufgabe[], an: boolean): void {
    const auswahl = new Set(this._auswahl);
    for (const aufgabe of sichtbar) {
      if (an) {
        auswahl.add(aufgabe.id);
      } else {
        auswahl.delete(aufgabe.id);
      }
    }
    this._auswahl = auswahl;
  }

  private _bearbeite(aufgabe: Aufgabe | null): void {
    const [a = "", b = ""] = this._fach?.sprachen ?? [];
    const mathe = aufgabe?.typ === "mathe" ? aufgabe : null;
    const vokabel = aufgabe?.typ === "vokabel" ? aufgabe : null;
    const sach = aufgabe?.typ === "sach" ? aufgabe : null;
    this._entwurf = {
      id: aufgabe?.id ?? null,
      // Math: a is the task and b the result; knowledge: question and answer
      a: mathe ? mathe.aufgabe : sach ? sach.frage : (vokabel?.frage[a] ?? ""),
      b: mathe ? mathe.loesung : sach ? sach.antwort : (vokabel?.frage[b] ?? ""),
      form: sach?.form ?? "kurz",
      kernpunkte: (sach?.kernpunkte ?? []).join("\n"),
      falsche: (sach?.falsche_optionen ?? []).join("\n"),
      altA: (vokabel?.alternativen[a] ?? []).join(" | "),
      altB: (mathe ? mathe.alternativen : (vokabel?.alternativen[b] ?? [])).join(" | "),
      rechenweg: (mathe?.rechenweg ?? []).join("\n"),
      schwierigkeit: mathe?.schwierigkeit?.toString() ?? "",
      hinweis: aufgabe?.hinweis ?? "",
      seite: aufgabe?.seite?.toString() ?? "",
      lektion: aufgabe?.lektion ?? (this._filter.lektion === OHNE_LEKTION ? "" : this._filter.lektion),
      geprueft: aufgabe?.geprueft ?? true,
    };
  }

  private _setzeEntwurf<K extends keyof AufgabeEntwurf>(
    feld: K,
    neu: AufgabeEntwurf[K],
  ): void {
    if (this._entwurf) {
      this._entwurf = { ...this._entwurf, [feld]: neu };
    }
  }

  private async _speichereAufgabe(): Promise<void> {
    const entwurf = this._entwurf;
    const fach = this._fach;
    if (!entwurf || !fach) {
      return;
    }
    const [a = "", b = ""] = fach.sprachen;
    const eingabe: AufgabeEingabe = {
      ...(fach.typ === "mathe"
        ? {
            aufgabe: entwurf.a,
            loesung: entwurf.b,
            alternativen: teile(entwurf.altB),
            rechenweg: entwurf.rechenweg
              .split("\n")
              .map((schritt) => schritt.trim())
              .filter((schritt) => schritt.length > 0),
            schwierigkeit:
              entwurf.schwierigkeit === "" ? null : Number(entwurf.schwierigkeit),
          }
        : fach.typ === "sach"
          ? {
              frage: entwurf.a,
              antwort: entwurf.b,
              form: entwurf.form,
              kernpunkte: entwurf.form === "kurz" ? zeilen(entwurf.kernpunkte) : [],
              falsche_optionen: entwurf.form === "auswahl" ? zeilen(entwurf.falsche) : [],
            }
          : {
              frage: { [a]: entwurf.a, [b]: entwurf.b },
              alternativen: { [a]: teile(entwurf.altA), [b]: teile(entwurf.altB) },
            }),
      hinweis: entwurf.hinweis || null,
      seite: entwurf.seite.trim() === "" ? null : Number(entwurf.seite),
      lektion: entwurf.lektion || null,
      geprueft: entwurf.geprueft,
    };
    this._beschaeftigt = true;
    try {
      if (entwurf.id) {
        await this._api.aufgabeAendern(fach.id, entwurf.id, eingabe);
      } else {
        await this._api.aufgabeAnlegen(fach.id, eingabe);
      }
      this._entwurf = null;
      this._zeigeErfolg(this._t("gespeichert"));
      await this._neuLaden();
    } catch (fehler) {
      this._zeigeFehler(fehler);
    } finally {
      this._beschaeftigt = false;
    }
  }

  private async _setzeGeprueft(aufgabe: Aufgabe, geprueft: boolean): Promise<void> {
    try {
      await this._api.aufgabeAendern(aufgabe.fach_id, aufgabe.id, { geprueft });
      await this._ladeAufgaben();
    } catch (fehler) {
      this._zeigeFehler(fehler);
    }
  }

  /** Approve all selected tasks that still wait for it. */
  private async _freigeben(): Promise<void> {
    const offen = this._aufgaben.filter(
      (aufgabe) => this._auswahl.has(aufgabe.id) && !aufgabe.geprueft,
    );
    if (!offen.length) {
      return;
    }
    this._beschaeftigt = true;
    try {
      for (const aufgabe of offen) {
        await this._api.aufgabeAendern(aufgabe.fach_id, aufgabe.id, { geprueft: true });
      }
      this._auswahl = new Set();
      this._zeigeErfolg(this._t("freigegeben", { n: offen.length }));
    } catch (fehler) {
      this._zeigeFehler(fehler);
    } finally {
      this._beschaeftigt = false;
      await this._neuLaden();
    }
  }

  /** Check the stored solutions of the selected math tasks. */
  private async _nachrechnen(): Promise<void> {
    const ids = [...this._auswahl];
    if (!ids.length || !this._fachId) {
      return;
    }
    this._beschaeftigt = true;
    this._meldung = { text: this._t("nachrechnen_laeuft"), fehler: false };
    try {
      const ergebnis = await this._api.nachrechnen(this._fachId, ids);
      await this._ladeAufgaben();
      if (ergebnis.abweichend.length) {
        this._meldung = null;
        this._nachgerechnet = ergebnis;
        this._dialogFehler = "";
        this._dialog = "nachrechnen";
      } else {
        this._zeigeErfolg(
          this._t("nachgerechnet", {
            bestaetigt: ergebnis.bestaetigt,
            abweichend: 0,
            offen: ergebnis.nicht_pruefbar,
          }),
        );
      }
    } catch (fehler) {
      this._zeigeFehler(fehler);
    } finally {
      this._beschaeftigt = false;
    }
  }

  private _neueAufgabe(): void {
    if (this._fach?.typ === "mathe") {
      this._dialogFehler = "";
      this._dialog = "aufgabenart";
    } else {
      this._bearbeite(null);
    }
  }

  private _oeffneBildaufgabe(): void {
    const lektion = this._filter.lektion === OHNE_LEKTION ? "" : this._filter.lektion;
    this._bildEntwurf = {
      datei: null,
      vorschau: "",
      einleitung: "",
      lektion,
      seite: "",
      teile: [{ ...LEERER_TEIL }],
    };
    this._dialogFehler = "";
    this._dialog = "bildaufgabe";
  }

  private _setzeBild<K extends keyof BildEntwurf>(feld: K, neu: BildEntwurf[K]): void {
    if (this._bildEntwurf) {
      this._bildEntwurf = { ...this._bildEntwurf, [feld]: neu };
    }
  }

  private _bildGewaehlt(ereignis: Event): void {
    const datei = (ereignis.target as HTMLInputElement).files?.[0] ?? null;
    const entwurf = this._bildEntwurf;
    if (!entwurf) {
      return;
    }
    if (entwurf.vorschau) {
      URL.revokeObjectURL(entwurf.vorschau);
    }
    this._bildEntwurf = {
      ...entwurf,
      datei,
      vorschau: datei ? URL.createObjectURL(datei) : "",
    };
  }

  private _setzeTeil(index: number, feld: keyof Teilaufgabe, neu: string): void {
    const entwurf = this._bildEntwurf;
    if (!entwurf) {
      return;
    }
    const teile = entwurf.teile.map((teil, i) =>
      i === index ? { ...teil, [feld]: neu } : teil,
    );
    this._bildEntwurf = { ...entwurf, teile };
  }

  /** Upload the image and create one task per part. */
  private async _speichereBildaufgabe(): Promise<void> {
    const entwurf = this._bildEntwurf;
    const fach = this._fach;
    if (!entwurf || !fach) {
      return;
    }
    const zeilen = entwurf.teile.filter(
      (teil) => teil.aufgabe.trim() !== "" && teil.loesung.trim() !== "",
    );
    if (!entwurf.datei) {
      this._dialogFehler = this._t("bild_fehlt");
      return;
    }
    if (!zeilen.length) {
      this._dialogFehler = this._t("teil_fehlt");
      return;
    }
    this._beschaeftigt = true;
    this._dialogFehler = "";
    let angelegt = 0;
    try {
      const bild = await this._api.bildHochladen(entwurf.datei);
      const einleitung = entwurf.einleitung.trim();
      for (const teil of zeilen) {
        await this._api.aufgabeAnlegen(fach.id, {
          aufgabe: einleitung ? `${einleitung} ${teil.aufgabe.trim()}` : teil.aufgabe.trim(),
          loesung: teil.loesung,
          alternativen: teile(teil.alternativen),
          bild,
          lektion: entwurf.lektion || null,
          seite: entwurf.seite.trim() === "" ? null : Number(entwurf.seite),
        });
        angelegt += 1;
      }
      this._schliesseDialog();
      this._zeigeErfolg(this._t("bildaufgaben_gespeichert", { n: angelegt }));
    } catch (fehler) {
      this._dialogFehler = fehlertext(this._t, fehler);
    } finally {
      this._beschaeftigt = false;
      if (angelegt) {
        await this._neuLaden();
      }
    }
  }

  /** Let the AI write the solution steps the selected math tasks lack. */
  private async _erzeugeRechenwege(): Promise<void> {
    const ids = [...this._auswahl];
    if (!ids.length || !this._fachId) {
      return;
    }
    this._beschaeftigt = true;
    this._meldung = { text: this._t("rechenweg_erzeugen_laeuft"), fehler: false };
    try {
      const ergebnis = await this._api.rechenwegeErzeugen(this._fachId, ids);
      await this._ladeAufgaben();
      this._zeigeErfolg(this._t("rechenwege_erzeugt", ergebnis));
    } catch (fehler) {
      this._zeigeFehler(fehler);
    } finally {
      this._beschaeftigt = false;
    }
  }

  /** Mark the solutions of the selected math tasks as checked by the parent. */
  private async _markiereGeprueft(): Promise<void> {
    const ids = [...this._auswahl];
    if (!ids.length || !this._fachId) {
      return;
    }
    this._beschaeftigt = true;
    try {
      const anzahl = await this._api.alsGeprueftMarkieren(this._fachId, ids);
      await this._ladeAufgaben();
      this._zeigeErfolg(this._t("selbst_nachgerechnet_fertig", { n: anzahl }));
    } catch (fehler) {
      this._zeigeFehler(fehler);
    } finally {
      this._beschaeftigt = false;
    }
  }

  /** Replace the stored solutions by the results found when recalculating. */
  private async _uebernimmVorschlag(ids: string[]): Promise<void> {
    if (!ids.length || !this._fachId) {
      return;
    }
    this._beschaeftigt = true;
    try {
      const anzahl = await this._api.vorschlagUebernehmen(this._fachId, ids);
      const erledigt = new Set(ids);
      if (this._nachgerechnet) {
        const rest = this._nachgerechnet.abweichend.filter(
          (eintrag) => !erledigt.has(eintrag.id),
        );
        this._nachgerechnet = { ...this._nachgerechnet, abweichend: rest };
        if (!rest.length && this._dialog === "nachrechnen") {
          this._schliesseDialog();
        }
      }
      this._zeigeErfolg(this._t("uebernommen", { n: anzahl }));
      await this._ladeAufgaben();
    } catch (fehler) {
      if (this._dialog === "nachrechnen") {
        this._dialogFehler = fehlertext(this._t, fehler);
      } else {
        this._zeigeFehler(fehler);
      }
    } finally {
      this._beschaeftigt = false;
    }
  }

  private _uebernimmAlle(): void {
    const eintraege = this._nachgerechnet?.abweichend ?? [];
    const frage = this._t("alle_uebernehmen_frage", {
      n: eintraege.length,
      ki: eintraege.filter((eintrag) => eintrag.durch === "ki").length,
    });
    if (window.confirm(frage)) {
      void this._uebernimmVorschlag(eintraege.map((eintrag) => eintrag.id));
    }
  }

  private _oeffneGenerieren(): void {
    const lektion = this._filter.lektion === OHNE_LEKTION ? "" : this._filter.lektion;
    this._generieren = { lektion, anzahl: 10, schwierigkeit: "", beschreibung: "" };
    this._dialogFehler = "";
    this._dialog = "generieren";
  }

  private async _generiere(): Promise<void> {
    const entwurf = this._generieren;
    if (!entwurf || !this._fachId) {
      return;
    }
    this._beschaeftigt = true;
    this._dialogFehler = "";
    try {
      const ergebnis = await this._api.generieren(this._fachId, {
        anzahl: entwurf.anzahl,
        lektion: entwurf.lektion || null,
        schwierigkeit: entwurf.schwierigkeit === "" ? null : Number(entwurf.schwierigkeit),
        beschreibung: entwurf.beschreibung.trim() || null,
        beispiel_ids: [...this._auswahl],
      });
      this._schliesseDialog();
      this._auswahl = new Set();
      if (ergebnis.erzeugt) {
        // Show what waits for approval
        this._filter = { ...LEERER_FILTER, geprueft: "nein" };
      }
      this._zeigeErfolg(
        this._t("generiert", {
          erzeugt: ergebnis.erzeugt,
          verworfen: ergebnis.verworfen,
          doppelt: ergebnis.uebersprungen,
        }),
      );
      await this._neuLaden();
    } catch (fehler) {
      this._dialogFehler = fehlertext(this._t, fehler);
    } finally {
      this._beschaeftigt = false;
    }
  }

  private async _loesche(ids: string[]): Promise<void> {
    if (!ids.length || !this._fachId) {
      return;
    }
    if (!window.confirm(this._t("loeschen_frage", { n: ids.length }))) {
      return;
    }
    this._beschaeftigt = true;
    try {
      let ergebnis = await this._api.aufgabenLoeschen(this._fachId, ids, false);
      const betroffen = Object.keys(ergebnis.zugeordnet);
      if (betroffen.length) {
        const arbeitIds = new Set(Object.values(ergebnis.zugeordnet).flat());
        const namen = (this._uebersicht?.arbeiten ?? [])
          .filter((arbeit) => arbeitIds.has(arbeit.id))
          .map((arbeit) => `${arbeit.thema} (${this._datum(arbeit.datum)})`)
          .join(", ");
        const frage = this._t("loeschen_warnung", {
          n: betroffen.length,
          arbeiten: namen,
        });
        if (!window.confirm(frage)) {
          return;
        }
        ergebnis = await this._api.aufgabenLoeschen(this._fachId, ids, true);
      }
      this._zeigeErfolg(this._t("geloescht", { n: ergebnis.geloescht }));
      await this._neuLaden();
    } catch (fehler) {
      this._zeigeFehler(fehler);
    } finally {
      this._beschaeftigt = false;
    }
  }

  private _schliesseDialog(): void {
    this._dialog = null;
    this._vorschau = null;
    this._jsonDaten = null;
    this._arbeit = null;
    this._generieren = null;
    this._nachgerechnet = null;
    if (this._bildEntwurf?.vorschau) {
      URL.revokeObjectURL(this._bildEntwurf.vorschau);
    }
    this._bildEntwurf = null;
    this._grossbild = "";
    this._bildText = "";
    for (const adresse of this._seiten?.vorschauen ?? []) {
      URL.revokeObjectURL(adresse);
    }
    this._seiten = null;
    for (const adresse of this._foto?.vorschauen ?? []) {
      URL.revokeObjectURL(adresse);
    }
    this._foto = null;
    this._sim = null;
    this._dialogFehler = "";
  }

  // ---------------------------------------------------- simulated exams

  private _simVerfuegbar(entwurf: SimulationsEntwurf): number {
    return entwurf.arbeit.simulierbar?.[entwurf.weg] ?? MAX_SIM_AUFGABEN;
  }

  private _oeffneSimulation(arbeit: Arbeit): void {
    const entwurf: SimulationsEntwurf = { arbeit, anzahl: 10, weg: "ausdruck", seiten: null };
    entwurf.anzahl = Math.max(1, Math.min(10, this._simVerfuegbar(entwurf)));
    this._sim = entwurf;
    this._dialogFehler = "";
    this._dialog = "simulation";
  }

  private async _simuliere(): Promise<void> {
    const entwurf = this._sim;
    if (!entwurf) {
      return;
    }
    this._beschaeftigt = true;
    this._dialogFehler = "";
    try {
      const ergebnis = await this._api.simulieren(
        entwurf.arbeit.id,
        entwurf.anzahl,
        entwurf.weg,
      );
      if (ergebnis.weg === "messenger") {
        this._schliesseDialog();
        this._zeigeErfolg(this._t("sim_gestartet", { n: ergebnis.anzahl }));
        this._tab = "uebersicht";
        return;
      }
      const seiten: string[] = [];
      for (const bild of ergebnis.bilder) {
        seiten.push(await this._api.bildAdresse(bild));
      }
      this._sim = { ...entwurf, anzahl: ergebnis.anzahl, seiten };
    } catch (fehler) {
      this._dialogFehler = fehlertext(this._t, fehler);
    } finally {
      this._beschaeftigt = false;
    }
  }

  /** Open the pages of the sheet in a window of their own and print them. */
  private _druckeSimulation(): void {
    const seiten = this._sim?.seiten ?? [];
    const fenster = window.open("", "_blank");
    if (!fenster) {
      this._dialogFehler = this._t("sim_druck_blockiert");
      return;
    }
    const dokument = fenster.document;
    dokument.title = this._sim?.arbeit.thema ?? "";
    const stil = dokument.createElement("style");
    stil.textContent =
      "@page{size:A4;margin:0}body{margin:0}img{display:block;width:100%;page-break-after:always}";
    dokument.head.append(stil);
    let offen = seiten.length;
    for (const adresse of seiten) {
      const bild = dokument.createElement("img");
      bild.addEventListener("load", () => {
        offen -= 1;
        if (offen === 0) {
          fenster.focus();
          fenster.print();
        }
      });
      bild.src = new URL(adresse, window.location.origin).href;
      dokument.body.append(bild);
    }
  }

  // ------------------------------------------------- import from photos

  private _oeffneFoto(): void {
    this._foto = {
      dateien: [],
      vorschauen: [],
      lektion: this._filter.lektion === OHNE_LEKTION ? "" : this._filter.lektion,
      zeilen: null,
    };
    this._dialogFehler = "";
    this._dialog = "foto";
  }

  private _fotoGewaehlt(ereignis: Event): void {
    const entwurf = this._foto;
    if (!entwurf) {
      return;
    }
    const gewaehlt = [...((ereignis.target as HTMLInputElement).files ?? [])];
    for (const adresse of entwurf.vorschauen) {
      URL.revokeObjectURL(adresse);
    }
    const dateien = gewaehlt.slice(0, MAX_SEITEN);
    this._dialogFehler =
      gewaehlt.length > MAX_SEITEN ? this._t("seiten_zu_viele", { n: MAX_SEITEN }) : "";
    this._foto = {
      ...entwurf,
      dateien,
      vorschauen: dateien.map((datei) => URL.createObjectURL(datei)),
    };
  }

  /** Upload the photos and let the AI read the tasks on them. */
  private async _leseFoto(): Promise<void> {
    const entwurf = this._foto;
    const fach = this._fach;
    if (!entwurf || !entwurf.dateien.length || !fach) {
      return;
    }
    const [a = "", b = ""] = fach.sprachen;
    this._beschaeftigt = true;
    this._dialogFehler = "";
    try {
      const seiten: string[] = [];
      for (const datei of entwurf.dateien) {
        seiten.push(await this._api.bildHochladen(datei, true));
      }
      const vorschau = await this._api.fotoAuslesen(fach.id, seiten);
      if (!vorschau.zeilen.length) {
        this._dialogFehler = this._t("foto_leer");
        return;
      }
      this._foto = {
        ...entwurf,
        zeilen: vorschau.zeilen.map((roh) => ({
          // Tasks that need a figure belong into "task with an image"
          an: !roh.vorhanden && !roh.braucht_bild,
          a: vorschau.typ === "mathe" ? (roh.aufgabe ?? "") : (roh.frage?.[a] ?? ""),
          b: vorschau.typ === "mathe" ? (roh.loesung ?? "") : (roh.frage?.[b] ?? ""),
          hinweis: roh.hinweis ?? "",
          seite: roh.seite?.toString() ?? "",
          geaendert: false,
          roh,
        })),
      };
    } catch (fehler) {
      this._dialogFehler = fehlertext(this._t, fehler);
    } finally {
      this._beschaeftigt = false;
    }
  }

  private _setzeFotoZeile(index: number, neu: Partial<FotoEntwurfZeile>): void {
    const entwurf = this._foto;
    if (!entwurf?.zeilen) {
      return;
    }
    this._foto = {
      ...entwurf,
      zeilen: entwurf.zeilen.map((zeile, i) => (i === index ? { ...zeile, ...neu } : zeile)),
    };
  }

  /** Store the lines of the preview that are ticked. */
  private async _uebernimmFoto(): Promise<void> {
    const entwurf = this._foto;
    const fach = this._fach;
    if (!entwurf?.zeilen || !fach) {
      return;
    }
    const [a = "", b = ""] = fach.sprachen;
    const zeilen = entwurf.zeilen
      .filter((zeile) => zeile.an)
      .map((zeile): Record<string, unknown> => {
        const seite = zeile.seite.trim() === "" ? null : Number(zeile.seite);
        if (fach.typ === "mathe") {
          return {
            aufgabe: zeile.a,
            loesung: zeile.b,
            seite,
            // A corrected line is no longer the one that was checked
            verifikation: zeile.geaendert ? "keine" : zeile.roh.verifikation,
          };
        }
        return {
          frage: { [a]: zeile.a, [b]: zeile.b },
          alternativen: zeile.geaendert ? {} : (zeile.roh.alternativen ?? {}),
          hinweis: zeile.hinweis || null,
          seite,
        };
      });
    if (!zeilen.length) {
      return;
    }
    this._beschaeftigt = true;
    this._dialogFehler = "";
    try {
      const ergebnis = await this._api.fotoUebernehmen(
        fach.id,
        zeilen,
        entwurf.lektion || null,
      );
      if (ergebnis.fehler.length && !ergebnis.importiert) {
        this._dialogFehler = this._t("foto_fehler", { n: ergebnis.fehler.length });
        return;
      }
      this._schliesseDialog();
      this._zeigeErfolg(
        this._t("foto_fertig", {
          n: ergebnis.importiert,
          doppelt: ergebnis.uebersprungen,
          fehler: ergebnis.fehler.length,
        }),
      );
      await this._neuLaden();
    } catch (fehler) {
      this._dialogFehler = fehlertext(this._t, fehler);
    } finally {
      this._beschaeftigt = false;
    }
  }

  // --------------------------------------------- questions from book pages

  private _oeffneSeiten(): void {
    this._seiten = {
      dateien: [],
      vorschauen: [],
      lektion: this._filter.lektion === OHNE_LEKTION ? "" : this._filter.lektion,
      anzahl: 8,
      form: "gemischt",
      schwerpunkt: "",
    };
    this._dialogFehler = "";
    this._dialog = "seiten";
  }

  private _seitenGewaehlt(ereignis: Event): void {
    const entwurf = this._seiten;
    if (!entwurf) {
      return;
    }
    const gewaehlt = [...((ereignis.target as HTMLInputElement).files ?? [])];
    for (const adresse of entwurf.vorschauen) {
      URL.revokeObjectURL(adresse);
    }
    const dateien = gewaehlt.slice(0, MAX_SEITEN);
    this._dialogFehler =
      gewaehlt.length > MAX_SEITEN ? this._t("seiten_zu_viele", { n: MAX_SEITEN }) : "";
    this._seiten = {
      ...entwurf,
      dateien,
      vorschauen: dateien.map((datei) => URL.createObjectURL(datei)),
    };
  }

  /** Upload the pages and let the AI create questions about them. */
  private async _erzeugeFragen(): Promise<void> {
    const entwurf = this._seiten;
    if (!entwurf || !entwurf.dateien.length || !this._fachId) {
      return;
    }
    this._beschaeftigt = true;
    this._dialogFehler = "";
    try {
      const seiten: string[] = [];
      for (const datei of entwurf.dateien) {
        seiten.push(await this._api.bildHochladen(datei, true));
      }
      const ergebnis = await this._api.fragenAusSeiten(this._fachId, {
        seiten,
        anzahl: entwurf.anzahl,
        form: entwurf.form,
        lektion: entwurf.lektion || null,
        schwerpunkt: entwurf.schwerpunkt.trim() || null,
      });
      this._schliesseDialog();
      this._auswahl = new Set();
      if (ergebnis.erzeugt) {
        // Show what waits for approval
        this._filter = { ...LEERER_FILTER, geprueft: "nein" };
      }
      this._zeigeErfolg(
        this._t("seiten_fertig", {
          erzeugt: ergebnis.erzeugt,
          verworfen: ergebnis.verworfen,
          doppelt: ergebnis.uebersprungen,
        }),
      );
      await this._neuLaden();
    } catch (fehler) {
      this._dialogFehler = fehlertext(this._t, fehler);
    } finally {
      this._beschaeftigt = false;
    }
  }

  // ------------------------------------------------------------- lessons

  private _oeffneLektionen(): void {
    this._lektionName = "";
    this._dialogFehler = "";
    this._dialog = "lektion";
  }

  private async _lektionAnlegen(): Promise<void> {
    const name = this._lektionName.trim();
    if (!name || !this._fachId) {
      return;
    }
    this._dialogFehler = "";
    try {
      await this._api.lektionHinzufuegen(this._fachId, name);
      this._lektionName = "";
      this._zeigeErfolg(this._t("lektion_angelegt", { name }));
      await this._neuLaden();
    } catch (fehler) {
      this._dialogFehler = fehlertext(this._t, fehler);
    }
  }

  private async _lektionLoeschen(name: string): Promise<void> {
    this._dialogFehler = "";
    try {
      await this._api.lektionLoeschen(this._fachId, name);
      if (this._filter.lektion === name) {
        this._setzeFilter("lektion", "");
      }
      await this._neuLaden();
    } catch (fehler) {
      this._dialogFehler = fehlertext(this._t, fehler);
    }
  }

  private _lektionAuswahl(
    gewaehlt: string,
    geaendert: (neu: string) => void,
    label: string,
  ): TemplateResult {
    // A lesson that is not in the list any more stays selectable
    const lektionen = [...(this._fach?.lektionen ?? [])];
    if (gewaehlt && !lektionen.includes(gewaehlt)) {
      lektionen.push(gewaehlt);
    }
    return html`
      <select
        aria-label=${label}
        .value=${gewaehlt}
        @change=${(e: Event) => geaendert(wert(e))}
      >
        <option value="" ?selected=${gewaehlt === ""}>
          ${this._t("keine_lektion")}
        </option>
        ${lektionen.map(
          (lektion) =>
            html`<option value=${lektion} ?selected=${lektion === gewaehlt}>
              ${lektion}
            </option>`,
        )}
      </select>
    `;
  }

  // -------------------------------------------------------------- import

  private _oeffneImport(): void {
    this._importText = "";
    this._importTrenner = "";
    this._importGeprueft = true;
    this._importLektion =
      this._filter.lektion === OHNE_LEKTION ? "" : this._filter.lektion;
    this._vorschau = null;
    this._dialogFehler = "";
    this._dialog = "import";
  }

  private async _importVorschau(): Promise<void> {
    this._dialogFehler = "";
    try {
      this._vorschau = await this._api.importVorschau(
        this._fachId,
        this._importText,
        this._importTrenner || null,
      );
    } catch (fehler) {
      this._dialogFehler = fehlertext(this._t, fehler);
    }
  }

  private async _importUebernehmen(): Promise<void> {
    this._beschaeftigt = true;
    this._dialogFehler = "";
    try {
      const ergebnis = await this._api.importText(
        this._fachId,
        this._importText,
        this._importLektion.trim() || null,
        this._importTrenner || null,
        this._importGeprueft,
      );
      this._schliesseDialog();
      this._zeigeErfolg(
        this._t("import_ergebnis", {
          n: ergebnis.importiert,
          u: ergebnis.uebersprungen,
        }),
      );
      await this._neuLaden();
    } catch (fehler) {
      this._dialogFehler = fehlertext(this._t, fehler);
    } finally {
      this._beschaeftigt = false;
    }
  }

  private async _exportiere(): Promise<void> {
    const fach = this._fach;
    if (!fach) {
      return;
    }
    try {
      const daten = await this._api.export(fach.id, this._mitStatistik);
      const blob = new Blob([JSON.stringify(daten, null, 2)], {
        type: "application/json",
      });
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      const name = fach.name.replace(/[^\p{L}\p{N}_-]+/gu, "_");
      link.download = `learnbuddy-${name}-${new Date().toISOString().slice(0, 10)}.json`;
      link.click();
      URL.revokeObjectURL(link.href);
      this._schliesseDialog();
      const ohneBild = Number(daten.ausgelassen_mit_bild ?? 0);
      if (ohneBild) {
        this._zeigeErfolg(this._t("export_ohne_bild", { n: ohneBild }));
      }
    } catch (fehler) {
      this._dialogFehler = fehlertext(this._t, fehler);
    }
  }

  private async _dateiGewaehlt(ereignis: Event): Promise<void> {
    const eingabe = ereignis.target as HTMLInputElement;
    const datei = eingabe.files?.[0];
    eingabe.value = "";
    if (!datei) {
      return;
    }
    try {
      const daten: unknown = JSON.parse(await datei.text());
      if (typeof daten !== "object" || daten === null || Array.isArray(daten)) {
        throw new Error("no object");
      }
      this._jsonDaten = daten as Record<string, unknown>;
      this._jsonLektion = "";
      this._dialogFehler = "";
      this._dialog = "importJson";
    } catch {
      this._meldung = { text: this._t("datei_ungueltig"), fehler: true };
    }
  }

  private async _importiereJson(): Promise<void> {
    if (!this._jsonDaten) {
      return;
    }
    this._beschaeftigt = true;
    try {
      const ergebnis = await this._api.importJson(
        this._fachId,
        this._jsonDaten,
        this._mitStatistik,
        this._jsonLektion || null,
      );
      this._schliesseDialog();
      let text = this._t("import_ergebnis", {
        n: ergebnis.importiert,
        u: ergebnis.uebersprungen,
      });
      if (ergebnis.fehler.length) {
        text += ` ${this._t("import_fehler", { n: ergebnis.fehler.length })}`;
      }
      this._zeigeErfolg(text);
      await this._neuLaden();
    } catch (fehler) {
      this._dialogFehler = fehlertext(this._t, fehler);
    } finally {
      this._beschaeftigt = false;
    }
  }

  // --------------------------------------------------------------- exams

  private _oeffneArbeit(arbeit: Arbeit | null, ids: string[] = []): void {
    const gezielt = arbeit
      ? arbeit.lektionen.length > 0 || arbeit.aufgaben_ids.length > 0
      : ids.length > 0;
    this._arbeit = {
      id: arbeit?.id ?? null,
      art: arbeit?.art ?? "arbeit",
      datum: arbeit?.datum ?? "",
      thema: arbeit?.thema ?? "",
      abfragen: arbeit?.abfragen_pro_tag ?? 3,
      start: arbeit?.start_tage_vorher ?? 7,
      intensivierung: arbeit?.intensivierung ?? true,
      frist: arbeit?.antwortfrist_minuten ?? null,
      simUm: lokaleZeit(arbeit?.simulation_um ?? null),
      simAnzahl: arbeit?.simulation_anzahl ?? 10,
      modus: gezielt ? "auswahl" : "alle",
      lektionen: new Set(arbeit?.lektionen ?? []),
      ids: new Set(arbeit?.aufgaben_ids ?? ids),
      seit: "",
      seiteVon: "",
      seiteBis: "",
    };
    this._dialogFehler = "";
    this._dialog = "arbeit";
  }

  private _setzeArbeit<K extends keyof ArbeitEntwurf>(
    feld: K,
    neu: ArbeitEntwurf[K],
  ): void {
    if (this._arbeit) {
      this._arbeit = { ...this._arbeit, [feld]: neu };
    }
  }

  private _arbeitMenge(feld: "lektionen" | "ids", eintrag: string, an: boolean): void {
    if (!this._arbeit) {
      return;
    }
    const menge = new Set(this._arbeit[feld]);
    if (an) {
      menge.add(eintrag);
    } else {
      menge.delete(eintrag);
    }
    this._setzeArbeit(feld, menge);
    // A whole lesson is the obvious topic as long as none was entered
    if (feld === "lektionen" && an && !this._arbeit.thema.trim()) {
      this._setzeArbeit("thema", eintrag);
    }
  }

  private _arbeitSeit(): void {
    const arbeit = this._arbeit;
    if (!arbeit?.seit) {
      return;
    }
    const ids = new Set(arbeit.ids);
    for (const aufgabe of this._aufgaben) {
      if (aufgabe.erstellt.slice(0, 10) >= arbeit.seit) {
        ids.add(aufgabe.id);
      }
    }
    this._setzeArbeit("ids", ids);
  }

  private _arbeitSeiten(): void {
    const arbeit = this._arbeit;
    if (!arbeit || (!arbeit.seiteVon && !arbeit.seiteBis)) {
      return;
    }
    const ids = new Set(arbeit.ids);
    for (const aufgabe of this._aufgaben) {
      if (inSeiten(aufgabe.seite, arbeit.seiteVon, arbeit.seiteBis)) {
        ids.add(aufgabe.id);
      }
    }
    this._setzeArbeit("ids", ids);
  }

  private _arbeitUmfang(arbeit: {
    lektionen: Iterable<string>;
    ids: Iterable<string>;
  }): number | null {
    const lektionen = new Set(arbeit.lektionen);
    const ids = new Set(arbeit.ids);
    if (!lektionen.size && !ids.size) {
      return null;
    }
    return this._aufgaben.filter(
      (aufgabe) =>
        ids.has(aufgabe.id) ||
        (aufgabe.lektion !== null && lektionen.has(aufgabe.lektion)),
    ).length;
  }

  private async _speichereArbeit(): Promise<void> {
    const arbeit = this._arbeit;
    if (!arbeit) {
      return;
    }
    const gezielt = arbeit.modus === "auswahl";
    const eingabe: ArbeitEingabe = {
      datum: arbeit.datum,
      thema: arbeit.thema,
      art: arbeit.art,
      lektionen: gezielt ? [...arbeit.lektionen] : [],
      aufgaben_ids: gezielt ? [...arbeit.ids] : [],
      abfragen_pro_tag: arbeit.abfragen,
      start_tage_vorher: arbeit.start,
      intensivierung: arbeit.intensivierung,
      antwortfrist_minuten: arbeit.frist,
      // Sent with its zone so that the server does not have to guess
      simulation_um: arbeit.simUm ? new Date(arbeit.simUm).toISOString() : null,
      simulation_anzahl: arbeit.simAnzahl,
    };
    if (!arbeit.id) {
      eingabe.fach_id = this._fachId;
    }
    this._beschaeftigt = true;
    this._dialogFehler = "";
    try {
      await this._api.arbeitSpeichern(arbeit.id, eingabe);
      this._schliesseDialog();
      this._auswahl = new Set();
      this._tab = "arbeiten";
      this._zeigeErfolg(this._t("gespeichert"));
      await this._neuLaden(20);
    } catch (fehler) {
      this._dialogFehler = fehlertext(this._t, fehler);
    } finally {
      this._beschaeftigt = false;
    }
  }

  private async _loescheArbeit(arbeit: Arbeit): Promise<void> {
    if (!window.confirm(this._t("arbeit_loeschen_frage", { thema: arbeit.thema }))) {
      return;
    }
    try {
      await this._api.arbeitLoeschen(arbeit.id);
      this._zeigeErfolg(this._t("geloescht_arbeit"));
      await this._neuLaden(20);
    } catch (fehler) {
      this._zeigeFehler(fehler);
    }
  }

  private _datum(iso: string): string {
    const datum = new Date(`${iso.slice(0, 10)}T00:00:00`);
    return Number.isNaN(datum.getTime())
      ? iso
      : datum.toLocaleDateString(this.hass?.language ?? "en", {
          year: "numeric",
          month: "2-digit",
          day: "2-digit",
        });
  }

  /** Format a point in time with date and time of day. */
  private _zeitpunkt(iso: string): string {
    const zeit = new Date(iso);
    return Number.isNaN(zeit.getTime())
      ? iso
      : zeit.toLocaleString(this.hass?.language ?? "en", {
          year: "numeric",
          month: "2-digit",
          day: "2-digit",
          hour: "2-digit",
          minute: "2-digit",
        });
  }

  private _menue(): void {
    this.dispatchEvent(
      new CustomEvent("hass-toggle-menu", { bubbles: true, composed: true }),
    );
  }

  // -------------------------------------------------------------- render

  protected render(): TemplateResult {
    const t = this._t;
    const uebersicht = this._uebersicht;
    return html`
      <header>
        ${this.narrow
          ? html`<button class="icon" aria-label="Menu" @click=${this._menue}>
              <ha-icon icon="mdi:menu"></ha-icon>
            </button>`
          : nothing}
        <h1>${t("titel")}</h1>
        ${uebersicht && uebersicht.kinder.length > 0
          ? html`<div class="kinder" role="group" aria-label=${t("kind")}>
              ${uebersicht.kinder.map(
                (kind) =>
                  html`<button
                    class="kindwahl"
                    aria-pressed=${kind.id === this._kindId ? "true" : "false"}
                    @click=${() => this._waehleKind(kind.id)}
                  >
                    ${kind.name}
                  </button>`,
              )}
            </div>`
          : nothing}
      </header>
      <main>
        ${this._veraltet
          ? html`<div class="meldung" role="status">
              <span>${t("neue_version")}</span>
              <button class="primaer" @click=${() => window.location.reload()}>
                ${t("neu_laden")}
              </button>
            </div>`
          : nothing}
        ${this._meldung
          ? html`<div
              class="meldung ${this._meldung.fehler ? "fehler" : ""}"
              role=${this._meldung.fehler ? "alert" : "status"}
            >
              <span>${this._meldung.text}</span>
              <button
                class="icon"
                aria-label=${t("schliessen")}
                @click=${() => {
                  this._meldung = null;
                }}
              >
                <ha-icon icon="mdi:close"></ha-icon>
              </button>
            </div>`
          : nothing}
        ${this._inhalt()}
      </main>
      ${this._dialogInhalt()}
    `;
  }

  private async _oeffne(ereignis: CustomEvent): Promise<void> {
    const { ziel, fachId } = ereignis.detail as { ziel: Tab; fachId: string };
    if (fachId !== this._fachId) {
      this._fachId = fachId;
      this._zuruecksetzen();
    }
    this._tab = ziel;
    await this._neuLaden();
  }

  private async _waehleTab(tab: Tab): Promise<void> {
    this._tab = tab;
    if (tab !== "uebersicht") {
      // Statistics may have changed while the overview was open
      await this._neuLaden();
    }
  }

  private _inhalt(): TemplateResult {
    const t = this._t;
    if (this._laedt) {
      return html`<div class="leer">${t("laden")}</div>`;
    }
    if (!this._uebersicht?.kinder.length) {
      return html`<div class="card leer">${t("keine_kinder")}</div>`;
    }
    const anzahl: Record<Tab, number | null> = {
      uebersicht: null,
      aufgaben: this._fach ? this._aufgaben.length : null,
      arbeiten: this._fach ? this._arbeitenDesFachs.length : null,
    };
    const namen: Record<Tab, string> = {
      uebersicht: t("tab_uebersicht"),
      aufgaben: t("tab_aufgaben"),
      arbeiten: t("tab_arbeiten"),
    };
    return html`
      <div class="tabs" role="tablist">
        ${(["uebersicht", "aufgaben", "arbeiten"] as const).map(
          (tab) =>
            html`<button
              role="tab"
              aria-selected=${this._tab === tab ? "true" : "false"}
              @click=${() => this._waehleTab(tab)}
            >
              ${namen[tab]}${anzahl[tab] === null ? "" : ` (${anzahl[tab]})`}
            </button>`,
        )}
      </div>
      ${this._tab === "uebersicht"
        ? html`<lh-uebersicht
            .hass=${this.hass}
            .narrow=${this.narrow}
            .kindId=${this._kindId}
            @lh-oeffnen=${this._oeffne}
          ></lh-uebersicht>`
        : this._fachBereich()}
    `;
  }

  private _fachBereich(): TemplateResult {
    const t = this._t;
    const faecher = this._faecherDesKindes;
    if (!this._fach) {
      return html`<div class="card leer">${t("keine_faecher")}</div>`;
    }
    return html`
      ${faecher.length > 0
        ? html`<div class="kinder fachwahl" role="group" aria-label=${t("fach")}>
            ${faecher.map(
              (fach) =>
                html`<button
                  class="kindwahl"
                  aria-pressed=${fach.id === this._fachId ? "true" : "false"}
                  @click=${() => this._waehleFach(fach.id)}
                >
                  ${fach.name}
                </button>`,
            )}
          </div>`
        : nothing}
      ${this._tab === "aufgaben" ? this._aufgabenAnsicht() : this._arbeitenAnsicht()}
    `;
  }

  private _aufgabenAnsicht(): TemplateResult {
    const t = this._t;
    const fach = this._fach as Fach;
    const sichtbar = this._gefiltert();
    const gewaehlt = [...this._auswahl];
    const alleGewaehlt =
      sichtbar.length > 0 && sichtbar.every((aufgabe) => this._auswahl.has(aufgabe.id));
    const [a = "", b = ""] = fach.sprachen;
    const sprache = this.hass?.language ?? "en";
    const filter = this._filter;
    const mathe = fach.typ === "mathe";
    const sach = fach.typ === "sach";
    const kind = this._uebersicht?.kinder.find((k) => k.id === this._kindId);
    // Older servers only tell whether an AI is selected and reads images
    const ki: KiStatus =
      fach.ki_status ?? (fach.ki ? (fach.ki_bilder ? "ok" : "ohne_bilder") : "keine");
    const kiAn = ki === "ok" || ki === "ohne_bilder";
    const kiBilder = ki === "ok";
    const kiGrund = ki === "ok" ? "" : t(`ki_${ki}`);
    return html`
      <div class="leiste">
        <button class="primaer" @click=${this._neueAufgabe}>
          ${t(sach ? "neue_frage" : "neue_aufgabe")}
        </button>
        <button @click=${this._oeffneLektionen}>${t("lektion_hinzufuegen")}</button>
        ${mathe
          ? html`<button
              ?disabled=${!kiAn}
              title=${kiAn ? "" : kiGrund}
              @click=${this._oeffneGenerieren}
            >
              ${t("generieren")}
            </button>`
          : nothing}
        ${sach
          ? html`<button
              ?disabled=${!kiBilder}
              title=${kiGrund}
              @click=${this._oeffneSeiten}
            >
              ${t("seiten")}
            </button>`
          : html`
              <button @click=${this._oeffneImport}>${t("importieren")}</button>
              <button
                ?disabled=${!kiBilder}
                title=${kiGrund}
                @click=${this._oeffneFoto}
              >
                ${t("foto_import")}
              </button>
            `}
        <button
          ?disabled=${!this._aufgaben.length}
          @click=${() => {
            this._mitStatistik = false;
            this._dialogFehler = "";
            this._dialog = "export";
          }}
        >
          ${t("export_json")}
        </button>
        <button
          @click=${() => {
            this.renderRoot.querySelector<HTMLInputElement>("#datei")?.click();
          }}
        >
          ${t("import_json")}
        </button>
        <input
          id="datei"
          type="file"
          accept="application/json,.json"
          hidden
          @change=${this._dateiGewaehlt}
        />
        <span class="abstand"></span>
        ${gewaehlt.length
          ? html`
              <span>${t("ausgewaehlt", { n: gewaehlt.length })}</span>
              ${this._aufgaben.some((x) => this._auswahl.has(x.id) && !x.geprueft)
                ? html`<button ?disabled=${this._beschaeftigt} @click=${this._freigeben}>
                    ${t("freigeben")}
                  </button>`
                : nothing}
              ${mathe
                ? html`<button ?disabled=${this._beschaeftigt} @click=${this._nachrechnen}>
                    ${t("nachrechnen")}
                  </button>`
                : nothing}
              ${mathe
                ? html`<button
                    ?disabled=${this._beschaeftigt}
                    title=${t("selbst_nachgerechnet_hinweis")}
                    @click=${this._markiereGeprueft}
                  >
                    ${t("selbst_nachgerechnet")}
                  </button>`
                : nothing}
              ${mathe
                ? html`<button
                    ?disabled=${this._beschaeftigt || !kiAn}
                    title=${kiAn ? "" : kiGrund}
                    @click=${this._erzeugeRechenwege}
                  >
                    ${t("rechenweg_erzeugen")}
                  </button>`
                : nothing}
              <button @click=${() => this._oeffneArbeit(null, gewaehlt)}>
                ${t("arbeit_aus_auswahl")}
              </button>
              <button
                class="gefahr"
                ?disabled=${this._beschaeftigt}
                @click=${() => this._loesche(gewaehlt)}
              >
                ${t("loeschen")}
              </button>
            `
          : nothing}
      </div>

      ${ki === "nicht_verfuegbar"
        ? html`<div class="meldung fehler" role="status">
            <span>
              ${t("ki_hinweis_nicht_verfuegbar")}
              ${sach ? t("ki_hinweis_sach_zusatz") : ""}
            </span>
          </div>`
        : ki === "keine" && sach
          ? html`<div class="meldung fehler" role="status">
              <span>${t("sach_ohne_ki")}</span>
            </div>`
          : ki === "ok"
            ? nothing
            : html`<p class="klein" role="note" style="margin: 0 0 12px">
                <ha-icon icon="mdi:information-outline" style="--mdc-icon-size: 16px"></ha-icon>
                ${t(`ki_hinweis_${ki}`)}
              </p>`}
      ${mathe &&
      kind &&
      !kind.bilder &&
      this._aufgaben.some((x) => x.typ === "mathe" && x.bild)
        ? html`<div class="meldung fehler" role="status">
            <span>${t("keine_bilder", { name: kind.name })}</span>
          </div>`
        : nothing}

      <div class="card filter">
        <label class="feld">
          ${t("filter_suche")}
          <input
            type="search"
            .value=${filter.suche}
            @input=${(e: Event) => this._setzeFilter("suche", wert(e))}
          />
        </label>
        <label class="feld">
          ${t("filter_lektion")}
          <select
            .value=${filter.lektion}
            @change=${(e: Event) => this._setzeFilter("lektion", wert(e))}
          >
            <option value="">${t("alle")}</option>
            ${fach.lektionen.map(
              (lektion) =>
                html`<option value=${lektion} ?selected=${filter.lektion === lektion}>
                  ${lektion}
                </option>`,
            )}
            <option value=${OHNE_LEKTION}>${t("ohne_lektion")}</option>
          </select>
        </label>
        <label class="feld">
          ${t("filter_quelle")}
          <select
            .value=${filter.quelle}
            @change=${(e: Event) => this._setzeFilter("quelle", wert(e))}
          >
            <option value="">${t("alle")}</option>
            <option value="manuell">${t("quelle_manuell")}</option>
            <option value="upload">${t("quelle_upload")}</option>
            <option value="generiert">${t("quelle_generiert")}</option>
          </select>
        </label>
        <label class="feld">
          ${t("filter_geprueft")}
          <select
            .value=${filter.geprueft}
            @change=${(e: Event) => this._setzeFilter("geprueft", wert(e))}
          >
            <option value="">${t("alle")}</option>
            <option value="ja">${t("ja")}</option>
            <option value="nein">${t("nein")}</option>
          </select>
        </label>
        <label class="feld">
          ${t("filter_fehlerquote")}
          <input
            type="number"
            min="0"
            max="100"
            .value=${filter.fehlerquote}
            @input=${(e: Event) => this._setzeFilter("fehlerquote", wert(e))}
          />
        </label>
        <label class="feld">
          ${t("filter_von")}
          <input
            type="date"
            .value=${filter.von}
            @change=${(e: Event) => this._setzeFilter("von", wert(e))}
          />
        </label>
        <label class="feld">
          ${t("filter_bis")}
          <input
            type="date"
            .value=${filter.bis}
            @change=${(e: Event) => this._setzeFilter("bis", wert(e))}
          />
        </label>
        <label class="feld">
          ${t("filter_seite_von")}
          <input
            type="number"
            min="1"
            .value=${filter.seiteVon}
            @input=${(e: Event) => this._setzeFilter("seiteVon", wert(e))}
          />
        </label>
        <label class="feld">
          ${t("filter_seite_bis")}
          <input
            type="number"
            min="1"
            .value=${filter.seiteBis}
            @input=${(e: Event) => this._setzeFilter("seiteBis", wert(e))}
          />
        </label>
        <button
          @click=${() => {
            this._filter = { ...LEERER_FILTER };
            this._nurIds = null;
          }}
        >
          ${t("filter_zuruecksetzen")}
        </button>
      </div>

      <div class="klein" style="margin: 0 4px 8px">
        ${t("anzahl", { n: sichtbar.length, gesamt: this._aufgaben.length })}
      </div>

      <div class="card tabelle-rahmen">
        <table>
          <thead>
            <tr>
              <th class="schmal">
                <input
                  type="checkbox"
                  aria-label=${t("alle_auswaehlen")}
                  .checked=${alleGewaehlt}
                  @change=${(e: Event) => this._alleUmschalten(sichtbar, angehakt(e))}
                />
              </th>
              <th>
                ${mathe
                  ? t("spalte_aufgabe")
                  : sach
                    ? t("spalte_frage")
                    : sprachname(sprache, a)}
              </th>
              <th>
                ${mathe
                  ? t("spalte_loesung")
                  : sach
                    ? t("spalte_musterantwort")
                    : sprachname(sprache, b)}
              </th>
              ${mathe
                ? html`<th class="schmal" title=${t("schwierigkeit_hinweis")}>
                    ${t("spalte_schwierigkeit")}
                  </th>`
                : nothing}
              <th>${t("spalte_hinweis")}</th>
              <th class="schmal">${t("spalte_seite")}</th>
              <th>${t("spalte_lektion")}</th>
              <th class="schmal" title=${t("box_hinweis")}>${t("spalte_box")}</th>
              <th class="schmal">${t("spalte_fehler")}</th>
              <th class="schmal">${t("spalte_geprueft")}</th>
              <th class="schmal">${t("spalte_erstellt")}</th>
              <th class="schmal"></th>
            </tr>
          </thead>
          <tbody>
            ${this._entwurf && this._entwurf.id === null
              ? this._editorZeile(this._entwurf, a, b)
              : nothing}
            ${sichtbar.map((aufgabe) =>
              this._entwurf?.id === aufgabe.id
                ? this._editorZeile(this._entwurf, a, b)
                : this._zeile(aufgabe, a, b),
            )}
          </tbody>
        </table>
        ${sichtbar.length === 0 && !this._entwurf
          ? html`<div class="leer">
              ${t(this._aufgaben.length ? "keine_treffer" : "keine_aufgaben")}
            </div>`
          : nothing}
      </div>
    `;
  }

  private _zeile(aufgabe: Aufgabe, a: string, b: string): TemplateResult {
    const t = this._t;
    const sprache = this.hass?.language ?? "en";
    const mathe = aufgabe.typ === "mathe" ? aufgabe : null;
    const sach = aufgabe.typ === "sach" ? aufgabe : null;
    const boxen = (mathe ? ["mathe"] : sach ? ["sach"] : [`${a}>${b}`, `${b}>${a}`])
      .map((richtung) => aufgabe.statistik[richtung]?.box ?? 1)
      .join(" · ");
    const wort = (code: string): TemplateResult =>
      aufgabe.typ !== "vokabel"
        ? html``
        : html`
            ${aufgabe.frage[code] ?? ""}
            ${aufgabe.alternativen[code]?.length
              ? html`<div class="klein">${aufgabe.alternativen[code]?.join(" | ")}</div>`
              : nothing}
          `;
    return html`
      <tr class=${this._auswahl.has(aufgabe.id) ? "gewaehlt" : ""}>
        <td class="schmal">
          <input
            type="checkbox"
            aria-label=${kurztext(aufgabe, a, b)}
            .checked=${this._auswahl.has(aufgabe.id)}
            @change=${(e: Event) => this._umschalten(aufgabe.id, angehakt(e))}
          />
        </td>
        ${mathe
          ? this._matheZellen(mathe)
          : sach
            ? this._sachZellen(sach)
            : html`
              <td data-label=${sprachname(sprache, a)}>${wort(a)}</td>
              <td data-label=${sprachname(sprache, b)}>${wort(b)}</td>
            `}
        <td data-label=${t("spalte_hinweis")}>${aufgabe.hinweis ?? ""}</td>
        <td class="schmal" data-label=${t("spalte_seite")}>${aufgabe.seite ?? ""}</td>
        <td data-label=${t("spalte_lektion")}>
          ${aufgabe.lektion ?? ""}
          ${aufgabe.arbeiten.length
            ? html`<span class="marke" title=${t("tab_arbeiten")}>
                ${aufgabe.arbeiten.length} ×
                <ha-icon
                  icon="mdi:calendar-star"
                  style="--mdc-icon-size: 12px"
                ></ha-icon>
              </span>`
            : nothing}
        </td>
        <td class="schmal" data-label=${t("spalte_box")} title=${t("box_hinweis")}>
          ${boxen}
        </td>
        <td class="schmal" data-label=${t("spalte_fehler")}>
          ${aufgabe.fehlerquote === null
            ? html`<span class="klein">–</span>`
            : html`<span class="marke ${aufgabe.fehlerquote >= 50 ? "warn" : "ok"}">
                ${Math.round(aufgabe.fehlerquote)} %
              </span>`}
        </td>
        <td class="schmal" data-label=${t("spalte_geprueft")}>
          <input
            type="checkbox"
            aria-label=${t("spalte_geprueft")}
            .checked=${aufgabe.geprueft}
            @change=${(e: Event) => this._setzeGeprueft(aufgabe, angehakt(e))}
          />
        </td>
        <td class="schmal klein" data-label=${t("spalte_erstellt")}>
          ${this._datum(aufgabe.erstellt)}
        </td>
        <td class="schmal">
          <button
            class="icon"
            title=${t("bearbeiten")}
            aria-label=${t("bearbeiten")}
            @click=${() => this._bearbeite(aufgabe)}
          >
            <ha-icon icon="mdi:pencil"></ha-icon>
          </button>
          <button
            class="icon"
            title=${t("loeschen")}
            aria-label=${t("loeschen")}
            ?disabled=${this._beschaeftigt}
            @click=${() => this._loesche([aufgabe.id])}
          >
            <ha-icon icon="mdi:delete"></ha-icon>
          </button>
        </td>
      </tr>
    `;
  }

  private _sachZellen(aufgabe: SachAufgabe): TemplateResult {
    const t = this._t;
    const adresse = aufgabe.quelle_bild
      ? this._bildAdressen[aufgabe.quelle_bild]
      : undefined;
    return html`
      <td data-label=${t("spalte_frage")}>
        ${adresse
          ? html`<button
              class="vorschaubild"
              style="float: right; margin-left: 8px; border: none; background: none"
              title=${t("quellseite_anzeigen")}
              aria-label=${t("quellseite_anzeigen")}
              @click=${() => {
                this._grossbild = adresse;
                this._bildText = aufgabe.stelle
                  ? `${t("belegstelle")}: „${aufgabe.stelle}“`
                  : "";
                this._dialogFehler = "";
                this._dialog = "bild";
              }}
            >
              <img class="vorschaubild" src=${adresse} alt="" loading="lazy" />
            </button>`
          : nothing}
        ${aufgabe.frage}
        <div class="klein">
          <span class="marke">${t(`form_${aufgabe.form}`)}</span>
          ${aufgabe.stelle && !adresse
            ? html`<span class="marke" title=${aufgabe.stelle}>
                <ha-icon
                  icon="mdi:format-quote-close"
                  style="--mdc-icon-size: 12px"
                ></ha-icon>
                ${t("belegstelle")}
              </span>`
            : nothing}
        </div>
      </td>
      <td data-label=${t("spalte_musterantwort")}>
        ${aufgabe.antwort}
        ${aufgabe.form === "auswahl"
          ? html`<div class="klein">
              ${aufgabe.falsche_optionen.map((option) => html`<div>✗ ${option}</div>`)}
            </div>`
          : aufgabe.kernpunkte.length
            ? html`<div class="klein">
                ${aufgabe.kernpunkte.map((punkt) => html`<div>• ${punkt}</div>`)}
              </div>`
            : nothing}
      </td>
    `;
  }

  private _matheZellen(aufgabe: MatheAufgabe): TemplateResult {
    const t = this._t;
    const adresse = aufgabe.bild ? this._bildAdressen[aufgabe.bild] : undefined;
    return html`
      <td data-label=${t("spalte_aufgabe")}>
        ${adresse
          ? html`<button
              class="vorschaubild"
              style="float: right; margin-left: 8px; border: none; background: none"
              title=${t("bild_anzeigen")}
              aria-label=${t("bild_anzeigen")}
              @click=${() => {
                this._grossbild = adresse;
                this._dialogFehler = "";
                this._dialog = "bild";
              }}
            >
              <img class="vorschaubild" src=${adresse} alt="" loading="lazy" />
            </button>`
          : aufgabe.bild
            ? html`<ha-icon
                icon="mdi:image-outline"
                style="float: right; --mdc-icon-size: 18px"
              ></ha-icon>`
            : nothing}
        ${aufgabe.aufgabe}
        <div class="klein">
          ${aufgabe.verifikation === "keine"
            ? nothing
            : aufgabe.verifikation === "abweichung"
              ? html`<span class="marke warn">
                  <ha-icon icon="mdi:alert" style="--mdc-icon-size: 12px"></ha-icon>
                  ${t("verifikation_abweichung")}
                </span>`
              : html`<span class="marke ok">
                  <ha-icon
                    icon="mdi:check-decagram"
                    style="--mdc-icon-size: 12px"
                  ></ha-icon>
                  ${t(`verifikation_${aufgabe.verifikation}`)}
                </span>`}
          ${aufgabe.rechenweg.length
            ? html`<span class="marke" title=${aufgabe.rechenweg.join("\n")}>
                <ha-icon icon="mdi:stairs" style="--mdc-icon-size: 12px"></ha-icon>
                ${t("rechenweg_vorhanden")}
              </span>`
            : nothing}
        </div>
      </td>
      <td data-label=${t("spalte_loesung")}>
        ${aufgabe.loesung}
        ${aufgabe.alternativen.length
          ? html`<div class="klein">${aufgabe.alternativen.join(" | ")}</div>`
          : nothing}
        ${aufgabe.vorschlag
          ? html`<div class="klein" style="margin-top: 4px">
              ${t(aufgabe.vorschlag_durch === "ki" ? "vorschlag_ki" : "vorschlag")}:
              <strong>${aufgabe.vorschlag}</strong>
              <button
                style="margin-left: 4px; padding: 2px 8px"
                title=${t("uebernehmen_titel")}
                ?disabled=${this._beschaeftigt}
                @click=${() => this._uebernimmVorschlag([aufgabe.id])}
              >
                ${t("uebernehmen_loesung")}
              </button>
            </div>`
          : nothing}
      </td>
      <td
        class="schmal"
        data-label=${t("spalte_schwierigkeit")}
        title=${t("schwierigkeit_hinweis")}
      >
        ${aufgabe.schwierigkeit ?? html`<span class="klein">–</span>`}
      </td>
    `;
  }

  private _editorZeile(entwurf: AufgabeEntwurf, a: string, b: string): TemplateResult {
    const t = this._t;
    const mathe = this._fach?.typ === "mathe";
    const sach = this._fach?.typ === "sach";
    const sprache = this.hass?.language ?? "en";
    const mehrzeilig = (
      feld: "a" | "b" | "kernpunkte" | "falsche",
      label: string,
      hoehe = 64,
    ): TemplateResult => html`
      <textarea
        style="min-height: ${hoehe}px"
        aria-label=${label}
        placeholder=${label}
        maxlength="500"
        .value=${entwurf[feld]}
        @input=${(e: Event) => this._setzeEntwurf(feld, wert(e))}
      ></textarea>
    `;
    const eingabe = (
      feld: "a" | "b" | "altA" | "altB" | "hinweis",
      label: string,
      platzhalter = "",
    ): TemplateResult => html`
      <input
        type="text"
        aria-label=${label}
        placeholder=${platzhalter}
        maxlength="500"
        .value=${entwurf[feld]}
        @input=${(e: Event) => this._setzeEntwurf(feld, wert(e))}
        @keydown=${(e: KeyboardEvent) => {
          if (e.key === "Enter") {
            void this._speichereAufgabe();
          }
        }}
      />
    `;
    const alt = `${t("spalte_alternativen")} (${t("alternativen_hinweis")})`;
    return html`
      <tr class="gewaehlt">
        <td class="schmal"></td>
        ${mathe
          ? html`
              <td data-label=${t("spalte_aufgabe")}>
                ${eingabe("a", t("spalte_aufgabe"))}
                <textarea
                  style="margin-top: 4px; min-height: 64px"
                  aria-label=${t("rechenweg")}
                  placeholder=${t("rechenweg")}
                  .value=${entwurf.rechenweg}
                  @input=${(e: Event) => this._setzeEntwurf("rechenweg", wert(e))}
                ></textarea>
              </td>
              <td data-label=${t("spalte_loesung")}>
                ${eingabe("b", t("spalte_loesung"))}
                <div style="margin-top: 4px">${eingabe("altB", alt, alt)}</div>
              </td>
              <td class="schmal" data-label=${t("spalte_schwierigkeit")}>
                <select
                  aria-label=${t("schwierigkeit")}
                  title=${t("schwierigkeit_hinweis")}
                  .value=${entwurf.schwierigkeit}
                  @change=${(e: Event) => this._setzeEntwurf("schwierigkeit", wert(e))}
                >
                  <option value="" ?selected=${entwurf.schwierigkeit === ""}>–</option>
                  ${["1", "2", "3", "4", "5"].map(
                    (stufe) =>
                      html`<option value=${stufe} ?selected=${entwurf.schwierigkeit === stufe}>
                        ${stufe}
                      </option>`,
                  )}
                </select>
              </td>
            `
          : sach
            ? html`
                <td data-label=${t("spalte_frage")}>
                  ${mehrzeilig("a", t("spalte_frage"))}
                  <select
                    style="margin-top: 4px"
                    aria-label=${t("form")}
                    .value=${entwurf.form}
                    @change=${(e: Event) =>
                      this._setzeEntwurf("form", wert(e) === "auswahl" ? "auswahl" : "kurz")}
                  >
                    <option value="kurz" ?selected=${entwurf.form === "kurz"}>
                      ${t("form_kurz")}
                    </option>
                    <option value="auswahl" ?selected=${entwurf.form === "auswahl"}>
                      ${t("form_auswahl")}
                    </option>
                  </select>
                </td>
                <td data-label=${t("spalte_musterantwort")}>
                  ${mehrzeilig(
                    "b",
                    t(entwurf.form === "auswahl" ? "richtige_antwort" : "spalte_musterantwort"),
                    entwurf.form === "auswahl" ? 32 : 64,
                  )}
                  <div style="margin-top: 4px">
                    ${entwurf.form === "auswahl"
                      ? mehrzeilig("falsche", t("falsche_optionen"))
                      : mehrzeilig("kernpunkte", t("kernpunkte"))}
                  </div>
                </td>
              `
            : html`
              <td data-label=${sprachname(sprache, a)}>
                ${eingabe("a", sprachname(sprache, a))}
                <div style="margin-top: 4px">${eingabe("altA", alt, alt)}</div>
              </td>
              <td data-label=${sprachname(sprache, b)}>
                ${eingabe("b", sprachname(sprache, b))}
                <div style="margin-top: 4px">${eingabe("altB", alt, alt)}</div>
              </td>
            `}
        <td data-label=${t("spalte_hinweis")}>
          ${eingabe("hinweis", t("spalte_hinweis"))}
        </td>
        <td class="schmal" data-label=${t("spalte_seite")}>
          <input
            type="number"
            min="1"
            max="9999"
            style="width: 5em"
            aria-label=${t("spalte_seite")}
            .value=${entwurf.seite}
            @input=${(e: Event) => this._setzeEntwurf("seite", wert(e))}
          />
        </td>
        <td data-label=${t("spalte_lektion")}>
          ${this._lektionAuswahl(
            entwurf.lektion,
            (neu) => this._setzeEntwurf("lektion", neu),
            t("spalte_lektion"),
          )}
        </td>
        <td class="schmal"></td>
        <td class="schmal"></td>
        <td class="schmal" data-label=${t("spalte_geprueft")}>
          <input
            type="checkbox"
            aria-label=${t("spalte_geprueft")}
            .checked=${entwurf.geprueft}
            @change=${(e: Event) => this._setzeEntwurf("geprueft", angehakt(e))}
          />
        </td>
        <td class="schmal"></td>
        <td class="schmal">
          <button
            class="icon"
            title=${t("speichern")}
            aria-label=${t("speichern")}
            ?disabled=${this._beschaeftigt}
            @click=${this._speichereAufgabe}
          >
            <ha-icon icon="mdi:check"></ha-icon>
          </button>
          <button
            class="icon"
            title=${t("abbrechen")}
            aria-label=${t("abbrechen")}
            @click=${() => {
              this._entwurf = null;
            }}
          >
            <ha-icon icon="mdi:close"></ha-icon>
          </button>
        </td>
      </tr>
    `;
  }

  private _arbeitenAnsicht(): TemplateResult {
    const t = this._t;
    const heute = new Date().toISOString().slice(0, 10);
    const arbeiten = this._arbeitenDesFachs;
    return html`
      <div class="leiste">
        <button class="primaer" @click=${() => this._oeffneArbeit(null)}>
          ${t("neue_arbeit")}
        </button>
      </div>
      ${arbeiten.length === 0
        ? html`<div class="card leer">${t("keine_arbeiten")}</div>`
        : arbeiten.map((arbeit) => {
            const umfang = this._arbeitUmfang({
              lektionen: arbeit.lektionen,
              ids: arbeit.aufgaben_ids,
            });
            return html`
              <div class="card arbeit">
                <div class="info">
                  <div class="titel">
                    ${arbeit.thema}
                    <span class="marke">
                      ${t(arbeit.art === "hue" ? "art_hue" : "art_arbeit")}
                    </span>
                    ${arbeit.datum < heute
                      ? html`<span class="marke warn">${t("vergangen")}</span>`
                      : nothing}
                  </div>
                  <div class="klein">
                    ${this._datum(arbeit.datum)} ·
                    ${umfang === null
                      ? t("arbeit_alle")
                      : t("arbeit_umfang", { n: umfang })}
                    ${arbeit.lektionen.length
                      ? html` · ${arbeit.lektionen.join(", ")}`
                      : nothing}
                    · ${arbeit.abfragen_pro_tag} × / ${arbeit.start_tage_vorher} d
                  </div>
                  ${arbeit.simulation_um
                    ? html`<div class="klein">
                        <ha-icon
                          icon="mdi:calendar-clock"
                          style="--mdc-icon-size: 14px"
                        ></ha-icon>
                        ${t(arbeit.simulation_geplant ? "sim_plan_offen" : "sim_plan_erledigt", {
                          zeit: this._zeitpunkt(arbeit.simulation_um),
                          n: arbeit.simulation_anzahl ?? 10,
                        })}
                      </div>`
                    : nothing}
                </div>
                <button
                  ?disabled=${arbeit.simulierbar?.ausdruck === 0}
                  title=${arbeit.simulierbar?.ausdruck === 0 ? t("sim_keine_aufgaben") : ""}
                  @click=${() => this._oeffneSimulation(arbeit)}
                >
                  ${t(arbeit.art === "hue" ? "sim_knopf_hue" : "sim_knopf_arbeit")}
                </button>
                <button @click=${() => this._oeffneArbeit(arbeit)}>
                  ${t("bearbeiten")}
                </button>
                <button class="gefahr" @click=${() => this._loescheArbeit(arbeit)}>
                  ${t("loeschen")}
                </button>
              </div>
            `;
          })}
    `;
  }

  // ------------------------------------------------------------- dialogs

  private _dialogInhalt(): TemplateResult | typeof nothing {
    if (!this._dialog) {
      return nothing;
    }
    let inhalt: TemplateResult;
    switch (this._dialog) {
      case "generieren":
        inhalt = this._generierenDialog();
        break;
      case "aufgabenart":
        inhalt = this._aufgabenartDialog();
        break;
      case "bildaufgabe":
        inhalt = this._bildaufgabeDialog();
        break;
      case "bild":
        inhalt = html`
          <img class="grossbild" src=${this._grossbild} alt=${this._t("bild")} />
          ${this._bildText
            ? html`<p style="margin: 12px 0 0">${this._bildText}</p>`
            : nothing}
          <div class="aktionen">
            <button class="primaer" @click=${this._schliesseDialog}>
              ${this._t("schliessen")}
            </button>
          </div>
        `;
        break;
      case "nachrechnen":
        inhalt = this._nachrechnenDialog();
        break;
      case "seiten":
        inhalt = this._seitenDialog();
        break;
      case "foto":
        inhalt = this._fotoDialog();
        break;
      case "simulation":
        inhalt = this._simulationDialog();
        break;
      case "import":
        inhalt = this._importDialog();
        break;
      case "export":
        inhalt = this._exportDialog();
        break;
      case "importJson":
        inhalt = this._importJsonDialog();
        break;
      case "lektion":
        inhalt = this._lektionDialog();
        break;
      default:
        inhalt = this._arbeitDialog();
    }
    return html`
      <div
        class="overlay"
        @click=${(e: Event) => {
          if (e.target === e.currentTarget) {
            this._schliesseDialog();
          }
        }}
      >
        <div
          class="dialog ${this._dialog === "foto" && this._foto?.zeilen ? "breit" : ""}"
          role="dialog"
          aria-modal="true"
        >
          ${inhalt}
          ${this._dialogFehler
            ? html`<div class="meldung fehler" role="alert" style="margin-top: 12px">
                <span>${this._dialogFehler}</span>
              </div>`
            : nothing}
        </div>
      </div>
    `;
  }

  private _simulationDialog(): TemplateResult {
    const t = this._t;
    const entwurf = this._sim;
    if (!entwurf) {
      return html``;
    }
    const hue = entwurf.arbeit.art === "hue";
    const titel = `${t(hue ? "sim_knopf_hue" : "sim_knopf_arbeit")}: ${entwurf.arbeit.thema}`;
    if (entwurf.seiten) {
      return html`
        <h2>${titel}</h2>
        <p class="klein">${t("sim_blatt_hilfe", { n: entwurf.anzahl })}</p>
        ${entwurf.seiten.map(
          (adresse, index) => html`
            <img
              class="grossbild"
              style="max-height: 60vh; margin: 12px auto; border: 1px solid var(--lh-border)"
              src=${adresse}
              alt=${`${t("spalte_seite")} ${index + 1}`}
            />
            <div class="aktionen" style="margin-top: 4px">
              <a
                class="knopf"
                href=${adresse}
                download=${`${hue ? "hue" : "klassenarbeit"}-${index + 1}.png`}
              >
                ${t("sim_herunterladen", { n: index + 1 })}
              </a>
            </div>
          `,
        )}
        <div class="aktionen">
          <button @click=${this._schliesseDialog}>${t("schliessen")}</button>
          <button class="primaer" @click=${this._druckeSimulation}>${t("sim_drucken")}</button>
        </div>
      `;
    }
    const verfuegbar = this._simVerfuegbar(entwurf);
    const hoechstens = Math.min(verfuegbar, MAX_SIM_AUFGABEN);
    const kind = this._uebersicht?.kinder.find((k) => k.id === this._kindId);
    const wege: SimulationsWeg[] = ["ausdruck", "messenger"];
    return html`
      <h2>${titel}</h2>
      <p class="klein">${t("sim_hilfe")}</p>
      <div class="wahl">
        ${wege.map(
          (weg) => html`
            <button
              class=${entwurf.weg === weg ? "primaer" : ""}
              aria-pressed=${entwurf.weg === weg ? "true" : "false"}
              @click=${() => {
                const neu = { ...entwurf, weg };
                const grenze = Math.min(this._simVerfuegbar(neu), MAX_SIM_AUFGABEN);
                this._sim = { ...neu, anzahl: Math.max(1, Math.min(neu.anzahl, grenze)) };
              }}
            >
              <strong>${t(`sim_weg_${weg}`)}</strong>
              <span class="klein">
                ${t(`sim_weg_${weg}_hilfe`, { name: kind?.name ?? "" })}
              </span>
            </button>
          `,
        )}
      </div>
      <label class="feld" style="margin-top: 12px; max-width: 260px">
        ${t("sim_anzahl")}
        <input
          type="number"
          min="1"
          max=${hoechstens}
          .value=${String(entwurf.anzahl)}
          @input=${(e: Event) => {
            const zahl = Math.round(Number(wert(e))) || 1;
            this._sim = { ...entwurf, anzahl: Math.max(1, Math.min(zahl, hoechstens)) };
          }}
        />
        <span class="klein">${t("sim_verfuegbar", { n: verfuegbar })}</span>
      </label>
      ${verfuegbar === 0
        ? html`<div class="meldung fehler" role="status" style="margin-top: 12px">
            <span>${t("sim_keine_aufgaben")}</span>
          </div>`
        : nothing}
      <div class="aktionen">
        <button @click=${this._schliesseDialog}>${t("abbrechen")}</button>
        <button
          class="primaer"
          ?disabled=${this._beschaeftigt || verfuegbar === 0}
          @click=${this._simuliere}
        >
          ${t(entwurf.weg === "messenger" ? "sim_start_messenger" : "sim_start_ausdruck")}
        </button>
      </div>
    `;
  }

  private _fotoDialog(): TemplateResult {
    const t = this._t;
    const entwurf = this._foto;
    const fach = this._fach;
    if (!entwurf || !fach) {
      return html``;
    }
    const mathe = fach.typ === "mathe";
    const [a = "", b = ""] = fach.sprachen;
    const sprache = this.hass?.language ?? "en";
    const zeilen = entwurf.zeilen;
    if (!zeilen) {
      return html`
        <h2>${t("foto_titel")}</h2>
        <p class="klein">${t(mathe ? "foto_hilfe_mathe" : "foto_hilfe")}</p>
        <label class="feld">
          ${t("seiten_waehlen", { n: MAX_SEITEN })} *
          <input
            type="file"
            multiple
            accept="image/png,image/jpeg,image/webp"
            aria-label=${t("seiten_waehlen", { n: MAX_SEITEN })}
            @change=${this._fotoGewaehlt}
          />
        </label>
        ${entwurf.vorschauen.length
          ? html`<div class="leiste" style="margin: 12px 0 0">
              ${entwurf.vorschauen.map(
                (adresse, index) =>
                  html`<img
                    class="grossbild"
                    style="max-height: 140px; margin: 0"
                    src=${adresse}
                    alt=${`${t("spalte_seite")} ${index + 1}`}
                  />`,
              )}
            </div>`
          : nothing}
        ${this._beschaeftigt
          ? html`<p class="klein" role="status">${t("seiten_laeuft")}</p>`
          : nothing}
        <div class="aktionen">
          <button @click=${this._schliesseDialog}>${t("abbrechen")}</button>
          <button
            class="primaer"
            ?disabled=${this._beschaeftigt || !entwurf.dateien.length}
            @click=${this._leseFoto}
          >
            ${t("foto_auslesen")}
          </button>
        </div>
      `;
    }
    const gewaehlt = zeilen.filter((zeile) => zeile.an).length;
    const feld = (
      index: number,
      name: "a" | "b" | "hinweis",
      label: string,
      inhalt: string,
    ): TemplateResult => html`
      <input
        type="text"
        aria-label=${label}
        maxlength="500"
        .value=${inhalt}
        @input=${(e: Event) =>
          this._setzeFotoZeile(index, { [name]: wert(e), geaendert: true })}
      />
    `;
    return html`
      <h2>${t("foto_vorschau_titel")}</h2>
      <p class="klein">${t("foto_vorschau_hilfe")}</p>
      <div class="tabelle-rahmen" style="max-height: 50vh; overflow: auto">
        <table>
          <thead>
            <tr>
              <th class="schmal">
                <input
                  type="checkbox"
                  aria-label=${t("alle_auswaehlen")}
                  .checked=${gewaehlt === zeilen.length}
                  @change=${(e: Event) => {
                    const an = angehakt(e);
                    this._foto = {
                      ...entwurf,
                      zeilen: zeilen.map((zeile) => ({ ...zeile, an })),
                    };
                  }}
                />
              </th>
              <th>${mathe ? t("spalte_aufgabe") : sprachname(sprache, a)}</th>
              <th>${mathe ? t("spalte_loesung") : sprachname(sprache, b)}</th>
              ${mathe ? nothing : html`<th>${t("spalte_hinweis")}</th>`}
              <th class="schmal">${t("spalte_seite")}</th>
            </tr>
          </thead>
          <tbody>
            ${zeilen.map((zeile, index) => {
              const roh = zeile.roh;
              const abweichung =
                !zeile.geaendert && roh.verifikation === "abweichung" && roh.vorschlag;
              return html`
                <tr class=${zeile.an ? "gewaehlt" : ""}>
                  <td class="schmal">
                    <input
                      type="checkbox"
                      aria-label=${zeile.a}
                      .checked=${zeile.an}
                      @change=${(e: Event) =>
                        this._setzeFotoZeile(index, { an: angehakt(e) })}
                    />
                  </td>
                  <td>
                    ${feld(index, "a", mathe ? t("spalte_aufgabe") : sprachname(sprache, a), zeile.a)}
                    <div class="klein">
                      ${roh.vorhanden
                        ? html`<span class="marke">${t("foto_vorhanden")}</span>`
                        : nothing}
                      ${roh.braucht_bild
                        ? html`<span class="marke warn">${t("foto_braucht_bild")}</span>`
                        : nothing}
                    </div>
                  </td>
                  <td>
                    ${feld(index, "b", mathe ? t("spalte_loesung") : sprachname(sprache, b), zeile.b)}
                    ${mathe && !roh.braucht_bild
                      ? html`<div class="klein">
                          ${zeile.geaendert || roh.verifikation === "keine"
                            ? html`<span class="marke">${t("foto_unbestaetigt")}</span>`
                            : abweichung
                              ? html`<span class="marke warn">
                                    ${t(
                                      roh.vorschlag_durch === "ki"
                                        ? "nachrechnen_ki"
                                        : "nachrechnen_berechnet",
                                    )}:
                                    ${roh.vorschlag}
                                  </span>
                                  <button
                                    @click=${() =>
                                      this._setzeFotoZeile(index, {
                                        b: roh.vorschlag ?? zeile.b,
                                        roh: {
                                          ...roh,
                                          verifikation:
                                            roh.vorschlag_durch === "ki" ? "ki" : "rechnerisch",
                                          vorschlag: null,
                                        },
                                      })}
                                  >
                                    ${t("uebernehmen_loesung")}
                                  </button>`
                              : html`<span class="marke ok">
                                  ${t(`verifikation_${roh.verifikation ?? "ki"}`)}
                                </span>`}
                        </div>`
                      : nothing}
                    ${!mathe && !zeile.geaendert
                      ? html`<div class="klein">
                          ${Object.values(roh.alternativen ?? {})
                            .flat()
                            .join(" | ")}
                        </div>`
                      : nothing}
                  </td>
                  ${mathe
                    ? nothing
                    : html`<td>${feld(index, "hinweis", t("spalte_hinweis"), zeile.hinweis)}</td>`}
                  <td class="schmal">
                    <input
                      type="number"
                      min="1"
                      max="9999"
                      style="width: 5em"
                      aria-label=${t("spalte_seite")}
                      .value=${zeile.seite}
                      @input=${(e: Event) => this._setzeFotoZeile(index, { seite: wert(e) })}
                    />
                  </td>
                </tr>
              `;
            })}
          </tbody>
        </table>
      </div>
      <label class="feld" style="margin-top: 12px">
        ${t("spalte_lektion")}
        ${this._lektionAuswahl(
          entwurf.lektion,
          (neu) => {
            this._foto = { ...entwurf, lektion: neu };
          },
          t("spalte_lektion"),
        )}
      </label>
      <div class="aktionen">
        <button @click=${this._schliesseDialog}>${t("abbrechen")}</button>
        <button
          class="primaer"
          ?disabled=${this._beschaeftigt || !gewaehlt}
          @click=${this._uebernimmFoto}
        >
          ${t("foto_uebernehmen", { n: gewaehlt })}
        </button>
      </div>
    `;
  }

  private _seitenDialog(): TemplateResult {
    const t = this._t;
    const entwurf = this._seiten;
    if (!entwurf) {
      return html``;
    }
    const setze = <K extends keyof SeitenEntwurf>(feld: K, neu: SeitenEntwurf[K]): void => {
      this._seiten = { ...entwurf, [feld]: neu };
    };
    const formen: (SachForm | "gemischt")[] = ["gemischt", "kurz", "auswahl"];
    return html`
      <h2>${t("seiten_titel")}</h2>
      <p class="klein">${t("seiten_hilfe")}</p>
      <label class="feld">
        ${t("seiten_waehlen", { n: MAX_SEITEN })} *
        <input
          type="file"
          multiple
          accept="image/png,image/jpeg,image/webp"
          aria-label=${t("seiten_waehlen", { n: MAX_SEITEN })}
          @change=${this._seitenGewaehlt}
        />
      </label>
      ${entwurf.vorschauen.length
        ? html`<div class="leiste" style="margin: 12px 0 0">
            ${entwurf.vorschauen.map(
              (adresse, index) =>
                html`<img
                  class="grossbild"
                  style="max-height: 140px; margin: 0"
                  src=${adresse}
                  alt=${`${t("spalte_seite")} ${index + 1}`}
                />`,
            )}
          </div>`
        : nothing}
      <div class="raster" style="margin-top: 12px">
        <label class="feld">
          ${t("spalte_lektion")}
          ${this._lektionAuswahl(
            entwurf.lektion,
            (neu) => setze("lektion", neu),
            t("spalte_lektion"),
          )}
        </label>
        <label class="feld">
          ${t("seiten_anzahl")}
          <input
            type="number"
            min="1"
            max="15"
            .value=${String(entwurf.anzahl)}
            @input=${(e: Event) =>
              setze("anzahl", Math.min(Math.max(Math.round(Number(wert(e))) || 1, 1), 15))}
          />
        </label>
        <label class="feld">
          ${t("form")}
          <select
            .value=${entwurf.form}
            @change=${(e: Event) =>
              setze("form", formen.find((form) => form === wert(e)) ?? "gemischt")}
          >
            ${formen.map(
              (form) =>
                html`<option value=${form} ?selected=${entwurf.form === form}>
                  ${t(`form_${form}`)}
                </option>`,
            )}
          </select>
        </label>
      </div>
      <label class="feld" style="margin-top: 12px">
        ${t("seiten_schwerpunkt")}
        <input
          type="text"
          maxlength="500"
          placeholder=${t("seiten_schwerpunkt_hilfe")}
          .value=${entwurf.schwerpunkt}
          @input=${(e: Event) => setze("schwerpunkt", wert(e))}
        />
      </label>
      ${this._beschaeftigt
        ? html`<p class="klein" role="status">${t("seiten_laeuft")}</p>`
        : nothing}
      <div class="aktionen">
        <button @click=${this._schliesseDialog}>${t("abbrechen")}</button>
        <button
          class="primaer"
          ?disabled=${this._beschaeftigt || !entwurf.dateien.length}
          @click=${this._erzeugeFragen}
        >
          ${t("seiten_start")}
        </button>
      </div>
    `;
  }

  private _aufgabenartDialog(): TemplateResult {
    const t = this._t;
    return html`
      <h2>${t("aufgabenart_titel")}</h2>
      <div class="wahl">
        <button
          @click=${() => {
            this._schliesseDialog();
            this._bearbeite(null);
          }}
        >
          <strong>${t("aufgabenart_rechnen")}</strong>
          <span class="klein">${t("aufgabenart_rechnen_hilfe")}</span>
        </button>
        <button @click=${this._oeffneBildaufgabe}>
          <strong>${t("aufgabenart_bild")}</strong>
          <span class="klein">${t("aufgabenart_bild_hilfe")}</span>
        </button>
      </div>
      <div class="aktionen">
        <button @click=${this._schliesseDialog}>${t("abbrechen")}</button>
      </div>
    `;
  }

  private _bildaufgabeDialog(): TemplateResult {
    const t = this._t;
    const entwurf = this._bildEntwurf;
    if (!entwurf) {
      return html``;
    }
    const kind = this._uebersicht?.kinder.find((k) => k.id === this._kindId);
    const alt = `${t("spalte_alternativen")} (${t("alternativen_hinweis")})`;
    return html`
      <h2>${t("bildaufgabe_titel")}</h2>
      ${kind && !kind.bilder
        ? html`<div class="meldung fehler" role="status" style="margin-bottom: 12px">
            <span>${t("keine_bilder", { name: kind.name })}</span>
          </div>`
        : nothing}
      <label class="feld">
        ${t("bild")} *
        <input
          type="file"
          accept="image/png,image/jpeg,image/webp,image/gif"
          aria-label=${t("bild_waehlen")}
          @change=${this._bildGewaehlt}
        />
        <span>${t("bild_hilfe")}</span>
      </label>
      ${entwurf.vorschau
        ? html`<img
            class="grossbild"
            style="max-height: 240px; margin: 12px auto"
            src=${entwurf.vorschau}
            alt=${t("bild_vorschau")}
          />`
        : nothing}
      <label class="feld" style="margin-top: 12px">
        ${t("einleitung")}
        <textarea
          maxlength="300"
          style="min-height: 56px"
          placeholder=${t("einleitung_hilfe")}
          .value=${entwurf.einleitung}
          @input=${(e: Event) => this._setzeBild("einleitung", wert(e))}
        ></textarea>
      </label>
      <div class="raster" style="margin-top: 12px">
        <label class="feld">
          ${t("spalte_lektion")}
          ${this._lektionAuswahl(
            entwurf.lektion,
            (neu) => this._setzeBild("lektion", neu),
            t("spalte_lektion"),
          )}
        </label>
        <label class="feld">
          ${t("spalte_seite")}
          <input
            type="number"
            min="1"
            max="9999"
            .value=${entwurf.seite}
            @input=${(e: Event) => this._setzeBild("seite", wert(e))}
          />
        </label>
      </div>
      <fieldset>
        <legend>${t("teilaufgaben")}</legend>
        <p class="klein" style="margin-top: 0">${t("teilaufgaben_hilfe")}</p>
        ${entwurf.teile.map(
          (teil, index) => html`
            <div class="teil">
              <label class="feld">
                ${t("teilaufgabe", { n: index + 1 })}
                <input
                  type="text"
                  maxlength="400"
                  placeholder="a) …"
                  .value=${teil.aufgabe}
                  @input=${(e: Event) => this._setzeTeil(index, "aufgabe", wert(e))}
                />
              </label>
              <label class="feld">
                ${t("spalte_loesung")}
                <input
                  type="text"
                  maxlength="100"
                  .value=${teil.loesung}
                  @input=${(e: Event) => this._setzeTeil(index, "loesung", wert(e))}
                />
              </label>
              <label class="feld">
                ${t("spalte_alternativen")}
                <input
                  type="text"
                  maxlength="300"
                  placeholder=${alt}
                  .value=${teil.alternativen}
                  @input=${(e: Event) => this._setzeTeil(index, "alternativen", wert(e))}
                />
              </label>
              <button
                class="icon"
                title=${t("teilaufgabe_entfernen")}
                aria-label=${t("teilaufgabe_entfernen")}
                ?disabled=${entwurf.teile.length < 2}
                @click=${() =>
                  this._setzeBild(
                    "teile",
                    entwurf.teile.filter((_, i) => i !== index),
                  )}
              >
                <ha-icon icon="mdi:delete"></ha-icon>
              </button>
            </div>
          `,
        )}
        <button
          ?disabled=${entwurf.teile.length >= 8}
          @click=${() => this._setzeBild("teile", [...entwurf.teile, { ...LEERER_TEIL }])}
        >
          ${t("teilaufgabe_hinzufuegen")}
        </button>
      </fieldset>
      <div class="aktionen">
        <button ?disabled=${this._beschaeftigt} @click=${this._schliesseDialog}>
          ${t("abbrechen")}
        </button>
        <button
          class="primaer"
          ?disabled=${this._beschaeftigt}
          @click=${this._speichereBildaufgabe}
        >
          ${t("speichern")}
        </button>
      </div>
    `;
  }

  private _nachrechnenDialog(): TemplateResult {
    const t = this._t;
    const ergebnis = this._nachgerechnet;
    if (!ergebnis) {
      return html``;
    }
    return html`
      <h2>${t("nachrechnen_titel")}</h2>
      <p class="klein">
        ${t("nachrechnen_zusammenfassung", {
          bestaetigt: ergebnis.bestaetigt,
          offen: ergebnis.nicht_pruefbar,
        })}
      </p>
      <div class="liste">
        ${ergebnis.abweichend.map(
          (eintrag) => html`
            <div class="eintrag">
              <span style="flex: 1">
                ${eintrag.aufgabe}
                <div class="klein">
                  ${t("nachrechnen_eingetragen")}: ${eintrag.loesung} ·
                  ${t(eintrag.durch === "ki" ? "nachrechnen_ki" : "nachrechnen_berechnet")}:
                  <strong>${eintrag.berechnet ?? "?"}</strong>
                </div>
              </span>
              ${eintrag.berechnet
                ? html`<button
                    title=${t("uebernehmen_titel")}
                    ?disabled=${this._beschaeftigt}
                    @click=${() => this._uebernimmVorschlag([eintrag.id])}
                  >
                    ${t("uebernehmen_loesung")}
                  </button>`
                : nothing}
            </div>
          `,
        )}
      </div>
      <div class="aktionen">
        <button
          @click=${() => {
            this._nurIds = new Set(ergebnis.abweichend.map((eintrag) => eintrag.id));
            this._auswahl = new Set();
            this._schliesseDialog();
          }}
        >
          ${t("nur_abweichende")}
        </button>
        <button ?disabled=${this._beschaeftigt} @click=${this._uebernimmAlle}>
          ${t("alle_uebernehmen")}
        </button>
        <button class="primaer" @click=${this._schliesseDialog}>${t("schliessen")}</button>
      </div>
    `;
  }

  private _generierenDialog(): TemplateResult {
    const t = this._t;
    const entwurf = this._generieren;
    if (!entwurf) {
      return html``;
    }
    const setze = <K extends keyof GenerierEntwurf>(feld: K, neu: GenerierEntwurf[K]): void => {
      this._generieren = { ...entwurf, [feld]: neu };
    };
    const markiert = this._auswahl.size;
    return html`
      <h2>${t("generieren_titel")}</h2>
      <p class="klein">${t("generieren_hilfe")}</p>
      <div class="raster">
        <label class="feld">
          ${t("spalte_lektion")}
          ${this._lektionAuswahl(
            entwurf.lektion,
            (neu) => setze("lektion", neu),
            t("spalte_lektion"),
          )}
        </label>
        <label class="feld">
          ${t("generieren_anzahl")}
          <input
            type="number"
            min="1"
            max="20"
            .value=${String(entwurf.anzahl)}
            @input=${(e: Event) =>
              setze("anzahl", Math.min(20, Math.max(1, Number(wert(e)) || 1)))}
          />
        </label>
        <label class="feld">
          ${t("schwierigkeit")}
          <select
            title=${t("schwierigkeit_hinweis")}
            .value=${entwurf.schwierigkeit}
            @change=${(e: Event) => setze("schwierigkeit", wert(e))}
          >
            <option value="" ?selected=${entwurf.schwierigkeit === ""}>
              ${t("schwierigkeit_beliebig")}
            </option>
            ${["1", "2", "3", "4", "5"].map(
              (stufe) =>
                html`<option value=${stufe} ?selected=${entwurf.schwierigkeit === stufe}>
                  ${stufe}
                </option>`,
            )}
          </select>
        </label>
      </div>
      <label class="feld" style="margin-top: 12px">
        ${t("generieren_beschreibung")}
        <textarea
          maxlength="500"
          placeholder=${t("generieren_beschreibung_hilfe")}
          .value=${entwurf.beschreibung}
          @input=${(e: Event) => setze("beschreibung", wert(e))}
        ></textarea>
      </label>
      <p class="klein">
        ${markiert
          ? t("generieren_beispiele_auswahl", { n: markiert })
          : t("generieren_beispiele_thema")}
      </p>
      ${this._beschaeftigt
        ? html`<p class="klein" role="status">${t("generieren_laeuft")}</p>`
        : nothing}
      <div class="aktionen">
        <button ?disabled=${this._beschaeftigt} @click=${this._schliesseDialog}>
          ${t("abbrechen")}
        </button>
        <button class="primaer" ?disabled=${this._beschaeftigt} @click=${this._generiere}>
          ${t("generieren_start")}
        </button>
      </div>
    `;
  }

  private _importDialog(): TemplateResult {
    const t = this._t;
    const [a = "", b = ""] = this._fach?.sprachen ?? [];
    const sprache = this.hass?.language ?? "en";
    const vorschau = this._vorschau;
    const neu = vorschau?.zeilen.filter((zeile) => !zeile.vorhanden).length ?? 0;
    const mathe = this._fach?.typ === "mathe";
    return html`
      <h2>${t(mathe ? "import_titel_mathe" : "import_titel")}</h2>
      <p class="klein">
        ${mathe
          ? t("import_hilfe_mathe")
          : t("import_hilfe", { a: sprachname(sprache, a), b: sprachname(sprache, b) })}
      </p>
      <label class="feld">
        ${t("import_inhalt")}
        <textarea
          .value=${this._importText}
          placeholder=${mathe
            ? "7 · 8; 56\n3/4 + 1/8; 7/8 | 0,875; Brüche"
            : "Hund; dog|hound; Nomen\ngehen; to go"}
          @input=${(e: Event) => {
            this._importText = wert(e);
            this._vorschau = null;
          }}
        ></textarea>
      </label>
      <div class="raster" style="margin-top: 12px">
        <label class="feld">
          ${t("spalte_lektion")}
          ${this._lektionAuswahl(
            this._importLektion,
            (neu) => {
              this._importLektion = neu;
            },
            t("spalte_lektion"),
          )}
        </label>
        <label class="feld">
          ${t("import_trennzeichen")}
          <input
            type="text"
            maxlength="5"
            .value=${this._importTrenner}
            @input=${(e: Event) => {
              this._importTrenner = wert(e);
              this._vorschau = null;
            }}
          />
        </label>
      </div>
      <label class="feld zeile">
        <input
          type="checkbox"
          .checked=${this._importGeprueft}
          @change=${(e: Event) => {
            this._importGeprueft = angehakt(e);
          }}
        />
        ${t("import_geprueft")}
      </label>
      ${vorschau
        ? html`
            <div class="liste" style="margin-top: 12px">
              ${vorschau.zeilen.map(
                (zeile) => html`
                  <label>
                    <span style="flex: 1">
                      ${zeile.frage
                        ? `${zeile.frage[a] ?? ""} → ${zeile.frage[b] ?? ""}`
                        : `${zeile.aufgabe ?? ""} → ${zeile.loesung ?? ""}`}
                      ${zeile.hinweis
                        ? html`<span class="klein"> (${zeile.hinweis})</span>`
                        : nothing}
                    </span>
                    <span class="marke ${zeile.vorhanden ? "" : "ok"}">
                      ${t(zeile.vorhanden ? "vorschau_vorhanden" : "vorschau_neu")}
                    </span>
                  </label>
                `,
              )}
            </div>
            ${vorschau.fehlerzeilen.length
              ? html`<p class="klein" style="color: var(--lh-error)">
                  ${t("vorschau_fehler", { zeilen: vorschau.fehlerzeilen.join(", ") })}
                </p>`
              : nothing}
          `
        : nothing}
      <div class="aktionen">
        <button @click=${this._schliesseDialog}>${t("abbrechen")}</button>
        <button ?disabled=${!this._importText.trim()} @click=${this._importVorschau}>
          ${t("vorschau")}
        </button>
        <button
          class="primaer"
          ?disabled=${!vorschau || neu === 0 || this._beschaeftigt}
          @click=${this._importUebernehmen}
        >
          ${t("uebernehmen")} ${vorschau ? `(${neu})` : ""}
        </button>
      </div>
    `;
  }

  private _lektionDialog(): TemplateResult {
    const t = this._t;
    const lektionen = this._fach?.lektionen ?? [];
    const anzahl = (name: string): number =>
      this._aufgaben.filter((aufgabe) => aufgabe.lektion === name).length;
    return html`
      <h2>${t("lektion_titel")}</h2>
      <p class="klein">${t("lektion_hilfe")}</p>
      <div class="leiste">
        <label class="feld" style="flex: 1">
          ${t("lektion_name")}
          <input
            id="lektion-name"
            type="text"
            maxlength="100"
            .value=${this._lektionName}
            @input=${(e: Event) => {
              this._lektionName = wert(e);
            }}
            @keydown=${(e: KeyboardEvent) => {
              if (e.key === "Enter") {
                void this._lektionAnlegen();
              }
            }}
          />
        </label>
        <button
          class="primaer"
          style="align-self: flex-end"
          ?disabled=${!this._lektionName.trim()}
          @click=${this._lektionAnlegen}
        >
          ${t("hinzufuegen")}
        </button>
      </div>
      ${lektionen.length === 0
        ? html`<div class="leer">${t("lektion_keine")}</div>`
        : html`<div class="liste">
            ${lektionen.map((name) => {
              const n = anzahl(name);
              return html`
                <div class="eintrag">
                  <span style="flex: 1">${name}</span>
                  <span class="klein">${t("lektion_anzahl", { n })}</span>
                  <button
                    class="icon"
                    title=${n > 0 ? t("lektion_loeschen_hinweis") : t("loeschen")}
                    aria-label=${`${t("loeschen")}: ${name}`}
                    ?disabled=${n > 0}
                    @click=${() => this._lektionLoeschen(name)}
                  >
                    <ha-icon icon="mdi:delete"></ha-icon>
                  </button>
                </div>
              `;
            })}
          </div>`}
      <div class="aktionen">
        <button class="primaer" @click=${this._schliesseDialog}>
          ${t("schliessen")}
        </button>
      </div>
    `;
  }

  private _statistikSchalter(): TemplateResult {
    return html`
      <label class="feld zeile">
        <input
          type="checkbox"
          .checked=${this._mitStatistik}
          @change=${(e: Event) => {
            this._mitStatistik = angehakt(e);
          }}
        />
        ${this._t("mit_statistik")}
      </label>
    `;
  }

  private _exportDialog(): TemplateResult {
    const t = this._t;
    return html`
      <h2>${t("export_titel")}</h2>
      ${this._statistikSchalter()}
      <div class="aktionen">
        <button @click=${this._schliesseDialog}>${t("abbrechen")}</button>
        <button class="primaer" @click=${this._exportiere}>${t("herunterladen")}</button>
      </div>
    `;
  }

  private _importJsonDialog(): TemplateResult {
    const t = this._t;
    const aufgaben = this._jsonDaten?.["aufgaben"];
    const anzahl = Array.isArray(aufgaben) ? aufgaben.length : 0;
    return html`
      <h2>${t("import_json_titel")}</h2>
      <p>${t("arbeit_umfang", { n: anzahl })}</p>
      <p class="klein">${t("import_json_hilfe")}</p>
      <label class="feld" style="margin-bottom: 12px">
        ${t("import_json_lektion")}
        <select
          id="json-lektion"
          .value=${this._jsonLektion}
          @change=${(e: Event) => {
            this._jsonLektion = wert(e);
          }}
        >
          <option value="" ?selected=${this._jsonLektion === ""}>
            ${t("import_json_aus_datei")}
          </option>
          ${(this._fach?.lektionen ?? []).map(
            (lektion) =>
              html`<option value=${lektion} ?selected=${lektion === this._jsonLektion}>
                ${lektion}
              </option>`,
          )}
        </select>
        <span>${t("import_json_lektion_hilfe")}</span>
      </label>
      ${this._statistikSchalter()}
      <div class="aktionen">
        <button @click=${this._schliesseDialog}>${t("abbrechen")}</button>
        <button
          class="primaer"
          ?disabled=${this._beschaeftigt}
          @click=${this._importiereJson}
        >
          ${t("uebernehmen")}
        </button>
      </div>
    `;
  }

  private _arbeitDialog(): TemplateResult {
    const t = this._t;
    const arbeit = this._arbeit;
    const fach = this._fach;
    if (!arbeit || !fach) {
      return html``;
    }
    const [a = "", b = ""] = fach.sprachen;
    const umfang =
      arbeit.modus === "alle"
        ? this._aufgaben.length
        : (this._arbeitUmfang(arbeit) ?? this._aufgaben.length);
    const zahl = (
      feld: "abfragen" | "start",
      label: string,
      max: number,
    ): TemplateResult => html`
      <label class="feld">
        ${label}
        <input
          type="number"
          min="1"
          max=${max}
          .value=${String(arbeit[feld])}
          @input=${(e: Event) => this._setzeArbeit(feld, Number(wert(e)) || 1)}
        />
      </label>
    `;
    const ohneThema = !arbeit.thema.trim();
    const fehlt =
      ohneThema && !arbeit.datum
        ? "arbeit_fehlt_beides"
        : ohneThema
          ? "arbeit_fehlt_thema"
          : !arbeit.datum
            ? "arbeit_fehlt_datum"
            : null;
    return html`
      <h2>${t(arbeit.id ? "arbeit_titel_bearbeiten" : "arbeit_titel_neu")}</h2>
      <div class="raster">
        <label class="feld">
          ${t("thema")} *
          <input
            type="text"
            required
            maxlength="200"
            .value=${arbeit.thema}
            @input=${(e: Event) => this._setzeArbeit("thema", wert(e))}
          />
        </label>
        <label class="feld">
          ${t("datum")} *
          <input
            type="date"
            required
            .value=${arbeit.datum}
            @change=${(e: Event) => this._setzeArbeit("datum", wert(e))}
          />
        </label>
        <label class="feld">
          ${t("art")}
          <select
            .value=${arbeit.art}
            @change=${(e: Event) =>
              this._setzeArbeit("art", wert(e) === "hue" ? "hue" : "arbeit")}
          >
            <option value="arbeit" ?selected=${arbeit.art === "arbeit"}>
              ${t("art_arbeit")}
            </option>
            <option value="hue" ?selected=${arbeit.art === "hue"}>
              ${t("art_hue")}
            </option>
          </select>
        </label>
        ${zahl("abfragen", t("abfragen_pro_tag"), 24)}
        ${zahl("start", t("start_tage_vorher"), 90)}
        <label class="feld">
          ${t("antwortfrist")}
          <input
            type="number"
            min="1"
            max="1440"
            placeholder=${t("antwortfrist_leer")}
            .value=${arbeit.frist === null ? "" : String(arbeit.frist)}
            @input=${(e: Event) => {
              const zahlwert = Math.round(Number(wert(e)));
              this._setzeArbeit(
                "frist",
                zahlwert >= 1 ? Math.min(zahlwert, 1440) : null,
              );
            }}
          />
          <span class="klein">${t("antwortfrist_hinweis")}</span>
        </label>
      </div>
      <label class="feld zeile" style="margin-bottom: 12px">
        <input
          type="checkbox"
          .checked=${arbeit.intensivierung}
          @change=${(e: Event) => this._setzeArbeit("intensivierung", angehakt(e))}
        />
        ${t("intensivierung")}
      </label>

      <fieldset>
        <legend>${t("sim_plan")}</legend>
        <p class="klein" style="margin-top: 0">${t("sim_plan_hilfe")}</p>
        <div class="raster">
          <label class="feld">
            ${t("sim_plan_um")}
            <input
              type="datetime-local"
              .value=${arbeit.simUm}
              @change=${(e: Event) => this._setzeArbeit("simUm", wert(e))}
            />
          </label>
          <label class="feld">
            ${t("sim_anzahl")}
            <input
              type="number"
              min="1"
              max=${MAX_SIM_AUFGABEN}
              .value=${String(arbeit.simAnzahl)}
              @input=${(e: Event) =>
                this._setzeArbeit(
                  "simAnzahl",
                  Math.max(1, Math.min(Math.round(Number(wert(e))) || 1, MAX_SIM_AUFGABEN)),
                )}
            />
          </label>
        </div>
        ${arbeit.simUm
          ? html`<button
              style="margin-top: 8px"
              @click=${() => this._setzeArbeit("simUm", "")}
            >
              ${t("sim_plan_entfernen")}
            </button>`
          : nothing}
      </fieldset>

      <fieldset>
        <legend>
          ${t("aufgaben_der_arbeit")} – ${t("arbeit_umfang", { n: umfang })}
        </legend>
        <div class="chips" style="margin-bottom: 10px">
          ${(["alle", "auswahl"] as const).map(
            (modus) => html`
              <label class="feld zeile">
                <input
                  type="radio"
                  name="modus"
                  .checked=${arbeit.modus === modus}
                  @change=${() => this._setzeArbeit("modus", modus)}
                />
                ${t(modus === "alle" ? "auswahl_alle" : "auswahl_gezielt")}
              </label>
            `,
          )}
        </div>
        ${arbeit.modus === "auswahl"
          ? html`
              ${fach.lektionen.length
                ? html`
                    <div class="klein">${t("schnell_lektionen")}</div>
                    <div class="chips" style="margin: 6px 0 12px">
                      ${fach.lektionen.map(
                        (lektion) => html`
                          <label class="feld zeile">
                            <input
                              type="checkbox"
                              .checked=${arbeit.lektionen.has(lektion)}
                              @change=${(e: Event) =>
                                this._arbeitMenge("lektionen", lektion, angehakt(e))}
                            />
                            ${lektion}
                          </label>
                        `,
                      )}
                    </div>
                  `
                : nothing}
              <div class="leiste">
                <label class="feld" style="flex: 1; max-width: 220px">
                  ${t("schnell_seit")}
                  <input
                    type="date"
                    .value=${arbeit.seit}
                    @change=${(e: Event) => this._setzeArbeit("seit", wert(e))}
                  />
                </label>
                <button ?disabled=${!arbeit.seit} @click=${this._arbeitSeit}>
                  ${t("hinzufuegen")}
                </button>
              </div>
              <div class="leiste">
                <label class="feld" style="flex: 1; max-width: 220px">
                  ${t("schnell_seiten")}
                  <input
                    type="number"
                    min="1"
                    .value=${arbeit.seiteVon}
                    @input=${(e: Event) => this._setzeArbeit("seiteVon", wert(e))}
                  />
                </label>
                <label class="feld" style="flex: 1; max-width: 220px">
                  ${t("schnell_seiten_bis")}
                  <input
                    type="number"
                    min="1"
                    .value=${arbeit.seiteBis}
                    @input=${(e: Event) => this._setzeArbeit("seiteBis", wert(e))}
                  />
                </label>
                <button
                  ?disabled=${!arbeit.seiteVon && !arbeit.seiteBis}
                  @click=${this._arbeitSeiten}
                >
                  ${t("hinzufuegen")}
                </button>
                <span class="abstand"></span>
                <button
                  ?disabled=${arbeit.ids.size === 0}
                  @click=${() => this._setzeArbeit("ids", new Set())}
                >
                  ${t("auswahl_leeren")}
                </button>
              </div>
              <div class="klein">${t("einzelne_aufgaben")} (${arbeit.ids.size})</div>
              <div class="liste" style="margin-top: 6px">
                ${this._aufgaben.map((aufgabe) => {
                  const perLektion =
                    aufgabe.lektion !== null && arbeit.lektionen.has(aufgabe.lektion);
                  return html`
                    <label>
                      <input
                        type="checkbox"
                        .checked=${perLektion || arbeit.ids.has(aufgabe.id)}
                        ?disabled=${perLektion}
                        @change=${(e: Event) =>
                          this._arbeitMenge("ids", aufgabe.id, angehakt(e))}
                      />
                      <span style="flex: 1">
                        ${kurztext(aufgabe, a, b)}
                      </span>
                      <span class="klein">${aufgabe.lektion ?? ""}</span>
                    </label>
                  `;
                })}
              </div>
            `
          : nothing}
      </fieldset>
      <div class="aktionen">
        ${fehlt
          ? html`<span class="klein" role="status" style="margin-right: auto">
              ${t(fehlt)}
            </span>`
          : nothing}
        <button @click=${this._schliesseDialog}>${t("abbrechen")}</button>
        <button
          class="primaer"
          ?disabled=${this._beschaeftigt || fehlt !== null}
          @click=${this._speichereArbeit}
        >
          ${t("speichern")}
        </button>
      </div>
    `;
  }
}

// A tab that stays open across an update loads the new bundle as well; the
// elements of the first one stay in use until the page is reloaded.
if (!customElements.get("learnbuddy-panel")) {
  customElements.define("learnbuddy-panel", LearnBuddyPanel);
}

declare global {
  interface HTMLElementTagNameMap {
    "learnbuddy-panel": LearnBuddyPanel;
  }
}
