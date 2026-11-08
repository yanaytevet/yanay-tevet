import {
  afterNextRender,
  Component,
  computed,
  DestroyRef,
  effect,
  ElementRef,
  inject,
  input,
  signal,
  untracked,
  viewChild,
} from '@angular/core';
import {NgIcon} from '@ng-icons/core';
import {featherAlertTriangle, featherCheck, featherTrash2, featherX} from '@ng-icons/feather-icons';
import {startsRtl} from '../engine/bidi';
import {
  AnnotationInfo,
  FontFamily,
  PageSize,
  Point,
  Rect,
  TextLineInfo,
  WidgetInfo,
} from '../engine/pdf-engine.types';
import {hexToRgb, PdfEditorStore, rgbToCss, SubstitutionMarker} from '../pdf-editor.store';

export const CSS_FONT_FAMILY: Record<FontFamily, string> = {
  sans: 'Helvetica, Arial, "Noto Sans Hebrew", sans-serif',
  serif: '"Times New Roman", Times, "Noto Serif Hebrew", serif',
  mono: '"Courier New", Courier, monospace',
};

const ANNOTATION_NAMES: Record<string, string> = {
  Stamp: 'Signature', Ink: 'Drawing', Text: 'Note', FreeText: 'Text box', Highlight: 'Highlight',
  Underline: 'Underline', StrikeOut: 'Strike-out', Square: 'Box', Circle: 'Circle', Line: 'Line',
};

// The largest bitmap a page is rendered to, so a big zoom on a big page doesn't exhaust memory.
const MAX_PIXELS = 16_000_000;
// Where the first baseline of an added text box sits below its top, in font sizes (line height 1.25).
const BASELINE_OFFSET = 0.9;

interface LineEdit {
  line: TextLineInfo;
  text: string;
  font: FontFamily | 'original';
  bold: boolean;
  italic: boolean;
}

interface TextDraft {
  x: number;
  y: number;
  text: string;
  match: TextLineInfo | null;
}

interface Drag {
  start: Point;
  current: Point;
  points: Point[];
}

interface AnnotationMove {
  index: number;
  start: Point;
  offset: Point;
}

function normalise(a: Point, b: Point): Rect {
  return [Math.min(a[0], b[0]), Math.min(a[1], b[1]), Math.max(a[0], b[0]), Math.max(a[1], b[1])];
}

function distanceToRect(p: Point, r: Rect): number {
  const dx = Math.max(r[0] - p[0], 0, p[0] - r[2]);
  const dy = Math.max(r[1] - p[1], 0, p[1] - r[3]);
  return Math.hypot(dx, dy);
}

@Component({
  selector: 'app-pdf-page-view',
  imports: [NgIcon],
  templateUrl: './pdf-page-view.component.html',
  styleUrl: './pdf-page-view.component.css',
})
export class PdfPageViewComponent {
  protected readonly store = inject(PdfEditorStore);
  private readonly host = inject<ElementRef<HTMLElement>>(ElementRef);
  private readonly destroyRef = inject(DestroyRef);

  readonly page = input.required<number>();
  readonly size = input.required<PageSize>();

  protected readonly featherCheck = featherCheck;
  protected readonly featherX = featherX;
  protected readonly featherTrash2 = featherTrash2;
  protected readonly featherAlertTriangle = featherAlertTriangle;

  private readonly canvas = viewChild<ElementRef<HTMLCanvasElement>>('canvas');
  private readonly lineInput = viewChild<ElementRef<HTMLInputElement>>('lineInput');
  private readonly draftInput = viewChild<ElementRef<HTMLTextAreaElement>>('draftInput');
  private readonly layer = viewChild<ElementRef<HTMLElement>>('layer');

  private readonly visible = signal(false);
  protected readonly rendered = signal(false);
  private paintToken = 0;
  private paintTimer: ReturnType<typeof setTimeout> | null = null;

  protected readonly lines = signal<TextLineInfo[]>([]);
  protected readonly annotations = signal<AnnotationInfo[]>([]);
  protected readonly widgets = signal<WidgetInfo[]>([]);

  protected readonly zoom = this.store.zoom;
  protected readonly tool = this.store.tool;
  protected readonly width = computed(() => this.size().width * this.zoom());
  protected readonly height = computed(() => this.size().height * this.zoom());
  private readonly version = computed(() => `${this.store.docVersion()}:${this.store.pageVersions()[this.page()] ?? 0}`);

  protected readonly usesLayer = computed(() => !['select', 'editText'].includes(this.tool()));
  protected readonly layerCursor = computed(() => (this.tool() === 'addText' ? 'text' : this.tool() === 'note' ? 'copy' : 'crosshair'));

