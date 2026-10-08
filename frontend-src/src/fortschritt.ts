import { LitElement, css, html, nothing, svg, type PropertyValues, type TemplateResult } from "lit";
import { property, state } from "lit/decorators.js";

import { Api } from "./api";
import { fehlertext, uebersetzer, type Uebersetzer } from "./i18n";
import { styles } from "./styles";
import type {
  FehlerAufgabe,
  Fortschritt,
  Hass,
  SchwacheLektion,
  SimulationsEintrag,
  Tageszahlen,
  Wochenreport,
} from "./types";

type Ergebnis = "richtig" | "teilweise" | "falsch" | "unbeantwortet";

/**
 * Colours of the answer results, bottom to top of a stacked bar. Checked as a
 * set for both surfaces: neighbours stay apart with normal and with
 * colour-deficient vision. The table view is the relief for the steps below
 * 3:1 contrast on the light surface.
 */
const ERGEBNISSE: Ergebnis[] = ["richtig", "teilweise", "falsch", "unbeantwortet"];
const ERGEBNIS_HELL: Record<Ergebnis, string> = {
  richtig: "#2a78d6",
  teilweise: "#1baf7a",
  falsch: "#eb6834",
  unbeantwortet: "#4a3aa7",
};
const ERGEBNIS_DUNKEL: Record<Ergebnis, string> = {
  richtig: "#3987e5",
  teilweise: "#199e70",
  falsch: "#d95926",
  unbeantwortet: "#9085e9",
};
/** Subjects take these hues in fixed order; more subjects are not drawn. */
const FACH_HELL = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300"];
const FACH_DUNKEL = ["#3987e5", "#d95926", "#199e70", "#c98500", "#d55181", "#008300"];
const ZEITRAEUME = [7, 30, 90];

// Geometry of the charts in CSS pixels; the width follows the card
const HOEHE_BREIT = 200;
const HOEHE_SCHMAL = 170;
const LINKS = 38;
const RECHTS = 12;
const OBEN = 10;
const UNTEN = 24;
const MAX_BALKEN = 24;
const LUECKE = 2;

/** Drawing size of one chart. */
interface Mass {
  b: number;
  h: number;
}

interface Abschnitt {
  titel: string;
  zeilen: string[];
}

/** Round a maximum up to a pleasant axis end. */
function achsenende(wert: number): number {
  if (wert <= 4) {
    return 4;
  }
  const stufe = 10 ** Math.floor(Math.log10(wert));
  for (const faktor of [1, 2, 4, 5, 10]) {
    if (wert <= faktor * stufe) {
      return faktor * stufe;
    }
  }
  return 10 * stufe;
}

/** Progress over time and the weekly report of a child. */
export class LhFortschritt extends LitElement {
  static styles = [
    styles,
    css`
      :host {
        min-height: 0;
        background: none;
        margin-top: 16px;
      }
      .kopf {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        align-items: center;
        margin-bottom: 12px;
      }
      .kopf h2 {
        flex: 1 1 140px;
        margin: 0;
        font-size: 18px;
        font-weight: 500;
      }
      .wahl {
        display: inline-flex;
        gap: 4px;
      }
      .wahl button[aria-pressed="true"] {
        background: var(--lh-accent);
        border-color: var(--lh-accent);
        color: var(--text-primary-color, #fff);
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
      .card h3 {
        font-size: 16px;
        font-weight: 500;
        margin: 0 0 2px;
      }
      h4 {
        font-size: 14px;
        font-weight: 500;
        margin: 12px 0 4px;
      }
      .diagramm {
        position: relative;
        margin-top: 8px;
      }
      svg {
        display: block;
        width: 100%;
      }
      svg text {
        font-size: 11px;
        fill: var(--secondary-text-color);
      }
      .gitter {
        stroke: var(--lh-border);
        stroke-width: 1;
      }
      .fadenkreuz {
        stroke: var(--secondary-text-color);
        stroke-width: 1;
        stroke-dasharray: 3 3;
      }
      .tooltip {
        position: absolute;
        top: 0;
        z-index: 1;
        pointer-events: none;
        background: var(--lh-card);
        color: var(--primary-text-color);
        border: 1px solid var(--lh-border);
        border-radius: 8px;
        padding: 6px 10px;
        font-size: 12px;
        white-space: nowrap;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
      }
      .tooltip .tag {
        font-weight: 500;
        margin-bottom: 2px;
      }
      .legende {
        display: flex;
        flex-wrap: wrap;
        gap: 4px 14px;
        margin-top: 6px;
        font-size: 12px;
        color: var(--secondary-text-color);
      }
      .punkt {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 2px;
        margin-right: 5px;
        vertical-align: -1px;
      }
      ul {
        margin: 4px 0 0;
        padding-left: 18px;
      }
      li {
        margin: 3px 0;
      }
      .tabelle {
        overflow-x: auto;
      }
      .tabelle table {
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
      }
      .tabelle th,
      .tabelle td {
        text-align: right;
        padding: 4px 8px;
        border-bottom: 1px solid var(--lh-border);
        white-space: nowrap;
      }
      .tabelle th:first-child,
      .tabelle td:first-child {
        text-align: left;
      }
      .report h3 {
        font-size: 15px;
        font-weight: 500;
        margin: 16px 0 4px;
      }
      .report .woche {
        display: flex;
        gap: 8px;
        align-items: center;
        margin-bottom: 4px;
      }
      .report .woche span {
        flex: 1;
        text-align: center;
        font-weight: 500;
      }
    `,
  ];

