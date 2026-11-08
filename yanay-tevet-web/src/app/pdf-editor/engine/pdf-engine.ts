import type {PDFDocument, PDFPage, PDFWidget} from 'mupdf';
import {hasRtl, startsRtl} from './bidi';
import {ExistingFontEncoder, FallbackFonts} from './font-encoders';
import {mupdf} from './mupdf-runtime';
import {
  AddTextStyle,
  AnnotationInfo,
  DocState,
  FontChoice,
  LineRef,
  MarkupType,
  OpenResult,
  PdfEngineApi,
  Point,
  Rect,
  RenderedPage,
  RgbColor,
  TextLineInfo,
  TextWriteResult,
  WidgetInfo,
  WidgetKind,
} from './pdf-engine.types';
import {dominantStyle, EditableLine, extractLines, fontChoiceOf, lineInfo, LineChar, toRgb} from './text-lines';
import {CharToWrite, FontRegistry, redact, writeText} from './text-writer';
import {webFontFromPdfFont} from './web-font';

const MOVABLE_ANNOTATIONS = new Set(['Stamp', 'Text', 'FreeText', 'Square', 'Circle']);
const HIDDEN_ANNOTATIONS = new Set(['Popup', 'Link', 'Widget']);

function inherit(char: string, from: LineChar | undefined): CharToWrite {
  return {char, style: from?.style ?? null, source: null};
}

function keep(c: LineChar, char: string): CharToWrite {
  return {char, style: c.style, source: {visualIndex: c.visualIndex, measuredAdvance: c.measuredAdvance}};
}

// Maps the new text onto the old line: characters an edit leaves alone (by longest common subsequence)
// keep their style and spacing; inserted ones take the style of the character before them.
export function diffChars(old: LineChar[], newText: string): CharToWrite[] {
  const next = Array.from(newText);
  const n = old.length;
  const m = next.length;
  const matchOf = new Array<number>(m).fill(-1);
  if (n * m <= 250_000) {
    const lengths = new Uint16Array((n + 1) * (m + 1));
    const at = (i: number, j: number) => i * (m + 1) + j;
    for (let i = n - 1; i >= 0; i--) {
      for (let j = m - 1; j >= 0; j--) {
        lengths[at(i, j)] = old[i].char === next[j]
          ? lengths[at(i + 1, j + 1)] + 1
          : Math.max(lengths[at(i + 1, j)], lengths[at(i, j + 1)]);
      }
    }
    let i = 0;
    let j = 0;
    while (i < n && j < m) {
      if (old[i].char === next[j]) {
        matchOf[j] = i;
        i++;
        j++;
      } else if (lengths[at(i + 1, j)] >= lengths[at(i, j + 1)]) {
        i++;
      } else {
        j++;
      }
    }
  } else {
    // A very long line: the common prefix and suffix are enough.
    let prefix = 0;
    while (prefix < n && prefix < m && old[prefix].char === next[prefix]) {
      matchOf[prefix] = prefix;
      prefix++;
    }
    let suffix = 0;
    while (suffix < n - prefix && suffix < m - prefix && old[n - 1 - suffix].char === next[m - 1 - suffix]) {
      matchOf[m - 1 - suffix] = n - 1 - suffix;
      suffix++;
    }
  }
  const firstMatch = matchOf.find(i => i >= 0);
  let previous: LineChar | undefined = firstMatch !== undefined ? old[firstMatch] : old[0];
  return next.map((char, j) => {
    if (matchOf[j] >= 0) {
      previous = old[matchOf[j]];
      return keep(previous, char);
    }
    return inherit(char, previous);
  });
}

function lineRedactionRect(line: EditableLine): Rect {
  const [x0, y0, x1, y1] = line.bbox;
  if (Math.abs(line.dir[1]) < 0.01) {
    const middle = (y0 + y1) / 2;
    const half = (y1 - y0) / 4;
    return [x0 + 0.2, middle - half, x1 - 0.2, middle + half];
  }
  const middle = (x0 + x1) / 2;
  const half = (x1 - x0) / 4;
  return [middle - half, y0 + 0.2, middle + half, y1 - 0.2];
}