  protected readonly lineBoxes = computed(() => {
    const z = this.zoom();
    return this.lines().filter(l => l.horizontal).map(line => ({
      line,
      left: line.bbox[0] * z,
      top: line.bbox[1] * z,
      width: (line.bbox[2] - line.bbox[0]) * z,
      height: (line.bbox[3] - line.bbox[1]) * z,
    }));
  });

  protected readonly markers = computed(() => {
    const z = this.zoom();
    return this.store.substitutions().filter(m => m.page === this.page()).map(marker => ({
      marker,
      left: marker.bbox[2] * z + 4,
      top: (marker.bbox[1] + marker.bbox[3]) / 2 * z - 10,
      label: `Some characters are drawn in ${marker.fonts.join(', ')}: the original font doesn't have them. Click to pick a font for the line.`,
    }));
  });

  // Editing an existing line.
  protected readonly editing = signal<LineEdit | null>(null);
  protected readonly editView = computed(() => {
    const edit = this.editing();
    if (!edit || this.tool() !== 'editText') {
      return null;
    }
    const z = this.zoom();
    const line = edit.line;
    const family = edit.font === 'original' ? line.font.family : edit.font;
    const bold = edit.font === 'original' ? line.font.bold : edit.bold;
    const italic = edit.font === 'original' ? line.font.italic : edit.italic;
    return {
      left: line.rtl ? null : line.bbox[0] * z - 2,
      right: line.rtl ? (this.size().width - line.bbox[2]) * z - 2 : null,
      top: line.bbox[1] * z - 2,
      minWidth: (line.bbox[2] - line.bbox[0]) * z + 4,
      height: (line.bbox[3] - line.bbox[1]) * z + 4,
      fontSize: line.size * z,
      fontFamily: CSS_FONT_FAMILY[family],
      fontWeight: bold ? 700 : 400,
      fontStyle: italic ? 'italic' : 'normal',
      color: rgbToCss(line.color),
      dir: line.rtl ? 'rtl' : 'ltr',
      original: `${line.fontName} · ${line.size}pt`,
      custom: edit.font !== 'original',
    };
  });

  // A new text box.
  protected readonly draft = signal<TextDraft | null>(null);
  protected readonly draftView = computed(() => {
    const draft = this.draft();
    if (!draft || this.tool() !== 'addText') {
      return null;
    }
    const z = this.zoom();
    const settings = this.store.addTextSettings();
    const match = draft.match;
    const family = match ? match.font.family : (settings.family === 'match' ? 'sans' : settings.family);
    const size = match ? match.size : settings.size;
    const rtl = startsRtl(draft.text);
    return {
      left: rtl ? null : draft.x * z,
      right: rtl ? (this.size().width - draft.x) * z : null,
      top: draft.y * z,
      fontSize: size * z,
      fontFamily: CSS_FONT_FAMILY[family],
      fontWeight: (match ? match.font.bold : settings.bold) ? 700 : 400,
      fontStyle: (match ? match.font.italic : settings.italic) ? 'italic' : 'normal',
      color: match ? rgbToCss(match.color) : settings.color,
      caption: match ? `Matching ${match.fontName} · ${match.size}pt` : `${family[0].toUpperCase()}${family.slice(1)} · ${size}pt`,
      rtl,
    };
  });
  private committingDraft = false;

  // Dragging out a rectangle, a highlight or a stroke.
  private readonly drag = signal<Drag | null>(null);
  protected readonly dragBox = computed(() => {
    const drag = this.drag();
    if (!drag || this.tool() === 'draw') {
      return null;
    }
    const z = this.zoom();
    const r = normalise(drag.start, drag.current);
    return {left: r[0] * z, top: r[1] * z, width: (r[2] - r[0]) * z, height: (r[3] - r[1]) * z};
  });
  protected readonly strokePoints = computed(() => {
    const drag = this.drag();
    if (!drag || this.tool() !== 'draw') {
      return null;
    }
    const z = this.zoom();
    return drag.points.map(p => `${p[0] * z},${p[1] * z}`).join(' ');
  });
  protected readonly strokeWidth = computed(() => this.store.drawWidth() * this.zoom());