  @property({ attribute: false }) hass?: Hass;

  @property({ type: Boolean, reflect: true }) narrow = false;

  @property() kindId = "";

  /** Whether the weekly report is switched on. */
  @property({ type: Boolean }) wochenreport = false;

  /** Changes whenever the overview reloaded, to follow new answers. */
  @property({ attribute: false }) stand?: unknown;

  @state() private _tage = 30;

  @state() private _daten?: Fortschritt;

  @state() private _fehler = "";

  @state() private _tabelle = false;

  /** Hovered day per chart. */
  @state() private _zeiger: { diagramm: string; index: number } | null = null;

  @state() private _report: Wochenreport | null = null;

  @state() private _reportVersatz = -1;

  @state() private _reportOffen = false;

  @state() private _reportHinweis = "";

  /** Measured width of every chart, so that text keeps its size. */
  @state() private _breiten: Record<string, number> = {};

  private _beobachter?: ResizeObserver;

  private get _t(): Uebersetzer {
    return uebersetzer(this.hass?.language ?? "en");
  }

  private get _api(): Api {
    return new Api(this.hass as Hass);
  }

  private get _dunkel(): boolean {
    return Boolean(this.hass?.themes?.darkMode);
  }

  protected willUpdate(geaendert: PropertyValues): void {
    if (geaendert.has("kindId") || geaendert.has("stand")) {
      void this._lade();
    }
    if (geaendert.has("kindId")) {
      this._reportOffen = false;
    }
  }

  private _mass(name: string, hoehe: number): Mass {
    return { b: Math.max(240, this._breiten[name] ?? 600), h: hoehe };
  }

  connectedCallback(): void {
    super.connectedCallback();
    this._beobachter = new ResizeObserver((eintraege) => {
      const breiten = { ...this._breiten };
      let geaendert = false;
      for (const eintrag of eintraege) {
        const name = (eintrag.target as HTMLElement).dataset.name ?? "";
        const breite = Math.round(eintrag.contentRect.width);
        if (name && breite && breiten[name] !== breite) {
          breiten[name] = breite;
          geaendert = true;
        }
      }
      if (geaendert) {
        this._breiten = breiten;
      }
    });
  }

  disconnectedCallback(): void {
    super.disconnectedCallback();
    this._beobachter?.disconnect();
  }

  protected updated(): void {
    // Charts come and go with the table view and with new data
    for (const diagramm of this.renderRoot.querySelectorAll(".diagramm")) {
      this._beobachter?.observe(diagramm);
    }
  }

  private async _lade(): Promise<void> {
    if (!this.hass || !this.kindId) {
      return;
    }
    try {
      this._daten = await this._api.fortschritt(this.kindId, this._tage);
      this._fehler = "";
    } catch (fehler) {
      this._fehler = fehlertext(this._t, fehler);
    }
  }

  private async _setzeTage(tage: number): Promise<void> {
    this._tage = tage;
    this._zeiger = null;
    await this._lade();
  }

  // ----------------------------------------------------------- formatting

  private _datum(iso: string | undefined, lang = false): string {
    if (!iso) {
      return "";
    }
    const datum = new Date(`${iso.slice(0, 10)}T00:00:00`);
    return datum.toLocaleDateString(
      this.hass?.language ?? "en",
      lang
        ? { weekday: "short", day: "2-digit", month: "2-digit", year: "numeric" }
        : { day: "2-digit", month: "2-digit" },
    );
  }

