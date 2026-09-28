import {Component, computed, DestroyRef, inject, signal} from '@angular/core';
import {takeUntilDestroyed, toSignal} from '@angular/core/rxjs-interop';
import {FormControl, ReactiveFormsModule} from '@angular/forms';
import {NgIcon} from '@ng-icons/core';
import {featherAlertTriangle, featherCheck, featherX} from '@ng-icons/feather-icons';
import {
  CalendarType,
  ConvertedDateSchema,
  convertSpecialDateView,
  createSpecialDateView,
  getHebrewYearView,
  HebrewYearSchema,
  SpecialDateCategory,
  SpecialDateSchema,
  updateSpecialDateView,
} from '../../../generated-files/api/special-dates';
import {BaseDialogComponent} from '../../common/dialogs/base-dialog.component';
import {
  formatFullDateWithWeekday,
  SPECIAL_DATE_CATEGORIES,
  SPECIAL_DATE_CATEGORY_BY_VALUE,
  todayIso,
} from '../special-dates.constants';

export interface SpecialDateDialogData {
  specialDate: SpecialDateSchema | null;
}

const ADAR = 12;
const ADAR_II = 13;

@Component({
  selector: 'app-special-date-dialog',
  standalone: true,
  imports: [ReactiveFormsModule, NgIcon],
  templateUrl: './special-date-dialog.component.html',
})
export class SpecialDateDialogComponent extends BaseDialogComponent<SpecialDateDialogData, SpecialDateSchema> {
  private readonly destroyRef = inject(DestroyRef);

  readonly isEdit = !!this.data.specialDate;
  readonly title = this.isEdit ? 'עריכת אירוע' : 'אירוע חדש';
  readonly confirmActionName = this.isEdit ? 'שמירה' : 'הוספה';

  readonly nameCtrl = new FormControl<string>(this.data.specialDate?.name ?? '', {nonNullable: true});
  readonly gregorianDateCtrl = new FormControl<string>(this.data.specialDate?.date ?? '', {nonNullable: true});
  readonly hebrewYearCtrl = new FormControl<number | null>(this.data.specialDate?.hebrew_year ?? null);
  readonly hebrewMonthCtrl = new FormControl<number | null>(this.data.specialDate?.hebrew_month ?? null);
  readonly hebrewDayCtrl = new FormControl<number | null>(this.data.specialDate?.hebrew_day ?? null);

  readonly category = signal<SpecialDateCategory>(this.data.specialDate?.category ?? 'birthday');
  readonly inputCalendar = signal<CalendarType>(this.data.specialDate?.input_calendar ?? 'gregorian');
  readonly afterSunset = signal<boolean>(this.data.specialDate?.after_sunset ?? false);
  readonly remindHebrew = signal<boolean>(this.data.specialDate?.remind_hebrew ?? true);
  readonly remindGregorian = signal<boolean>(this.data.specialDate?.remind_gregorian ?? true);
  readonly hebrewYear = signal<HebrewYearSchema | null>(null);
  readonly converted = signal<ConvertedDateSchema | null>(null);
  readonly conversionError = signal<string>('');
  readonly isSaving = signal<boolean>(false);
  readonly errorMessage = signal<string>('');

  readonly categories = SPECIAL_DATE_CATEGORIES;

  readonly categoryOption = computed(() => SPECIAL_DATE_CATEGORY_BY_VALUE[this.category()]);
  readonly categorySelected = computed(() => {
    const selected = this.category();
    return Object.fromEntries(SPECIAL_DATE_CATEGORIES.map(c => [c.value, c.value === selected]));
  });
  readonly isHebrewInput = computed(() => this.inputCalendar() === 'hebrew');
  readonly noReminders = computed(() => !this.remindHebrew() && !this.remindGregorian());

  private readonly nameValue = toSignal(this.nameCtrl.valueChanges, {initialValue: this.nameCtrl.value});
  private readonly hebrewMonthValue = toSignal(this.hebrewMonthCtrl.valueChanges, {initialValue: this.hebrewMonthCtrl.value});

  readonly namePreview = computed(() => {
    const name = this.nameValue().trim();
    if (!name) {
      return '';
    }
    const option = this.categoryOption();
    return option.namePrefix ? `${option.emoji} ${option.namePrefix} ${name}` : `${option.emoji} ${name}`;
  });
  readonly hebrewDayOptions = computed(() => {
    const year = this.hebrewYear();
    if (!year) {
      return [];
    }
    const month = year.months.find(m => m.value === this.hebrewMonthValue());
    return year.days.slice(0, month?.days ?? 30);
  });
  readonly convertedGregorianLabel = computed(() => {
    const converted = this.converted();
    return converted ? formatFullDateWithWeekday(converted.date) : '';
  });
  readonly convertedHebrewLabel = computed(() => this.converted()?.hebrew_date ?? '');
  readonly canSave = computed(() => !!this.nameValue().trim() && !!this.converted() && !this.isSaving());

  private conversionRequestId = 0;
  private yearRequestId = 0;

  protected readonly featherAlertTriangle = featherAlertTriangle;
  protected readonly featherCheck = featherCheck;
  protected readonly featherX = featherX;