  // Annotations and form fields (select tool).
  protected readonly selectedAnnotation = signal<number | null>(null);
  private readonly move = signal<AnnotationMove | null>(null);
  protected readonly annotationBoxes = computed(() => {
    const z = this.zoom();
    const move = this.move();
    return this.annotations().map(annotation => {
      const offset = move && move.index === annotation.index ? move.offset : [0, 0];
      return {
        annotation,
        left: (annotation.rect[0] + offset[0]) * z,
        top: (annotation.rect[1] + offset[1]) * z,
        width: Math.max((annotation.rect[2] - annotation.rect[0]) * z, 12),
        height: Math.max((annotation.rect[3] - annotation.rect[1]) * z, 12),
        selected: annotation.index === this.selectedAnnotation(),
        label: annotation.contents
          ? `${ANNOTATION_NAMES[annotation.type] ?? annotation.type}: ${annotation.contents}`
          : (ANNOTATION_NAMES[annotation.type] ?? annotation.type),
        name: ANNOTATION_NAMES[annotation.type] ?? annotation.type,
      };
    });
  });
  protected readonly widgetBoxes = computed(() => {
    const z = this.zoom();
    return this.widgets().filter(w => !w.readOnly && ['text', 'checkbox', 'radio', 'choice'].includes(w.kind)).map(widget => {
      const height = (widget.rect[3] - widget.rect[1]) * z;
      return {
        widget,
        left: widget.rect[0] * z,
        top: widget.rect[1] * z,
        width: (widget.rect[2] - widget.rect[0]) * z,
        height,
        fontSize: Math.max(10, Math.min(height * 0.65, 14 * z)),
      };
    });
  });

  constructor() {
    afterNextRender(() => {
      const nearby = new IntersectionObserver(entries => this.visible.set(entries[0].isIntersecting), {rootMargin: '800px 0px'});
      const current = new IntersectionObserver(entries => {
        if (entries[0].isIntersecting) {
          this.store.currentPage.set(this.page());
        }
      }, {threshold: 0.5});
      nearby.observe(this.host.nativeElement);
      current.observe(this.host.nativeElement);
      this.destroyRef.onDestroy(() => {
        nearby.disconnect();
        current.disconnect();
      });
    });

    effect(() => {
      if (!this.visible()) {
        return;
      }
      const version = this.version();
      const zoom = this.zoom();
      untracked(() => this.schedulePaint(version, zoom));
    });

    effect(() => {
      if (!this.visible()) {
        return;
      }
      this.version();
      const tool = this.tool();
      untracked(() => this.loadOverlays(tool));
    });

    this.destroyRef.onDestroy(() => {
      if (this.paintTimer) {
        clearTimeout(this.paintTimer);
      }
    });
  }

  private schedulePaint(version: string, zoom: number): void {
    if (this.paintTimer) {
      clearTimeout(this.paintTimer);
    }
    // Zooming re-renders once the zoom settles; until then the old bitmap is stretched.
    const delay = this.rendered() ? 120 : 0;
    this.paintTimer = setTimeout(() => this.paint(version, zoom), delay);
  }

  private async paint(version: string, zoom: number): Promise<void> {
    const token = ++this.paintToken;
    const size = this.size();
    let scale = zoom * Math.min(window.devicePixelRatio || 1, 3);
    const pixels = size.width * size.height * scale * scale;
    if (pixels > MAX_PIXELS) {
      scale *= Math.sqrt(MAX_PIXELS / pixels);
    }
    try {
      const result = await this.store.render(this.page(), scale);
      const canvas = this.canvas()?.nativeElement;
      if (token !== this.paintToken || !canvas || version !== this.version()) {
        return;
      }
      canvas.width = result.width;
      canvas.height = result.height;
      canvas.getContext('2d')?.putImageData(new ImageData(new Uint8ClampedArray(result.pixels), result.width, result.height), 0, 0);
      this.rendered.set(true);
    } catch {
      // The page went away (a page operation); the next version renders it again.
    }
  }

  private async loadOverlays(tool: string): Promise<void> {
    const page = this.page();
    try {
      if (tool === 'editText' || tool === 'addText') {
        this.lines.set(await this.store.textLines(page));
      }
      if (tool === 'select') {
        const [annotations, widgets] = await Promise.all([this.store.annotations(page), this.store.widgets(page)]);
        this.annotations.set(annotations);
        this.widgets.set(widgets);
      }
    } catch {
      this.lines.set([]);
      this.annotations.set([]);
      this.widgets.set([]);
    }
  }

  private toPage(event: PointerEvent | MouseEvent): Point {
    const rect = (this.layer()?.nativeElement ?? this.host.nativeElement).getBoundingClientRect();
    const z = this.zoom();
    return [(event.clientX - rect.left) / z, (event.clientY - rect.top) / z];
  }

  // Editing existing text

  protected startEdit(line: TextLineInfo): void {
    this.draft.set(null);
    this.editing.set({line, text: line.text, font: 'original', bold: line.font.bold, italic: line.font.italic});
    setTimeout(() => this.lineInput()?.nativeElement.focus());
  }

