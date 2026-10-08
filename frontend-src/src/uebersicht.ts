import { LitElement, css, html, nothing, type PropertyValues, type TemplateResult } from "lit";
import { property, state } from "lit/decorators.js";

import { Api } from "./api";
import "./fortschritt";
import { fehlertext, sprachname, uebersetzer, type Uebersetzer } from "./i18n";
import { styles } from "./styles";
import type {
  Dashboard,
  DashboardArbeit,
  DashboardFach,
  Hass,
  Vorschlag,
} from "./types";

/**
 * Ordinal one-hue ramps for the five Leitner boxes (box 1 -> box 5). Every
 * step keeps at least 2:1 contrast against its surface; on dark surfaces the
 * ramp runs towards lighter steps so that "more mastered" stays "more ink".
 */
const BOX_FARBEN_HELL = ["#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#104281"];
const BOX_FARBEN_DUNKEL = ["#184f95", "#256abf", "#3987e5", "#6da7ec", "#b7d3f6"];

const AKTUALISIEREN_MS = 60_000;
// Most questions that can be asked in a row (as in the integration)
const MAX_ABFRAGE = 20;
const ABFRAGE_STANDARD = 5;

/** What the dialog "Ask now" is about to send. */
interface Abfrage {
  fachId: string | null;
  lektionen: Set<string>;
  anzahl: number;
}
const EVENTS = ["learnbuddy_question_sent", "learnbuddy_answer_evaluated"];

/** Overview of one child: state, statistics, subjects and upcoming exams. */
export class LhUebersicht extends LitElement {
  static styles = [
    styles,
    css`
      :host {
        min-height: 0;
        background: none;
      }
      .raster {
        display: grid;
        gap: 16px;
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }
      .raster > .breit {
        grid-column: 1 / -1;
      }
      :host([narrow]) .raster {
        grid-template-columns: minmax(0, 1fr);
      }
      .card {
        margin: 0;
      }
      h2 {
        font-size: 16px;
        font-weight: 500;
        margin: 0 0 12px;
      }
      .status {
        display: flex;
        flex-wrap: wrap;
        gap: 16px 24px;
        align-items: center;
      }
      .status .zustand {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 18px;
        font-weight: 500;
      }
      .status .zustand ha-icon {
        --mdc-icon-size: 28px;
      }
      .status .zustand.gut ha-icon {
        color: #0ca30c;
      }
      .status .zustand.aus ha-icon {
        color: var(--lh-muted);
      }
      .status .fakten {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
        gap: 8px 20px;
        flex: 1;
        min-width: 240px;
      }
      .fakt .wert {
        font-size: 14px;
      }
      .status .knoepfe {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
      }
      .kacheln {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
        gap: 12px;
      }
      .kachel {
        background: var(--lh-card);
        border: 1px solid var(--lh-border);
        border-radius: var(--lh-radius);
        padding: 14px 16px;
      }
      .kachel .zahl {
        font-size: 30px;
        line-height: 1.15;
        font-weight: 500;
        font-variant-numeric: tabular-nums;
      }
      .kachel .name {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 13px;
        color: var(--lh-muted);
      }
      .kachel .name ha-icon {
        --mdc-icon-size: 16px;
      }
      .balken {
        display: flex;
        gap: 2px;
        height: 12px;
        border-radius: 4px;
        overflow: hidden;
        background: rgba(128, 128, 128, 0.15);
      }
      .balken.gross {
        height: 22px;
      }
      .balken span {
        min-width: 3px;
      }
      .legende {
        display: flex;
        flex-wrap: wrap;
        gap: 6px 16px;
        margin-top: 10px;
        font-size: 12px;
        color: var(--lh-muted);
      }
      .legende i {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 2px;
        margin-right: 5px;
      }
      .legende b {
        font-weight: 500;
        color: var(--primary-text-color);
      }
      .zeile {
        display: flex;
        gap: 12px;
        align-items: center;
        padding: 10px 0;
        border-top: 1px solid var(--lh-border);
      }
      .zeile:first-of-type {
        border-top: none;
        padding-top: 0;
      }
      h2.abstand {
        margin-top: 20px;
      }
      .kalenderfuss {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        align-items: center;
        margin-top: 10px;
      }
      .kalenderfuss span {
        flex: 1 1 160px;
      }
      .warnung {
        color: var(--lh-error);
        margin-bottom: 6px;
      }
      .zeile .mitte {
        flex: 1;
        min-width: 0;
      }
      .zeile .titel {
        font-size: 15px;
        overflow-wrap: anywhere;
      }
      .countdown {
        flex: none;
        width: 76px;
        text-align: center;
        border: 1px solid var(--lh-border);
        border-radius: 10px;
        padding: 6px 4px;
      }
      .countdown .tage {
        font-size: 15px;
        font-weight: 500;
      }
      .countdown.bald {
        border-color: var(--lh-accent);
      }
      .mini {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-top: 6px;
      }
      .mini .balken {
        flex: 1;
        max-width: 220px;
      }
      .fachknoepfe {
        display: flex;
        gap: 6px;
        flex-wrap: wrap;
        justify-content: flex-end;
      }
      .auswahl {
        display: grid;
        gap: 8px;
      }
      .auswahl button {
        text-align: left;
        border-radius: 10px;
        padding: 12px 14px;
        white-space: normal;
      }
    `,
  ];

