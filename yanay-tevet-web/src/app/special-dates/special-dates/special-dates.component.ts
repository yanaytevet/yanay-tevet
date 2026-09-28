import {Component, computed, DestroyRef, inject, signal} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import {NgIcon} from '@ng-icons/core';
import {
  featherBellOff,
  featherEdit2,
  featherPlus,
  featherSearch,
  featherTrash2,
  featherUsers,
} from '@ng-icons/feather-icons';
import {
  deleteSpecialDateView,
  getUpcomingSpecialDatesView,
  listSpecialDateCalendarsView,
  paginateSpecialDatesView,
  SpecialDateCalendarSchema,
  SpecialDateCategory,
  SpecialDateSchema,
  UpcomingSpecialDatesSchema,
} from '../../../generated-files/api/special-dates';
import {DialogService} from '../../common/dialogs/dialogs.service';
import {CalendarShareDialogComponent, CalendarShareDialogData} from '../calendar-share-dialog/calendar-share-dialog.component';
import {CalendarsDialogComponent} from '../calendars-dialog/calendars-dialog.component';
import {MoveDatesDialogComponent, MoveDatesDialogData} from '../move-dates-dialog/move-dates-dialog.component';
import {SpecialDateDialogComponent, SpecialDateDialogData} from '../special-date-dialog/special-date-dialog.component';
import {
  CALENDAR_CHIPS,
  calendarColorClass,
  formatDaysUntil,
  formatFullDate,
  formatLongDate,
  formatYears,
  readLastCalendarId,
  SPECIAL_DATE_CATEGORIES,
  SPECIAL_DATE_CATEGORY_BY_VALUE,
} from '../special-dates.constants';

type SpecialDatesTab = 'upcoming' | 'all';

const SEARCH_DEBOUNCE_MS = 250;
const MAX_PAGE_SIZE = 1000;

