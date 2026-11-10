import {
  afterNextRender,
  Component,
  HostListener,
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
  sans: 'Arial, Helvetica, sans-serif',
  serif: '"Times New Roman", Times, serif',
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
  // Set when the editor was opened from a substitution warning: the bundled fonts the line uses.
  substitutedFonts: string[] | null;
  // Fonts on this computer that would draw the new characters exactly, offered before saving.
  localFontOffer?: string[];
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
  private readonly log = this.store.log;
  // The page version an editor or text box was opened on.
  private openedAtVersion = '';
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

  protected readonly usesLayer = computed(() => !['select', 'editText', 'move'].includes(this.tool()));
  // Fill & select shares Move text's line layer: click a line to select it, drag to move it.
  protected readonly linesMovable = computed(() => this.tool() === 'move' || this.tool() === 'select');
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
  // A saved edit's box stays, read-only, until the page has re-rendered with the new line, so the old line
  // doesn't flash back in between. Holds the version the page had when the edit was saved.
  protected readonly editSavedAt = signal<string | null>(null);
  // The CSS family of the PDF's own font, once loaded, keyed by PDF font name.
  private readonly loadedFonts = signal<Record<string, string>>({});
  protected readonly editView = computed(() => {
    const edit = this.editing();
    if (!edit || (this.tool() !== 'editText' && this.tool() !== 'select')) {
      return null;
    }
    const z = this.zoom();
    const line = edit.line;
    const family = edit.font === 'original' ? line.font.family : edit.font;
    const ownFont = edit.font === 'original' ? this.loadedFonts()[line.pdfFontName] : undefined;
    const bold = edit.font === 'original' ? line.font.bold : edit.bold;
    const italic = edit.font === 'original' ? line.font.italic : edit.italic;
    const fontFamily = ownFont ? `"${ownFont}", ${CSS_FONT_FAMILY[family]}` : CSS_FONT_FAMILY[family];
    const fontWeight = bold && !ownFont ? 700 : 400;
    const fontStyle = italic && !ownFont ? 'italic' : 'normal';
    const font = `${fontStyle} ${fontWeight} ${line.size * z}px ${fontFamily}`;
    const spacing = edit.font === 'original' ? this.matchingSpacing(line, font, z) : {word: 0, letter: 0};
    const height = (line.bbox[3] - line.bbox[1]) * z + 4;
    return {
      // Less the input's border and padding, so its text starts where the line's does.
      left: line.rtl ? null : line.bbox[0] * z - 3,
      right: line.rtl ? (this.size().width - line.bbox[2]) * z - 3 : null,
      top: this.boxTopForBaseline(line, font, height, z),
      minWidth: (line.bbox[2] - line.bbox[0]) * z + 4,
      height,
      fontSize: line.size * z,
      fontFamily,
      // The PDF's font is already the right weight and slant; asking for more would fake it on top.
      fontWeight,
      fontStyle,
      wordSpacing: spacing.word,
      letterSpacing: spacing.letter,
      color: rgbToCss(line.color),
      dir: line.rtl ? 'rtl' : 'ltr',
      saving: this.editSavedAt() !== null,
      localFontOffer: edit.localFontOffer
        ? `Some of these characters aren't in this PDF's copy of ${edit.localFontOffer.map(n => n.replace(',', ' ')).join(', ')}. Use the copy installed on this computer, so they match exactly? Your browser will ask once.`
        : null,
      original: `${line.fontName} · ${line.size}pt`,
      custom: edit.font !== 'original',
      substitutionNote: edit.substitutedFonts
        ? `The original font lacks some of these characters, so they're drawn in ${edit.substitutedFonts.join(', ')}. To draw the whole line in one font, pick it here.`
        : null,
    };
  });

  private measureContext: CanvasRenderingContext2D | null = null;

  // The PDF spaces a line its own way (justified, kerned, positioned glyph by glyph), so the browser's layout of
  // the same text in the same font can come out wider or narrower, and the line would jump as the edit box
  // opens. The difference is spread over the spaces (or, without any, the characters) so the box's text ends
  // where the line does.
  private matchingSpacing(line: TextLineInfo, font: string, z: number): {word: number; letter: number} {
    this.measureContext ??= document.createElement('canvas').getContext('2d');
    const context = this.measureContext;
    const characters = Array.from(line.text).length;
    if (!context || characters < 2 || line.textWidth <= 0) {
      return {word: 0, letter: 0};
    }
    context.font = font;
    const difference = line.textWidth * z - context.measureText(line.text).width;
    const spaces = Array.from(line.text).filter(c => c === ' ').length;
    const limit = line.size * z * 0.5;
    if (spaces > 0) {
      const word = difference / spaces;
      return Math.abs(word) <= limit ? {word, letter: 0} : {word: 0, letter: 0};
    }
    const letter = difference / characters;
    return Math.abs(letter) <= limit ? {word: 0, letter} : {word: 0, letter: 0};
  }

  // Where the edit box goes so its text's baseline lands on the line's. An input centres its text, so the
  // baseline sits half the leftover height plus the font's ascent below the top of its content (inside a 1px
  // border; .paper-input has no vertical padding).
  private boxTopForBaseline(line: TextLineInfo, font: string, height: number, z: number): number {
    this.measureContext ??= document.createElement('canvas').getContext('2d');
    const context = this.measureContext;
    if (!context) {
      return line.bbox[1] * z - 2;
    }
    context.font = font;
    const metrics = context.measureText(line.text);
    const ascent = metrics.fontBoundingBoxAscent;
    const descent = metrics.fontBoundingBoxDescent;
    const border = 1;
    const content = height - 2 * border;
    return line.baseline * z - border - (content - (ascent + descent)) / 2 - ascent;
  }

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
    const ownFont = match ? this.loadedFonts()[match.pdfFontName] : undefined;
    const size = match ? match.size : settings.size;
    const rtl = startsRtl(draft.text);
    return {
      left: rtl ? null : draft.x * z,
      right: rtl ? (this.size().width - draft.x) * z : null,
      top: draft.y * z,
      fontSize: size * z,
      fontFamily: ownFont ? `"${ownFont}", ${CSS_FONT_FAMILY[family]}` : CSS_FONT_FAMILY[family],
      fontWeight: (match ? match.font.bold : settings.bold) && !ownFont ? 700 : 400,
      fontStyle: (match ? match.font.italic : settings.italic) && !ownFont ? 'italic' : 'normal',
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

  // Moving lines (move tool).
  protected readonly selectedLines = signal<number[]>([]);
  protected readonly moveOffset = signal<Point>([0, 0]);
  // Snapshots of the selected lines cut from the rendered page: `cover` is where the line was (painted over),
  // `rect` where the snapshot sits before the drag offset is added.
  protected readonly ghosts = signal<{index: number; url: string; cover: Rect; rect: Rect}[]>([]);
  // Between dropping lines and the page catching up: the selection outline waits for the moved lines.
  private readonly settling = signal(false);
  private moveGesture: {kind: 'drag'; start: Point} | {kind: 'box'; start: Point; current: Point; additive: boolean} | null = null;
  private nudgeTimer: ReturnType<typeof setTimeout> | null = null;
  private pendingReselect: {text: string; bbox: Rect}[] = [];
  private clearGhostsOnPaint = false;

  protected readonly moveView = computed(() => {
    const z = this.zoom();
    const selected = new Set(this.selectedLines());
    const [dx, dy] = this.moveOffset();
    const pad = 2;
    const box = (r: Rect) => ({left: (r[0] - pad) * z, top: (r[1] - pad) * z, width: (r[2] - r[0] + 2 * pad) * z, height: (r[3] - r[1] + 2 * pad) * z});
    return {
      lines: this.lines().filter(l => l.horizontal).map(line => ({line, selected: selected.has(line.index), ...box(line.bbox)})),
      selected: this.settling() ? [] : this.lines().filter(l => selected.has(l.index)).map(line => ({index: line.index, ...box([line.bbox[0] + dx, line.bbox[1] + dy, line.bbox[2] + dx, line.bbox[3] + dy])})),
      ghosts: this.ghosts().map(g => ({index: g.index, url: g.url, cover: box(g.cover), ...box([g.rect[0] + dx, g.rect[1] + dy, g.rect[2] + dx, g.rect[3] + dy])})),
    };
  });
  protected readonly selectionBox = signal<{left: number; top: number; width: number; height: number} | null>(null);

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

    // An open editor holds text from before the page changed (an undo, another edit); saving it would
    // fail or overwrite the change, so it closes.
    effect(() => {
      const version = this.version();
      untracked(() => {
        if (this.pendingReselect.length === 0 && version !== this.openedAtVersion) {
          this.selectedLines.set([]);
        }
        const edit = this.editSavedAt() === null ? this.editing() : null;
        const draft = this.draft();
        if ((edit || draft) && version !== this.openedAtVersion) {
          this.log.log('editor-closed-page-changed', {page: this.page(), editing: edit?.line.text ?? null, typed: edit?.text ?? draft?.text ?? null});
          this.editing.set(null);
          this.draft.set(null);
        }
      });
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
      if (this.clearGhostsOnPaint) {
        this.clearGhostsOnPaint = false;
        this.ghosts.set([]);
      }
      const savedAt = this.editSavedAt();
      if (savedAt !== null && version !== savedAt) {
        this.closeSavedEdit();
      }
    } catch {
      // The page went away (a page operation); the next version renders it again.
    }
  }

  private async loadOverlays(tool: string): Promise<void> {
    const page = this.page();
    try {
      if (tool === 'editText' || tool === 'addText' || tool === 'move' || tool === 'select') {
        const lines = await this.store.textLines(page);
        this.lines.set(lines);
        this.reselectMoved(lines);
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
    if (this.editSavedAt() !== null) {
      return;
    }
    this.log.log('line-click', {page: this.page(), line: {i: line.index, text: line.text, bbox: line.bbox, rtl: line.rtl, font: line.fontName, size: line.size}});
    this.openedAtVersion = this.version();
    this.loadFont(line);
    this.draft.set(null);
    this.selectedLines.set([]);
    this.editing.set({line, text: line.text, font: 'original', bold: line.font.bold, italic: line.font.italic, substitutedFonts: null});
    setTimeout(() => this.lineInput()?.nativeElement.focus());
  }

  protected editMarker(marker: SubstitutionMarker): void {
    const centre: Point = [(marker.bbox[0] + marker.bbox[2]) / 2, (marker.bbox[1] + marker.bbox[3]) / 2];
    void this.editLineAt(centre, marker.fonts);
  }

  // Fill & select's shortcut: double-click text to edit it right there, staying in Fill & select. Fields and
  // annotations keep their own clicks.
  protected onPaperDoubleClick(event: MouseEvent): void {
    const target = event.target as HTMLElement;
    if (this.tool() !== 'select' || target.closest('.annotation-target, .pdf-field, .line-input, .edit-toolbar')) {
      return;
    }
    void this.editLineAt(this.toPage(event), null);
  }

  // Opens the line at `point` for editing, if there is one: in place in Fill & select, otherwise in Edit text.
  private async editLineAt(point: Point, substitutedFonts: string[] | null): Promise<void> {
    const lines = await this.store.textLines(this.page());
    const line = lines.find(l => distanceToRect(point, l.bbox) === 0) ?? lines.find(l => distanceToRect(point, l.bbox) < 4);
    if (!line) {
      return;
    }
    window.getSelection()?.removeAllRanges();
    if (this.tool() !== 'select') {
      this.store.tool.set('editText');
    }
    this.lines.set(lines);
    this.startEdit(line);
    if (substitutedFonts) {
      this.editing.update(e => (e ? {...e, substitutedFonts} : e));
    }
  }

  private loadFont(line: TextLineInfo): void {
    if (this.loadedFonts()[line.pdfFontName]) {
      return;
    }
    void this.store.webFontFamily(this.page(), line.pdfFontName).then(family => {
      if (family) {
        this.loadedFonts.update(fonts => ({...fonts, [line.pdfFontName]: family}));
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
    if (this.editSavedAt() !== null) {
      return;
    }
    const edit = this.editing();
    this.log.log('edit-cancel', {page: this.page(), line: edit?.line.text, typed: edit?.text});
    this.editing.set(null);
  }

  protected async commitEdit(fontsSettled = false): Promise<void> {
    const edit = this.editing();
    if (!edit || this.editSavedAt() !== null || edit.localFontOffer) {
      return;
    }
    if (edit.text === edit.line.text && edit.font === 'original') {
      this.log.log('edit-unchanged', {page: this.page(), line: edit.line.text});
      this.editing.set(null);
      return;
    }
    if (!fontsSettled && edit.font === 'original' && !this.store.localFontsDeclined()) {
      const wanted = await this.store.localFontsWanted(this.page(), edit.line, edit.text);
      if (wanted.length > 0) {
        const permission = await this.store.localFontPermission();
        if (permission === 'prompt') {
          // Chrome asks only from a click, so the question goes in the box first.
          this.editing.update(e => (e ? {...e, localFontOffer: wanted} : e));
          return;
        }
        if (permission === 'granted') {
          await this.store.provideLocalFonts(wanted);
        }
      }
    }
    const override = edit.font === 'original' ? null : {family: edit.font, bold: edit.bold, italic: edit.italic};
    this.editSavedAt.set(this.version());
    const saved = await this.store.editLine(this.page(), edit.line, edit.text, override);
    if (!saved) {
      this.closeSavedEdit();
    }
  }

  protected async useLocalFonts(): Promise<void> {
    const offer = this.editing()?.localFontOffer;
    if (!offer) {
      return;
    }
    await this.store.provideLocalFonts(offer);
    this.editing.update(e => (e ? {...e, localFontOffer: undefined} : e));
    await this.commitEdit(true);
  }

  protected async useLookAlikes(): Promise<void> {
    this.store.declineLocalFonts();
    this.editing.update(e => (e ? {...e, localFontOffer: undefined} : e));
    await this.commitEdit(true);
  }

  private closeSavedEdit(): void {
    this.editSavedAt.set(null);
    this.editing.set(null);
  }

  protected async deleteLine(): Promise<void> {
    const edit = this.editing();
    if (!edit || this.editSavedAt() !== null) {
      return;
    }
    // An empty box keeps covering the line until the page re-renders without it.
    this.editing.set({...edit, text: ''});
    this.editSavedAt.set(this.version());
    const saved = await this.store.editLine(this.page(), edit.line, '', null);
    if (!saved) {
      this.closeSavedEdit();
    }
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
    this.openedAtVersion = this.version();
    this.editing.set(null);
    const match = this.store.addTextSettings().family === 'match' ? this.nearestLine(point) : null;
    const size = match ? match.size : this.store.addTextSettings().size;
    this.draft.set({x: point[0], y: point[1] - size * 0.6, text: '', match});
    if (match) {
      this.loadFont(match);
    }
    this.log.log('draft-start', {page: this.page(), point, match: match ? {i: match.index, text: match.text, font: match.fontName, size: match.size} : null});
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
      this.log.log('draft-cancel', {page: this.page(), typed: this.draft()?.text});
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
    this.log.log('page-press', {page: this.page(), tool, point});
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

  // Moving lines

  private lineAt(point: Point): TextLineInfo | null {
    return this.lines().find(l => l.horizontal && distanceToRect(point, l.bbox) < 2) ?? null;
  }

  private snapshotGhosts(): void {
    const canvas = this.canvas()?.nativeElement;
    if (!canvas || this.ghosts().length > 0) {
      return;
    }
    const scale = canvas.width / this.size().width;
    const pad = 2;
    const ghosts = this.lines().filter(l => this.selectedLines().includes(l.index)).map(line => {
      const rect: Rect = [line.bbox[0] - pad, line.bbox[1] - pad, line.bbox[2] + pad, line.bbox[3] + pad];
      const crop = document.createElement('canvas');
      crop.width = Math.max(1, Math.round((rect[2] - rect[0]) * scale));
      crop.height = Math.max(1, Math.round((rect[3] - rect[1]) * scale));
      crop.getContext('2d')?.drawImage(canvas, rect[0] * scale, rect[1] * scale, crop.width, crop.height, 0, 0, crop.width, crop.height);
      const bbox: Rect = [line.bbox[0], line.bbox[1], line.bbox[2], line.bbox[3]];
      return {index: line.index, url: crop.toDataURL(), cover: bbox, rect: bbox};
    });
    this.ghosts.set(ghosts);
  }

  protected onMoveDown(event: PointerEvent): void {
    // Until the page has caught up with the last move, a new gesture would start from stale snapshots.
    if (event.button !== 0 || this.committingMove || this.clearGhostsOnPaint) {
      return;
    }
    // A line edited in place in Fill & select is saved by clicking anywhere else, as in a text editor.
    if (this.tool() === 'select' && this.editing() && this.editSavedAt() === null) {
      void this.commitEdit();
      return;
    }
    const point = this.toPage(event);
    const line = this.lineAt(point);
    (event.target as HTMLElement).setPointerCapture(event.pointerId);
    if (line) {
      const selected = this.selectedLines();
      if (event.shiftKey) {
        this.selectedLines.set(selected.includes(line.index) ? selected.filter(i => i !== line.index) : [...selected, line.index]);
        return;
      }
      if (!selected.includes(line.index)) {
        this.selectedLines.set([line.index]);
      }
      this.moveGesture = {kind: 'drag', start: point};
    } else {
      if (!event.shiftKey) {
        this.selectedLines.set([]);
      }
      this.moveGesture = {kind: 'box', start: point, current: point, additive: event.shiftKey};
    }
  }

  protected onMovePointer(event: PointerEvent): void {
    const gesture = this.moveGesture;
    if (!gesture) {
      return;
    }
    const point = this.toPage(event);
    if (gesture.kind === 'drag') {
      this.snapshotGhosts();
      this.moveOffset.set([point[0] - gesture.start[0], point[1] - gesture.start[1]]);
    } else {
      gesture.current = point;
      const z = this.zoom();
      const r = normalise(gesture.start, point);
      this.selectionBox.set({left: r[0] * z, top: r[1] * z, width: (r[2] - r[0]) * z, height: (r[3] - r[1]) * z});
    }
  }

  protected async onMoveUp(): Promise<void> {
    const gesture = this.moveGesture;
    this.moveGesture = null;
    if (!gesture) {
      return;
    }
    if (gesture.kind === 'box') {
      this.selectionBox.set(null);
      const r = normalise(gesture.start, gesture.current);
      const inside = this.lines().filter(l => l.horizontal && l.bbox[0] < r[2] && r[0] < l.bbox[2] && l.bbox[1] < r[3] && r[1] < l.bbox[3]).map(l => l.index);
      this.selectedLines.set(gesture.additive ? [...new Set([...this.selectedLines(), ...inside])] : inside);
      this.log.log('move-select', {page: this.page(), count: this.selectedLines().length});
      return;
    }
    await this.commitMove();
  }

  private committingMove = false;

  private async commitMove(): Promise<void> {
    const [dx, dy] = this.moveOffset();
    if (Math.hypot(dx, dy) < 0.5) {
      this.ghosts.set([]);
      this.moveOffset.set([0, 0]);
      return;
    }
    const lines = this.lines().filter(l => this.selectedLines().includes(l.index));
    this.pendingReselect = lines.map(l => ({text: l.text, bbox: [l.bbox[0] + dx, l.bbox[1] + dy, l.bbox[2] + dx, l.bbox[3] + dy] as Rect}));
    this.openedAtVersion = this.version();
    this.committingMove = true;
    // The snapshots stay where they were dropped until the page has re-rendered, and the outline waits for
    // the moved lines to be found again; whichever comes first, nothing jumps back to the old place.
    this.ghosts.update(ghosts => ghosts.map(g => ({...g, rect: [g.rect[0] + dx, g.rect[1] + dy, g.rect[2] + dx, g.rect[3] + dy] as Rect})));
    this.moveOffset.set([0, 0]);
    this.settling.set(true);
    this.clearGhostsOnPaint = true;
    const moved = await this.store.moveLines(this.page(), lines, [dx, dy]);
    this.committingMove = false;
    if (!moved) {
      this.clearGhostsOnPaint = false;
      this.pendingReselect = [];
      this.settling.set(false);
      this.ghosts.set([]);
    }
  }

  // After a move the lines are extracted afresh; select the moved ones again so they can be nudged further.
  private reselectMoved(lines: TextLineInfo[]): void {
    if (this.pendingReselect.length === 0) {
      return;
    }
    const centre = (r: Rect): Point => [(r[0] + r[2]) / 2, (r[1] + r[3]) / 2];
    const found = this.pendingReselect.map(want => lines.find(l => l.text === want.text
      && Math.hypot(centre(l.bbox)[0] - centre(want.bbox)[0], centre(l.bbox)[1] - centre(want.bbox)[1]) < 6)?.index)
      .filter((i): i is number => i !== undefined);
    this.pendingReselect = [];
    this.openedAtVersion = this.version();
    this.selectedLines.set(found);
    this.settling.set(false);
  }

  @HostListener('window:keydown', ['$event'])
  protected onMoveKey(event: KeyboardEvent): void {
    if (!this.linesMovable() || this.selectedLines().length === 0 || this.committingMove || this.clearGhostsOnPaint
      || (event.target as HTMLElement | null)?.closest('input, textarea, select')) {
      return;
    }
    if (event.key === 'Escape') {
      this.selectedLines.set([]);
      return;
    }
    const step = event.shiftKey ? 10 : 1;
    const deltas: Record<string, Point> = {ArrowLeft: [-step, 0], ArrowRight: [step, 0], ArrowUp: [0, -step], ArrowDown: [0, step]};
    const delta = deltas[event.key];
    if (!delta) {
      return;
    }
    event.preventDefault();
    this.snapshotGhosts();
    this.moveOffset.update(([x, y]) => [x + delta[0], y + delta[1]]);
    if (this.nudgeTimer) {
      clearTimeout(this.nudgeTimer);
    }
    // Nudges collect into one move (and one undo step) once the keys go quiet.
    this.nudgeTimer = setTimeout(() => void this.commitMove(), 700);
  }

  // Annotations

  protected selectAnnotation(index: number, event: PointerEvent): void {
    event.stopPropagation();
    this.log.log('annotation-select', {page: this.page(), index});
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

  protected clearSelection(event: PointerEvent): void {
    this.selectedAnnotation.set(null);
    // Picking a form field or an annotation in Fill & select lets go of the selected text.
    if ((event.target as HTMLElement).closest('.pdf-field, .annotation-target')) {
      this.selectedLines.set([]);
    }
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
