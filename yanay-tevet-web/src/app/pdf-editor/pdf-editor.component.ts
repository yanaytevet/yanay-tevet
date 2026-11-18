import {afterNextRender, Component, computed, effect, ElementRef, HostListener, inject, Injector, signal, untracked, viewChild} from '@angular/core';
import {
  bootstrapArrowClockwise,
  bootstrapArrowsMove,
  bootstrapArrowCounterclockwise,
  bootstrapChatSquareText,
  bootstrapCursor,
  bootstrapCursorText,
  bootstrapFlag,
  bootstrapEraser,
  bootstrapFonts,
  bootstrapHighlighter,
  bootstrapLayoutSidebar,
  bootstrapPencil,
  bootstrapPenFill,
} from '@ng-icons/bootstrap-icons';
import {NgIcon} from '@ng-icons/core';
import {featherDownload, featherUpload, featherX, featherZoomIn, featherZoomOut} from '@ng-icons/feather-icons';
import {LoadingStateComponent} from '../common/components/page/loading-state/loading-state.component';
import {PageHeaderComponent} from '../common/components/page/page-header/page-header.component';
import {DialogService} from '../common/dialogs/dialogs.service';
import {LanguageService} from '../shared/i18n/language.service';
import {fill, injectStrings} from '../shared/i18n/strings';
import {FontFamily, MarkupType} from './engine/pdf-engine.types';
import {PDF_EDITOR_STRINGS} from './i18n';
import {PdfPageViewComponent} from './page-view/pdf-page-view.component';
import {AddTextSettings, PdfEditorStore, PdfTool} from './pdf-editor.store';
import {SignatureDialogComponent} from './signature-dialog/signature-dialog.component';
import {PdfThumbnailsComponent} from './thumbnails/pdf-thumbnails.component';

interface ToolDef {
  tool: PdfTool;
  icon: string;
}

const TOOLS: ToolDef[] = [
  {tool: 'select', icon: bootstrapCursor},
  {tool: 'editText', icon: bootstrapCursorText},
  {tool: 'move', icon: bootstrapArrowsMove},
  {tool: 'addText', icon: bootstrapFonts},
  {tool: 'erase', icon: bootstrapEraser},
  {tool: 'markup', icon: bootstrapHighlighter},
  {tool: 'note', icon: bootstrapChatSquareText},
  {tool: 'draw', icon: bootstrapPencil},
  {tool: 'sign', icon: bootstrapPenFill},
];
const MARKUP_TYPES: MarkupType[] = ['Highlight', 'Underline', 'StrikeOut'];

const ZOOM_STEPS = [0.25, 0.33, 0.5, 0.67, 0.8, 1, 1.25, 1.5, 2, 3, 4];
const MIN_ZOOM = ZOOM_STEPS[0];
const MAX_ZOOM = ZOOM_STEPS[ZOOM_STEPS.length - 1];

@Component({
  selector: 'app-pdf-editor',
  imports: [NgIcon, PageHeaderComponent, LoadingStateComponent, PdfPageViewComponent, PdfThumbnailsComponent],
  providers: [PdfEditorStore],
  templateUrl: './pdf-editor.component.html',
  styleUrl: './pdf-editor.component.css',
  host: {class: 'flex flex-col h-full min-h-0 overflow-hidden'},
})
export class PdfEditorComponent {
  protected readonly store = inject(PdfEditorStore);
  private readonly dialogService = inject(DialogService);
  private readonly languageService = inject(LanguageService);
  protected readonly t = injectStrings(PDF_EDITOR_STRINGS);

  protected readonly featherUpload = featherUpload;
  protected readonly featherDownload = featherDownload;
  protected readonly featherX = featherX;
  protected readonly featherZoomIn = featherZoomIn;
  protected readonly featherZoomOut = featherZoomOut;
  protected readonly bootstrapArrowCounterclockwise = bootstrapArrowCounterclockwise;
  protected readonly bootstrapArrowClockwise = bootstrapArrowClockwise;
  protected readonly bootstrapLayoutSidebar = bootstrapLayoutSidebar;
  protected readonly bootstrapFlag = bootstrapFlag;
  protected readonly logEnabled = this.store.log.enabled;

  protected readonly tools = computed(() => TOOLS.map(def => ({...def, ...this.t().tools[def.tool]})));
  protected readonly markupTypes = computed(() => MARKUP_TYPES.map(type => ({type, label: this.t().markupTypes[type]})));
  // Ink colours: content, not interface, so they stay the same in both themes.
  protected readonly markupColors = ['#ffd400', '#7ee36b', '#ff8fd0', '#7cc7ff'];
  protected readonly inkColors = ['#14213d', '#1f4fd6', '#d62828', '#2a9d3f'];
  protected readonly drawWidths = [1, 2, 4];

