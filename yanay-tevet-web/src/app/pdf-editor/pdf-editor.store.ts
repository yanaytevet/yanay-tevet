import {computed, DestroyRef, effect, inject, Injectable, signal} from '@angular/core';
import {DialogService} from '../common/dialogs/dialogs.service';
import {LanguageService} from '../shared/i18n/language.service';
import {fill, injectStrings, plural} from '../shared/i18n/strings';
import {PdfEditorLog} from './debug/pdf-editor-log';
import {fontKey} from './engine/font-names';
import {PdfEngineClient} from './engine/pdf-engine-client';
import {
  AddTextStyle,
  AnnotationInfo,
  DocState,
  EngineError,
  FontChoice,
  FontFamily,
  MarkupType,
  Point,
  Rect,
  RenderedPage,
  RgbColor,
  TextLineInfo,
  TextWriteResult,
  WidgetInfo,
} from './engine/pdf-engine.types';
import {PDF_EDITOR_STRINGS} from './i18n';

export type PdfTool = 'select' | 'editText' | 'move' | 'addText' | 'erase' | 'markup' | 'note' | 'draw' | 'sign';

export type LocalFontPermission = 'granted' | 'denied' | 'prompt';

// Chrome and Edge's Local Font Access API (not in TypeScript's DOM types yet).
interface LocalFontData {
  postscriptName: string;
  fullName: string;
  blob(): Promise<Blob>;
}

type QueryLocalFonts = () => Promise<LocalFontData[]>;

const LOCAL_FONTS_KEY = 'pdf_editor_local_fonts';

export interface AddTextSettings {
  family: FontFamily | 'match';
  bold: boolean;
  italic: boolean;
  size: number;
  color: string;
}

// A line where some characters had to be drawn in a bundled font because the original font lacks them.
export interface SubstitutionMarker {
  id: number;
  page: number;
  bbox: Rect;
  fonts: string[];
}

export function hexToRgb(hex: string): RgbColor {
  const n = parseInt(hex.slice(1), 16);
  return [((n >> 16) & 255) / 255, ((n >> 8) & 255) / 255, (n & 255) / 255];
}

export function rgbToCss(color: RgbColor): string {
  return `rgb(${color.map(c => Math.round(c * 255)).join(' ')})`;
}

function overlaps(a: Rect, b: Rect): boolean {
  return a[0] < b[2] && b[0] < a[2] && a[1] < b[3] && b[1] < a[3];
}

// The open document and everything the editor's pieces share. One per editor page.
@Injectable()
export class PdfEditorStore {
  private readonly dialogService = inject(DialogService);
  private readonly languageService = inject(LanguageService);
  private readonly t = injectStrings(PDF_EDITOR_STRINGS);
  readonly log = inject(PdfEditorLog);
  private client: PdfEngineClient | null = null;
  private nextMarkerId = 1;
  // Fonts loaded into the page for the edit boxes, per open document: PDF font name → CSS family.
  private webFonts = new Map<string, Promise<string | null>>();
  private nextWebFont = 1;
  private readonly busyCount = signal(0);

  readonly fileName = signal<string | null>(null);
  readonly state = signal<DocState | null>(null);
  readonly loading = signal(false);
  readonly busy = computed(() => this.busyCount() > 0);
  readonly tool = signal<PdfTool>('select');
  readonly zoom = signal(1);
  // Bumped when any page may have changed (undo, page operations); pages re-render.
  readonly docVersion = signal(0);
  readonly pageVersions = signal<Record<number, number>>({});
  readonly substitutions = signal<SubstitutionMarker[]>([]);
  readonly currentPage = signal(0);

  readonly markupType = signal<MarkupType>('Highlight');
  readonly markupColor = signal('#ffd400');
  readonly drawColor = signal('#1f4fd6');
  readonly drawWidth = signal(2);
  readonly addTextSettings = signal<AddTextSettings>({family: 'match', bold: false, italic: false, size: 12, color: '#000000'});
  // A PNG data URL.
  readonly signature = signal<string | null>(null);

