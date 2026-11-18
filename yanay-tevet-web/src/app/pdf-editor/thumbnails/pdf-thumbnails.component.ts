import {CdkDrag, CdkDragDrop, CdkDropList} from '@angular/cdk/drag-drop';
import {Component, computed, ElementRef, inject, output, viewChild} from '@angular/core';
import {NgIcon} from '@ng-icons/core';
import {featherFilePlus, featherPlus, featherRotateCcw, featherRotateCw, featherScissors, featherTrash2} from '@ng-icons/feather-icons';
import {DialogService} from '../../common/dialogs/dialogs.service';
import {fill, injectStrings} from '../../shared/i18n/strings';
import {PDF_EDITOR_STRINGS} from '../i18n';
import {PdfEditorStore} from '../pdf-editor.store';
import {PdfThumbnailComponent} from './pdf-thumbnail.component';

@Component({
  selector: 'app-pdf-thumbnails',
  imports: [CdkDropList, CdkDrag, NgIcon, PdfThumbnailComponent],
  templateUrl: './pdf-thumbnails.component.html',
  host: {class: 'flex flex-col flex-1 min-h-0'},
})
export class PdfThumbnailsComponent {
  protected readonly store = inject(PdfEditorStore);
  private readonly dialogService = inject(DialogService);
  protected readonly t = injectStrings(PDF_EDITOR_STRINGS);

  readonly pageSelected = output<number>();

  protected readonly featherRotateCcw = featherRotateCcw;
  protected readonly featherRotateCw = featherRotateCw;
  protected readonly featherTrash2 = featherTrash2;
  protected readonly featherPlus = featherPlus;
  protected readonly featherFilePlus = featherFilePlus;
  protected readonly featherScissors = featherScissors;

  private readonly pdfInput = viewChild<ElementRef<HTMLInputElement>>('pdfInput');

  protected readonly isCurrent = computed(() =>
    Object.fromEntries(this.store.pages().map(p => [p.index, p.index === this.store.currentPage()])),
  );

  protected readonly goToLabels = computed(() =>
    Object.fromEntries(this.store.pages().map(p => [p.index, fill(this.t().thumbnails.goToPage, {page: p.index + 1})])),
  );

  protected async onDrop(event: CdkDragDrop<unknown>): Promise<void> {
    if (event.previousIndex !== event.currentIndex) {
      await this.store.movePage(event.previousIndex, event.currentIndex);
    }
  }

  protected chooseInsertPdf(): void {
    this.pdfInput()?.nativeElement.click();
  }

  protected async onInsertPdf(event: Event): Promise<void> {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    input.value = '';
    if (file) {
      await this.store.insertPdf(file, this.store.currentPage() + 1);
    }
  }

  protected async extract(): Promise<void> {
    const strings = this.t().thumbnails;
    const pages = await this.dialogService.getValuesFromMultipleSelectionDialog({
      title: strings.savePages,
      text: strings.extractText,
      options: this.store.pages().map(p => ({
        display: fill(strings.pageOption, {page: p.index + 1}),
        value: p.index,
        isChecked: p.index === this.store.currentPage(),
      })),
      confirmActionName: strings.savePdf,
    });
    if (pages && pages.length > 0) {
      await this.store.extractPages([...pages].sort((a, b) => a - b));
    }
  }
}