// MuPDF lays out a single-line field holding non-Latin text one line too low, outside the field. Moves
// the baseline back to the middle of the field.
function fixSingleLineAppearance(widget: PDFWidget): void {
  const appearance = widget.getObject().get('AP').get('N');
  if (!appearance.isStream()) {
    return;
  }
  const bbox: number[] = [];
  appearance.get('BBox').forEach(v => bbox.push(v.asNumber()));
  if (bbox.length !== 4) {
    return;
  }
  const height = bbox[3] - bbox[1];
  const content = appearance.readStream().asString();
  const pattern = /(1 0 0 -1 -?[\d.]+ )(-?[\d.]+)( Tm)/g;
  const baselines = [...content.matchAll(pattern)].map(m => Number(m[2]));
  if (baselines.length === 0 || Math.max(...baselines) <= height) {
    return;
  }
  const size = Number(/\/\S+ ([\d.]+) Tf/.exec(content)?.[1] ?? 12);
  const shift = (height + size * 0.7) / 2 - Math.min(...baselines);
  // The text's clip box, drawn after the flip into top-down coordinates, is off by the same amount.
  const flip = content.indexOf(' cm\n');
  const head = flip >= 0 ? content.slice(0, flip) : content;
  const tail = flip >= 0 ? content.slice(flip) : '';
  const moved = tail
    .replace(pattern, (_m, before: string, y: string, after: string) => `${before}${(Number(y) + shift).toFixed(3)}${after}`)
    .replace(/(-?[\d.]+) (-?[\d.]+)( -?[\d.]+ -?[\d.]+ re)/g, (_m, x: string, y: string, rest: string) => `${x} ${(Number(y) + shift).toFixed(3)}${rest}`);
  appearance.writeStream(head + moved);
}

// Where a rewritten line is pinned: its start, or for right-to-left text its end, on the baseline.
function lineAnchor(line: EditableLine): Point {
  // Measured from the characters the line keeps: padding spaces trimmed off its ends don't count.
  const kept = new Set(line.logical.map(c => c.visualIndex));
  const visualFirst = line.visual.find(c => kept.has(c.visualIndex)) ?? line.visual[0];
  const visualLast = [...line.visual].reverse().find(c => kept.has(c.visualIndex)) ?? line.visual[line.visual.length - 1];
  const lastAdvance = Math.hypot(visualLast.quad[2] - visualLast.quad[0], visualLast.quad[3] - visualLast.quad[1]);
  return line.rtl
    ? [visualLast.origin[0] + lastAdvance * line.dir[0], visualLast.origin[1] + lastAdvance * line.dir[1]]
    : visualFirst.origin;
}

function widgetKind(widget: PDFWidget): WidgetKind {
  switch (widget.getFieldType()) {
    case 'checkbox':
      return 'checkbox';
    case 'radiobutton':
      return 'radio';
    case 'combobox':
    case 'listbox':
      return 'choice';
    case 'signature':
      return 'signature';
    case 'text':
      return 'text';
    default:
      return 'button';
  }
}

export class PdfEngine implements PdfEngineApi {
  private doc: PDFDocument | null = null;
  private registry: FontRegistry | null = null;
  private readonly lineCache = new Map<number, EditableLine[]>();
  private readonly fallbackFonts: FallbackFonts;

  constructor(loadFontFile: (name: string) => Promise<ArrayBuffer>) {
    this.fallbackFonts = new FallbackFonts(loadFontFile);
    mupdf().installLoadFontFunction((_name, script, bold) => (script ? this.fallbackFonts.fontForScript(script, bold) : null));
  }

  private get document(): PDFDocument {
    if (!this.doc) {
      throw new Error('No document is open');
    }
    return this.doc;
  }

  private get fonts(): FontRegistry {
    if (!this.registry) {
      throw new Error('No document is open');
    }
    return this.registry;
  }

  private loadPage(index: number): PDFPage {
    return this.document.loadPage(index);
  }

  private lines(page: number): EditableLine[] {
    let lines = this.lineCache.get(page);
    if (!lines) {
      lines = extractLines(this.loadPage(page));
      this.lineCache.set(page, lines);
    }
    return lines;
  }