  readonly pages = computed(() => (this.state()?.pageSizes ?? []).map((size, index) => ({index, size})));
  readonly pageCount = computed(() => this.state()?.pageCount ?? 0);
  readonly canUndo = computed(() => this.state()?.canUndo ?? false);
  readonly canRedo = computed(() => this.state()?.canRedo ?? false);
  readonly maxPageWidth = computed(() => Math.max(1, ...(this.state()?.pageSizes ?? []).map(s => s.width)));

  constructor() {
    inject(DestroyRef).onDestroy(() => this.client?.terminate());
    effect(() => this.log.log('tool', {tool: this.tool()}));
    effect(() => this.log.log('zoom', {zoom: this.zoom()}));
  }

  // The page's lines, for the log: what an edit did to its neighbours.
  private async linesForLog(page: number): Promise<unknown[] | null> {
    if (!this.log.enabled) {
      return null;
    }
    try {
      return (await this.engine.call('textLines', page)).map(l => ({i: l.index, text: l.text, bbox: l.bbox}));
    } catch {
      return null;
    }
  }

  private logState(type: string, data: Record<string, unknown>): void {
    const state = this.state();
    this.log.log(type, {...data, pages: state?.pageCount, canUndo: state?.canUndo, canRedo: state?.canRedo});
  }

  private get engine(): PdfEngineClient {
    if (!this.client) {
      this.client = new PdfEngineClient();
    }
    return this.client;
  }

  private async perform<T>(work: () => Promise<T>): Promise<T | null> {
    this.busyCount.update(n => n + 1);
    try {
      return await work();
    } catch (error) {
      this.log.log('error', {message: error instanceof Error ? error.message : String(error)});
      await this.dialogService.showNotificationDialog({
        title: this.t().dialogs.failedTitle,
        text: error instanceof EngineError
          ? fill(this.t().engineErrors[error.code], error.params)
          : error instanceof Error ? error.message : String(error),
      });
      return null;
    } finally {
      this.busyCount.update(n => n - 1);
    }
  }

  private applyState(state: DocState, changedPage: number | 'all'): void {
    this.state.set(state);
    if (changedPage === 'all') {
      this.docVersion.update(v => v + 1);
      this.substitutions.set([]);
      this.currentPage.update(p => Math.min(p, state.pageCount - 1));
    } else {
      this.pageVersions.update(v => ({...v, [changedPage]: (v[changedPage] ?? 0) + 1}));
    }
  }

  async open(file: File): Promise<void> {
    this.loading.set(true);
    try {
      const data = await file.arrayBuffer();
      const result = await this.perform(() => this.engine.call('open', data));
      if (!result) {
        return;
      }
      if (result.needsPassword && !(await this.unlock())) {
        return;
      }
      const state = await this.perform(() => this.engine.call('state'));
      if (state) {
        this.fileName.set(file.name);
        this.webFonts = new Map();
        this.substitutions.set([]);
        this.pageVersions.set({});
        this.currentPage.set(0);
        this.applyState(state, 'all');
        this.log.log('open', {file: file.name, bytes: file.size, pages: state.pageCount});
      }
    } finally {
      this.loading.set(false);
    }
  }

  private async unlock(): Promise<boolean> {
    let text = this.t().dialogs.passwordText;
    for (let attempt = 0; attempt < 3; attempt++) {
      const strings = this.t().dialogs;
      const password = await this.dialogService.getTextFromInputDialog({
        title: strings.passwordTitle,
        text,
        label: strings.passwordLabel,
        inputType: 'password',
        confirmActionName: strings.open,
      });
      if (password === null) {
        return false;
      }
      if (await this.perform(() => this.engine.call('authenticate', password))) {
        return true;
      }
      text = this.t().dialogs.passwordWrong;
    }
    return false;
  }

  close(): void {
    this.log.log('close', {file: this.fileName()});
    this.client?.terminate();
    this.client = null;
    this.state.set(null);
    this.fileName.set(null);
    this.substitutions.set([]);
  }

