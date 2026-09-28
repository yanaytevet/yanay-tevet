import {Component, computed, signal} from '@angular/core';
import {NgIcon} from '@ng-icons/core';
import {featherCheck, featherX} from '@ng-icons/feather-icons';
import {
  listSpecialDateCalendarsView,
  moveSpecialDatesView,
  paginateSpecialDatesView,
  SpecialDateCalendarSchema,
  SpecialDateSchema,
} from '../../../generated-files/api/special-dates';
import {BaseDialogComponent} from '../../common/dialogs/base-dialog.component';
import {calendarColorClass, SPECIAL_DATE_CATEGORY_BY_VALUE} from '../special-dates.constants';

export interface MoveDatesDialogData {
  targetCalendarId: number;
  isAfterJoin: boolean;
}

const MAX_PAGE_SIZE = 1000;

function duplicateKey(specialDate: SpecialDateSchema): string {
  return `${specialDate.name.trim().toLowerCase()}|${specialDate.hebrew_month}|${specialDate.hebrew_day}`;
}

@Component({
  selector: 'app-move-dates-dialog',
  standalone: true,
  imports: [NgIcon],
  templateUrl: './move-dates-dialog.component.html',
})
export class MoveDatesDialogComponent extends BaseDialogComponent<MoveDatesDialogData, boolean> {
  readonly target = signal<SpecialDateCalendarSchema | null>(null);
  readonly calendars = signal<SpecialDateCalendarSchema[]>([]);
  readonly candidates = signal<SpecialDateSchema[]>([]);
  readonly duplicateIds = signal<Set<number>>(new Set());
  readonly selectedIds = signal<Set<number>>(new Set());
  readonly isLoading = signal<boolean>(true);
  readonly isMoving = signal<boolean>(false);
  readonly errorMessage = signal<string>('');

  readonly rows = computed(() => {
    const calendarsById = new Map(this.calendars().map(c => [c.id, c]));
    const selected = this.selectedIds();
    const duplicates = this.duplicateIds();
    return this.candidates().map(d => ({
      specialDate: d,
      emoji: SPECIAL_DATE_CATEGORY_BY_VALUE[d.category].emoji,
      calendarName: calendarsById.get(d.calendar_id ?? -1)?.name ?? '',
      calendarColor: calendarColorClass(d.calendar_id ?? 0),
      isSelected: selected.has(d.id),
      isDuplicate: duplicates.has(d.id),
    }));
  });
  readonly selectedCount = computed(() => this.selectedIds().size);
  readonly allSelected = computed(() => this.candidates().length > 0
    && this.candidates().every(d => this.selectedIds().has(d.id) || this.duplicateIds().has(d.id)));
  readonly title = this.data.isAfterJoin ? 'הצטרפת ללוח! 🎉' : 'העברת אירועים';

  protected readonly featherCheck = featherCheck;
  protected readonly featherX = featherX;

  constructor() {
    super();
    void this.load();
  }

  private async load(): Promise<void> {
    try {
      const [calendarsRes, datesRes] = await Promise.all([
        listSpecialDateCalendarsView(),
        paginateSpecialDatesView({query: {page: 0, page_size: MAX_PAGE_SIZE}}),
      ]);
      if (calendarsRes.error || datesRes.error) {
        return;
      }
      const calendars = calendarsRes.data.calendars;
      this.calendars.set(calendars);
      this.target.set(calendars.find(c => c.id === this.data.targetCalendarId) ?? null);
      const ownedSourceIds = new Set(calendars.filter(c => c.is_owner && c.id !== this.data.targetCalendarId).map(c => c.id));
      const allDates = datesRes.data.data;
      const targetKeys = new Set(allDates.filter(d => d.calendar_id === this.data.targetCalendarId).map(duplicateKey));
      const candidates = allDates.filter(d => d.calendar_id !== null && ownedSourceIds.has(d.calendar_id));
      this.candidates.set(candidates);
      this.duplicateIds.set(new Set(candidates.filter(d => targetKeys.has(duplicateKey(d))).map(d => d.id)));
    } finally {
      this.isLoading.set(false);
    }
  }

  toggle(id: number): void {
    this.selectedIds.update(current => {
      const next = new Set(current);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  }

  toggleAll(): void {
    if (this.allSelected()) {
      this.selectedIds.set(new Set());
      return;
    }
    const duplicates = this.duplicateIds();
    this.selectedIds.set(new Set(this.candidates().filter(d => !duplicates.has(d.id)).map(d => d.id)));
  }

  async onMove(): Promise<void> {
    const ids = [...this.selectedIds()];
    if (ids.length === 0 || this.isMoving()) {
      return;
    }
    this.isMoving.set(true);
    this.errorMessage.set('');
    try {
      const res = await moveSpecialDatesView({body: {special_date_ids: ids, calendar_id: this.data.targetCalendarId}});
      if (res.error) {
        const err = res.error as {detail?: string};
        this.errorMessage.set(err?.detail || 'ההעברה נכשלה, נסו שוב.');
        return;
      }
      this.emitClose(true);
    } finally {
      this.isMoving.set(false);
    }
  }

  onClose(): void {
    this.emitClose(false);
  }
}