  private _prozent(wert: number | null | undefined): string {
    return wert === null || wert === undefined ? "–" : `${wert} %`;
  }

  private _simText(eintrag: SimulationsEintrag): string {
    const t = this._t;
    const worum = [eintrag.fach, eintrag.thema].filter(Boolean).join(": ");
    const punkte = t("sim_punkte", {
      p: eintrag.punkte.toLocaleString(this.hass?.language ?? "en"),
      m: eintrag.moeglich,
      proz: eintrag.prozent ?? 0,
    });
    return `${this._datum(eintrag.tag)}${worum ? ` · ${worum}` : ""} – ${punkte}${
      eintrag.vollstaendig ? "" : ` (${t("sim_unvollstaendig")})`
    }`;
  }

  private _lektionText(eintrag: SchwacheLektion): string {
    return `${eintrag.fach} · ${eintrag.lektion}: ${this._t("fehlerquote_n", {
      n: eintrag.fehlerquote,
      f: eintrag.falsch,
      g: eintrag.richtig + eintrag.falsch,
    })}`;
  }

  // ---------------------------------------------------------------- charts

  /** Columns that catch the pointer, one per day, plus the crosshair. */
  private _spalten(m: Mass, diagramm: string, anzahl: number): TemplateResult {
    const breite = (m.b - LINKS - RECHTS) / anzahl;
    const aktiv = this._zeiger?.diagramm === diagramm ? this._zeiger.index : -1;
    return svg`
      ${
        aktiv >= 0
          ? svg`<line class="fadenkreuz"
              x1=${LINKS + (aktiv + 0.5) * breite} x2=${LINKS + (aktiv + 0.5) * breite}
              y1=${OBEN} y2=${m.h - UNTEN}></line>`
          : nothing
      }
      ${Array.from({ length: anzahl }, (_, index) => svg`<rect
          x=${LINKS + index * breite} y=${OBEN}
          width=${breite} height=${m.h - OBEN - UNTEN}
          fill="transparent"
          @pointerenter=${() => {
            this._zeiger = { diagramm, index };
          }}
        ></rect>`)}
    `;
  }

  private _achsen(m: Mass, max: number, einheit: string, tage: string[]): TemplateResult {
    const innen = m.h - OBEN - UNTEN;
    const breite = (m.b - LINKS - RECHTS) / tage.length;
    // Roughly one date label per 60 pixels
    const schritt = Math.max(1, Math.ceil(tage.length / Math.max(2, (m.b - LINKS) / 60)));
    return svg`
      ${[0, 0.5, 1].map((anteil) => {
        const y = m.h - UNTEN - anteil * innen;
        return svg`
          <line class="gitter" x1=${LINKS} x2=${m.b - RECHTS} y1=${y} y2=${y}></line>
          <text x=${LINKS - 6} y=${y + 4} text-anchor="end">
            ${Math.round(anteil * max)}${einheit}
          </text>`;
      })}
      ${tage.map((tag, index) =>
        index % schritt === 0
          ? svg`<text x=${LINKS + (index + 0.5) * breite} y=${m.h - 6}
              text-anchor="middle">${this._datum(tag)}</text>`
          : nothing,
      )}
    `;
  }

  private _tooltip(
    m: Mass,
    diagramm: string,
    anzahl: number,
    inhalt: (index: number) => TemplateResult,
  ): TemplateResult | typeof nothing {
    const zeiger = this._zeiger;
    if (!zeiger || zeiger.diagramm !== diagramm) {
      return nothing;
    }
    const anteil = (LINKS + ((zeiger.index + 0.5) * (m.b - LINKS - RECHTS)) / anzahl) / m.b;
    // Flip to the other side of the crosshair in the right half
    const stil =
      anteil > 0.5
        ? `right: calc(${(1 - anteil) * 100}% + 10px)`
        : `left: calc(${anteil * 100}% + 10px)`;
    return html`<div class="tooltip" style=${stil}>${inhalt(zeiger.index)}</div>`;
  }