  render(page: number, scale: number): Promise<RenderedPage> {
    return this.engine.call('render', page, scale);
  }

  // A CSS font-family for a PDF font, loaded from the font embedded in the file; null if the browser can't
  // use it, and the edit box falls back to a generic family.
  // Fonts installed on this computer, for characters a PDF's own copy of a font lacks: the same font draws
  // them exactly. Chrome and Edge only; the user allows it once.
  readonly localFontsSupported = typeof window !== 'undefined' && 'queryLocalFonts' in window;

  localFontsDeclined(): boolean {
    try {
      return sessionStorage.getItem(LOCAL_FONTS_KEY) === 'declined';
    } catch {
      return false;
    }
  }

  declineLocalFonts(): void {
    this.log.log('local-fonts-declined', {});
    // For this visit only: a misclick shouldn't hide the offer for good.
    try {
      sessionStorage.setItem(LOCAL_FONTS_KEY, 'declined');
    } catch {
      // Storage blocked: the offer comes back on the next edit, which is harmless.
    }
  }

  async localFontPermission(): Promise<LocalFontPermission> {
    try {
      const status = await navigator.permissions.query({name: 'local-fonts' as PermissionName});
      return status.state;
    } catch {
      return 'prompt';
    }
  }

  async localFontsWanted(page: number, line: TextLineInfo, newText: string): Promise<string[]> {
    if (!this.localFontsSupported) {
      return [];
    }
    try {
      return await this.engine.call('localFontsWanted', page, line.index, line.text, newText);
    } catch {
      return [];
    }
  }

  // Hands the installed copies of the PDF fonts `names` to the engine; asks for permission if it hasn't been
  // given, so call it from a click. Fonts are matched by fontKey(), since a PDF may name a font differently
  // from the font itself. Returns the fonts the engine took.
  async provideLocalFonts(names: string[]): Promise<string[]> {
    const query = (window as unknown as {queryLocalFonts?: QueryLocalFonts}).queryLocalFonts;
    if (!query || names.length === 0) {
      return [];
    }
    const provided: string[] = [];
    try {
      const installed = await query.call(window);
      for (const name of names) {
        const key = fontKey(name);
        const font = installed.find(f => fontKey(f.postscriptName) === key) ?? installed.find(f => fontKey(f.fullName) === key);
        if (!font) {
          continue;
        }
        const data = await (await font.blob()).arrayBuffer();
        if (await this.engine.call('addLocalFont', name, font.postscriptName, data)) {
          provided.push(name);
        }
      }
    } catch (error) {
      this.log.log('local-fonts-error', {message: error instanceof Error ? error.message : String(error)});
    }
    this.log.log('local-fonts', {wanted: names, provided});
    return provided;
  }

  webFontFamily(page: number, pdfFontName: string): Promise<string | null> {
    let family = this.webFonts.get(pdfFontName);
    if (!family) {
      family = this.loadWebFont(page, pdfFontName);
      this.webFonts.set(pdfFontName, family);
    }
    return family;
  }

  private async loadWebFont(page: number, pdfFontName: string): Promise<string | null> {
    try {
      const data = await this.engine.call('webFont', page, pdfFontName);
      if (!data) {
        this.log.log('web-font', {font: pdfFontName, loaded: false, reason: 'not TrueType/OpenType'});
        return null;
      }
      const family = `pdf-font-${this.nextWebFont++}`;
      const face = new FontFace(family, data);
      await face.load();
      document.fonts.add(face);
      this.log.log('web-font', {font: pdfFontName, loaded: true, family, bytes: data.byteLength});
      return family;
    } catch (error) {
      this.log.log('web-font', {font: pdfFontName, loaded: false, reason: error instanceof Error ? error.message : String(error)});
      return null;
    }
  }

  textLines(page: number): Promise<TextLineInfo[]> {
    return this.engine.call('textLines', page);
  }

  annotations(page: number): Promise<AnnotationInfo[]> {
    return this.engine.call('annotations', page);
  }

