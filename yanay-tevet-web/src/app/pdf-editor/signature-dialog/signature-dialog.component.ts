import {AfterViewInit, Component, ElementRef, signal, viewChild} from '@angular/core';
import {NgIcon} from '@ng-icons/core';
import {featherTrash2} from '@ng-icons/feather-icons';
import {BaseDialogComponent} from '../../common/dialogs/base-dialog.component';
import {CheckboxMarkComponent} from '../../common/components/inputs/checkbox-mark/checkbox-mark.component';

const STORAGE_KEY = 'pdf_editor_signatures';
const MAX_SAVED = 4;
const INK = '#14213d';

function loadSaved(): string[] {
  try {
    const value = JSON.parse(localStorage.getItem(STORAGE_KEY) ?? '[]');
    return Array.isArray(value) ? value.filter((v): v is string => typeof v === 'string') : [];
  } catch {
    return [];
  }
}

function storeSaved(list: string[]): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(list));
  } catch {
    // Storage is full or blocked; the signature still works for this session.
  }
}

// Crops a drawing to its ink, with a little margin, as a transparent PNG.
function trimmedPng(canvas: HTMLCanvasElement): string | null {
  const context = canvas.getContext('2d');
  if (!context) {
    return null;
  }
  const {width, height} = canvas;
  const data = context.getImageData(0, 0, width, height).data;
  let x0 = width;
  let y0 = height;
  let x1 = -1;
  let y1 = -1;
  for (let y = 0; y < height; y++) {
    for (let x = 0; x < width; x++) {
      if (data[(y * width + x) * 4 + 3] > 0) {
        x0 = Math.min(x0, x);
        y0 = Math.min(y0, y);
        x1 = Math.max(x1, x);
        y1 = Math.max(y1, y);
      }
    }
  }
  if (x1 < 0) {
    return null;
  }
  const margin = 8;
  const out = document.createElement('canvas');
  out.width = x1 - x0 + 1 + margin * 2;
  out.height = y1 - y0 + 1 + margin * 2;
  out.getContext('2d')?.drawImage(canvas, x0, y0, x1 - x0 + 1, y1 - y0 + 1, margin, margin, x1 - x0 + 1, y1 - y0 + 1);
  return out.toDataURL('image/png');
}

@Component({
  selector: 'app-signature-dialog',
  imports: [NgIcon, CheckboxMarkComponent],
  templateUrl: './signature-dialog.component.html',
  styleUrl: './signature-dialog.component.css',
})
export class SignatureDialogComponent extends BaseDialogComponent<void, string> implements AfterViewInit {
  protected readonly featherTrash2 = featherTrash2;

  private readonly pad = viewChild<ElementRef<HTMLCanvasElement>>('pad');
  protected readonly mode = signal<'draw' | 'upload'>('draw');
  protected readonly saved = signal<string[]>(loadSaved());
  protected readonly hasInk = signal(false);
  protected readonly remember = signal(true);
  protected readonly uploaded = signal<string | null>(null);
  private last: {x: number; y: number} | null = null;

  override ngAfterViewInit(): void {
    super.ngAfterViewInit();
    this.setUpPad();
  }

  private setUpPad(): void {
    const canvas = this.pad()?.nativeElement;
    if (!canvas) {
      return;
    }
    const ratio = window.devicePixelRatio || 1;
    canvas.width = canvas.clientWidth * ratio;
    canvas.height = canvas.clientHeight * ratio;
    const context = canvas.getContext('2d');
    if (context) {
      context.scale(ratio, ratio);
      context.lineCap = 'round';
      context.lineJoin = 'round';
      context.lineWidth = 2.5;
      context.strokeStyle = INK;
    }
  }

  protected setMode(mode: 'draw' | 'upload'): void {
    this.mode.set(mode);
    if (mode === 'draw') {
      setTimeout(() => this.setUpPad());
      this.hasInk.set(false);
    }
  }

  private point(event: PointerEvent): {x: number; y: number} {
    const rect = (event.target as HTMLElement).getBoundingClientRect();
    return {x: event.clientX - rect.left, y: event.clientY - rect.top};
  }

  protected onDown(event: PointerEvent): void {
    (event.target as HTMLElement).setPointerCapture(event.pointerId);
    this.last = this.point(event);
  }

  protected onMove(event: PointerEvent): void {
    if (!this.last) {
      return;
    }
    const context = this.pad()?.nativeElement.getContext('2d');
    const next = this.point(event);
    if (context) {
      context.beginPath();
      context.moveTo(this.last.x, this.last.y);
      context.lineTo(next.x, next.y);
      context.stroke();
      this.hasInk.set(true);
    }
    this.last = next;
  }

  protected onUp(): void {
    this.last = null;
  }

  protected clear(): void {
    const canvas = this.pad()?.nativeElement;
    canvas?.getContext('2d')?.clearRect(0, 0, canvas.width, canvas.height);
    this.hasInk.set(false);
  }

  protected toggleRemember(): void {
    this.remember.update(v => !v);
  }

  protected async onUpload(event: Event): Promise<void> {
    const file = (event.target as HTMLInputElement).files?.[0];
    if (!file) {
      return;
    }
    const image = new Image();
    image.src = URL.createObjectURL(file);
    try {
      await image.decode();
      const canvas = document.createElement('canvas');
      canvas.width = image.naturalWidth;
      canvas.height = image.naturalHeight;
      canvas.getContext('2d')?.drawImage(image, 0, 0);
      this.uploaded.set(canvas.toDataURL('image/png'));
    } catch {
      this.uploaded.set(null);
    } finally {
      URL.revokeObjectURL(image.src);
    }
  }

  protected use(): void {
    const canvas = this.pad()?.nativeElement;
    const signature = this.mode() === 'draw' ? (canvas ? trimmedPng(canvas) : null) : this.uploaded();
    if (!signature) {
      return;
    }
    if (this.remember()) {
      storeSaved([signature, ...this.saved().filter(s => s !== signature)].slice(0, MAX_SAVED));
    }
    this.emitClose(signature);
  }

  protected useSaved(signature: string): void {
    this.emitClose(signature);
  }

  protected removeSaved(signature: string): void {
    const list = this.saved().filter(s => s !== signature);
    this.saved.set(list);
    storeSaved(list);
  }
}
