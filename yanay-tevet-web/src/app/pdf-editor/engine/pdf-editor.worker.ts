/// <reference lib="webworker" />

import type * as Mupdf from 'mupdf';
import {setMupdf} from './mupdf-runtime';
import {PdfEngine} from './pdf-engine';
import type {RenderedPage, WorkerRequest, WorkerResponse} from './pdf-engine.types';

// MuPDF is served as-is from /pdf-editor/mupdf (angular.json copies it there) rather than bundled: it
// finds its 10 MB .wasm file next to its own URL, which a bundled copy would not have.
const engineReady: Promise<PdfEngine> = (async () => {
  const url = new URL('/pdf-editor/mupdf/mupdf.js', self.location.origin).href;
  const module = (await import(/* @vite-ignore */ url)) as typeof Mupdf;
  // MuPDF warns about every quirk it repairs in a file; those are noise in the console.
  module.setLog({error: message => console.error(message), warning: () => undefined});
  setMupdf(module);
  return new PdfEngine(async name => {
    const response = await fetch(new URL(`/pdf-editor/fonts/${name}`, self.location.origin));
    if (!response.ok) {
      throw new Error(`Could not load the font ${name}`);
    }
    return response.arrayBuffer();
  });
})();

function transferables(result: unknown): Transferable[] {
  if (result instanceof ArrayBuffer) {
    return [result];
  }
  if (result && typeof result === 'object' && 'pixels' in result) {
    return [(result as RenderedPage).pixels];
  }
  return [];
}

addEventListener('message', async (event: MessageEvent<WorkerRequest>) => {
  const {id, method, args} = event.data;
  let response: WorkerResponse;
  try {
    const engine = await engineReady;
    const fn = engine[method] as (...a: unknown[]) => Promise<unknown>;
    const result = await fn.apply(engine, args);
    postMessage({id, result} satisfies WorkerResponse, transferables(result));
    return;
  } catch (error) {
    response = {id, error: error instanceof Error ? error.message : String(error)};
  }
  postMessage(response);
});
