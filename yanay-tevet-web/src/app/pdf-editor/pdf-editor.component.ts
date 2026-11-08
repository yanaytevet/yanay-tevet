import {Component, computed, effect, ElementRef, HostListener, inject, signal, untracked, viewChild} from '@angular/core';
import {
  bootstrapArrowClockwise,
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
import {FontFamily, MarkupType} from './engine/pdf-engine.types';
import {PdfPageViewComponent} from './page-view/pdf-page-view.component';
import {AddTextSettings, PdfEditorStore, PdfTool} from './pdf-editor.store';
import {SignatureDialogComponent} from './signature-dialog/signature-dialog.component';
import {PdfThumbnailsComponent} from './thumbnails/pdf-thumbnails.component';

interface ToolDef {
  tool: PdfTool;
  label: string;
  icon: string;
  hint: string;
}

const ZOOM_STEPS = [0.25, 0.33, 0.5, 0.67, 0.8, 1, 1.25, 1.5, 2, 3, 4];

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

  protected readonly tools: ToolDef[] = [
    {tool: 'select', label: 'Select', icon: bootstrapCursor,
      hint: 'Fill in form fields. Click a note, drawing or signature to move or delete it.'},
    {tool: 'editText', label: 'Edit text', icon: bootstrapCursorText,
      hint: 'Click a line to change or delete it. It keeps its font; characters that font lacks are marked with a warning.'},
    {tool: 'addText', label: 'Add text', icon: bootstrapFonts, hint: 'Click where the text should start.'},
    {tool: 'erase', label: 'Erase', icon: bootstrapEraser, hint: 'Drag over text or images to remove them from the file.'},
    {tool: 'markup', label: 'Highlight', icon: bootstrapHighlighter, hint: 'Drag across text to mark it.'},
    {tool: 'note', label: 'Note', icon: bootstrapChatSquareText, hint: 'Click to leave a note.'},
    {tool: 'draw', label: 'Draw', icon: bootstrapPencil, hint: 'Draw freehand on the page.'},
    {tool: 'sign', label: 'Sign', icon: bootstrapPenFill, hint: 'Drag a box, or click, to place your signature.'},
  ];
  protected readonly markupTypes: {type: MarkupType; label: string}[] = [
    {type: 'Highlight', label: 'Highlight'},
    {type: 'Underline', label: 'Underline'},
    {type: 'StrikeOut', label: 'Strike out'},
  ];
  // Ink colours: content, not interface, so they stay the same in both themes.
  protected readonly markupColors = ['#ffd400', '#7ee36b', '#ff8fd0', '#7cc7ff'];
  protected readonly inkColors = ['#14213d', '#1f4fd6', '#d62828', '#2a9d3f'];
  protected readonly drawWidths = [1, 2, 4];

  protected readonly activeTool = computed(() => this.tools.find(t => t.tool === this.store.tool()) ?? this.tools[0]);
  protected readonly isActiveTool = computed(() => Object.fromEntries(this.tools.map(t => [t.tool, t.tool === this.store.tool()])));
  protected readonly isMarkupType = computed(() => Object.fromEntries(this.markupTypes.map(m => [m.type, m.type === this.store.markupType()])));
  protected readonly isMarkupColor = computed(() => Object.fromEntries(this.markupColors.map(c => [c, c === this.store.markupColor()])));
  protected readonly isInkColor = computed(() => Object.fromEntries(this.inkColors.map(c => [c, c === this.store.drawColor()])));
  protected readonly isDrawWidth = computed(() => Object.fromEntries(this.drawWidths.map(w => [w, w === this.store.drawWidth()])));
  protected readonly zoomLabel = computed(() => `${Math.round(this.store.zoom() * 100)}%`);
  protected readonly pageLabel = computed(() => `Page ${this.store.currentPage() + 1} of ${this.store.pageCount()}`);

  protected readonly showPages = signal(typeof window !== 'undefined' && window.matchMedia('(min-width: 768px)').matches);
  protected readonly dragOver = signal(false);
  // Fitting the width until the user picks a zoom; then the zoom stays put.
  private fitMode = true;

  private readonly fileInput = viewChild<ElementRef<HTMLInputElement>>('fileInput');
  private readonly scroller = viewChild<ElementRef<HTMLElement>>('scroller');

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
    if (mod && event.key.toLowerCase() === 'z') {
      event.preventDefault();
      void (event.shiftKey ? this.store.redo() : this.store.undo());
    } else if (mod && event.key.toLowerCase() === 'y') {
      event.preventDefault();
      void this.store.redo();
    } else if (event.key === 'Escape') {
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
      label: 'note',
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
      const confirmed = await this.dialogService.getBooleanFromConfirmationDialog({
        title: 'Close without downloading?',
        text: 'Your changes live only in this tab. Download the PDF first to keep them.',
        confirmActionName: 'Close',
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
