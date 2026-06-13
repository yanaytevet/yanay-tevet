import {Component, computed, signal} from '@angular/core';
import {toSignal} from '@angular/core/rxjs-interop';
import {FormControl, ReactiveFormsModule} from '@angular/forms';
import {NgIcon, provideIcons} from '@ng-icons/core';
import {featherPlus, featherTrash2, featherX} from '@ng-icons/feather-icons';
import {MeasurementType} from '../../../../generated-files/api/workout-plan';
import {BaseDialogComponent} from '../../../common/dialogs/base-dialog.component';
import {MEASUREMENT_TYPE_LABELS, MEASUREMENT_TYPE_ORDER} from '../../workout-plan.constants';

export interface ExerciseSetRow {
  reps: number | null;
  durationSeconds: number | null;
}

export interface ExerciseDialogData {
  title: string;
  confirmActionName: string;
  name: string;
  measurementType: MeasurementType;
  notes: string;
  sets: ExerciseSetRow[];
}

export interface ExerciseDialogResult {
  name: string;
  measurementType: MeasurementType;
  notes: string;
  sets: ExerciseSetRow[];
}

@Component({
  selector: 'app-exercise-dialog',
  standalone: true,
  imports: [ReactiveFormsModule, NgIcon],
  providers: [provideIcons({featherPlus, featherTrash2, featherX})],
  templateUrl: './exercise-dialog.component.html',
})
export class ExerciseDialogComponent extends BaseDialogComponent<ExerciseDialogData, ExerciseDialogResult> {
  readonly nameCtrl = new FormControl<string>('', {nonNullable: true});
  readonly notesCtrl = new FormControl<string>('', {nonNullable: true});
  readonly measurementTypeCtrl = new FormControl<MeasurementType>('reps', {nonNullable: true});

  readonly sets = signal<ExerciseSetRow[]>([]);

  readonly measurementTypeOrder = MEASUREMENT_TYPE_ORDER;
  readonly measurementTypeLabels = MEASUREMENT_TYPE_LABELS;

  private readonly nameValue = toSignal(this.nameCtrl.valueChanges, {initialValue: ''});
  readonly measurementType = toSignal(this.measurementTypeCtrl.valueChanges, {initialValue: 'reps' as MeasurementType});
  readonly isReps = computed(() => this.measurementType() === 'reps');
  readonly canSave = computed(() => !!this.nameValue()?.trim());

  protected readonly featherPlus = featherPlus;
  protected readonly featherTrash2 = featherTrash2;
  protected readonly featherX = featherX;

  constructor() {
    super();
    this.nameCtrl.setValue(this.data.name);
    this.notesCtrl.setValue(this.data.notes);
    this.measurementTypeCtrl.setValue(this.data.measurementType);
    this.sets.set(this.data.sets.map(s => ({reps: s.reps, durationSeconds: s.durationSeconds})));
  }

  addSet(): void {
    const last = this.sets().at(-1);
    this.sets.update(prev => [...prev, {
      reps: last ? last.reps : null,
      durationSeconds: last ? last.durationSeconds : null,
    }]);
  }

  removeSet(index: number): void {
    this.sets.update(prev => prev.filter((_, i) => i !== index));
  }

  updateReps(index: number, event: Event): void {
    const value = this.parseNumber((event.target as HTMLInputElement).value);
    this.sets.update(prev => prev.map((s, i) => (i === index ? {...s, reps: value} : s)));
  }

  updateDuration(index: number, event: Event): void {
    const value = this.parseNumber((event.target as HTMLInputElement).value);
    this.sets.update(prev => prev.map((s, i) => (i === index ? {...s, durationSeconds: value} : s)));
  }

  onSave(): void {
    const name = this.nameCtrl.value.trim();
    if (!name) {
      return;
    }
    this.emitClose({
      name,
      measurementType: this.measurementTypeCtrl.value,
      notes: this.notesCtrl.value.trim(),
      sets: this.sets(),
    });
  }

  onClose(): void {
    this.emitClose(null);
  }

  private parseNumber(raw: string): number | null {
    const trimmed = raw.trim();
    if (trimmed === '') {
      return null;
    }
    const parsed = Number(trimmed);
    return Number.isFinite(parsed) && parsed >= 0 ? Math.floor(parsed) : null;
  }
}