  constructor() {
    super();
    this.gregorianDateCtrl.valueChanges.pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe(() => void this.refreshConversion());
    this.hebrewYearCtrl.valueChanges.pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe(year => void this.onHebrewYearChanged(year));
    this.hebrewMonthCtrl.valueChanges.pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe(() => {
        this.clampHebrewDay();
        void this.refreshConversion();
      });
    this.hebrewDayCtrl.valueChanges.pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe(() => void this.refreshConversion());
    void this.initialize();
  }

  private async initialize(): Promise<void> {
    if (this.hebrewYearCtrl.value === null) {
      const res = await convertSpecialDateView({query: {calendar: 'gregorian', date: todayIso()}});
      if (!res.error) {
        this.setHebrewControls(res.data.hebrew_year, res.data.hebrew_month, res.data.hebrew_day);
      }
    }
    await this.loadHebrewYear(this.hebrewYearCtrl.value);
    await this.refreshConversion();
  }

  selectCategory(category: SpecialDateCategory): void {
    this.category.set(category);
  }

  selectInputCalendar(calendar: CalendarType): void {
    if (calendar === this.inputCalendar()) {
      return;
    }
    const converted = this.converted();
    if (converted) {
      if (calendar === 'gregorian') {
        this.gregorianDateCtrl.setValue(converted.date, {emitEvent: false});
      } else {
        this.setHebrewControls(converted.hebrew_year, converted.hebrew_month, converted.hebrew_day);
        void this.loadHebrewYear(converted.hebrew_year);
      }
    }
    this.inputCalendar.set(calendar);
    void this.refreshConversion();
  }

  toggleAfterSunset(): void {
    this.afterSunset.update(v => !v);
    void this.refreshConversion();
  }

  toggleRemindHebrew(): void {
    this.remindHebrew.update(v => !v);
  }

  toggleRemindGregorian(): void {
    this.remindGregorian.update(v => !v);
  }

  private setHebrewControls(year: number, month: number, day: number): void {
    this.hebrewYearCtrl.setValue(year, {emitEvent: false});
    this.hebrewMonthCtrl.setValue(month, {emitEvent: false});
    this.hebrewDayCtrl.setValue(day, {emitEvent: false});
  }

  private async onHebrewYearChanged(year: number | null): Promise<void> {
    await this.loadHebrewYear(year);
    const info = this.hebrewYear();
    const month = this.hebrewMonthCtrl.value;
    if (info && !info.is_leap && month === ADAR_II) {
      this.hebrewMonthCtrl.setValue(ADAR, {emitEvent: false});
    }
    this.clampHebrewDay();
    await this.refreshConversion();
  }

  private async loadHebrewYear(year: number | null): Promise<void> {
    if (year === null) {
      return;
    }
    const requestId = ++this.yearRequestId;
    const res = await getHebrewYearView({query: {year}});
    if (requestId !== this.yearRequestId || res.error) {
      return;
    }
    this.hebrewYear.set(res.data);
  }

  private clampHebrewDay(): void {
    const month = this.hebrewYear()?.months.find(m => m.value === this.hebrewMonthCtrl.value);
    const day = this.hebrewDayCtrl.value;
    if (month && day !== null && day > month.days) {
      this.hebrewDayCtrl.setValue(month.days, {emitEvent: false});
    }
  }

  private async refreshConversion(): Promise<void> {
    const requestId = ++this.conversionRequestId;
    this.conversionError.set('');
    const afterSunset = this.afterSunset();
    let res;
    if (this.isHebrewInput()) {
      const year = this.hebrewYearCtrl.value;
      const month = this.hebrewMonthCtrl.value;
      const day = this.hebrewDayCtrl.value;
      if (year === null || month === null || day === null) {
        this.converted.set(null);
        return;
      }
      res = await convertSpecialDateView({
        query: {calendar: 'hebrew', hebrew_year: year, hebrew_month: month, hebrew_day: day, after_sunset: afterSunset},
      });
    } else {
      const date = this.gregorianDateCtrl.value;
      if (!date) {
        this.converted.set(null);
        return;
      }
      res = await convertSpecialDateView({query: {calendar: 'gregorian', date, after_sunset: afterSunset}});
    }
    if (requestId !== this.conversionRequestId) {
      return;
    }
    if (res.error) {
      const err = res.error as {detail?: string};
      this.converted.set(null);
      this.conversionError.set(err?.detail || 'התאריך לא תקין.');
      return;
    }
    this.converted.set(res.data);
  }

  async onSave(): Promise<void> {
    const converted = this.converted();
    if (!this.canSave() || !converted) {
      return;
    }
    this.isSaving.set(true);
    this.errorMessage.set('');
    const body = {
      name: this.nameCtrl.value.trim(),
      category: this.category(),
      date: converted.date,
      after_sunset: converted.after_sunset,
      input_calendar: this.inputCalendar(),
      remind_hebrew: this.remindHebrew(),
      remind_gregorian: this.remindGregorian(),
    };
    try {
      const existing = this.data.specialDate;
      const res = existing
        ? await updateSpecialDateView({path: {object_id: existing.id}, body})
        : await createSpecialDateView({body});
      if (res.error) {
        const err = res.error as {detail?: string};
        this.errorMessage.set(err?.detail || 'השמירה נכשלה, נסו שוב.');
        return;
      }
      this.emitClose(res.data);
    } finally {
      this.isSaving.set(false);
    }
  }

  onClose(): void {
    this.emitClose(null);
  }
}
