import {afterNextRender, Component, computed, DestroyRef, effect, ElementRef, inject, input, signal, untracked, viewChild} from '@angular/core';
import {PageSize} from '../engine/pdf-engine.types';
import {PdfEditorStore} from '../pdf-editor.store';

const THUMBNAIL_WIDTH = 112;

@Component({
  selector: 'app-pdf-thumbnail',
  templateUrl: './pdf-thumbnail.component.html',
  styleUrl: './pdf-thumbnail.component.css',
})
export class PdfThumbnailComponent {
  private readonly store = inject(PdfEditorStore);
  private readonly host = inject<ElementRef<HTMLElement>>(ElementRef);
  private readonly destroyRef = inject(DestroyRef);

  readonly page = input.required<number>();
  readonly size = input.required<PageSize>();

  private readonly canvas = viewChild<ElementRef<HTMLCanvasElement>>('canvas');
  private readonly visible = signal(false);
  private paintToken = 0;

  protected readonly width = THUMBNAIL_WIDTH;
  protected readonly height = computed(() => THUMBNAIL_WIDTH * (this.size().height / this.size().width));
  private readonly version = computed(() => `${this.store.docVersion()}:${this.store.pageVersions()[this.page()] ?? 0}:${this.page()}`);

  constructor() {
    afterNextRender(() => {
      const observer = new IntersectionObserver(entries => this.visible.set(entries[0].isIntersecting), {rootMargin: '400px 0px'});
      observer.observe(this.host.nativeElement);
      this.destroyRef.onDestroy(() => observer.disconnect());
    });
    effect(() => {
      if (this.visible()) {
        const version = this.version();
        untracked(() => this.paint(version));
      }
    });
  }

  private async paint(version: string): Promise<void> {
    const token = ++this.paintToken;
    const scale = (THUMBNAIL_WIDTH / this.size().width) * Math.min(window.devicePixelRatio || 1, 2);
    try {
      const result = await this.store.render(this.page(), scale);
      const canvas = this.canvas()?.nativeElement;
      if (token !== this.paintToken || !canvas || version !== this.version()) {
        return;
      }
      canvas.width = result.width;
      canvas.height = result.height;
      canvas.getContext('2d')?.putImageData(new ImageData(new Uint8ClampedArray(result.pixels), result.width, result.height), 0, 0);
    } catch {
      // The page went away; the next version paints again.
    }
  }
}