  protected editMarker(marker: SubstitutionMarker): void {
    this.store.tool.set('editText');
    setTimeout(async () => {
      const lines = await this.store.textLines(this.page());
      this.lines.set(lines);
      const centre: Point = [(marker.bbox[0] + marker.bbox[2]) / 2, (marker.bbox[1] + marker.bbox[3]) / 2];
      const line = lines.find(l => distanceToRect(centre, l.bbox) === 0) ?? lines.find(l => distanceToRect(centre, l.bbox) < 4);
      if (line) {
        this.startEdit(line);
        this.editing.update(e => (e ? {...e, font: line.font.family} : e));
      }
    });
  }

  protected setEditText(text: string): void {
    this.editing.update(e => (e ? {...e, text} : e));
  }

  protected setEditFont(font: string): void {
    this.editing.update(e => (e ? {...e, font: font as LineEdit['font']} : e));
  }

  protected toggleEditBold(): void {
    this.editing.update(e => (e ? {...e, bold: !e.bold} : e));
  }

  protected toggleEditItalic(): void {
    this.editing.update(e => (e ? {...e, italic: !e.italic} : e));
  }

  protected cancelEdit(): void {
    this.editing.set(null);
  }

  protected async commitEdit(): Promise<void> {
    const edit = this.editing();
    if (!edit) {
      return;
    }
    if (edit.text === edit.line.text && edit.font === 'original') {
      this.editing.set(null);
      return;
    }
    const override = edit.font === 'original' ? null : {family: edit.font, bold: edit.bold, italic: edit.italic};
    this.editing.set(null);
    await this.store.editLine(this.page(), edit.line, edit.text, override);
  }

  protected async deleteLine(): Promise<void> {
    const edit = this.editing();
    if (!edit) {
      return;
    }
    this.editing.set(null);
    await this.store.editLine(this.page(), edit.line, '', null);
  }

  protected onEditKey(event: KeyboardEvent): void {
    if (event.key === 'Enter') {
      event.preventDefault();
      void this.commitEdit();
    } else if (event.key === 'Escape') {
      this.cancelEdit();
    }
  }

  // Adding text

  private nearestLine(point: Point): TextLineInfo | null {
    let best: TextLineInfo | null = null;
    let bestDistance = 200;
    for (const line of this.lines()) {
      const d = distanceToRect(point, line.bbox);
      if (line.horizontal && d < bestDistance) {
        best = line;
        bestDistance = d;
      }
    }
    return best;
  }

  private startDraft(point: Point): void {
    this.editing.set(null);
    const match = this.store.addTextSettings().family === 'match' ? this.nearestLine(point) : null;
    const size = match ? match.size : this.store.addTextSettings().size;
    this.draft.set({x: point[0], y: point[1] - size * 0.6, text: '', match});
    setTimeout(() => this.draftInput()?.nativeElement.focus());
  }

  protected setDraftText(text: string): void {
    this.draft.update(d => (d ? {...d, text} : d));
  }

  protected async commitDraft(): Promise<void> {
    const draft = this.draft();
    if (!draft || this.committingDraft) {
      return;
    }
    this.draft.set(null);
    if (draft.text.trim() === '') {
      return;
    }
    this.committingDraft = true;
    try {
      const settings = this.store.addTextSettings();
      const style = draft.match
        ? {kind: 'match' as const, lineIndex: draft.match.index}
        : {
          kind: 'custom' as const,
          style: {
            font: {family: settings.family === 'match' ? 'sans' as const : settings.family, bold: settings.bold, italic: settings.italic},
            size: settings.size,
            color: hexToRgb(settings.color),
          },
        };
      const size = draft.match ? draft.match.size : settings.size;
      const rtl = startsRtl(draft.text);
      const lines = draft.text.split('\n');
      const width = Math.max(...lines.map(l => l.length)) * size * 0.48;
      const bbox: Rect = rtl
        ? [draft.x - width, draft.y, draft.x, draft.y + lines.length * size * 1.25]
        : [draft.x, draft.y, draft.x + width, draft.y + lines.length * size * 1.25];
      await this.store.addText(this.page(), [draft.x, draft.y + size * BASELINE_OFFSET], rtl, draft.text, style, bbox);
    } finally {
      this.committingDraft = false;
    }
  }

  protected onDraftBlur(): void {
    // An empty box stays open until another click replaces it.
    if (this.draft()?.text.trim()) {
      void this.commitDraft();
    }
  }