  @property({ attribute: false }) hass?: Hass;

  @property({ type: Boolean, reflect: true }) narrow = false;

  @property() kindId = "";

  @state() private _daten?: Dashboard;

  @state() private _fehler = "";
  @state() private _kalenderLaeuft = false;

  @state() private _erfolg = "";

  @state() private _abfrage: Abfrage | null = null;

  @state() private _beschaeftigt = false;

  private _timer?: number;

  private _abos: Promise<() => void>[] = [];

  private get _t(): Uebersetzer {
    return uebersetzer(this.hass?.language ?? "en");
  }

  private get _api(): Api {
    return new Api(this.hass as Hass);
  }

  connectedCallback(): void {
    super.connectedCallback();
    this._timer = window.setInterval(() => void this._lade(), AKTUALISIEREN_MS);
  }

  private _abonniere(): void {
    const verbindung = this.hass?.connection;
    if (!verbindung || this._abos.length) {
      return;
    }
    // Refresh as soon as a question is sent or an answer is evaluated
    this._abos = EVENTS.map((typ) =>
      verbindung.subscribeEvents(() => void this._lade(), typ),
    );
  }

  disconnectedCallback(): void {
    super.disconnectedCallback();
    window.clearInterval(this._timer);
    for (const abo of this._abos) {
      void abo.then((beenden) => beenden()).catch(() => undefined);
    }
    this._abos = [];
  }

  protected willUpdate(geaendert: PropertyValues): void {
    this._abonniere();
    if (geaendert.has("kindId")) {
      this._daten = undefined;
      this._fehler = "";
      this._erfolg = "";
      void this._lade();
    }
  }

  private async _lade(): Promise<void> {
    if (!this.hass || !this.kindId) {
      return;
    }
    const kindId = this.kindId;
    try {
      const daten = await this._api.dashboard(kindId);
      if (kindId === this.kindId) {
        this._daten = daten;
        this._fehler = "";
      }
    } catch (fehler) {
      this._fehler = fehlertext(this._t, fehler);
    }
  }

  private async _frage(
    fachId: string | null,
    lektionen: string[] = [],
    anzahl = 1,
  ): Promise<void> {
    this._abfrage = null;
    this._beschaeftigt = true;
    this._erfolg = "";
    try {
      await this._api.frageStellen(this.kindId, fachId, lektionen, anzahl);
      this._fehler = "";
      this._erfolg = this._t(anzahl > 1 ? "fragen_gesendet" : "frage_gesendet");
    } catch (fehler) {
      this._fehler = fehlertext(this._t, fehler);
    } finally {
      this._beschaeftigt = false;
      await this._lade();
    }
  }

  /** Open the dialog that asks what and how much to ask. */
  private _jetztFragen(fachId: string | null = null): void {
    const faecher = this._daten?.faecher ?? [];
    const fach =
      faecher.find((f) => f.id === fachId) ?? (faecher.length === 1 ? faecher[0] : undefined);
    this._abfrage = {
      fachId: fach?.id ?? null,
      lektionen: new Set((fach?.lektionsliste ?? []).map((l) => l.name)),
      anzahl: this._abfrage?.anzahl ?? ABFRAGE_STANDARD,
    };
  }

  private async _brichFrageAb(): Promise<void> {
    if (!window.confirm(this._t("frage_abbrechen_frage"))) {
      return;
    }
    try {
      await this._api.frageAbbrechen(this.kindId);
      this._fehler = "";
    } catch (fehler) {
      this._fehler = fehlertext(this._t, fehler);
    }
    await this._lade();
  }