  protected readonly activeTool = computed(() => this.t().tools[this.store.tool()]);
  protected readonly isActiveTool = computed(() => Object.fromEntries(TOOLS.map(def => [def.tool, def.tool === this.store.tool()])));
  protected readonly isMarkupType = computed(() => Object.fromEntries(MARKUP_TYPES.map(type => [type, type === this.store.markupType()])));
  protected readonly isMarkupColor = computed(() => Object.fromEntries(this.markupColors.map(c => [c, c === this.store.markupColor()])));
  protected readonly isInkColor = computed(() => Object.fromEntries(this.inkColors.map(c => [c, c === this.store.drawColor()])));
  protected readonly isDrawWidth = computed(() => Object.fromEntries(this.drawWidths.map(w => [w, w === this.store.drawWidth()])));
  protected readonly zoomLabel = computed(() =>
    new Intl.NumberFormat(this.languageService.language(), {style: 'percent'}).format(Math.round(this.store.zoom() * 100) / 100));
  protected readonly pageLabel = computed(() => {
    const language = this.languageService.language();
    return fill(this.t().toolbar.pageOf, {
      page: (this.store.currentPage() + 1).toLocaleString(language),
      count: this.store.pageCount().toLocaleString(language),
    });
  });
  // Labels for the colour swatches and line widths, by value.
  protected readonly colourLabels = computed(() => Object.fromEntries(
    [...this.markupColors, ...this.inkColors].map(c => [c, fill(this.t().options.colourValue, {value: c})])));
  protected readonly widthLabels = computed(() => Object.fromEntries(
    this.drawWidths.map(w => [w, fill(this.t().options.widthValue, {value: w.toLocaleString(this.languageService.language())})])));

  protected readonly showPages = signal(typeof window !== 'undefined' && window.matchMedia('(min-width: 768px)').matches);
  protected readonly dragOver = signal(false);
  // Fitting the width until the user picks a zoom; then the zoom stays put.
  private fitMode = true;

  private readonly fileInput = viewChild<ElementRef<HTMLInputElement>>('fileInput');
  private readonly scroller = viewChild<ElementRef<HTMLElement>>('scroller');
  private readonly injector = inject(Injector);

  constructor() {
    // Fit the width when a document opens.
    effect(() => {
      const name = this.store.fileName();
      const scroller = this.scroller();
      if (name && scroller) {
        untracked(() => this.fitWidth());
      }
    });
  }

  @HostListener('window:keydown', ['$event'])
  protected onKey(event: KeyboardEvent): void {
    const target = event.target as HTMLElement | null;
    const mod = event.metaKey || event.ctrlKey;
    if (!this.store.state() || target?.closest('input, textarea, select, [contenteditable="true"]')) {
      if (this.store.state() && mod && ['z', 'y'].includes(event.key.toLowerCase())) {
        // Undo inside a text box undoes typing, not the document; worth knowing when that surprises someone.
        this.store.log.log('undo-key-in-text-box', {shift: event.shiftKey});
      }
      return;
    }
    if (mod && (event.key === '=' || event.key === '+')) {
      event.preventDefault();
      this.zoomBy(1);
    } else if (mod && event.key === '-') {
      event.preventDefault();
      this.zoomBy(-1);
    } else if (mod && event.key === '0') {
      event.preventDefault();
      this.fitWidth();
    } else if (mod && event.key.toLowerCase() === 'z') {
      event.preventDefault();
      void (event.shiftKey ? this.store.redo() : this.store.undo());
    } else if (mod && event.key.toLowerCase() === 'y') {
      event.preventDefault();
      void this.store.redo();
    } else if (event.key === 'Escape' && this.store.tool() !== 'move') {
      this.store.tool.set('select');
    }
  }

  @HostListener('window:resize')
  protected onResize(): void {
    if (this.fitMode) {
      this.fitWidth();
    }
  }

  @HostListener('window:beforeunload', ['$event'])
  protected onBeforeUnload(event: BeforeUnloadEvent): void {
    if (this.store.canUndo()) {
      event.preventDefault();
    }
  }

  protected async flag(): Promise<void> {
    const note = await this.dialogService.getTextFromInputDialog({
      title: 'What felt off?',
      text: 'Saved with what just happened, for Claude to read. A word or two is enough, or leave it empty.',
      label: 'Note',
      isTextArea: true,
      allowEmpty: true,
      confirmActionName: 'Flag it',
    });
    if (note !== null) {
      this.store.log.log('flag', {
        note,
        file: this.store.fileName(),
        tool: this.store.tool(),
        page: this.store.currentPage(),
        zoom: this.store.zoom(),
      });
    }
  }

  protected chooseFile(): void {
    this.fileInput()?.nativeElement.click();
  }