  private _antworten(daten: Fortschritt): TemplateResult {
    const t = this._t;
    const m = this._mass("antworten", HOEHE_BREIT);
    const farben = this._dunkel ? ERGEBNIS_DUNKEL : ERGEBNIS_HELL;
    const reihe = daten.reihe;
    const summe = (tag: Tageszahlen): number =>
      tag.richtig + tag.teilweise + tag.falsch + tag.unbeantwortet;
    const max = achsenende(Math.max(...reihe.map(summe)));
    const innen = m.h - OBEN - UNTEN;
    const slot = (m.b - LINKS - RECHTS) / reihe.length;
    const balken = Math.max(2, Math.min(MAX_BALKEN, slot - LUECKE));
    const saeulen = reihe.map((tag, index) => {
      const x = LINKS + index * slot + (slot - balken) / 2;
      let unten = m.h - UNTEN;
      const teile = ERGEBNISSE.filter((ergebnis) => tag[ergebnis] > 0);
      return teile.map((ergebnis, nummer) => {
        const hoehe = (tag[ergebnis] / max) * innen;
        // A gap in the surface colour separates the segments of a stack
        const sichtbar = Math.max(1, hoehe - (nummer > 0 ? LUECKE : 0));
        unten -= hoehe;
        const oben = nummer === teile.length - 1;
        const r = oben ? Math.min(4, balken / 2, sichtbar) : 0;
        // Rounded at the data end only, square at the baseline
        const pfad = `M${x},${unten + sichtbar} V${unten + r} q0,${-r} ${r},${-r} H${
          x + balken - r
        } q${r},0 ${r},${r} V${unten + sichtbar} Z`;
        return svg`<path d=${pfad} fill=${farben[ergebnis]}></path>`;
      });
    });
    return html`
      <h3>${t("fortschritt_antworten")}</h3>
      <div
        class="diagramm"
        data-name="antworten"
        @pointerleave=${() => {
          this._zeiger = null;
        }}
      >
        <svg viewBox="0 0 ${m.b} ${m.h}" height=${m.h} role="img" aria-label=${t("fortschritt_antworten")}>
          ${this._achsen(m, max, "", reihe.map((tag) => tag.tag))}
          ${saeulen}
          ${this._spalten(m, "antworten", reihe.length)}
        </svg>
        ${this._tooltip(m, "antworten", reihe.length, (index) => {
          const tag = reihe[index];
          if (!tag) {
            return html``;
          }
          return html`
            <div class="tag">${this._datum(tag.tag, true)}</div>
            ${ERGEBNISSE.map(
              (ergebnis) =>
                html`<div>
                  <span class="punkt" style="background: ${farben[ergebnis]}"></span>
                  ${t(`reihe_${ergebnis}`)}: ${tag[ergebnis]}
                </div>`,
            )}
          `;
        })}
      </div>
      <div class="legende">
        ${ERGEBNISSE.map(
          (ergebnis) =>
            html`<span>
              <span class="punkt" style="background: ${farben[ergebnis]}"></span>
              ${t(`reihe_${ergebnis}`)}
            </span>`,
        )}
      </div>
    `;
  }

  /** A line with gaps where there is no value. */
  private _linie(
    m: Mass,
    werte: (number | null)[],
    farbe: string | undefined,
    zeiger: number,
  ): TemplateResult {
    const innen = m.h - OBEN - UNTEN;
    const slot = (m.b - LINKS - RECHTS) / werte.length;
    const punkt = (wert: number, index: number): [number, number] => [
      LINKS + (index + 0.5) * slot,
      m.h - UNTEN - (wert / 100) * innen,
    ];
    let pfad = "";
    let offen = false;
    const einzeln: [number, number][] = [];
    werte.forEach((wert, index) => {
      if (wert === null) {
        offen = false;
        return;
      }
      const [x, y] = punkt(wert, index);
      pfad += `${offen ? "L" : "M"}${x},${y} `;
      // A value between two gaps would be an invisible path of one point
      if (!offen && (index === werte.length - 1 || werte[index + 1] === null)) {
        einzeln.push([x, y]);
      }
      offen = true;
    });
    const wertAmZeiger = zeiger >= 0 ? werte[zeiger] : null;
    return svg`
      <path d=${pfad} fill="none" stroke=${farbe} stroke-width="2"
        stroke-linejoin="round" stroke-linecap="round"></path>
      ${einzeln.map(
        ([x, y]) => svg`<circle cx=${x} cy=${y} r="3" fill=${farbe}></circle>`,
      )}
      ${
        wertAmZeiger !== null && wertAmZeiger !== undefined
          ? svg`<circle cx=${punkt(wertAmZeiger, zeiger)[0]} cy=${punkt(wertAmZeiger, zeiger)[1]}
              r="4" fill=${farbe} stroke="var(--lh-card)" stroke-width="2"></circle>`
          : nothing
      }
    `;
  }

