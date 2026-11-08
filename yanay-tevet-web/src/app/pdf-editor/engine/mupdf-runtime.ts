import type * as Mupdf from 'mupdf';

export type MupdfModule = typeof Mupdf;

let instance: MupdfModule | null = null;

// MuPDF is loaded at runtime from the app's assets (see pdf-editor.worker.ts), so the engine gets the module
// handed to it instead of importing it.
export function setMupdf(module: MupdfModule): void {
  instance = module;
}

export function mupdf(): MupdfModule {
  if (!instance) {
    throw new Error('MuPDF is not loaded');
  }
  return instance;
}