  private async _brichSimulationAb(): Promise<void> {
    if (!window.confirm(this._t("sim_abbrechen_frage"))) {
      return;
    }
    try {
      await this._api.simulationAbbrechen(this.kindId);
      this._fehler = "";
    } catch (fehler) {
      this._fehler = fehlertext(this._t, fehler);
    }
    await this._lade();
  }

  private async _setzeAktiv(aktiv: boolean): Promise<void> {
    try {
      await this._api.setzeAktiv(this.kindId, aktiv);
      this._fehler = "";
    } catch (fehler) {
      this._fehler = fehlertext(this._t, fehler);
    }
    await this._lade();
  }

  private _oeffne(ziel: "aufgaben" | "arbeiten", fachId: string): void {
    this.dispatchEvent(
      new CustomEvent("lh-oeffnen", { detail: { ziel, fachId } }),
    );
  }

  // ----------------------------------------------------------- formatting

  private _zeit(iso: string | null): string {
    if (!iso) {
      return "";
    }
    const datum = new Date(iso);
    const sprache = this.hass?.language ?? "en";
    const heute = new Date().toDateString() === datum.toDateString();
    return datum.toLocaleString(sprache, {
      ...(heute ? {} : { weekday: "short", day: "2-digit", month: "2-digit" }),
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  private _uhr(iso: string): string {
    return new Date(iso).toLocaleTimeString(this.hass?.language ?? "en", {
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  private _datum(iso: string): string {
    return new Date(`${iso}T00:00:00`).toLocaleDateString(
      this.hass?.language ?? "en",
      { weekday: "short", day: "2-digit", month: "2-digit" },
    );
  }

  private _tage(tage: number): string {
    if (tage <= 0) {
      return this._t("heute");
    }
    return tage === 1 ? this._t("morgen") : this._t("in_tagen", { n: tage });
  }

  private _balken(boxen: number[], gross = false): TemplateResult {
    const farben = this.hass?.themes?.darkMode ? BOX_FARBEN_DUNKEL : BOX_FARBEN_HELL;
    const summe = boxen.reduce((a, b) => a + b, 0);
    const t = this._t;
    const text = boxen
      .map((n, index) => `${t("box", { n: index + 1 })}: ${n}`)
      .join(", ");
    return html`
      <div class="balken ${gross ? "gross" : ""}" role="img" aria-label=${text}>
        ${summe === 0
          ? nothing
          : boxen.map((n, index) =>
              n === 0
                ? nothing
                : html`<span
                    style="flex: ${n}; background: ${farben[index] ?? ""}"
                    title="${t("box", { n: index + 1 })}: ${t("karten", { n })}"
                  ></span>`,
            )}
      </div>
    `;
  }

  private _legende(boxen: number[]): TemplateResult {
    const farben = this.hass?.themes?.darkMode ? BOX_FARBEN_DUNKEL : BOX_FARBEN_HELL;
    return html`
      <div class="legende">
        ${boxen.map(
          (n, index) => html`
            <span>
              <i style="background: ${farben[index] ?? ""}"></i>${this._t("box", {
                n: index + 1,
              })}:
              <b>${n}</b>
            </span>
          `,
        )}
      </div>
    `;
  }

  // -------------------------------------------------------------- render

  protected render(): TemplateResult {
    const t = this._t;
    const daten = this._daten;
    return html`
      ${this._fehler
        ? html`<div class="meldung fehler" role="alert">
            <span>${this._fehler}</span>
          </div>`
        : nothing}
      ${this._erfolg
        ? html`<div class="meldung" role="status">
            <span>${this._erfolg}</span>
            <button
              class="icon"
              aria-label=${t("schliessen")}
              @click=${() => {
                this._erfolg = "";
              }}
            >
              <ha-icon icon="mdi:close"></ha-icon>
            </button>
          </div>`
        : nothing}
      ${daten
        ? html`
            <div class="raster">
              <div class="card breit">${this._status(daten)}</div>
              <div class="kacheln breit">${this._kacheln(daten)}</div>
              <div class="card">${this._arbeiten(daten)}</div>
              <div class="card">${this._faecher(daten)}</div>
              <div class="card">${this._lernstand(daten)}</div>
              <div class="card">${this._schwierig(daten)}</div>
            </div>
            ${daten.verlauf
              ? html`<lh-fortschritt
                  .hass=${this.hass}
                  .narrow=${this.narrow}
                  .kindId=${this.kindId}
                  .wochenreport=${daten.wochenreport ?? false}
                  .stand=${daten}
                ></lh-fortschritt>`
              : nothing}
          `
        : this._fehler
          ? nothing
          : html`<div class="leer">${t("laden")}</div>`}
      ${this._abfrage && daten ? this._abfrageDialog(daten, this._abfrage) : nothing}
    `;
  }

  private _status(daten: Dashboard): TemplateResult {
    const t = this._t;
    const zustand = daten.zustand;
    const offen = zustand.offene_frage;
    const titel = zustand.pausiert
      ? zustand.pausiert_bis
        ? t("status_pausiert_bis", { zeit: this._zeit(zustand.pausiert_bis) })
        : t("status_pausiert")
      : t("status_aktiv");
    const fakt = (name: string, wert: string): TemplateResult => html`
      <div class="fakt">
        <div class="klein">${name}</div>
        <div class="wert">${wert}</div>
      </div>
    `;
    return html`
      <div class="status">
        <div class="zustand ${zustand.pausiert ? "aus" : "gut"}">
          <ha-icon
            icon=${zustand.pausiert ? "mdi:pause-circle" : "mdi:check-circle"}
          ></ha-icon>
          ${titel}
        </div>
        <div class="fakten">
          ${zustand.simulation
            ? fakt(
                t("sim_laeuft"),
                t("sim_laeuft_text", {
                  nr: Math.min(zustand.simulation.nummer, zustand.simulation.anzahl),
                  n: zustand.simulation.anzahl,
                }),
              )
            : nothing}
          ${fakt(
            t("offene_frage"),
            offen
              ? t("offene_frage_text", {
                  fach: offen.fach,
                  von: this._uhr(offen.gestellt_um),
                  bis: this._uhr(offen.timeout_um),
                })
              : t("keine_offene_frage"),
          )}
          ${fakt(
            t("naechste_abfrage"),
            offen && !zustand.pausiert
              ? t("nach_offener_frage")
              : zustand.naechste_abfrage && !zustand.pausiert
                ? this._zeit(zustand.naechste_abfrage)
                : t("keine_geplant"),
          )}
          ${fakt(
            t("letzte_frage"),
            zustand.letzte_frage_um
              ? this._zeit(zustand.letzte_frage_um)
              : t("noch_nie"),
          )}
        </div>
        <div class="knoepfe">
          <button
            class="primaer"
            ?disabled=${this._beschaeftigt ||
            daten.faecher.length === 0 ||
            Boolean(zustand.simulation)}
            @click=${() => this._jetztFragen()}
          >
            ${t("jetzt_fragen")}
          </button>
          <button @click=${() => this._setzeAktiv(!zustand.aktiv || zustand.pausiert)}>
            ${t(zustand.pausiert ? "fortsetzen" : "pausieren")}
          </button>
          ${offen && !zustand.simulation
            ? html`<button class="gefahr" @click=${this._brichFrageAb}>
                ${t("frage_abbrechen")}
              </button>`
            : nothing}
          ${zustand.simulation
            ? html`<button class="gefahr" @click=${this._brichSimulationAb}>
                ${t("sim_abbrechen")}
              </button>`
            : nothing}
        </div>
      </div>
    `;
  }

  private _kacheln(daten: Dashboard): TemplateResult {
    const t = this._t;
    const s = daten.statistik;
    const kachel = (name: string, zahl: string, icon: string): TemplateResult => html`
      <div class="kachel">
        <div class="zahl">${zahl}</div>
        <div class="name"><ha-icon icon=${icon}></ha-icon>${name}</div>
      </div>
    `;
    return html`
      ${kachel(t("kz_gefragt"), String(s.gefragt), "mdi:chat-question")}
      ${kachel(t("kz_richtig"), String(s.richtig), "mdi:check")}
      ${kachel(t("kz_falsch"), String(s.falsch), "mdi:close")}
      ${s.teilweise
        ? kachel(t("kz_teilweise"), String(s.teilweise), "mdi:circle-half-full")
        : nothing}
      ${kachel(t("kz_unbeantwortet"), String(s.unbeantwortet), "mdi:timer-sand")}
      ${kachel(
        t("kz_trefferquote"),
        s.trefferquote === null ? "–" : `${Math.round(s.trefferquote)} %`,
        "mdi:bullseye-arrow",
      )}
      ${kachel(t("kz_aufgaben"), String(s.aufgaben), "mdi:cards-outline")}
    `;
  }

  private _sicher(wert: number | null): TemplateResult | typeof nothing {
    return wert === null
      ? nothing
      : html`<span class="klein" title=${this._t("sicher_hinweis")}>
          ${this._t("sicher", { n: wert })}
        </span>`;
  }

  private _arbeiten(daten: Dashboard): TemplateResult {
    const t = this._t;
    const zeile = (arbeit: DashboardArbeit): TemplateResult => html`
      <div class="zeile">
        <div class="countdown ${arbeit.tage_bis <= 2 ? "bald" : ""}">
          <div class="tage">${this._tage(arbeit.tage_bis)}</div>
          <div class="klein">${this._datum(arbeit.datum)}</div>
        </div>
        <div class="mitte">
          <div class="titel">
            ${arbeit.fach}: ${arbeit.thema}
            <span class="marke">
              ${t(arbeit.art === "hue" ? "art_hue" : "art_arbeit")}
            </span>
          </div>
          <div class="klein">
            ${t("arbeit_umfang", { n: arbeit.aufgaben })} ·
            ${t("heute_abfragen", { n: arbeit.abfragen_heute })}
          </div>
          <div class="mini">${this._balken(arbeit.boxen)} ${this._sicher(arbeit.sicher)}</div>
        </div>
        <button
          class="icon"
          title=${t("arbeiten_oeffnen")}
          aria-label=${t("arbeiten_oeffnen")}
          @click=${() => this._oeffne("arbeiten", arbeit.fach_id)}
        >
          <ha-icon icon="mdi:chevron-right"></ha-icon>
        </button>
      </div>
    `;
    return html`
      <h2>${t("anstehend")}</h2>
      ${daten.arbeiten.length
        ? daten.arbeiten.map(zeile)
        : html`<div class="leer">${t("keine_anstehend")}</div>`}
      ${this._vorschlaege(daten)}
    `;
  }

  /** Exam dates of the calendar of the child that are not entered yet. */
  private _vorschlaege(daten: Dashboard): TemplateResult | typeof nothing {
    const kalender = daten.kalender;
    if (!kalender) {
      return nothing;
    }
    const t = this._t;
    const liste = daten.vorschlaege ?? [];
    const zeile = (vorschlag: Vorschlag): TemplateResult => html`
      <div class="zeile">
        <div class="countdown">
          <div class="klein">${this._datum(vorschlag.datum)}</div>
        </div>
        <div class="mitte">
          <div class="titel">
            ${vorschlag.text}
            <span class="marke">
              ${t(vorschlag.art === "hue" ? "art_hue" : "art_arbeit")}
            </span>
          </div>
          ${vorschlag.gleicher_tag.length
            ? html`<div class="klein">
                ${t("vorschlag_gleicher_tag", {
                  arbeiten: vorschlag.gleicher_tag.join(", "),
                })}
              </div>`
            : nothing}
        </div>
        <button class="primaer" @click=${() => this._trageEin(vorschlag)}>
          ${t("vorschlag_eintragen")}
        </button>
        <button @click=${() => this._ignoriere(vorschlag)}>
          ${t("vorschlag_ignorieren")}
        </button>
      </div>
    `;
    return html`
      <h2 class="abstand">${t("vorschlaege")}</h2>
      ${kalender.fehler
        ? html`<div class="klein warnung" role="status">${t("kalender_fehler")}</div>`
        : nothing}
      ${liste.length
        ? liste.map(zeile)
        : html`<div class="leer">${t("keine_vorschlaege")}</div>`}
      <div class="kalenderfuss">
        <span class="klein">
          ${kalender.geprueft_um
            ? t("kalender_geprueft", { zeit: this._zeit(kalender.geprueft_um) })
            : t("kalender_nie")}
        </span>
        <button ?disabled=${this._kalenderLaeuft} @click=${this._pruefeKalender}>
          ${t("kalender_pruefen")}
        </button>
        ${kalender.ignoriert
          ? html`<button @click=${this._zeigeIgnorierte}>
              ${t("kalender_ignorierte", { n: kalender.ignoriert })}
            </button>`
          : nothing}
      </div>
    `;
  }

  private _trageEin(vorschlag: Vorschlag): void {
    this.dispatchEvent(new CustomEvent("lh-vorschlag", { detail: { vorschlag } }));
  }

  private async _ignoriere(vorschlag: Vorschlag): Promise<void> {
    try {
      await this._api.kalenderIgnorieren(this.kindId, vorschlag.uid);
      this._fehler = "";
    } catch (fehler) {
      this._fehler = fehlertext(this._t, fehler);
    }
    await this._lade();
  }

  private async _zeigeIgnorierte(): Promise<void> {
    try {
      await this._api.kalenderWiederherstellen(this.kindId);
      this._fehler = "";
    } catch (fehler) {
      this._fehler = fehlertext(this._t, fehler);
    }
    await this._lade();
  }

  private async _pruefeKalender(): Promise<void> {
    this._kalenderLaeuft = true;
    try {
      await this._api.kalenderPruefen(this.kindId);
      this._fehler = "";
    } catch (fehler) {
      this._fehler = fehlertext(this._t, fehler);
    } finally {
      this._kalenderLaeuft = false;
    }
    await this._lade();
  }

  private _faecher(daten: Dashboard): TemplateResult {
    const t = this._t;
    const sprache = this.hass?.language ?? "en";
    const zeile = (fach: DashboardFach): TemplateResult => html`
      <div class="zeile">
        <div class="mitte">
          <div class="titel">
            ${fach.name}
            <span class="klein">
              ${fach.typ === "mathe"
                ? t("fachart_mathe")
                : fach.typ === "sach"
                  ? t("fachart_sach")
                  : fach.sprachen.map((code) => sprachname(sprache, code)).join(" ↔ ")}
            </span>
          </div>
          <div class="klein">
            ${t("fach_aufgaben", { n: fach.aufgaben, l: fach.lektionen })}
            ${fach.ungeprueft ? html` · ${t("ungeprueft", { n: fach.ungeprueft })}` : nothing}
            ${fach.trefferquote === null
              ? nothing
              : html` · ${t("kz_trefferquote")} ${Math.round(fach.trefferquote)} %`}
          </div>
          <div class="mini">${this._balken(fach.boxen)} ${this._sicher(fach.sicher)}</div>
        </div>
        <div class="fachknoepfe">
          <button
            ?disabled=${this._beschaeftigt || fach.aufgaben === 0}
            @click=${() => this._jetztFragen(fach.id)}
          >
            ${t("jetzt_fragen_kurz")}
          </button>
          <button @click=${() => this._oeffne("aufgaben", fach.id)}>
            ${t("aufgaben_oeffnen")}
          </button>
        </div>
      </div>
    `;
    return html`
      <h2>${t("faecher_titel")}</h2>
      ${daten.faecher.length
        ? daten.faecher.map(zeile)
        : html`<div class="leer">${t("keine_faecher")}</div>`}
    `;
  }

  private _lernstand(daten: Dashboard): TemplateResult {
    const t = this._t;
    const boxen = daten.statistik.boxen;
    const summe = boxen.reduce((a, b) => a + b, 0);
    return html`
      <h2>${t("lernstand")}</h2>
      ${summe === 0
        ? html`<div class="leer">${t("keine_karten")}</div>`
        : html`
            ${this._balken(boxen, true)} ${this._legende(boxen)}
            <p class="klein">${t("lernstand_hinweis")}</p>
          `}
    `;
  }

  private _schwierig(daten: Dashboard): TemplateResult {
    const t = this._t;
    return html`
      <h2>
        ${t(daten.faecher.some((f) => f.typ !== "vokabel") ? "schwierig_aufgaben" : "schwierig")}
      </h2>
      ${daten.schwierig.length
        ? daten.schwierig.map(
            (eintrag) => html`
              <div class="zeile">
                <div class="mitte">
                  <div class="titel">
                    ${eintrag.aufgabe ?? Object.values(eintrag.frage ?? {}).join(" – ")}
                  </div>
                  <div class="klein">
                    ${eintrag.fach} · ${t("fehler_mal", { n: eintrag.falsch })}
                  </div>
                </div>
                <span class="marke ${eintrag.fehlerquote >= 50 ? "warn" : ""}">
                  ${Math.round(eintrag.fehlerquote)} %
                </span>
              </div>
            `,
          )
        : html`<div class="leer">${t("keine_schwierig")}</div>`}
    `;
  }

  private _abfrageDialog(daten: Dashboard, abfrage: Abfrage): TemplateResult {
    const t = this._t;
    const schliessen = (): void => {
      this._abfrage = null;
    };
    const fach = daten.faecher.find((f) => f.id === abfrage.fachId) ?? null;
    const lektionen = fach?.lektionsliste ?? [];
    // All lessons ticked means the whole subject, also tasks without a lesson
    const alle = lektionen.every((l) => abfrage.lektionen.has(l.name));
    const umfang =
      fach === null
        ? daten.faecher.reduce((summe, f) => summe + f.aufgaben, 0)
        : alle
          ? fach.aufgaben
          : lektionen
              .filter((l) => abfrage.lektionen.has(l.name))
              .reduce((summe, l) => summe + l.aufgaben, 0);
    const setze = (teil: Partial<Abfrage>): void => {
      this._abfrage = { ...abfrage, ...teil };
    };
    const waehleFach = (id: string): void => {
      const neu = daten.faecher.find((f) => f.id === id);
      setze({
        fachId: neu ? neu.id : null,
        lektionen: new Set((neu?.lektionsliste ?? []).map((l) => l.name)),
      });
    };
    const schalte = (name: string, an: boolean): void => {
      const auswahl = new Set(abfrage.lektionen);
      if (an) {
        auswahl.add(name);
      } else {
        auswahl.delete(name);
      }
      setze({ lektionen: auswahl });
    };
    const senden = (): void => {
      const anzahl = Math.min(MAX_ABFRAGE, Math.max(1, Math.round(abfrage.anzahl) || 1));
      void this._frage(
        abfrage.fachId,
        fach === null || alle ? [] : [...abfrage.lektionen],
        anzahl,
      );
    };
    return html`
      <div
        class="overlay"
        @click=${(e: Event) => {
          if (e.target === e.currentTarget) {
            schliessen();
          }
        }}
      >
        <div class="dialog" role="dialog" aria-modal="true" style="width: min(440px, 100%)">
          <h2>${t("abfrage_titel")}</h2>
          <label class="feld">
            ${t("abfrage_fach")}
            <select
              .value=${abfrage.fachId ?? ""}
              @change=${(e: Event) => waehleFach((e.target as HTMLSelectElement).value)}
            >
              ${daten.faecher.length > 1
                ? html`<option value="" ?selected=${abfrage.fachId === null}>
                    ${t("egal_welches")}
                  </option>`
                : nothing}
              ${daten.faecher.map(
                (f) => html`
                  <option
                    value=${f.id}
                    ?selected=${f.id === abfrage.fachId}
                    ?disabled=${f.aufgaben === 0}
                  >
                    ${f.name} (${f.aufgaben})
                  </option>
                `,
              )}
            </select>
          </label>
          ${lektionen.length > 0
            ? html`
                <fieldset class="lektionswahl">
                  <legend>${t("abfrage_lektionen")}</legend>
                  ${lektionen.map(
                    (l) => html`
                      <label>
                        <input
                          type="checkbox"
                          .checked=${abfrage.lektionen.has(l.name)}
                          @change=${(e: Event) =>
                            schalte(l.name, (e.target as HTMLInputElement).checked)}
                        />
                        ${l.name}
                        <span class="klein">${t("arbeit_umfang", { n: l.aufgaben })}</span>
                      </label>
                    `,
                  )}
                  ${fach && fach.ohne_lektion > 0
                    ? html`<div class="klein">
                        ${t("abfrage_ohne_lektion", { n: fach.ohne_lektion })}
                      </div>`
                    : nothing}
                </fieldset>
              `
            : nothing}
          <label class="feld">
            ${t("abfrage_anzahl")}
            <input
              type="number"
              min="1"
              max=${MAX_ABFRAGE}
              .value=${String(abfrage.anzahl)}
              @input=${(e: Event) =>
                setze({ anzahl: Number((e.target as HTMLInputElement).value) })}
            />
          </label>
          <div class="klein">${t("abfrage_umfang", { n: umfang })}</div>
          <div class="aktionen">
            <button @click=${schliessen}>${t("abbrechen")}</button>
            <button
              class="primaer"
              ?disabled=${this._beschaeftigt || umfang === 0}
              @click=${senden}
            >
              ${t("abfrage_senden")}
            </button>
          </div>
        </div>
      </div>
    `;
  }
}