  private _quote(daten: Fortschritt): TemplateResult {
    const t = this._t;
    const m = this._mass("quote", HOEHE_SCHMAL);
    const farbe = (this._dunkel ? FACH_DUNKEL : FACH_HELL)[0];
    const reihe = daten.reihe;
    const werte = reihe.map((tag) => tag.trefferquote);
    const zeiger = this._zeiger?.diagramm === "quote" ? this._zeiger.index : -1;
    return html`
      <h3>${t("fortschritt_quote")}</h3>
      <div class="klein">${t("fortschritt_quote_hilfe")}</div>
      <div
        class="diagramm"
        data-name="quote"
        @pointerleave=${() => {
          this._zeiger = null;
        }}
      >
        <svg viewBox="0 0 ${m.b} ${m.h}" height=${m.h} role="img" aria-label=${t("fortschritt_quote")}>
          ${this._achsen(m, 100, " %", reihe.map((tag) => tag.tag))}
          ${this._linie(m, werte, farbe, zeiger)}
          ${this._spalten(m, "quote", reihe.length)}
        </svg>
        ${this._tooltip(m, "quote", reihe.length, (index) => html`
          <div class="tag">${this._datum(reihe[index]?.tag, true)}</div>
          <div>${t("fortschritt_quote")}: ${this._prozent(reihe[index]?.trefferquote)}</div>
        `)}
      </div>
    `;
  }

  private _lernstand(daten: Fortschritt): TemplateResult {
    const t = this._t;
    const m = this._mass("lernstand", HOEHE_SCHMAL);
    const farben = this._dunkel ? FACH_DUNKEL : FACH_HELL;
    const faecher = daten.faecher.slice(0, farben.length);
    const tage = daten.reihe.map((tag) => tag.tag);
    const zeiger = this._zeiger?.diagramm === "lernstand" ? this._zeiger.index : -1;
    return html`
      <h3>${t("fortschritt_lernstand")}</h3>
      <div class="klein">${t("fortschritt_lernstand_hilfe")}</div>
      <div
        class="diagramm"
        data-name="lernstand"
        @pointerleave=${() => {
          this._zeiger = null;
        }}
      >
        <svg
          viewBox="0 0 ${m.b} ${m.h}"
          height=${m.h}
          role="img"
          aria-label=${t("fortschritt_lernstand")}
        >
          ${this._achsen(m, 100, " %", tage)}
          ${faecher.map((fach, index) => this._linie(m, fach.lernstand, farben[index], zeiger))}
          ${this._spalten(m, "lernstand", tage.length)}
        </svg>
        ${this._tooltip(m, "lernstand", tage.length, (index) => html`
          <div class="tag">${this._datum(tage[index], true)}</div>
          ${faecher.map(
            (fach, nummer) =>
              html`<div>
                <span class="punkt" style="background: ${farben[nummer]}"></span>
                ${fach.name}: ${this._prozent(fach.lernstand[index])}
              </div>`,
          )}
        `)}
      </div>
      ${faecher.length > 1
        ? html`<div class="legende">
            ${faecher.map(
              (fach, index) =>
                html`<span>
                  <span class="punkt" style="background: ${farben[index]}"></span>
                  ${fach.name}
                </span>`,
            )}
          </div>`
        : nothing}
    `;
  }

  private _alsTabelle(daten: Fortschritt): TemplateResult {
    const t = this._t;
    const zeilen = daten.reihe
      .map((tag, index) => ({ tag, index }))
      .filter(({ tag }) => tag.gefragt || tag.richtig || tag.falsch || tag.teilweise)
      .reverse();
    if (!zeilen.length) {
      return html`<div class="leer">${t("fortschritt_keine_daten")}</div>`;
    }
    return html`
      <div class="tabelle">
        <table>
          <thead>
            <tr>
              <th>${t("reihe_tag")}</th>
              <th>${t("reihe_gefragt")}</th>
              ${ERGEBNISSE.map((ergebnis) => html`<th>${t(`reihe_${ergebnis}`)}</th>`)}
              <th>${t("fortschritt_quote")}</th>
              ${daten.faecher.map((fach) => html`<th>${fach.name}</th>`)}
            </tr>
          </thead>
          <tbody>
            ${zeilen.map(
              ({ tag, index }) =>
                html`<tr>
                  <td>${this._datum(tag.tag, true)}</td>
                  <td>${tag.gefragt}</td>
                  ${ERGEBNISSE.map((ergebnis) => html`<td>${tag[ergebnis]}</td>`)}
                  <td>${this._prozent(tag.trefferquote)}</td>
                  ${daten.faecher.map(
                    (fach) => html`<td>${this._prozent(fach.lernstand[index])}</td>`,
                  )}
                </tr>`,
            )}
          </tbody>
        </table>
      </div>
    `;
  }

