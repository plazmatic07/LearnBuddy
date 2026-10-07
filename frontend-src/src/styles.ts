import { css } from "lit";

export const styles = css`
  :host {
    display: block;
    min-height: 100vh;
    background: var(--primary-background-color);
    color: var(--primary-text-color);
    font-family: var(--paper-font-body1_-_font-family, Roboto, sans-serif);
    font-size: 14px;
    --lh-border: var(--divider-color, rgba(128, 128, 128, 0.3));
    --lh-card: var(--card-background-color, #fff);
    --lh-radius: var(--ha-card-border-radius, 12px);
    --lh-muted: var(--secondary-text-color);
    --lh-accent: var(--primary-color);
    --lh-error: var(--error-color, #db4437);
    --lh-ok: var(--success-color, #43a047);
  }
  * {
    box-sizing: border-box;
  }
  header {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
    padding: 8px 16px;
    min-height: 56px;
    background: var(--app-header-background-color, var(--lh-accent));
    color: var(--app-header-text-color, #fff);
    position: sticky;
    top: 0;
    z-index: 2;
  }
  header h1 {
    font-size: 20px;
    font-weight: 400;
    margin: 0 auto 0 0;
  }
  header label {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 13px;
  }
  .kinder {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }
  .kinder.fachwahl {
    margin-bottom: 12px;
  }
  button.kindwahl {
    border-radius: 18px;
    padding: 7px 16px;
  }
  header button.kindwahl {
    background: transparent;
    color: inherit;
    border-color: currentColor;
    opacity: 0.75;
  }
  button.kindwahl[aria-pressed="true"] {
    background: var(--lh-accent);
    border-color: var(--lh-accent);
    color: var(--text-primary-color, #fff);
  }
  header button.kindwahl[aria-pressed="true"] {
    background: var(--app-header-text-color, #fff);
    border-color: var(--app-header-text-color, #fff);
    color: var(--app-header-background-color, var(--lh-accent));
    opacity: 1;
    font-weight: 500;
  }
  main {
    padding: 16px;
    max-width: 1400px;
    margin: 0 auto;
  }
  .card {
    background: var(--lh-card);
    border: 1px solid var(--lh-border);
    border-radius: var(--lh-radius);
    padding: 16px;
    margin-bottom: 16px;
  }
  .tabs {
    display: flex;
    gap: 4px;
    margin-bottom: 16px;
    border-bottom: 1px solid var(--lh-border);
  }
  .tabs button {
    border: none;
    border-bottom: 3px solid transparent;
    border-radius: 0;
    background: none;
    padding: 10px 16px;
    font-size: 15px;
    color: var(--lh-muted);
  }
  .tabs button[aria-selected="true"] {
    color: var(--lh-accent);
    border-bottom-color: var(--lh-accent);
  }
  .leiste {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px;
    margin-bottom: 12px;
  }
  .leiste .abstand {
    flex: 1;
  }
  .filter {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 10px 12px;
    align-items: end;
  }
  .feld {
    display: flex;
    flex-direction: column;
    gap: 4px;
    font-size: 12px;
    color: var(--lh-muted);
    min-width: 0;
  }
  .feld.zeile {
    flex-direction: row;
    align-items: center;
    gap: 8px;
    font-size: 14px;
    color: var(--primary-text-color);
  }
  input,
  select,
  textarea {
    font: inherit;
    font-size: 14px;
    color: var(--primary-text-color);
    background: var(--secondary-background-color, rgba(128, 128, 128, 0.08));
    border: 1px solid var(--lh-border);
    border-radius: 6px;
    padding: 7px 8px;
    min-width: 0;
    width: 100%;
  }
  input[type="checkbox"],
  input[type="radio"] {
    width: 18px;
    height: 18px;
    flex: none;
    accent-color: var(--lh-accent);
  }
  header select {
    width: auto;
    max-width: 200px;
    color: var(--primary-text-color);
    background: var(--lh-card);
  }
  textarea {
    min-height: 160px;
    resize: vertical;
    font-family: var(--code-font-family, monospace);
  }
  input:focus-visible,
  select:focus-visible,
  textarea:focus-visible,
  button:focus-visible {
    outline: 2px solid var(--lh-accent);
    outline-offset: 1px;
  }
  button {
    font: inherit;
    cursor: pointer;
    border: 1px solid var(--lh-border);
    background: var(--lh-card);
    color: var(--primary-text-color);
    border-radius: 18px;
    padding: 7px 14px;
    white-space: nowrap;
  }
  button:hover:not(:disabled) {
    border-color: var(--lh-accent);
  }
  button:disabled {
    opacity: 0.5;
    cursor: default;
  }
  button.primaer {
    background: var(--lh-accent);
    border-color: var(--lh-accent);
    color: var(--text-primary-color, #fff);
  }
  button.gefahr {
    color: var(--lh-error);
    border-color: var(--lh-error);
  }
  button.icon {
    border: none;
    background: none;
    padding: 6px;
    border-radius: 50%;
    color: var(--lh-muted);
    line-height: 0;
  }
  button.icon:hover:not(:disabled) {
    color: var(--lh-accent);
    background: rgba(128, 128, 128, 0.12);
  }
  header button.icon {
    color: inherit;
  }
  .tabelle-rahmen {
    overflow-x: auto;
    padding: 0;
  }
  table {
    width: 100%;
    border-collapse: collapse;
  }
  th,
  td {
    text-align: left;
    padding: 8px 10px;
    border-bottom: 1px solid var(--lh-border);
    vertical-align: top;
  }
  th {
    font-size: 12px;
    font-weight: 500;
    color: var(--lh-muted);
    white-space: nowrap;
    position: sticky;
    top: 0;
    background: var(--lh-card);
  }
  tr:last-child td {
    border-bottom: none;
  }
  tr.gewaehlt td {
    background: rgba(var(--rgb-primary-color, 3, 169, 244), 0.08);
  }
  td.schmal,
  th.schmal {
    width: 1%;
    white-space: nowrap;
  }
  .klein {
    font-size: 12px;
    color: var(--lh-muted);
  }
  .marke {
    display: inline-block;
    font-size: 11px;
    padding: 1px 7px;
    border-radius: 9px;
    border: 1px solid var(--lh-border);
    color: var(--lh-muted);
    white-space: nowrap;
  }
  .marke.warn {
    color: var(--lh-error);
    border-color: var(--lh-error);
  }
  .marke.ok {
    color: var(--lh-ok);
    border-color: var(--lh-ok);
  }
  .meldung {
    padding: 10px 14px;
    border-radius: 8px;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 8px;
    background: rgba(67, 160, 71, 0.14);
  }
  .meldung.fehler {
    background: rgba(219, 68, 55, 0.14);
    color: var(--lh-error);
  }
  .meldung span {
    flex: 1 1 220px;
  }
  .leer {
    padding: 28px 16px;
    text-align: center;
    color: var(--lh-muted);
  }
  .overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: flex-start;
    justify-content: center;
    padding: 24px 12px;
    overflow-y: auto;
    z-index: 10;
  }
  .dialog {
    background: var(--lh-card);
    border-radius: var(--lh-radius);
    width: min(720px, 100%);
    padding: 20px;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.35);
  }
  a.knopf {
    display: inline-block;
    padding: 6px 14px;
    border: 1px solid var(--lh-border);
    border-radius: 18px;
    color: var(--primary-text-color);
    text-decoration: none;
    font-size: 14px;
  }
  .dialog.breit {
    width: min(1100px, 100%);
  }
  .vorschaubild {
    display: block;
    width: 56px;
    height: 42px;
    object-fit: cover;
    border-radius: 6px;
    border: 1px solid var(--lh-border);
    background: #fff;
    cursor: zoom-in;
    padding: 0;
  }
  .grossbild {
    display: block;
    max-width: 100%;
    max-height: 70vh;
    margin: 0 auto;
    border-radius: 8px;
    background: #fff;
  }
  .wahl {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 12px;
  }
  .wahl button {
    display: block;
    text-align: left;
    padding: 16px;
    height: auto;
    white-space: normal;
    border-radius: var(--lh-radius);
  }
  .wahl button.primaer .klein {
    color: inherit;
    opacity: 0.92;
  }
  .wahl button strong {
    display: block;
    margin-bottom: 4px;
    font-size: 15px;
  }
  .teil {
    display: grid;
    grid-template-columns: 2fr 1fr 1fr auto;
    gap: 8px;
    align-items: end;
    margin-bottom: 8px;
  }
  @media (max-width: 600px) {
    .teil {
      grid-template-columns: 1fr;
    }
  }
  .dialog h2 {
    margin: 0 0 12px;
    font-size: 18px;
    font-weight: 500;
  }
  .dialog .raster {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 12px;
    margin-bottom: 12px;
  }
  .dialog .aktionen {
    display: flex;
    justify-content: flex-end;
    gap: 8px;
    margin-top: 16px;
  }
  fieldset {
    border: 1px solid var(--lh-border);
    border-radius: 8px;
    padding: 12px;
    margin: 0 0 12px;
    min-width: 0;
  }
  legend {
    padding: 0 6px;
    font-size: 12px;
    color: var(--lh-muted);
  }
  .liste {
    max-height: 240px;
    overflow-y: auto;
    border: 1px solid var(--lh-border);
    border-radius: 6px;
  }
  .liste label,
  .liste .eintrag {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 10px;
    border-bottom: 1px solid var(--lh-border);
  }
  .liste label:last-child,
  .liste .eintrag:last-child {
    border-bottom: none;
  }
  .chips {
    display: flex;
    flex-wrap: wrap;
    gap: 6px 14px;
  }
  .arbeit {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
  }
  .arbeit .info {
    flex: 1;
    min-width: 200px;
  }
  .arbeit .titel {
    font-size: 16px;
  }

  /* Narrow screens: every table row becomes a card */
  :host([narrow]) main {
    padding: 8px;
  }
  :host([narrow]) table,
  :host([narrow]) tbody,
  :host([narrow]) tr,
  :host([narrow]) td {
    display: block;
    width: 100%;
  }
  :host([narrow]) thead {
    display: none;
  }
  :host([narrow]) tr {
    border-bottom: 1px solid var(--lh-border);
    padding: 8px 4px;
  }
  :host([narrow]) td {
    border: none;
    padding: 3px 10px;
  }
  :host([narrow]) td[data-label]:not(:empty)::before {
    content: attr(data-label) ": ";
    font-size: 12px;
    color: var(--lh-muted);
  }
  :host([narrow]) td.schmal {
    white-space: normal;
  }
`;
