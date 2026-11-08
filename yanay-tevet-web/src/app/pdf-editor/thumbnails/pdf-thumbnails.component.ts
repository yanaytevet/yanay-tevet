import {CdkDrag, CdkDragDrop, CdkDropList} from '@angular/cdk/drag-drop';
import {Component, computed, ElementRef, inject, output, viewChild} from '@angular/core';
import {NgIcon} from '@ng-icons/core';
import {featherFilePlus, featherPlus, featherRotateCcw, featherRotateCw, featherScissors, featherTrash2} from '@ng-icons/feather-icons';
import {DialogService} from '../../common/dialogs/dialogs.service';
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
    const pages = await this.dialogService.getValuesFromMultipleSelectionDialog({
      title: 'Save pages as a new PDF',
      text: 'Pick the pages to save. This file stays as it is.',
      options: this.store.pages().map(p => ({display: `Page ${p.index + 1}`, value: p.index, isChecked: p.index === this.store.currentPage()})),
      confirmActionName: 'Save PDF',
    });
    if (pages && pages.length > 0) {
      await this.store.extractPages([...pages].sort((a, b) => a - b));
    }
  }
}
