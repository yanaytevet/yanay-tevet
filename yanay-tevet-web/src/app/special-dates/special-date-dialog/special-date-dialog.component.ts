import {Component, computed, DestroyRef, inject, signal} from '@angular/core';
import {takeUntilDestroyed, toSignal} from '@angular/core/rxjs-interop';
import {FormControl, ReactiveFormsModule} from '@angular/forms';
import {NgIcon} from '@ng-icons/core';
import {featherCheck, featherX} from '@ng-icons/feather-icons';
import {
  createSpecialDateView,
  getHebrewDateView,
  SpecialDateCategory,
  SpecialDateRecurrence,
  SpecialDateSchema,
  updateSpecialDateView,
} from '../../../generated-files/api/special-dates';
import {BaseDialogComponent} from '../../common/dialogs/base-dialog.component';
import {
  DEFAULT_RECURRENCE_BY_CATEGORY,
  SPECIAL_DATE_CATEGORIES,
  SPECIAL_DATE_RECURRENCES,
} from '../special-dates.constants';

export interface SpecialDateDialogData {
  specialDate: SpecialDateSchema | null;
}

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

  readonly descriptionCtrl = new FormControl<string>(this.data.specialDate?.description ?? '', {nonNullable: true});
  readonly dateCtrl = new FormControl<string>(this.data.specialDate?.date ?? '', {nonNullable: true});
  readonly recurrenceCtrl = new FormControl<SpecialDateRecurrence>(
    this.data.specialDate?.recurrence ?? 'both', {nonNullable: true});

  readonly category = signal<SpecialDateCategory>(this.data.specialDate?.category ?? 'birthday');
  readonly afterSunset = signal<boolean>(this.data.specialDate?.after_sunset ?? false);
  readonly hebrewPreview = signal<string>(this.data.specialDate?.hebrew_date ?? '');
  readonly isSaving = signal<boolean>(false);
  readonly errorMessage = signal<string>('');

  readonly categories = SPECIAL_DATE_CATEGORIES;
  readonly recurrences = SPECIAL_DATE_RECURRENCES;

  readonly categorySelected = computed(() => {
    const selected = this.category();
    return Object.fromEntries(SPECIAL_DATE_CATEGORIES.map(c => [c.value, c.value === selected]));
  });

  private readonly descriptionValue = toSignal(this.descriptionCtrl.valueChanges, {initialValue: this.descriptionCtrl.value});
  private readonly dateValue = toSignal(this.dateCtrl.valueChanges, {initialValue: this.dateCtrl.value});
  readonly canSave = computed(() => !!this.descriptionValue().trim() && !!this.dateValue() && !this.isSaving());

  private recurrenceTouched = this.isEdit;
  private previewRequestId = 0;

  protected readonly featherCheck = featherCheck;
  protected readonly featherX = featherX;

  constructor() {
    super();
    this.dateCtrl.valueChanges.pipe(takeUntilDestroyed(this.destroyRef)).subscribe(() => void this.refreshHebrewPreview());
    this.recurrenceCtrl.valueChanges.pipe(takeUntilDestroyed(this.destroyRef)).subscribe(() => this.recurrenceTouched = true);
  }

  selectCategory(category: SpecialDateCategory): void {
    this.category.set(category);
    if (!this.recurrenceTouched) {
      this.recurrenceCtrl.setValue(DEFAULT_RECURRENCE_BY_CATEGORY[category], {emitEvent: false});
    }
  }

  toggleAfterSunset(): void {
    this.afterSunset.update(v => !v);
    void this.refreshHebrewPreview();
  }

  private async refreshHebrewPreview(): Promise<void> {
    const date = this.dateCtrl.value;
    const requestId = ++this.previewRequestId;
    if (!date) {
      this.hebrewPreview.set('');
      return;
    }
    const res = await getHebrewDateView({query: {date, after_sunset: this.afterSunset()}});
    if (requestId !== this.previewRequestId) {
      return;
    }
    this.hebrewPreview.set(res.error ? '' : res.data.hebrew_date);
  }

  async onSave(): Promise<void> {
    if (!this.canSave()) {
      return;
    }
    this.isSaving.set(true);
    this.errorMessage.set('');
    const body = {
      description: this.descriptionCtrl.value.trim(),
      date: this.dateCtrl.value,
      after_sunset: this.afterSunset(),
      category: this.category(),
      recurrence: this.recurrenceCtrl.value,
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