  protected onDraftKey(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      void this.commitDraft();
    } else if (event.key === 'Escape') {
      this.draft.set(null);
    }
  }

  // The drawing layer: erase, markup, draw, sign, note, add text

  protected onLayerDown(event: PointerEvent): void {
    if (event.button !== 0) {
      return;
    }
    const point = this.toPage(event);
    const tool = this.tool();
    if (tool === 'addText') {
      event.preventDefault();
      if (this.draft()) {
        void this.commitDraft();
      }
      this.startDraft(point);
      return;
    }
    if (tool === 'note') {
      void this.store.addNote(this.page(), point);
      return;
    }
    (event.target as HTMLElement).setPointerCapture(event.pointerId);
    this.drag.set({start: point, current: point, points: [point]});
  }

  protected onLayerMove(event: PointerEvent): void {
    const drag = this.drag();
    if (!drag) {
      return;
    }
    const point = this.toPage(event);
    this.drag.set({...drag, current: point, points: this.tool() === 'draw' ? [...drag.points, point] : drag.points});
  }

  protected async onLayerUp(event: PointerEvent): Promise<void> {
    const drag = this.drag();
    if (!drag) {
      return;
    }
    this.drag.set(null);
    const end = this.toPage(event);
    const rect = normalise(drag.start, end);
    const tiny = rect[2] - rect[0] < 3 && rect[3] - rect[1] < 3;
    const page = this.page();
    switch (this.tool()) {
      case 'erase':
        if (!tiny) {
          await this.store.eraseArea(page, rect);
        }
        break;
      case 'markup':
        await this.store.addMarkup(page, drag.start, end);
        break;
      case 'draw':
        if (drag.points.length > 1) {
          await this.store.addInk(page, [...drag.points, end]);
        }
        break;
      case 'sign':
        await this.placeSignature(tiny ? null : rect, drag.start);
        break;
    }
  }

  private async placeSignature(rect: Rect | null, at: Point): Promise<void> {
    const signature = this.store.signature();
    if (!signature) {
      return;
    }
    const image = new Image();
    image.src = signature;
    await image.decode();
    const aspect = image.height / Math.max(image.width, 1);
    let target: Rect;
    if (rect) {
      // Fit inside the box the user dragged, centred, without stretching.
      const boxWidth = rect[2] - rect[0];
      const boxHeight = rect[3] - rect[1];
      const width = Math.min(boxWidth, boxHeight / aspect);
      const height = width * aspect;
      const x = rect[0] + (boxWidth - width) / 2;
      const y = rect[1] + (boxHeight - height) / 2;
      target = [x, y, x + width, y + height];
    } else {
      const width = 160;
      const height = width * aspect;
      target = [at[0] - width / 2, at[1] - height / 2, at[0] + width / 2, at[1] + height / 2];
    }
    await this.store.addSignature(this.page(), target);
  }

  // Annotations

  protected selectAnnotation(index: number, event: PointerEvent): void {
    event.stopPropagation();
    this.selectedAnnotation.set(index);
    const annotation = this.annotations().find(a => a.index === index);
    if (annotation?.movable) {
      (event.target as HTMLElement).setPointerCapture(event.pointerId);
      this.move.set({index, start: this.toPage(event), offset: [0, 0]});
    }
  }

  protected onAnnotationMove(event: PointerEvent): void {
    const move = this.move();
    if (!move) {
      return;
    }
    const point = this.toPage(event);
    this.move.set({...move, offset: [point[0] - move.start[0], point[1] - move.start[1]]});
  }

  protected async onAnnotationUp(): Promise<void> {
    const move = this.move();
    this.move.set(null);
    if (!move || Math.hypot(move.offset[0], move.offset[1]) < 2) {
      return;
    }
    const annotation = this.annotations().find(a => a.index === move.index);
    if (annotation) {
      const [x0, y0, x1, y1] = annotation.rect;
      const [dx, dy] = move.offset;
      await this.store.moveAnnotation(this.page(), move.index, [x0 + dx, y0 + dy, x1 + dx, y1 + dy]);
    }
  }

  protected async deleteSelectedAnnotation(): Promise<void> {
    const index = this.selectedAnnotation();
    if (index !== null) {
      this.selectedAnnotation.set(null);
      await this.store.deleteAnnotation(this.page(), index);
    }
  }

  protected clearSelection(): void {
    this.selectedAnnotation.set(null);
  }

  // Form fields

  protected async commitField(widget: WidgetInfo, value: string): Promise<void> {
    if (value !== widget.value) {
      await this.store.setWidgetValue(this.page(), widget.index, value);
    }
  }

  protected async toggleField(widget: WidgetInfo): Promise<void> {
    await this.store.setWidgetValue(this.page(), widget.index, !widget.checked);
  }
}