  private operation<T>(name: string, structural: boolean, fn: () => T): T {
    const doc = this.document;
    doc.beginOperation(name);
    try {
      const result = fn();
      doc.endOperation();
      return result;
    } catch (error) {
      doc.abandonOperation();
      throw error;
    } finally {
      this.lineCache.clear();
      if (structural) {
        this.fonts.resetPageFonts();
      }
    }
  }

  async open(data: ArrayBuffer): Promise<OpenResult> {
    const m = mupdf();
    const doc = m.Document.openDocument(new Uint8Array(data), 'application/pdf').asPDF();
    if (!doc) {
      throw new Error('This file is not a PDF');
    }
    this.doc = doc;
    this.registry = new FontRegistry(doc, this.fallbackFonts);
    this.lineCache.clear();
    if (doc.needsPassword()) {
      return {needsPassword: true};
    }
    doc.enableJournal();
    return {needsPassword: false};
  }

  async authenticate(password: string): Promise<boolean> {
    const ok = this.document.authenticatePassword(password) !== 0;
    if (ok) {
      this.document.enableJournal();
    }
    return ok;
  }

  async state(): Promise<DocState> {
    const doc = this.document;
    const pageCount = doc.countPages();
    const pageSizes = [];
    for (let i = 0; i < pageCount; i++) {
      const [x0, y0, x1, y1] = doc.loadPage(i).getBounds();
      pageSizes.push({width: x1 - x0, height: y1 - y0});
    }
    return {pageCount, pageSizes, canUndo: doc.canUndo(), canRedo: doc.canRedo()};
  }

  async render(page: number, scale: number): Promise<RenderedPage> {
    const m = mupdf();
    const pixmap = this.loadPage(page).toPixmap(m.Matrix.scale(scale, scale), m.ColorSpace.DeviceRGB, false, true);
    const width = pixmap.getWidth();
    const height = pixmap.getHeight();
    const stride = pixmap.getStride();
    const rgb = pixmap.getPixels();
    const rgba = new Uint8ClampedArray(width * height * 4);
    for (let y = 0; y < height; y++) {
      let source = y * stride;
      let target = y * width * 4;
      for (let x = 0; x < width; x++) {
        rgba[target] = rgb[source];
        rgba[target + 1] = rgb[source + 1];
        rgba[target + 2] = rgb[source + 2];
        rgba[target + 3] = 255;
        source += 3;
        target += 4;
      }
    }
    pixmap.destroy();
    return {width, height, pixels: rgba.buffer};
  }

  async textLines(page: number): Promise<TextLineInfo[]> {
    return this.lines(page).map((line, i) => lineInfo(line, i));
  }

  async webFont(page: number, fontName: string): Promise<ArrayBuffer | null> {
    const pdfPage = this.loadPage(page);
    for (const ref of this.fonts.fontObjectsNamed(pdfPage, fontName)) {
      const encoder = ExistingFontEncoder.fromFontObject(ref);
      const font = webFontFromPdfFont(ref, encoder?.unicodeMap() ?? null);
      if (font) {
        return copyBuffer(font);
      }
    }
    return null;
  }

  // The bundled fonts an edit will need: one per style whose own font lacks one of its characters.
  private fallbackNeeds(page: number, chars: CharToWrite[]): FontChoice[] {
    const pdfPage = this.loadPage(page);
    const needs = new Map<string, FontChoice>();
    for (const c of chars) {
      if (c.char.trim() === '') {
        continue;
      }
      const codePoint = c.char.codePointAt(0)!;
      const own = c.style ? this.fonts.existingFor(page, pdfPage, c.style.font, [codePoint]) : null;
      if (!own?.encode(codePoint)) {
        const choice = c.style ? fontChoiceOf(c.style.font) : {family: 'sans' as const, bold: false, italic: false};
        needs.set(`${choice.family}|${choice.bold}|${choice.italic}`, choice);
      }
    }
    return [...needs.values()];
  }

  private findLine(page: number, lineIndex: number, expectedText: string): EditableLine {
    const line = this.lines(page)[lineIndex];
    if (!line || line.text !== expectedText) {
      throw new Error('The page changed; pick the line again');
    }
    return line;
  }

