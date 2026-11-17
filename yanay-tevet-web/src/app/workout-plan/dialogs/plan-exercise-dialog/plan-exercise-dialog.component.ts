import {Component, inject, signal} from '@angular/core';
import {
  ExerciseSchema,
  PlanExerciseSchema,
  PlanExerciseTargetsSchema,
} from '../../../../generated-files/api/workout-plan';
import {BaseDialogComponent} from '../../../common/dialogs/base-dialog.component';
import {ExerciseNamePipe} from '../../shared/exercise-name.pipe';
import {formatDuration, parseDuration} from '../../shared/workout-format';
import {WorkoutI18nService} from '../../shared/workout-i18n.service';

export interface PlanExerciseDialogData {
  exercise: ExerciseSchema;
  // Absent when adding the exercise to a day for the first time.
  entry?: PlanExerciseSchema;
}

// The targets of one exercise on a day. Only the fields that fit its tracking type are shown.
@Component({
  selector: 'app-plan-exercise-dialog',
  imports: [ExerciseNamePipe],
  templateUrl: './plan-exercise-dialog.component.html',
})
export class PlanExerciseDialogComponent extends BaseDialogComponent<PlanExerciseDialogData, PlanExerciseTargetsSchema> {
  protected readonly i18n = inject(WorkoutI18nService);
  protected readonly tracking = this.data.exercise.tracking_type;
  private readonly isCardio = this.tracking === 'distance' || this.tracking === 'laps';

  readonly sets = signal<string>(String(this.data.entry?.target_sets ?? (this.isCardio ? 1 : 3)));
  readonly reps = signal<string>(this.numberText(this.data.entry ? this.data.entry.target_reps : 12));
  readonly weight = signal<string>(this.numberText(this.data.entry?.target_weight_kg));
  readonly duration = signal<string>(formatDuration(this.data.entry?.target_seconds));
  readonly distance = signal<string>(this.numberText(this.data.entry?.target_distance_km));
  readonly laps = signal<string>(this.numberText(this.data.entry?.target_laps));
  readonly rest = signal<string>(String(this.data.entry?.rest_seconds ?? 50));
  readonly notes = signal<string>(this.data.entry?.notes ?? '');

  save(): void {
    const body: PlanExerciseTargetsSchema = {
      target_sets: this.toInt(this.sets()) ?? 1,
      rest_seconds: this.toInt(this.rest()) ?? 50,
      notes: this.notes().trim(),
    };
    switch (this.tracking) {
      case 'weight_reps':
        body.target_reps = this.toInt(this.reps());
        body.target_weight_kg = this.toFloat(this.weight());
        break;
      case 'reps':
        body.target_reps = this.toInt(this.reps());
        break;
      case 'time':
        body.target_seconds = parseDuration(this.duration());
        break;
      case 'distance':
        body.target_distance_km = this.toFloat(this.distance());
        break;
      case 'laps':
        body.target_laps = this.toInt(this.laps());
        break;
    }
    this.emitClose(body);
  }

  onInput(field: 'sets' | 'reps' | 'weight' | 'duration' | 'distance' | 'laps' | 'rest' | 'notes', event: Event): void {
    const value = (event.target as HTMLInputElement | HTMLTextAreaElement).value;
    switch (field) {
      case 'sets': this.sets.set(value); break;
      case 'reps': this.reps.set(value); break;
      case 'weight': this.weight.set(value); break;
      case 'duration': this.duration.set(value); break;
      case 'distance': this.distance.set(value); break;
      case 'laps': this.laps.set(value); break;
      case 'rest': this.rest.set(value); break;
      case 'notes': this.notes.set(value); break;
    }
  }

  private numberText(value: number | null | undefined): string {
    return value === null || value === undefined ? '' : String(value);
  }

  private toInt(text: string): number | null {
    const value = parseInt(text, 10);
    return Number.isNaN(value) || value < 0 ? null : value;
  }

  private toFloat(text: string): number | null {
    const value = parseFloat(text.replace(',', '.'));
    return Number.isNaN(value) || value < 0 ? null : value;
  }
}
