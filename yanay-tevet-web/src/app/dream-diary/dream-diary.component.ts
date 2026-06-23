import {Component, computed, inject, signal} from '@angular/core';
import {
  deleteDreamDiaryEntryView,
  generateDreamDiaryEntryImageView,
  getDreamDiaryCalendarView,
  paginateDreamDiaryEntriesView,
  uploadDreamDiaryEntryImageView,
  DreamDiaryEntrySchema,
} from '../../generated-files/api/dream-diary';
import {DialogService} from '../common/dialogs/dialogs.service';
import {FilesUploadService} from '../common/services/files-upload.service';
import {RoutingService} from '../shared/services/routing.service';
import {ViewImageDialogComponent} from './dialogs/view-image-dialog/view-image-dialog.component';
import {featherDelete, featherEdit, featherUpload, featherZap} from '@ng-icons/feather-icons';
import {NgIcon, provideIcons} from '@ng-icons/core';

interface CalendarDay {
  date: string;
  dayOfMonth: number;
  isLogged: boolean;
  isToday: boolean;
  isCurrentMonth: boolean;
  isEmpty: boolean;
}

const PAGE_SIZE = 10;
const WEEK_COUNT = 4;

@Component({
  selector: 'app-dream-diary',
  standalone: true,
  imports: [NgIcon],
  providers: [provideIcons({featherDelete, featherUpload, featherEdit, featherZap})],
  templateUrl: './dream-diary.component.html',
  styleUrl: './dream-diary.component.css',
})
export class DreamDiaryComponent {
  private dialogService = inject(DialogService);
  private filesUploadService = inject(FilesUploadService);
  private routingService = inject(RoutingService);

  entries = signal<DreamDiaryEntrySchema[]>([]);
  totalAmount = signal<number>(0);
  currentPage = signal<number>(0);
  isLoadingEntries = signal<boolean>(false);
  isLoadingMore = signal<boolean>(false);
  loggedDates = signal<string[]>([]);
  uploadingId = signal<number | null>(null);
  generatingImageId = signal<number | null>(null);

  hasMore = computed(() => this.entries().length < this.totalAmount());

  calendarDays = computed<CalendarDay[]>(() => {
    const logged = new Set(this.loggedDates());
    const today = new Date();
    const todayStr = this.toDateString(today);

    // Earliest day in the 28-day window
    const firstDay = new Date(today);
    firstDay.setDate(today.getDate() - (WEEK_COUNT * 7 - 1));

    // Walk back to the Sunday of that week so columns align with headers
    const cursor = new Date(firstDay);
    cursor.setDate(firstDay.getDate() - firstDay.getDay());

    const days: CalendarDay[] = [];
    while (cursor <= today) {
      const dateStr = this.toDateString(cursor);
      const inRange = cursor >= firstDay;
      days.push({
        date: dateStr,
        dayOfMonth: cursor.getDate(),
        isLogged: inRange && logged.has(dateStr),
        isToday: dateStr === todayStr,
        isCurrentMonth: cursor.getMonth() === today.getMonth(),
        isEmpty: !inRange,
      });
      cursor.setDate(cursor.getDate() + 1);
    }
    // Pad the final row so the grid stays rectangular
    while (days.length % 7 !== 0) {
      const dateStr = this.toDateString(cursor);
      days.push({date: dateStr, dayOfMonth: cursor.getDate(), isLogged: false, isToday: false, isCurrentMonth: false, isEmpty: true});
      cursor.setDate(cursor.getDate() + 1);
    }
    return days;
  });

  readonly weekDayLabels = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
  readonly featherDelete = featherDelete;
  readonly featherUpload = featherUpload;
  readonly featherEdit = featherEdit;
  readonly featherZap = featherZap;

  constructor() {
    this.loadCalendar();
    this.loadEntries(0);
  }

  private toDateString(d: Date): string {
    return d.toISOString().slice(0, 10);
  }

  private async loadCalendar(): Promise<void> {
    try {
      const res = await getDreamDiaryCalendarView();
      this.loggedDates.set(res.data.logged_dates);
    } catch {
      // ignore
    }
  }

  private async loadEntries(page: number): Promise<void> {
    this.isLoadingEntries.set(true);
    try {
      const res = await paginateDreamDiaryEntriesView({
        query: {page, page_size: PAGE_SIZE},
      });
      this.entries.set(res.data.data);
      this.totalAmount.set(res.data.total_amount);
      this.currentPage.set(page);
    } finally {
      this.isLoadingEntries.set(false);
    }
  }

  async loadMore(): Promise<void> {
    this.isLoadingMore.set(true);
    try {
      const nextPage = this.currentPage() + 1;
      const res = await paginateDreamDiaryEntriesView({
        query: {page: nextPage, page_size: PAGE_SIZE},
      });
      this.entries.update(prev => [...prev, ...res.data.data]);
      this.currentPage.set(nextPage);
    } finally {
      this.isLoadingMore.set(false);
    }
  }

  async goToCreatePage(): Promise<void> {
    await this.routingService.navigateToDreamDiaryNewEntry();
  }

  async openImageDialog(imageUrl: string): Promise<void> {
    await this.dialogService.open(ViewImageDialogComponent, imageUrl, 75);
  }

  async goToEditPage(entry: DreamDiaryEntrySchema): Promise<void> {
    await this.routingService.navigateToDreamDiaryEditEntry(entry.id);
  }

  async deleteEntry(entry: DreamDiaryEntrySchema): Promise<void> {
    const confirmed = await this.dialogService.getBooleanFromConfirmationDialog({
      title: 'Delete Entry',
      text: 'Are you sure you want to delete this dream diary entry?',
      confirmActionName: 'Delete',
      cancelActionName: 'Cancel',
    });
    if (!confirmed) {
      return;
    }
    try {
      await deleteDreamDiaryEntryView({path: {object_id: entry.id}});
      this.entries.update(prev => prev.filter(e => e.id !== entry.id));
      this.totalAmount.update(n => n - 1);
      await this.loadCalendar();
    } catch (err) {
      await this.dialogService.showNotificationDialog({
        title: 'Error',
        text: `Failed to delete entry: ${err}`,
      });
    }
  }

  async uploadImage(entry: DreamDiaryEntrySchema): Promise<void> {
    try {
      const updated = await this.filesUploadService.uploadFile<DreamDiaryEntrySchema>(
        'image/*',
        async (files: File[]) => {
          this.uploadingId.set(entry.id);
          const res = await uploadDreamDiaryEntryImageView({
            body: {files},
            path: {object_id: entry.id},
          });
          return res.data;
        },
      );
      this.entries.update(prev =>
        prev.map(e => (e.id === entry.id ? updated : e)),
      );
    } catch (err) {
      await this.dialogService.showNotificationDialog({
        title: 'Error',
        text: `Failed to upload image: ${err}`,
      });
    } finally {
      this.uploadingId.set(null);
    }
  }

  async generateImage(entry: DreamDiaryEntrySchema): Promise<void> {
    this.generatingImageId.set(entry.id);
    try {
      const res = await generateDreamDiaryEntryImageView({
        body: {},
        path: {object_id: entry.id},
      });
      this.entries.update(prev => prev.map(e => (e.id === entry.id ? res.data : e)));
    } catch (err) {
      await this.dialogService.showNotificationDialog({
        title: 'Error',
        text: `Failed to generate image: ${err}`,
      });
    } finally {
      this.generatingImageId.set(null);
    }
  }

  formatTime(isoString: string): string {
    return new Date(isoString).toLocaleString(undefined, {
      weekday: 'short',
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  }
}