  async editLine(page: number, lineIndex: number, expectedText: string, newText: string, fontOverride: FontChoice | null): Promise<TextWriteResult> {
    const line = this.findLine(page, lineIndex, expectedText);
    const style = dominantStyle(line);
    const chars = diffChars(line.logical, newText);
    await this.fallbackFonts.prepare(fontOverride ? [fontOverride] : this.fallbackNeeds(page, chars));

    const anchor = lineAnchor(line);

    const outcome = this.operation('Edit text', false, () => {
      const pdfPage = this.loadPage(page);
      this.fonts.warm(page, pdfPage, line.logical);
      redact(pdfPage, lineRedactionRect(line), false);
      if (newText.trim() === '') {
        return {substitutedFonts: [], missingCharacters: []};
      }
      return writeText(this.document, page, pdfPage, this.fonts, {
        chars,
        rtl: line.rtl,
        anchor,
        anchorIsEnd: line.rtl,
        dir: line.dir,
        override: fontOverride ? {font: fontOverride, size: style.size, color: toRgb(style.color)} : null,
        existingFontsLabelByShape: line.labelsByShape,
      });
    });
    return {...outcome, state: await this.state()};
  }

  async moveLines(page: number, lines: LineRef[], offset: Point): Promise<DocState> {
    const targets = lines.map(ref => this.findLine(page, ref.index, ref.text));
    await this.fallbackFonts.prepare(this.fallbackNeeds(page, targets.flatMap(t => t.logical.map(c => keep(c, c.char)))));
    this.operation('Move text', false, () => {
      const pdfPage = this.loadPage(page);
      for (const target of targets) {
        this.fonts.warm(page, pdfPage, target.logical);
      }
      // Every line comes off before any goes back, so a line moved onto another's old place survives.
      for (const target of targets) {
        redact(pdfPage, lineRedactionRect(target), false);
      }
      for (const target of targets) {
        const anchor = lineAnchor(target);
        writeText(this.document, page, pdfPage, this.fonts, {
          chars: target.logical.map(c => keep(c, c.char)),
          rtl: target.rtl,
          anchor: [anchor[0] + offset[0], anchor[1] + offset[1]],
          anchorIsEnd: target.rtl,
          dir: target.dir,
          override: null,
          existingFontsLabelByShape: target.labelsByShape,
          keepSpacing: true,
        });
      }
    });
    return this.state();
  }

  async addText(page: number, anchor: Point, rtl: boolean, text: string, style: AddTextStyle): Promise<TextWriteResult> {
    let matched: EditableLine | null = null;
    if (style.kind === 'match') {
      matched = this.lines(page)[style.lineIndex] ?? null;
    }
    const matchedStyle = matched ? dominantStyle(matched) : null;
    await this.fallbackFonts.prepare(style.kind === 'custom'
      ? [style.style.font]
      : this.fallbackNeeds(page, Array.from(text).map(char => ({char, style: matchedStyle, source: null}))));
    const size = style.kind === 'custom' ? style.style.size : matchedStyle!.size;
    const lineHeight = size * 1.25;
    const outcome = this.operation('Add text', false, () => {
      const pdfPage = this.loadPage(page);
      const substituted = new Set<string>();
      const missing = new Set<string>();
      text.split('\n').forEach((lineText, i) => {
        if (lineText.trim() === '') {
          return;
        }
        const lineRtl = startsRtl(lineText) || (rtl && !/\p{L}/u.test(lineText));
        const result = writeText(this.document, page, pdfPage, this.fonts, {
          chars: Array.from(lineText).map(char => ({char, style: matchedStyle, source: null})),
          rtl: lineRtl,
          anchor: [anchor[0], anchor[1] + i * lineHeight],
          anchorIsEnd: rtl,
          dir: [1, 0],
          override: style.kind === 'custom' ? style.style : null,
          existingFontsLabelByShape: matched?.labelsByShape ?? true,
        });
        result.substitutedFonts.forEach(f => substituted.add(f));
        result.missingCharacters.forEach(c => missing.add(c));
      });
      return {substitutedFonts: [...substituted], missingCharacters: [...missing]};
    });
    return {...outcome, state: await this.state()};
  }

  async eraseArea(page: number, rect: Rect): Promise<DocState> {
    this.operation('Erase area', false, () => redact(this.loadPage(page), rect, true));
    return this.state();
  }

