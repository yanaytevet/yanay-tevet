import {Component, computed, inject, signal} from '@angular/core';
import {NgIcon} from '@ng-icons/core';
import {featherPlus, featherSearch} from '@ng-icons/feather-icons';
import {
  createExerciseView,
  ExerciseSchema,
  listExercisesView,
  MuscleGroup,
  TrackingType,
} from '../../../../generated-files/api/workout-plan';
import {BaseDialogComponent} from '../../../common/dialogs/base-dialog.component';
import {CheckboxMarkComponent} from '../../../common/components/inputs/checkbox-mark/checkbox-mark.component';
import {exerciseName, ExerciseNamePipe} from '../../shared/exercise-name.pipe';
import {WorkoutI18nService} from '../../shared/workout-i18n.service';

export const MUSCLE_GROUPS: MuscleGroup[] = [
  'back', 'biceps', 'chest', 'triceps', 'shoulders', 'legs', 'glutes', 'calves', 'abs', 'cardio', 'forearms',
  'full_body', 'other',
];
export const TRACKING_TYPES: TrackingType[] = ['weight_reps', 'reps', 'time', 'distance', 'laps'];

// Picks an exercise from the library, or creates a custom one on the spot and picks that.
@Component({
  selector: 'app-exercise-picker-dialog',
  imports: [NgIcon, ExerciseNamePipe, CheckboxMarkComponent],
  templateUrl: './exercise-picker-dialog.component.html',
})
export class ExercisePickerDialogComponent extends BaseDialogComponent<void, ExerciseSchema> {
  protected readonly i18n = inject(WorkoutI18nService);

  readonly exercises = signal<ExerciseSchema[]>([]);
  readonly search = signal<string>('');
  readonly group = signal<MuscleGroup | null>(null);
  readonly isCreating = signal<boolean>(false);
  readonly error = signal<string | null>(null);

  readonly newNameEn = signal<string>('');
  readonly newNameHe = signal<string>('');
  readonly newGroup = signal<MuscleGroup>('other');
  readonly newTracking = signal<TrackingType>('weight_reps');
  readonly newPerSide = signal<boolean>(false);

  readonly groups = computed(() => {
    const present = new Set(this.exercises().map(exercise => exercise.muscle_group));
    return MUSCLE_GROUPS.filter(group => present.has(group));
  });
  readonly filtered = computed(() => {
    const query = this.search().trim().toLowerCase();
    const group = this.group();
    const language = this.i18n.language();
    return this.exercises()
      .filter(exercise => group === null || exercise.muscle_group === group)
      .filter(exercise => !query
        || exercise.name_en.toLowerCase().includes(query) || exercise.name_he.includes(query))
      .sort((a, b) => exerciseName(a, language).localeCompare(exerciseName(b, language), language));
  });

  protected readonly muscleGroups = MUSCLE_GROUPS;
  protected readonly trackingTypes = TRACKING_TYPES;
  protected readonly featherPlus = featherPlus;
  protected readonly featherSearch = featherSearch;

  constructor() {
    super();
    void this.load();
  }

  private async load(): Promise<void> {
    const res = await listExercisesView();
    this.exercises.set(res.data.exercises);
  }

  pick(exercise: ExerciseSchema): void {
    this.emitClose(exercise);
  }

  startCreating(): void {
    const query = this.search().trim();
    if (this.i18n.language() === 'he') {
      this.newNameHe.set(query);
    } else {
      this.newNameEn.set(query);
    }
    this.newGroup.set(this.group() ?? 'other');
    this.isCreating.set(true);
  }

  async create(): Promise<void> {
    if (!this.newNameEn().trim() && !this.newNameHe().trim()) {
      this.error.set(this.i18n.t().nameRequired);
      return;
    }
    try {
      const res = await createExerciseView({body: {
        name_en: this.newNameEn().trim(),
        name_he: this.newNameHe().trim(),
        muscle_group: this.newGroup(),
        tracking_type: this.newTracking(),
        per_side: this.newPerSide(),
      }});
      this.emitClose(res.data);
    } catch (err) {
      this.error.set(`${err}`);
    }
  }

  onSearch(event: Event): void {
    this.search.set((event.target as HTMLInputElement).value);
  }

  onText(target: 'en' | 'he', event: Event): void {
    const value = (event.target as HTMLInputElement).value;
    if (target === 'en') {
      this.newNameEn.set(value);
    } else {
      this.newNameHe.set(value);
    }
  }

  onGroup(event: Event): void {
    this.newGroup.set((event.target as HTMLSelectElement).value as MuscleGroup);
  }

  onTracking(event: Event): void {
    this.newTracking.set((event.target as HTMLSelectElement).value as TrackingType);
  }
}