  widgets(page: number): Promise<WidgetInfo[]> {
    return this.engine.call('widgets', page);
  }

  private async reportText(page: number, bbox: Rect | null, result: TextWriteResult): Promise<void> {
    this.applyState(result.state, page);
    if (bbox) {
      this.substitutions.update(list => list.filter(m => m.page !== page || !overlaps(m.bbox, bbox)));
      if (result.substitutedFonts.length > 0) {
        this.substitutions.update(list => [...list, {id: this.nextMarkerId++, page, bbox, fonts: result.substitutedFonts}]);
      }
    }
    if (result.missingCharacters.length > 0) {
      await this.dialogService.showNotificationDialog({
        title: this.t().dialogs.missingTitle,
        text: fill(this.t().dialogs.missingText, {chars: result.missingCharacters.join(' ')}),
      });
    }
  }

  async editLine(page: number, line: TextLineInfo, newText: string, fontOverride: FontChoice | null): Promise<boolean> {
    const linesBefore = await this.linesForLog(page);
    const result = await this.perform(() => this.engine.call('editLine', page, line.index, line.text, newText, fontOverride));
    if (!result) {
      return false;
    }
    this.log.log('edit-line', {
      page, line: {i: line.index, text: line.text, bbox: line.bbox, rtl: line.rtl, font: line.fontName, size: line.size},
      newText, fontOverride, substituted: result.substitutedFonts, missing: result.missingCharacters,
      linesBefore, linesAfter: await this.linesForLog(page),
    });
    await this.reportText(page, newText.trim() === '' ? null : line.bbox, result);
    if (newText.trim() === '') {
      this.substitutions.update(list => list.filter(m => m.page !== page || !overlaps(m.bbox, line.bbox)));
    }
    return true;
  }

  async moveLines(page: number, lines: TextLineInfo[], offset: Point): Promise<boolean> {
    const state = await this.perform(() => this.engine.call('moveLines', page, lines.map(l => ({index: l.index, text: l.text})), offset));
    if (!state) {
      return false;
    }
    this.applyState(state, page);
    this.substitutions.update(list => list.filter(m => m.page !== page || !lines.some(l => overlaps(m.bbox, l.bbox))));
    this.log.log('move-lines', {page, lines: lines.map(l => ({i: l.index, text: l.text, bbox: l.bbox})), offset, linesAfter: await this.linesForLog(page)});
    return true;
  }

  async addText(page: number, anchor: Point, rtl: boolean, text: string, style: AddTextStyle, bbox: Rect): Promise<boolean> {
    const result = await this.perform(() => this.engine.call('addText', page, anchor, rtl, text, style));
    if (!result) {
      return false;
    }
    this.log.log('add-text', {page, anchor, rtl, text, style, substituted: result.substitutedFonts, linesAfter: await this.linesForLog(page)});
    await this.reportText(page, bbox, result);
    return true;
  }

  private async pageOperation(page: number, work: () => Promise<DocState>, type: string, data: Record<string, unknown>): Promise<void> {
    const state = await this.perform(work);
    if (state) {
      this.applyState(state, page);
      this.logState(type, {page, ...data});
    }
  }

  eraseArea(page: number, rect: Rect): Promise<void> {
    return this.pageOperation(page, () => this.engine.call('eraseArea', page, rect), 'erase', {rect});
  }

  async addMarkup(page: number, from: Point, to: Point): Promise<void> {
    const state = await this.perform(() => this.engine.call('addMarkup', page, this.markupType(), from, to, hexToRgb(this.markupColor())));
    if (state) {
      this.applyState(state, page);
    }
    this.log.log('markup', {page, type: this.markupType(), from, to, found: !!state});
  }

  async addNote(page: number, at: Point): Promise<void> {
    const strings = this.t().dialogs;
    const text = await this.dialogService.getTextFromInputDialog({
      title: strings.noteTitle,
      text: strings.noteText,
      label: strings.noteLabel,
      isTextArea: true,
      confirmActionName: strings.addNote,
    });
    if (text) {
      await this.pageOperation(page, () => this.engine.call('addNote', page, at, text), 'note', {at});
    }
  }