  private _aufgabenListe(aufgaben: FehlerAufgabe[]): TemplateResult {
    const t = this._t;
    return html`<ul>
      ${aufgaben.map(
        (aufgabe) =>
          html`<li>
            ${aufgabe.fach}: ${aufgabe.aufgabe} → ${aufgabe.loesung}
            <span class="klein">(${t("fehler_n", { n: aufgabe.falsch })})</span>
          </li>`,
      )}
    </ul>`;
  }

  private _schwach(daten: Fortschritt): TemplateResult {
    const t = this._t;
    return html`
      <h3>${t("fortschritt_schwach")}</h3>
      ${!daten.lektionen.length && !daten.aufgaben.length
        ? html`<div class="leer">${t("fortschritt_keine_schwach")}</div>`
        : nothing}
      ${daten.lektionen.length
        ? html`<h4>${t("fortschritt_lektionen")}</h4>
            <ul>
              ${daten.lektionen.map((eintrag) => html`<li>${this._lektionText(eintrag)}</li>`)}
            </ul>`
        : nothing}
      ${daten.aufgaben.length
        ? html`<h4>${t("fortschritt_aufgaben")}</h4>
            ${this._aufgabenListe(daten.aufgaben)}`
        : nothing}
    `;
  }

  private _simulationen(daten: Fortschritt): TemplateResult {
    const t = this._t;
    return html`
      <h3>${t("fortschritt_simulationen")}</h3>
      ${daten.simulationen.length
        ? html`<ul>
            ${daten.simulationen.map((eintrag) => html`<li>${this._simText(eintrag)}</li>`)}
          </ul>`
        : html`<div class="leer">${t("fortschritt_keine_sim")}</div>`}
    `;
  }

  // -------------------------------------------------------- weekly report

  private async _oeffneReport(versatz = -1): Promise<void> {
    try {
      this._report = await this._api.wochenreport(this.kindId, versatz);
      this._reportVersatz = versatz;
      this._reportHinweis = "";
      this._reportOffen = true;
      this._fehler = "";
    } catch (fehler) {
      this._fehler = fehlertext(this._t, fehler);
    }
  }

  private _veraenderung(neu: number | null, alt: number | null, einheit: string): string {
    const t = this._t;
    if (neu === null) {
      return "–";
    }
    if (alt === null) {
      return `${neu}${einheit} (${t("report_vorwoche", { wert: t("report_keine_vorwoche") })})`;
    }
    const pfeil = neu > alt ? "↑" : neu < alt ? "↓" : "→";
    return `${neu}${einheit} ${pfeil} (${t("report_vorwoche", { wert: `${alt}${einheit}` })})`;
  }

