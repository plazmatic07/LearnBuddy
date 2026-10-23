import type { Aufgabe } from "./types";

/** Whether a book page lies in a range given as raw input; empty means no limit. */
export function inSeiten(seite: number | null, von: string, bis: string): boolean {
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
export function kurztext(aufgabe: Aufgabe, a: string, b: string): string {
  if (aufgabe.typ === "mathe") {
    return `${aufgabe.aufgabe} = ${aufgabe.loesung}`;
  }
  if (aufgabe.typ === "sach") {
    return `${aufgabe.frage} – ${aufgabe.antwort}`;
  }
  return `${aufgabe.frage[a] ?? ""} – ${aufgabe.frage[b] ?? ""}`;
}
