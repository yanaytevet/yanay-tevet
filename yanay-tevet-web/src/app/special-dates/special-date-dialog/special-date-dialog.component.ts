import {Component, computed, DestroyRef, inject, signal} from '@angular/core';
import {takeUntilDestroyed, toSignal} from '@angular/core/rxjs-interop';
import {FormControl, ReactiveFormsModule} from '@angular/forms';
import {NgIcon} from '@ng-icons/core';
import {featherAlertTriangle, featherUsers, featherX} from '@ng-icons/feather-icons';
import {
  CalendarType,
  ConvertedDateSchema,
  convertSpecialDateView,
  createSpecialDateView,
  getHebrewYearView,
  HebrewYearSchema,
  SpecialDateCalendarSchema,
  SpecialDateCategory,
  SpecialDateSchema,
  updateSpecialDateView,
} from '../../../generated-files/api/special-dates';
import {BaseDialogComponent} from '../../common/dialogs/base-dialog.component';
import {LanguageService} from '../../shared/i18n/language.service';
import {fill, injectStrings} from '../../shared/i18n/strings';
import {SPECIAL_DATES_STRINGS} from '../i18n';
import {
  calendarColorClass,
  formatFullDateWithWeekday,
  formatHebrewDate,
  hebrewMonthName,
  SPECIAL_DATE_CATEGORIES,
  storeLastCalendarId,
  SPECIAL_DATE_CATEGORY_BY_VALUE,
  todayIso,
} from '../special-dates.constants';
import {CheckboxMarkComponent} from '../../common/components/inputs/checkbox-mark/checkbox-mark.component';

export interface SpecialDateDialogData {
  specialDate: SpecialDateSchema | null;
  calendars: SpecialDateCalendarSchema[];
  defaultCalendarId: number;
}

const ADAR = 12;
const ADAR_II = 13;

@Component({
  selector: 'app-special-date-dialog',
  standalone: true,
  imports: [CheckboxMarkComponent, ReactiveFormsModule, NgIcon],
  templateUrl: './special-date-dialog.component.html',
})
export class SpecialDateDialogComponent extends BaseDialogComponent<SpecialDateDialogData, SpecialDateSchema> {
  private readonly destroyRef = inject(DestroyRef);
  private readonly language = inject(LanguageService).language;
  protected readonly t = injectStrings(SPECIAL_DATES_STRINGS);

  readonly isEdit = !!this.data.specialDate;
  readonly title = computed(() => this.isEdit ? this.t().dialog.titleEdit : this.t().dialog.titleNew);
  readonly confirmActionName = computed(() => this.isEdit ? this.t().save : this.t().dialog.add);

  readonly nameCtrl = new FormControl<string>(this.data.specialDate?.name ?? '', {nonNullable: true});
  readonly gregorianDateCtrl = new FormControl<string>(this.data.specialDate?.date ?? '', {nonNullable: true});
  readonly hebrewYearCtrl = new FormControl<number | null>(this.data.specialDate?.hebrew_year ?? null);
  readonly hebrewMonthCtrl = new FormControl<number | null>(this.data.specialDate?.hebrew_month ?? null);
  readonly hebrewDayCtrl = new FormControl<number | null>(this.data.specialDate?.hebrew_day ?? null);

  readonly calendarId = signal<number>(this.data.specialDate?.calendar_id ?? this.data.defaultCalendarId);
  readonly showCalendarPicker = this.data.calendars.length > 1;
  readonly calendarOptions = computed(() => {
    const selected = this.calendarId();
    return this.data.calendars.map(c => ({
      id: c.id,
      name: c.name,
      isShared: c.member_count > 1,
      colorClass: calendarColorClass(c.id),
      isSelected: c.id === selected,
    }));
  });

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

  readonly categories = computed(() => {
    const t = this.t();
    return SPECIAL_DATE_CATEGORIES.map(c => ({value: c.value, emoji: c.emoji, label: t.categories[c.value].label}));
  });

  readonly categoryStrings = computed(() => this.t().categories[this.category()]);
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
    const emoji = SPECIAL_DATE_CATEGORY_BY_VALUE[this.category()].emoji;
    return `${emoji} ${fill(this.categoryStrings().nameTemplate, {name})}`;
  });
  // The picker's labels: the backend's Hebrew ones (gematria, Hebrew month names) in Hebrew, otherwise plain
  // numbers and the month names of the strings file.
  readonly hebrewDayOptions = computed(() => {
    const year = this.hebrewYear();
    if (!year) {
      return [];
    }
    const isHebrew = this.language() === 'he';
    const month = year.months.find(m => m.value === this.hebrewMonthValue());
    return year.days.slice(0, month?.days ?? 30)
      .map(d => ({value: d.value, label: isHebrew ? d.label : String(d.value)}));
  });
  readonly hebrewMonthOptions = computed(() => {
    const year = this.hebrewYear();
    if (!year) {
      return [];
    }
    const t = this.t();
    const isHebrew = this.language() === 'he';
    return year.months.map(m => ({value: m.value, label: isHebrew ? m.label : hebrewMonthName(m.value, year.is_leap, t)}));
  });
  readonly hebrewYearOptions = computed(() => {
    const isHebrew = this.language() === 'he';
    return (this.hebrewYear()?.years ?? []).map(y => ({value: y.value, label: isHebrew ? y.label : String(y.value)}));
  });
  readonly convertedGregorianLabel = computed(() => {
    const converted = this.converted();
    return converted ? formatFullDateWithWeekday(converted.date, this.language()) : '';
  });
  readonly convertedHebrewLabel = computed(() => {
    const converted = this.converted();
    return converted
      ? formatHebrewDate(converted.date, converted.after_sunset, converted.hebrew_date, this.language(), this.t())
      : '';
  });
  readonly canSave = computed(() => !!this.nameValue().trim() && !!this.converted() && !this.isSaving());

  private conversionRequestId = 0;
  private yearRequestId = 0;

  protected readonly featherAlertTriangle = featherAlertTriangle;
  protected readonly featherUsers = featherUsers;
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

  selectCalendar(calendarId: number): void {
    this.calendarId.set(calendarId);
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
      this.conversionError.set(err?.detail || this.t().dialog.invalidDate);
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
      calendar_id: this.calendarId(),
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
        this.errorMessage.set(err?.detail || this.t().dialog.saveFailed);
        return;
      }
      storeLastCalendarId(this.calendarId());
      this.emitClose(res.data);
    } finally {
      this.isSaving.set(false);
    }
  }

  onClose(): void {
    this.emitClose(null);
  }
}