  /** The report as titled lists; shown, copied and printed from the same data. */
  private _abschnitte(report: Wochenreport): Abschnitt[] {
    const t = this._t;
    const k = report.kennzahlen;
    const v = report.vorwoche;
    const beantwortet = (z: Tageszahlen): number => z.richtig + z.teilweise + z.falsch;
    const wann = (tage: number): string =>
      tage === 0
        ? t("report_heute")
        : tage === 1
          ? t("report_morgen")
          : t("report_in_tagen", { n: tage });
    const abschnitte: Abschnitt[] = [
      {
        titel: t("report_kennzahlen"),
        zeilen: [
          `${t("reihe_gefragt")}: ${k.gefragt}`,
          `${t("reihe_richtig")}: ${k.richtig}`,
          `${t("reihe_teilweise")}: ${k.teilweise}`,
          `${t("reihe_falsch")}: ${k.falsch}`,
          `${t("reihe_unbeantwortet")}: ${k.unbeantwortet}`,
          `${t("fortschritt_quote")}: ${this._prozent(k.trefferquote)}`,
          `${t("report_tage_aktiv")}: ${k.tage_aktiv}`,
        ],
      },
      {
        titel: t("report_vergleich"),
        zeilen: [
          `${t("report_antworten")}: ${this._veraenderung(beantwortet(k), beantwortet(v), "")}`,
          `${t("fortschritt_quote")}: ${this._veraenderung(k.trefferquote, v.trefferquote, " %")}`,
          ...report.faecher.map(
            (fach) =>
              `${t("report_lernstand", { fach: fach.name })}: ${this._veraenderung(
                fach.lernstand,
                fach.vorher,
                " %",
              )}`,
          ),
        ],
      },
    ];
    const schwach = [
      ...report.lektionen.map((eintrag) => this._lektionText(eintrag)),
      ...report.aufgaben.map(
        (aufgabe) =>
          `${aufgabe.fach}: ${aufgabe.aufgabe} – ${t("report_loesung", {
            loesung: aufgabe.loesung,
          })} (${t("fehler_n", { n: aufgabe.falsch })})`,
      ),
    ];
    if (schwach.length) {
      abschnitte.push({ titel: t("report_schwach"), zeilen: schwach });
    }
    abschnitte.push({
      titel: t("report_anstehend"),
      zeilen: report.arbeiten.length
        ? report.arbeiten.map(
            (arbeit) =>
              `${this._datum(arbeit.datum)} (${wann(arbeit.tage_bis)}) · ${arbeit.fach}: ${
                arbeit.thema
              } [${t(arbeit.art === "hue" ? "art_hue" : "art_arbeit")}]${
                arbeit.sicher === null ? "" : ` – ${t("report_sicher", { n: arbeit.sicher })}`
              }`,
          )
        : [t("report_keine_arbeiten")],
    });
    if (report.vorschlaege.length) {
      abschnitte.push({
        titel: t("report_vorschlaege"),
        zeilen: report.vorschlaege.map(
          (vorschlag) =>
            `${this._datum(vorschlag.datum)} · ${vorschlag.text} [${t(
              vorschlag.art === "hue" ? "art_hue" : "art_arbeit",
            )}]`,
        ),
      });
    }
    if (report.simulationen.length) {
      abschnitte.push({
        titel: t("report_simulationen"),
        zeilen: report.simulationen.map((eintrag) => this._simText(eintrag)),
      });
    }
    return abschnitte;
  }

  private _reportTitel(report: Wochenreport): string {
    const t = this._t;
    return `${t("report_woche", {
      von: this._datum(report.von),
      bis: this._datum(report.bis),
    })}${report.laufend ? ` (${t("report_laufend")})` : ""}`;
  }

  private _reportText(report: Wochenreport): string {
    return [
      `${this._t("wochenreport")} – ${this._reportTitel(report)}`,
      ...this._abschnitte(report).map(
        (abschnitt) =>
          `\n${abschnitt.titel}\n${abschnitt.zeilen.map((zeile) => `- ${zeile}`).join("\n")}`,
      ),
    ].join("\n");
  }

  private async _kopiereReport(): Promise<void> {
    if (!this._report) {
      return;
    }
    try {
      await navigator.clipboard.writeText(this._reportText(this._report));
      this._reportHinweis = this._t("report_kopiert");
    } catch {
      this._reportHinweis = this._t("report_kopieren_fehler");
    }
  }

  private _druckeReport(): void {
    const report = this._report;
    if (!report) {
      return;
    }
    const fenster = window.open("", "_blank");
    if (!fenster) {
      this._reportHinweis = this._t("report_druck_blockiert");
      return;
    }
    const dokument = fenster.document;
    dokument.title = this._t("wochenreport");
    const stil = dokument.createElement("style");
    stil.textContent =
      "body{font-family:sans-serif;margin:24px;color:#000}h1{font-size:20px}h2{font-size:15px;margin:18px 0 4px}li{margin:3px 0}";
    dokument.head.append(stil);
    const kopf = dokument.createElement("h1");
    kopf.textContent = `${this._t("wochenreport")} – ${this._reportTitel(report)}`;
    dokument.body.append(kopf);
    for (const abschnitt of this._abschnitte(report)) {
      const titel = dokument.createElement("h2");
      titel.textContent = abschnitt.titel;
      const liste = dokument.createElement("ul");
      for (const zeile of abschnitt.zeilen) {
        const punkt = dokument.createElement("li");
        punkt.textContent = zeile;
        liste.append(punkt);
      }
      dokument.body.append(titel, liste);
    }
    fenster.focus();
    fenster.print();
  }