  async annotations(page: number): Promise<AnnotationInfo[]> {
    return this.loadPage(page).getAnnotations()
      .map((annotation, index) => ({annotation, index}))
      .filter(({annotation}) => !HIDDEN_ANNOTATIONS.has(annotation.getType()))
      .map(({annotation, index}) => ({
        index,
        type: annotation.getType(),
        rect: annotation.getBounds(),
        contents: annotation.getContents(),
        movable: MOVABLE_ANNOTATIONS.has(annotation.getType()),
      }));
  }

  async addMarkup(page: number, type: MarkupType, from: Point, to: Point, color: RgbColor): Promise<DocState | null> {
    const pdfPage = this.loadPage(page);
    const quads = pdfPage.toStructuredText('').highlight(from, to);
    if (quads.length === 0) {
      return null;
    }
    this.operation(type, false, () => {
      const annotation = pdfPage.createAnnotation(type);
      annotation.setColor(color);
      annotation.setQuadPoints(quads);
      annotation.update();
    });
    return this.state();
  }

  async addNote(page: number, at: Point, text: string): Promise<DocState> {
    this.operation('Add note', false, () => {
      const annotation = this.loadPage(page).createAnnotation('Text');
      annotation.setRect([at[0], at[1], at[0] + 20, at[1] + 20]);
      annotation.setContents(text);
      annotation.setIcon('Comment');
      annotation.setColor([1, 0.8, 0]);
      annotation.update();
    });
    return this.state();
  }

  async addInk(page: number, strokes: Point[][], color: RgbColor, width: number): Promise<DocState> {
    this.operation('Draw', false, () => {
      const annotation = this.loadPage(page).createAnnotation('Ink');
      annotation.setInkList(strokes);
      annotation.setColor(color);
      annotation.setBorderWidth(width);
      annotation.update();
    });
    return this.state();
  }

  async addImage(page: number, rect: Rect, png: ArrayBuffer): Promise<DocState> {
    this.operation('Add signature', false, () => {
      const annotation = this.loadPage(page).createAnnotation('Stamp');
      annotation.setRect(rect);
      annotation.setStampImage(new (mupdf().Image)(new Uint8Array(png)));
      annotation.update();
    });
    return this.state();
  }

  async moveAnnotation(page: number, index: number, rect: Rect): Promise<DocState> {
    this.operation('Move', false, () => {
      const annotation = this.loadPage(page).getAnnotations()[index];
      annotation.setRect(rect);
      annotation.update();
    });
    return this.state();
  }

  async deleteAnnotation(page: number, index: number): Promise<DocState> {
    this.operation('Delete annotation', false, () => {
      const pdfPage = this.loadPage(page);
      pdfPage.deleteAnnotation(pdfPage.getAnnotations()[index]);
    });
    return this.state();
  }

  async widgets(page: number): Promise<WidgetInfo[]> {
    return this.loadPage(page).getWidgets().map((widget, index) => {
      const kind = widgetKind(widget);
      const value = widget.getValue();
      return {
        index,
        kind,
        name: widget.getName(),
        rect: widget.getBounds(),
        value,
        checked: (kind === 'checkbox' || kind === 'radio') && value !== 'Off' && value !== '',
        options: kind === 'choice' ? widget.getOptions() : [],
        multiline: kind === 'text' && widget.isMultiline(),
        readOnly: widget.isReadOnly(),
      };
    });
  }

  async setWidgetValue(page: number, index: number, value: string | boolean): Promise<DocState> {
    if (typeof value === 'string' && hasRtl(value)) {
      await this.fallbackFonts.prepare([{family: 'sans', bold: false, italic: false}]);
    }
    this.operation('Fill form', false, () => {
      const pdfPage = this.loadPage(page);
      const widget = pdfPage.getWidgets()[index];
      const kind = widgetKind(widget);
      if (kind === 'checkbox' || kind === 'radio') {
        const checked = widget.getValue() !== 'Off' && widget.getValue() !== '';
        if (checked !== value) {
          widget.toggle();
        }
      } else if (kind === 'choice') {
        widget.setChoiceValue(String(value));
      } else if (kind === 'text') {
        widget.setTextValue(String(value));
      }
      widget.update();
      if (kind === 'text' && !widget.isMultiline()) {
        fixSingleLineAppearance(widget);
        // Otherwise a viewer that honours the flag rebuilds the appearance and undoes the fix. Every
        // field already has an appearance: MuPDF builds them when it opens such a file.
        const acroForm = this.document.getTrailer().get('Root').get('AcroForm');
        if (acroForm.isDictionary()) {
          acroForm.delete('NeedAppearances');
        }
      }
      pdfPage.update();
    });
    return this.state();
  }

