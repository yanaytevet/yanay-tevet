import {Injectable, isDevMode} from '@angular/core';

// A record of what happened in the editor, for finding UX problems after the fact. Development builds only:
// it lives in this browser's localStorage, and the console exposes it as `window.__pdfEditorLog`
// (`events()`, `last(n)`, `flags()`, `clear()`), which is how a coding agent driving the browser reads it.

const STORAGE_KEY = 'pdf_editor_log';
const MAX_EVENTS = 600;

export interface PdfLogEvent {
  seq: number;
  at: string;
  type: string;
  [key: string]: unknown;
}

interface LogApi {
  events(): PdfLogEvent[];
  last(n: number): PdfLogEvent[];
  flags(): PdfLogEvent[];
  clear(): void;
}

function load(): PdfLogEvent[] {
  try {
    const value = JSON.parse(localStorage.getItem(STORAGE_KEY) ?? '[]');
    return Array.isArray(value) ? value : [];
  } catch {
    return [];
  }
}

function round(n: number): number {
  return Math.round(n * 10) / 10;
}

// Rounds numbers so rectangles and points stay readable in the log.
export function compact(value: unknown): unknown {
  if (typeof value === 'number') {
    return round(value);
  }
  if (Array.isArray(value)) {
    return value.map(compact);
  }
  if (value && typeof value === 'object') {
    return Object.fromEntries(Object.entries(value).map(([k, v]) => [k, compact(v)]));
  }
  return value;
}

@Injectable({providedIn: 'root'})
export class PdfEditorLog {
  readonly enabled = isDevMode();
  private events: PdfLogEvent[] = this.enabled ? load() : [];
  private seq = this.events.length > 0 ? this.events[this.events.length - 1].seq : 0;
  private saveTimer: ReturnType<typeof setTimeout> | null = null;

  constructor() {
    if (this.enabled) {
      const api: LogApi = {
        events: () => [...this.events],
        last: n => this.events.slice(-n),
        flags: () => this.events.filter(e => e.type === 'flag'),
        clear: () => {
          this.events = [];
          this.persist();
        },
      };
      (window as unknown as {__pdfEditorLog: LogApi}).__pdfEditorLog = api;
    }
  }

  log(type: string, data: Record<string, unknown> = {}): void {
    if (!this.enabled) {
      return;
    }
    const event: PdfLogEvent = {seq: ++this.seq, at: new Date().toISOString(), type, ...(compact(data) as Record<string, unknown>)};
    this.events.push(event);
    if (this.events.length > MAX_EVENTS) {
      this.events.splice(0, this.events.length - MAX_EVENTS);
    }
    console.debug('[pdf-editor]', type, event);
    if (!this.saveTimer) {
      this.saveTimer = setTimeout(() => this.persist(), 300);
    }
  }

  private persist(): void {
    this.saveTimer = null;
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(this.events));
    } catch {
      // Storage is full; drop the older half and keep going.
      this.events.splice(0, Math.floor(this.events.length / 2));
    }
  }
}
