import {Component, computed, inject, signal} from '@angular/core';
import {FormControl, ReactiveFormsModule} from '@angular/forms';
import {
  createDreamDiaryEntryView,
  deleteDreamDiaryEntryView,
  getDreamDiaryCalendarView,
  paginateDreamDiaryEntriesView,
  uploadDreamDiaryEntryImageView,
  DreamDiaryEntrySchema,
} from '../../generated-files/api/dream-diary';
import {BasePageComponent} from '../common/components/base-page-component';
import {DialogService} from '../common/dialogs/dialogs.service';
import {FilesUploadService} from '../common/services/files-upload.service';
import {featherBookOpen, featherDelete, featherUpload} from '@ng-icons/feather-icons';
import {NgIcon, provideIcons} from '@ng-icons/core';

interface CalendarDay {
  date: string;
  dayOfMonth: number;
  isLogged: boolean;
  isToday: boolean;
  isCurrentMonth: boolean;
}

const PAGE_SIZE = 10;
const WEEK_COUNT = 4;

@Component({
  selector: 'app-dream-diary',
  standalone: true,
  imports: [ReactiveFormsModule, NgIcon],
  providers: [provideIcons({featherDelete, featherUpload, featherBookOpen})],
  templateUrl: './dream-diary.component.html',
  styleUrl: './dream-diary.component.css',
})
export class DreamDiaryComponent {
  private dialogService = inject(DialogService);
  private filesUploadService = inject(FilesUploadService);

  entries = signal<DreamDiaryEntrySchema[]>([]);
  totalAmount = signal<number>(0);
  currentPage = signal<number>(0);
  isLoadingEntries = signal<boolean>(false);
  isLoadingMore = signal<boolean>(false);
  isCreating = signal<boolean>(false);
  loggedDates = signal<string[]>([]);

  hasMore = computed(() => this.entries().length < this.totalAmount());

  titleCtrl = new FormControl<string>('');
  textCtrl = new FormControl<string>('');
  timeCtrl = new FormControl<string>(this.getTodayLocalDatetimeString());

  calendarDays = computed<CalendarDay[]>(() => {
    const logged = new Set(this.loggedDates());
    const today = new Date();
    const todayStr = this.toDateString(today);
    const days: CalendarDay[] = [];
    for (let i = WEEK_COUNT * 7 - 1; i >= 0; i--) {
      const d = new Date(today);
      d.setDate(today.getDate() - i);
      const dateStr = this.toDateString(d);
      days.push({
        date: dateStr,
        dayOfMonth: d.getDate(),
        isLogged: logged.has(dateStr),
        isToday: dateStr === todayStr,
        isCurrentMonth: d.getMonth() === today.getMonth(),
      });
    }
    return days;
  });

  readonly weekDayLabels = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

  readonly featherDelete = featherDelete;
  readonly featherUpload = featherUpload;

  constructor() {
    this.loadCalendar();
    this.loadEntries(0);
  }

  private toDateString(d: Date): string {
    return d.toISOString().slice(0, 10);
  }

  private getTodayLocalDatetimeString(): string {
    const now = new Date();
    const pad = (n: number) => String(n).padStart(2, '0');
    return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}T${pad(now.getHours())}:${pad(now.getMinutes())}`;
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

  async createEntry(): Promise<void> {
    const text = this.textCtrl.value?.trim();
    if (!text) {
      return;
    }
    this.isCreating.set(true);
    try {
      const time = this.timeCtrl.value
        ? new Date(this.timeCtrl.value).toISOString()
        : new Date().toISOString();
      const entry = await createDreamDiaryEntryView({
        body: {
          title: this.titleCtrl.value?.trim() || '',
          text,
          time,
        },
      });
      this.entries.update(prev => [entry.data, ...prev]);
      this.totalAmount.update(n => n + 1);
      this.titleCtrl.setValue('');
      this.textCtrl.setValue('');
      this.timeCtrl.setValue(this.getTodayLocalDatetimeString());
      await this.loadCalendar();
    } catch (err) {
      await this.dialogService.showNotificationDialog({
        title: 'Error',
        text: `Failed to create entry: ${err}`,
      });
    } finally {
      this.isCreating.set(false);
    }
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