  addInk(page: number, stroke: Point[]): Promise<void> {
    return this.pageOperation(page, () => this.engine.call('addInk', page, [stroke], hexToRgb(this.drawColor()), this.drawWidth()),
      'draw', {points: stroke.length});
  }

  async addSignature(page: number, rect: Rect): Promise<void> {
    const signature = this.signature();
    if (!signature) {
      return;
    }
    const png = await (await fetch(signature)).arrayBuffer();
    await this.pageOperation(page, () => this.engine.call('addImage', page, rect, png), 'sign', {rect});
  }

  moveAnnotation(page: number, index: number, rect: Rect): Promise<void> {
    return this.pageOperation(page, () => this.engine.call('moveAnnotation', page, index, rect), 'move-annotation', {index, rect});
  }

  deleteAnnotation(page: number, index: number): Promise<void> {
    return this.pageOperation(page, () => this.engine.call('deleteAnnotation', page, index), 'delete-annotation', {index});
  }

  setWidgetValue(page: number, index: number, value: string | boolean): Promise<void> {
    return this.pageOperation(page, () => this.engine.call('setWidgetValue', page, index, value), 'fill-field', {index, value});
  }

  private async structural(work: () => Promise<DocState>, type: string, data: Record<string, unknown> = {}): Promise<void> {
    const state = await this.perform(work);
    if (state) {
      this.applyState(state, 'all');
      this.logState(type, data);
    }
  }

  rotatePage(page: number, degrees: number): Promise<void> {
    return this.structural(() => this.engine.call('rotatePage', page, degrees), 'rotate-page', {page, degrees});
  }

  async deletePage(page: number): Promise<void> {
    const strings = this.t().dialogs;
    const confirmed = await this.dialogService.getBooleanFromConfirmationDialog({
      title: fill(strings.deletePageTitle, {page: page + 1}),
      text: strings.deletePageText,
      confirmActionName: strings.deletePage,
      danger: true,
    });
    if (confirmed) {
      await this.structural(() => this.engine.call('deletePage', page), 'delete-page', {page});
    }
  }

  movePage(from: number, to: number): Promise<void> {
    return this.structural(() => this.engine.call('movePage', from, to), 'move-page', {from, to});
  }

  insertBlankPage(at: number): Promise<void> {
    return this.structural(() => this.engine.call('insertBlankPage', at), 'insert-blank-page', {at});
  }

  async insertPdf(file: File, at: number): Promise<void> {
    const data = await file.arrayBuffer();
    await this.structural(() => this.engine.call('insertPdf', at, data), 'insert-pdf', {at, file: file.name});
  }

  async extractPages(pages: number[]): Promise<void> {
    const data = await this.perform(() => this.engine.call('extractPages', pages));
    if (data) {
      const files = this.t().files;
      const name = pages.length === 1
        ? fill(files.onePage, {name: this.baseName(), page: pages[0] + 1})
        : fill(plural(this.languageService.language(), pages.length, files.pages), {name: this.baseName()});
      this.saveFile(data, name);
    }
  }

  undo(): Promise<void> {
    return this.structural(() => this.engine.call('undo'), 'undo');
  }

  redo(): Promise<void> {
    return this.structural(() => this.engine.call('redo'), 'redo');
  }

  async download(): Promise<void> {
    const data = await this.perform(() => this.engine.call('save'));
    if (data) {
      this.saveFile(data, fill(this.t().files.edited, {name: this.baseName()}));
      this.log.log('download', {bytes: data.byteLength});
    }
  }

  private baseName(): string {
    return (this.fileName() ?? 'document.pdf').replace(/\.pdf$/i, '');
  }

  private saveFile(data: ArrayBuffer, name: string): void {
    const url = URL.createObjectURL(new Blob([data], {type: 'application/pdf'}));
    const link = document.createElement('a');
    link.href = url;
    link.download = name;
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 10_000);
  }
}
