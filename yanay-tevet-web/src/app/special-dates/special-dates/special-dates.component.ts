import {Component, computed, DestroyRef, inject, signal} from '@angular/core';
import {NgIcon} from '@ng-icons/core';
import {featherBellOff, featherEdit2, featherPlus, featherSearch, featherTrash2} from '@ng-icons/feather-icons';
import {
  deleteSpecialDateView,
  getUpcomingSpecialDatesView,
  paginateSpecialDatesView,
  SpecialDateCategory,
  SpecialDateSchema,
  UpcomingSpecialDatesSchema,
} from '../../../generated-files/api/special-dates';
import {DialogService} from '../../common/dialogs/dialogs.service';
import {SpecialDateDialogComponent, SpecialDateDialogData} from '../special-date-dialog/special-date-dialog.component';
import {
  CALENDAR_CHIPS,
  formatDaysUntil,
  formatFullDate,
  formatLongDate,
  formatYears,
  SPECIAL_DATE_CATEGORIES,
  SPECIAL_DATE_CATEGORY_BY_VALUE,
} from '../special-dates.constants';

type SpecialDatesTab = 'upcoming' | 'all';

const SEARCH_DEBOUNCE_MS = 250;
const MAX_PAGE_SIZE = 500;

@Component({
  selector: 'app-special-dates',
  standalone: true,
  imports: [NgIcon],
  templateUrl: './special-dates.component.html',
})
export class SpecialDatesComponent {
  private readonly dialogService = inject(DialogService);

  readonly tab = signal<SpecialDatesTab>('upcoming');
  readonly upcoming = signal<UpcomingSpecialDatesSchema | null>(null);
  readonly allDates = signal<SpecialDateSchema[]>([]);
  readonly searchText = signal<string>('');
  readonly categoryFilter = signal<SpecialDateCategory | null>(null);
  readonly isLoadingUpcoming = signal<boolean>(true);
  readonly isLoadingAll = signal<boolean>(false);
  readonly hasLoadedAll = signal<boolean>(false);

  readonly categories = SPECIAL_DATE_CATEGORIES;

  readonly todayGregorian = computed(() => {
    const upcoming = this.upcoming();
    return upcoming ? formatFullDate(upcoming.today) : '';
  });
  readonly todayHebrew = computed(() => this.upcoming()?.today_hebrew_date ?? '');
  readonly totalCount = computed(() => this.upcoming()?.total_count ?? 0);
  readonly maxCount = computed(() => this.upcoming()?.max_count ?? MAX_PAGE_SIZE);
  readonly isAtLimit = computed(() => this.upcoming() !== null && this.totalCount() >= this.maxCount());
  readonly upcomingDays = computed(() => this.upcoming()?.days ?? 14);

  readonly upcomingRows = computed(() => (this.upcoming()?.occurrences ?? []).map(o => {
    const category = SPECIAL_DATE_CATEGORY_BY_VALUE[o.special_date.category];
    return {
      key: `${o.special_date.id}-${o.date}`,
      specialDate: o.special_date,
      emoji: category.emoji,
      categoryLabel: category.label,
      name: o.special_date.name,
      daysLabel: formatDaysUntil(o.days_until),
      isToday: o.days_until === 0,
      gregorianDate: formatLongDate(o.date),
      hebrewDate: o.hebrew_date,
      yearsLabel: formatYears(o.special_date.category, o.years),
      calendarChips: o.calendars.map(c => CALENDAR_CHIPS[c]),
    };
  }));
  readonly todayRows = computed(() => this.upcomingRows().filter(r => r.isToday));
  readonly laterRows = computed(() => this.upcomingRows().filter(r => !r.isToday));

  readonly allRows = computed(() => this.allDates().map(d => {
    const category = SPECIAL_DATE_CATEGORY_BY_VALUE[d.category];
    const gregorianDate = formatFullDate(d.date);
    const next: string[] = [];
    if (d.next_hebrew_date) {
      next.push(`עברי: ${formatFullDate(d.next_hebrew_date)}`);
    }
    if (d.next_gregorian_date) {
      next.push(`לועזי: ${formatFullDate(d.next_gregorian_date)}`);
    }
    const isHebrewInput = d.input_calendar === 'hebrew';
    return {
      specialDate: d,
      emoji: category.emoji,
      categoryLabel: category.label,
      name: d.name,
      primaryDate: isHebrewInput ? d.hebrew_date : gregorianDate,
      secondaryDate: isHebrewInput ? gregorianDate : d.hebrew_date,
      afterSunsetLabel: d.after_sunset ? (isHebrewInput ? 'בין השקיעה לחצות' : 'אחרי השקיעה') : '',
      hasReminders: d.remind_hebrew || d.remind_gregorian,
      nextLabel: next.join(' · '),
    };
  }));

