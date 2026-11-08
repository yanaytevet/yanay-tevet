import {PdfEngineApi, WorkerRequest, WorkerResponse} from './pdf-engine.types';

type Method = keyof PdfEngineApi;
type Result<M extends Method> = Awaited<ReturnType<PdfEngineApi[M]>>;

// The page's side of the PDF worker. Calls run one at a time, in order, inside the worker.
export class PdfEngineClient {
  private readonly worker = new Worker(new URL('./pdf-editor.worker', import.meta.url), {type: 'module'});
  private readonly pending = new Map<number, {resolve: (value: unknown) => void; reject: (error: Error) => void}>();
  private nextId = 1;

  constructor() {
    this.worker.addEventListener('message', (event: MessageEvent<WorkerResponse>) => {
      const response = event.data;
      const call = this.pending.get(response.id);
      if (!call) {
        return;
      }
      this.pending.delete(response.id);
      if ('error' in response) {
        call.reject(new Error(response.error));
      } else {
        call.resolve(response.result);
      }
    });
    this.worker.addEventListener('error', event => {
      const error = new Error(event.message || 'The PDF engine failed to start');
      for (const call of this.pending.values()) {
        call.reject(error);
      }
      this.pending.clear();
    });
  }

  call<M extends Method>(method: M, ...args: Parameters<PdfEngineApi[M]>): Promise<Result<M>> {
    const id = this.nextId++;
    const transfer = args.filter((a): a is ArrayBuffer => a instanceof ArrayBuffer);
    return new Promise<Result<M>>((resolve, reject) => {
      this.pending.set(id, {resolve: value => resolve(value as Result<M>), reject});
      this.worker.postMessage({id, method, args} satisfies WorkerRequest, transfer);
    });
  }

  terminate(): void {
    this.worker.terminate();
  }
}