  private _reportDialog(report: Wochenreport): TemplateResult {
    const t = this._t;
    return html`
      <div
        class="overlay"
        @click=${(e: Event) => {
          if (e.target === e.currentTarget) {
            this._reportOffen = false;
          }
        }}
      >
        <div class="dialog report" role="dialog" aria-modal="true">
          <h2>${t("wochenreport")}</h2>
          <div class="woche">
            <button
              class="icon"
              title=${t("report_frueher")}
              aria-label=${t("report_frueher")}
              @click=${() => this._oeffneReport(this._reportVersatz - 1)}
            >
              <ha-icon icon="mdi:chevron-left"></ha-icon>
            </button>
            <span>${this._reportTitel(report)}</span>
            <button
              class="icon"
              title=${t("report_spaeter")}
              aria-label=${t("report_spaeter")}
              ?disabled=${this._reportVersatz >= 0}
              @click=${() => this._oeffneReport(this._reportVersatz + 1)}
            >
              <ha-icon icon="mdi:chevron-right"></ha-icon>
            </button>
          </div>
          ${report.seit && report.seit > report.bis
            ? html`<p class="klein">
                ${t("fortschritt_seit", { datum: this._datum(report.seit, true) })}
              </p>`
            : nothing}
          ${this._abschnitte(report).map(
            (abschnitt) =>
              html`<h3>${abschnitt.titel}</h3>
                <ul>
                  ${abschnitt.zeilen.map((zeile) => html`<li>${zeile}</li>`)}
                </ul>`,
          )}
          ${this._reportHinweis
            ? html`<div class="meldung" role="status" style="margin-top: 12px">
                <span>${this._reportHinweis}</span>
              </div>`
            : nothing}
          <div class="aktionen">
            <button @click=${this._kopiereReport}>${t("report_kopieren")}</button>
            <button @click=${this._druckeReport}>${t("report_drucken")}</button>
            <button
              class="primaer"
              @click=${() => {
                this._reportOffen = false;
              }}
            >
              ${t("schliessen")}
            </button>
          </div>
        </div>
      </div>
    `;
  }

  // ---------------------------------------------------------------- render

  protected render(): TemplateResult {
    const t = this._t;
    const daten = this._daten;
    return html`
      <div class="kopf">
        <h2>${t("fortschritt")}</h2>
        <div class="wahl" role="group" aria-label=${t("fortschritt_zeitraum")}>
          ${ZEITRAEUME.map(
            (tage) =>
              html`<button
                aria-pressed=${tage === this._tage ? "true" : "false"}
                @click=${() => this._setzeTage(tage)}
              >
                ${t("fortschritt_tage", { n: tage })}
              </button>`,
          )}
        </div>
        <button
          @click=${() => {
            this._tabelle = !this._tabelle;
          }}
        >
          ${t(this._tabelle ? "fortschritt_diagramm" : "fortschritt_tabelle")}
        </button>
        ${this.wochenreport
          ? html`<button class="primaer" @click=${() => this._oeffneReport()}>
              ${t("wochenreport")}
            </button>`
          : nothing}
      </div>
      ${this._fehler
        ? html`<div class="meldung fehler" role="alert"><span>${this._fehler}</span></div>`
        : nothing}
      ${!daten
        ? nothing
        : !daten.seit
          ? html`<div class="card leer">${t("fortschritt_leer")}</div>`
          : html`
              <div class="klein" style="margin-bottom: 8px">
                ${t("fortschritt_seit", { datum: this._datum(daten.seit, true) })}
              </div>
              <div class="raster">
                ${this._tabelle
                  ? html`<div class="card breit">${this._alsTabelle(daten)}</div>`
                  : html`
                      <div class="card breit">${this._antworten(daten)}</div>
                      <div class="card">${this._quote(daten)}</div>
                      <div class="card">${this._lernstand(daten)}</div>
                    `}
                <div class="card">${this._schwach(daten)}</div>
                <div class="card">${this._simulationen(daten)}</div>
              </div>
            `}
      ${this._reportOffen && this._report ? this._reportDialog(this._report) : nothing}
    `;
  }
}

if (!customElements.get("lh-fortschritt")) {
  customElements.define("lh-fortschritt", LhFortschritt);
}