  readonly categoryFilterSelected = computed(() => {
    const selected = this.categoryFilter();
    return Object.fromEntries(SPECIAL_DATE_CATEGORIES.map(c => [c.value, c.value === selected]));
  });
  readonly isFiltering = computed(() => !!this.searchText().trim() || this.categoryFilter() !== null);

  protected readonly featherBellOff = featherBellOff;
  protected readonly featherEdit2 = featherEdit2;
  protected readonly featherPlus = featherPlus;
  protected readonly featherSearch = featherSearch;
  protected readonly featherTrash2 = featherTrash2;

  private searchTimeout: ReturnType<typeof setTimeout> | null = null;
  private searchRequestId = 0;

  constructor() {
    inject(DestroyRef).onDestroy(() => this.clearSearchTimeout());
    void this.loadUpcoming();
  }

  selectTab(tab: SpecialDatesTab): void {
    this.tab.set(tab);
    if (tab === 'all' && !this.hasLoadedAll()) {
      void this.loadAll();
    }
  }

  onSearchInput(event: Event): void {
    this.searchText.set((event.target as HTMLInputElement).value);
    this.clearSearchTimeout();
    this.searchTimeout = setTimeout(() => void this.loadAll(), SEARCH_DEBOUNCE_MS);
  }

  toggleCategoryFilter(category: SpecialDateCategory): void {
    this.categoryFilter.update(current => current === category ? null : category);
    void this.loadAll();
  }

  async addSpecialDate(): Promise<void> {
    if (this.isAtLimit()) {
      await this.dialogService.showNotificationDialog({
        title: 'הגעת למגבלה',
        text: `אפשר לשמור עד ${this.maxCount()} אירועים. מחקו אירועים ישנים כדי להוסיף חדשים.`,
      });
      return;
    }
    await this.openDialog({specialDate: null});
  }

  async editSpecialDate(specialDate: SpecialDateSchema): Promise<void> {
    await this.openDialog({specialDate});
  }

  async deleteSpecialDate(specialDate: SpecialDateSchema): Promise<void> {
    const confirmed = await this.dialogService.getBooleanFromConfirmationDialog({
      title: 'מחיקת אירוע',
      text: `למחוק את "${specialDate.name}"?`,
      confirmActionName: 'מחיקה',
      cancelActionName: 'ביטול',
    });
    if (!confirmed) {
      return;
    }
    const res = await deleteSpecialDateView({path: {object_id: specialDate.id}});
    if (res.error) {
      await this.dialogService.showNotificationDialog({title: 'שגיאה', text: 'המחיקה נכשלה, נסו שוב.'});
      return;
    }
    await this.reload();
  }

  private async openDialog(data: SpecialDateDialogData): Promise<void> {
    const saved = await this.dialogService.open<SpecialDateDialogData, SpecialDateSchema>(
      SpecialDateDialogComponent, data, 40);
    if (saved) {
      await this.reload();
    }
  }

  private async reload(): Promise<void> {
    await Promise.all([
      this.loadUpcoming(),
      this.hasLoadedAll() ? this.loadAll() : Promise.resolve(),
    ]);
  }

  private async loadUpcoming(): Promise<void> {
    try {
      const res = await getUpcomingSpecialDatesView();
      if (!res.error) {
        this.upcoming.set(res.data);
      }
    } finally {
      this.isLoadingUpcoming.set(false);
    }
  }

  private async loadAll(): Promise<void> {
    this.clearSearchTimeout();
    const requestId = ++this.searchRequestId;
    this.isLoadingAll.set(true);
    try {
      const search = this.searchText().trim();
      const res = await paginateSpecialDatesView({
        query: {
          page: 0,
          page_size: MAX_PAGE_SIZE,
          search: search || null,
          category: this.categoryFilter(),
        },
      });
      if (requestId !== this.searchRequestId || res.error) {
        return;
      }
      this.allDates.set(res.data.data);
      this.hasLoadedAll.set(true);
    } finally {
      if (requestId === this.searchRequestId) {
        this.isLoadingAll.set(false);
      }
    }
  }

  private clearSearchTimeout(): void {
    if (this.searchTimeout !== null) {
      clearTimeout(this.searchTimeout);
      this.searchTimeout = null;
    }
  }
}