  protected async onFileChosen(event: Event): Promise<void> {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    input.value = '';
    if (file) {
      await this.store.open(file);
    }
  }

  protected onDragOver(event: DragEvent): void {
    event.preventDefault();
    this.dragOver.set(true);
  }

  protected onDragLeave(): void {
    this.dragOver.set(false);
  }

  protected async onDrop(event: DragEvent): Promise<void> {
    event.preventDefault();
    this.dragOver.set(false);
    const file = event.dataTransfer?.files?.[0];
    if (file) {
      await this.store.open(file);
    }
  }

  protected async setTool(tool: PdfTool): Promise<void> {
    if (tool === 'sign' && !this.store.signature() && !(await this.chooseSignature())) {
      return;
    }
    this.store.tool.set(tool);
  }

  protected async chooseSignature(): Promise<boolean> {
    const signature = await this.dialogService.open<void, string>(SignatureDialogComponent, undefined, 60);
    if (signature) {
      this.store.signature.set(signature);
      return true;
    }
    return false;
  }

  protected updateAddText(change: Partial<AddTextSettings>): void {
    this.store.addTextSettings.update(s => ({...s, ...change}));
  }

  protected setAddTextFamily(value: string): void {
    this.updateAddText({family: value as FontFamily | 'match'});
  }

  protected setAddTextSize(value: string): void {
    const size = Number(value);
    if (size >= 4 && size <= 200) {
      this.updateAddText({size});
    }
  }

  protected zoomBy(direction: 1 | -1): void {
    const zoom = this.store.zoom();
    const next = direction > 0 ? ZOOM_STEPS.find(z => z > zoom + 0.001) : [...ZOOM_STEPS].reverse().find(z => z < zoom - 0.001);
    if (next) {
      this.fitMode = false;
      this.store.zoom.set(next);
    }
  }

  // Cmd/Ctrl + scroll, and a trackpad pinch (which browsers send as a wheel with Ctrl), zoom the pages
  // around the pointer instead of the whole browser page.
  protected onWheel(event: WheelEvent): void {
    if (!(event.ctrlKey || event.metaKey) || !this.store.state()) {
      return;
    }
    event.preventDefault();
    const perPixel = event.deltaMode === WheelEvent.DOM_DELTA_LINE ? 0.05 : 0.002;
    this.zoomAround(this.store.zoom() * Math.exp(-event.deltaY * perPixel), event.clientX, event.clientY);
  }

  private zoomAround(target: number, clientX: number, clientY: number): void {
    const scroller = this.scroller()?.nativeElement;
    const zoom = Math.min(MAX_ZOOM, Math.max(MIN_ZOOM, target));
    if (!scroller || Math.abs(zoom - this.store.zoom()) < 0.0005) {
      return;
    }
    // The page under the pointer, and where on it the pointer is, as a fraction of its size.
    const pages = [...scroller.querySelectorAll<HTMLElement>('[data-page]')];
    const page = pages.find(p => {
      const r = p.getBoundingClientRect();
      return clientY >= r.top && clientY <= r.bottom;
    }) ?? pages[0];
    const before = page?.getBoundingClientRect();
    this.fitMode = false;
    this.store.zoom.set(zoom);
    if (!page || !before) {
      return;
    }
    const fx = (clientX - before.left) / before.width;
    const fy = (clientY - before.top) / before.height;
    // Once the pages have their new size, the same spot goes back under the pointer.
    afterNextRender(() => {
      const after = page.getBoundingClientRect();
      scroller.scrollLeft += after.left + fx * after.width - clientX;
      scroller.scrollTop += after.top + fy * after.height - clientY;
    }, {injector: this.injector});
  }

  protected fitWidth(): void {
    const scroller = this.scroller()?.nativeElement;
    if (!scroller) {
      return;
    }
    this.fitMode = true;
    const available = scroller.clientWidth - 32;
    this.store.zoom.set(Math.min(2, Math.max(0.25, available / this.store.maxPageWidth())));
  }

  protected goToPage(index: number): void {
    this.scroller()?.nativeElement.querySelector(`[data-page="${index}"]`)?.scrollIntoView({behavior: 'smooth', block: 'start'});
    if (!window.matchMedia('(min-width: 768px)').matches) {
      this.showPages.set(false);
    }
  }

  protected togglePages(): void {
    this.showPages.update(v => !v);
  }

  protected async close(): Promise<void> {
    if (this.store.canUndo()) {
      const strings = this.t().closeDialog;
      const confirmed = await this.dialogService.getBooleanFromConfirmationDialog({
        title: strings.title,
        text: strings.text,
        confirmActionName: strings.confirm,
        danger: true,
      });
      if (!confirmed) {
        return;
      }
    }
    this.store.close();
    this.store.tool.set('select');
  }
}