@Component({
  selector: 'app-special-dates',
  standalone: true,
  imports: [NgIcon],
  templateUrl: './special-dates.component.html',
})
export class SpecialDatesComponent {
  private readonly dialogService = inject(DialogService);
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);

  readonly tab = signal<SpecialDatesTab>('upcoming');
  readonly calendars = signal<SpecialDateCalendarSchema[]>([]);
  readonly selectedCalendarId = signal<number | null>(null);
  readonly upcoming = signal<UpcomingSpecialDatesSchema | null>(null);
  readonly allDates = signal<SpecialDateSchema[]>([]);
  readonly searchText = signal<string>('');
  readonly categoryFilter = signal<SpecialDateCategory | null>(null);
  readonly isLoadingUpcoming = signal<boolean>(true);
  readonly isLoadingAll = signal<boolean>(false);
  readonly hasLoadedAll = signal<boolean>(false);

  readonly categories = SPECIAL_DATE_CATEGORIES;

  readonly hasMultipleCalendars = computed(() => this.calendars().length > 1);
  readonly totalEventCount = computed(() => this.calendars().reduce((sum, c) => sum + c.event_count, 0));
  readonly shareButtonLabel = computed(() => this.hasMultipleCalendars() ? 'לוחות ושיתוף' : 'שיתוף');
  readonly calendarsById = computed(() => new Map(this.calendars().map(c => [c.id, c])));
  readonly calendarChips = computed(() => {
    const selected = this.selectedCalendarId();
    return this.calendars().map(c => ({
      id: c.id,
      name: c.name,
      colorClass: calendarColorClass(c.id),
      isSelected: c.id === selected,
      isShared: c.member_count > 1,
      isHidden: c.hide_from_upcoming,
    }));
  });

  readonly todayGregorian = computed(() => {
    const upcoming = this.upcoming();
    return upcoming ? formatFullDate(upcoming.today) : '';
  });
  readonly todayHebrew = computed(() => this.upcoming()?.today_hebrew_date ?? '');
  readonly upcomingDays = computed(() => this.upcoming()?.days ?? 14);

  readonly upcomingRows = computed(() => {
    const selected = this.selectedCalendarId();
    const calendarsById = this.calendarsById();
    const showCalendar = this.hasMultipleCalendars();
    return (this.upcoming()?.occurrences ?? [])
      .filter(o => selected === null || o.special_date.calendar_id === selected)
      .map(o => {
        const category = SPECIAL_DATE_CATEGORY_BY_VALUE[o.special_date.category];
        const calendarId = o.special_date.calendar_id ?? 0;
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
          calendarName: showCalendar ? (calendarsById.get(calendarId)?.name ?? '') : '',
          calendarColor: calendarColorClass(calendarId),
        };
      });
  });
  readonly todayRows = computed(() => this.upcomingRows().filter(r => r.isToday));
  readonly laterRows = computed(() => this.upcomingRows().filter(r => !r.isToday));

  readonly allRows = computed(() => {
    const calendarsById = this.calendarsById();
    const showCalendar = this.hasMultipleCalendars();
    return this.allDates().map(d => {
      const category = SPECIAL_DATE_CATEGORY_BY_VALUE[d.category];
      const calendar = calendarsById.get(d.calendar_id ?? -1);
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
        calendarName: showCalendar ? (calendar?.name ?? '') : '',
        calendarColor: calendarColorClass(d.calendar_id ?? 0),
        addedByLabel: calendar && calendar.member_count > 1 && d.created_by_name ? `נוסף ע״י ${d.created_by_name}` : '',
      };
    });
  });

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
  protected readonly featherUsers = featherUsers;

  private searchTimeout: ReturnType<typeof setTimeout> | null = null;
  private searchRequestId = 0;

  constructor() {
    inject(DestroyRef).onDestroy(() => this.clearSearchTimeout());
    void this.initialize();
  }

  private async initialize(): Promise<void> {
    await Promise.all([this.loadCalendars(), this.loadUpcoming()]);
    const joined = Number(this.route.snapshot.queryParamMap.get('joined'));
    if (joined) {
      await this.router.navigate([], {queryParams: {}, replaceUrl: true});
      await this.openMoveDialog(joined, true);
    }
  }

  selectTab(tab: SpecialDatesTab): void {
    this.tab.set(tab);
    if (tab === 'all' && !this.hasLoadedAll()) {
      void this.loadAll();
    }
  }

  selectCalendar(calendarId: number | null): void {
    this.selectedCalendarId.update(current => current === calendarId ? null : calendarId);
    if (this.hasLoadedAll()) {
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

  async openSharing(): Promise<void> {
    const calendars = this.calendars();
    let changed: boolean | null;
    if (calendars.length === 1) {
      changed = await this.dialogService.open<CalendarShareDialogData, boolean>(
        CalendarShareDialogComponent, {calendarId: calendars[0].id}, 40);
    } else {
      changed = await this.dialogService.open<void, boolean>(CalendarsDialogComponent, undefined, 40);
    }
    if (changed) {
      await this.reload();
    }
  }

  async addSpecialDate(): Promise<void> {
    await this.openDialog(null);
  }

  async editSpecialDate(specialDate: SpecialDateSchema): Promise<void> {
    await this.openDialog(specialDate);
  }

  async deleteSpecialDate(specialDate: SpecialDateSchema): Promise<void> {
    const calendar = this.calendarsById().get(specialDate.calendar_id ?? -1);
    const shared = calendar && calendar.member_count > 1 ? ' הוא יימחק גם אצל שאר החברים בלוח.' : '';
    const confirmed = await this.dialogService.getBooleanFromConfirmationDialog({
      title: 'מחיקת אירוע',
      text: `למחוק את "${specialDate.name}"?${shared}`,
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

  private defaultCalendarId(): number {
    const calendars = this.calendars();
    const ids = new Set(calendars.map(c => c.id));
    const selected = this.selectedCalendarId();
    if (selected !== null && ids.has(selected)) {
      return selected;
    }
    const last = readLastCalendarId();
    if (last !== null && ids.has(last)) {
      return last;
    }
    return (calendars.find(c => c.is_owner) ?? calendars[0]).id;
  }

  private async openDialog(specialDate: SpecialDateSchema | null): Promise<void> {
    if (this.calendars().length === 0) {
      return;
    }
    const saved = await this.dialogService.open<SpecialDateDialogData, SpecialDateSchema>(
      SpecialDateDialogComponent,
      {specialDate, calendars: this.calendars(), defaultCalendarId: this.defaultCalendarId()},
      40,
    );
    if (saved) {
      await this.reload();
    }
  }

  private async openMoveDialog(targetCalendarId: number, isAfterJoin: boolean): Promise<void> {
    const moved = await this.dialogService.open<MoveDatesDialogData, boolean>(
      MoveDatesDialogComponent, {targetCalendarId, isAfterJoin}, 40);
    if (moved) {
      await this.reload();
    }
  }

  private async reload(): Promise<void> {
    await Promise.all([
      this.loadCalendars(),
      this.loadUpcoming(),
      this.hasLoadedAll() ? this.loadAll() : Promise.resolve(),
    ]);
  }

  private async loadCalendars(): Promise<void> {
    const res = await listSpecialDateCalendarsView();
    if (res.error) {
      return;
    }
    this.calendars.set(res.data.calendars);
    const selected = this.selectedCalendarId();
    if (selected !== null && !res.data.calendars.some(c => c.id === selected)) {
      this.selectedCalendarId.set(null);
    }
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
          calendar_id: this.selectedCalendarId(),
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