  async rotatePage(page: number, degrees: number): Promise<DocState> {
    this.operation('Rotate page', true, () => {
      const pageObject = this.document.findPage(page);
      const current = pageObject.getInheritable('Rotate');
      const rotation = ((current.isNumber() ? current.asNumber() : 0) + degrees + 360) % 360;
      pageObject.put('Rotate', rotation);
    });
    return this.state();
  }

  async deletePage(page: number): Promise<DocState> {
    if (this.document.countPages() <= 1) {
      throw new Error('A PDF needs at least one page');
    }
    this.operation('Delete page', true, () => this.document.deletePage(page));
    return this.state();
  }

  async movePage(from: number, to: number): Promise<DocState> {
    const order = Array.from({length: this.document.countPages()}, (_, i) => i);
    const [moved] = order.splice(from, 1);
    order.splice(to, 0, moved);
    this.operation('Move page', true, () => this.document.rearrangePages(order));
    return this.state();
  }

  async insertBlankPage(at: number): Promise<DocState> {
    const doc = this.document;
    const neighbour = doc.loadPage(Math.min(Math.max(at - 1, 0), doc.countPages() - 1));
    const [x0, y0, x1, y1] = neighbour.getBounds();
    this.operation('Insert page', true, () => {
      const pageObject = doc.addPage([0, 0, x1 - x0, y1 - y0], 0, {}, '');
      doc.insertPage(at, pageObject);
    });
    return this.state();
  }

  async insertPdf(at: number, data: ArrayBuffer): Promise<DocState> {
    const source = mupdf().Document.openDocument(new Uint8Array(data), 'application/pdf').asPDF();
    if (!source) {
      throw new Error('That file is not a PDF');
    }
    if (source.needsPassword()) {
      throw new Error('That PDF is password-protected');
    }
    this.operation('Insert PDF', true, () => {
      const graft = this.document.newGraftMap();
      for (let i = 0; i < source.countPages(); i++) {
        graft.graftPage(at + i, source, i);
      }
    });
    return this.state();
  }

  async extractPages(pages: number[]): Promise<ArrayBuffer> {
    const m = mupdf();
    const out = new m.PDFDocument();
    const graft = out.newGraftMap();
    for (const page of pages) {
      graft.graftPage(-1, this.document, page);
    }
    return copyBuffer(subsetCopy(out.saveToBuffer('garbage=compact,compress').asUint8Array()));
  }

  async undo(): Promise<DocState> {
    if (this.document.canUndo()) {
      this.document.undo();
    }
    this.afterHistoryChange();
    return this.state();
  }

  async redo(): Promise<DocState> {
    if (this.document.canRedo()) {
      this.document.redo();
    }
    this.afterHistoryChange();
    return this.state();
  }

  private afterHistoryChange(): void {
    this.lineCache.clear();
    this.fonts.resetAll();
  }

  async save(): Promise<ArrayBuffer> {
    return copyBuffer(subsetCopy(this.document.saveToBuffer('garbage=compact,compress').asUint8Array()));
  }

}

// Bundled fonts go into the document whole (half a megabyte each). The saved file gets them subset, done on a
// copy so the open document keeps the full fonts and its undo history.
function subsetCopy(saved: Uint8Array): Uint8Array {
  try {
    const copy = mupdf().Document.openDocument(saved.slice(), 'application/pdf').asPDF();
    if (!copy) {
      return saved;
    }
    copy.subsetFonts();
    return copy.saveToBuffer('garbage=compact,compress').asUint8Array();
  } catch {
    return saved;
  }
}

function copyBuffer(bytes: Uint8Array): ArrayBuffer {
  return bytes.slice().buffer as ArrayBuffer;
}
