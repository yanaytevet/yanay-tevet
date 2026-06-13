import {Component, computed, inject, signal} from '@angular/core';
import {ActivatedRoute} from '@angular/router';
import {NgIcon, provideIcons} from '@ng-icons/core';
import {
  featherArrowLeft,
  featherEdit,
  featherPlus,
  featherTrash2,
} from '@ng-icons/feather-icons';
import {
  createWorkoutExerciseView,
  deleteWorkoutExerciseView,
  deleteWorkoutRoutineView,
  getWorkoutRoutineView,
  paginateWorkoutExercisesView,
  updateWorkoutExerciseView,
  WorkoutExerciseSchema,
  WorkoutRoutineSchema,
} from '../../../generated-files/api/workout-plan';
import {DialogService} from '../../common/dialogs/dialogs.service';
import {RoutingService} from '../../shared/services/routing.service';
import {
  ExerciseDialogComponent,
  ExerciseDialogData,
  ExerciseDialogResult,
} from '../dialogs/exercise-dialog/exercise-dialog.component';

@Component({
  selector: 'app-workout-routine-detail',
  standalone: true,
  imports: [NgIcon],
  providers: [provideIcons({featherArrowLeft, featherEdit, featherPlus, featherTrash2})],
  templateUrl: './routine-detail.component.html',
})
export class RoutineDetailComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly routingService = inject(RoutingService);
  private readonly dialogService = inject(DialogService);

  readonly routineId = signal<number | null>(null);
  readonly routine = signal<WorkoutRoutineSchema | null>(null);
  readonly exercises = signal<WorkoutExerciseSchema[]>([]);
  readonly isLoading = signal<boolean>(true);
  readonly loadError = signal<string | null>(null);

  readonly setsSummaryById = computed(() => {
    const map: Record<number, string> = {};
    for (const exercise of this.exercises()) {
      map[exercise.id] = this.summariseSets(exercise);
    }
    return map;
  });

  protected readonly featherArrowLeft = featherArrowLeft;
  protected readonly featherEdit = featherEdit;
  protected readonly featherPlus = featherPlus;
  protected readonly featherTrash2 = featherTrash2;

  constructor() {
    this.route.paramMap.subscribe(params => {
      const idStr = params.get('id');
      if (idStr) {
        const id = Number(idStr);
        this.routineId.set(id);
        void this.load(id);
      }
    });
  }

  private async load(id: number): Promise<void> {
    this.isLoading.set(true);
    this.loadError.set(null);
    try {
      const [routineRes, exercisesRes] = await Promise.all([
        getWorkoutRoutineView({path: {object_id: id}}),
        paginateWorkoutExercisesView({path: {routine_id: id}, query: {page: 0, page_size: 500}}),
      ]);
      this.routine.set(routineRes.data);
      this.exercises.set(exercisesRes.data.data);
    } catch {
      this.loadError.set('Could not load this routine. You may not have access to it.');
    } finally {
      this.isLoading.set(false);
    }
  }

  async addExercise(): Promise<void> {
    const routineId = this.routineId();
    if (routineId === null) {
      return;
    }
    const result = await this.openExerciseDialog({
      title: 'Add exercise',
      confirmActionName: 'Add exercise',
      name: '',
      measurementType: 'reps',
      notes: '',
      sets: [{reps: null, durationSeconds: null}],
    });
    if (!result) {
      return;
    }
    try {
      const res = await createWorkoutExerciseView({
        body: {
          routine_id: routineId,
          name: result.name,
          measurement_type: result.measurementType,
          notes: result.notes,
          sets: result.sets.map(s => ({reps: s.reps, duration_seconds: s.durationSeconds})),
        },
      });
      this.exercises.update(prev => [...prev, res.data]);
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: 'Error', text: `${err}`});
    }
  }

  async editExercise(exercise: WorkoutExerciseSchema): Promise<void> {
    const result = await this.openExerciseDialog({
      title: 'Edit exercise',
      confirmActionName: 'Save',
      name: exercise.name,
      measurementType: exercise.measurement_type,
      notes: exercise.notes,
      sets: exercise.sets.map(s => ({reps: s.reps, durationSeconds: s.duration_seconds})),
    });
    if (!result) {
      return;
    }
    try {
      const res = await updateWorkoutExerciseView({
        body: {
          name: result.name,
          measurement_type: result.measurementType,
          notes: result.notes,
          sets: result.sets.map(s => ({reps: s.reps, duration_seconds: s.durationSeconds})),
        },
        path: {object_id: exercise.id},
      });
      this.exercises.update(prev => prev.map(e => (e.id === exercise.id ? res.data : e)));
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: 'Error', text: `${err}`});
    }
  }

  async deleteExercise(exercise: WorkoutExerciseSchema): Promise<void> {
    const confirmed = await this.dialogService.getBooleanFromConfirmationDialog({
      title: 'Delete exercise',
      text: `Delete "${exercise.name}"?`,
      confirmActionName: 'Delete',
      cancelActionName: 'Cancel',
    });
    if (!confirmed) {
      return;
    }
    try {
      await deleteWorkoutExerciseView({path: {object_id: exercise.id}});
      this.exercises.update(prev => prev.filter(e => e.id !== exercise.id));
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: 'Error', text: `${err}`});
    }
  }

  async editRoutine(): Promise<void> {
    const id = this.routineId();
    if (id !== null) {
      await this.routingService.navigateToWorkoutRoutineEdit(id);
    }
  }

  async deleteRoutine(): Promise<void> {
    const routine = this.routine();
    if (routine === null) {
      return;
    }
    const confirmed = await this.dialogService.getBooleanFromTextConfirmationDialog({
      title: 'Delete routine',
      text: 'This permanently deletes the routine and all of its exercises. This cannot be undone.',
      label: 'Routine name',
      validationText: routine.name,
      confirmActionName: 'Delete routine',
      cancelActionName: 'Cancel',
    });
    if (!confirmed) {
      return;
    }
    try {
      await deleteWorkoutRoutineView({path: {object_id: routine.id}});
      await this.routingService.navigateToWorkoutPlan();
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: 'Error', text: `${err}`});
    }
  }

  async back(): Promise<void> {
    await this.routingService.navigateToWorkoutPlan();
  }

  private openExerciseDialog(data: ExerciseDialogData): Promise<ExerciseDialogResult | null> {
    return this.dialogService.open<ExerciseDialogData, ExerciseDialogResult>(ExerciseDialogComponent, data, 45);
  }

  private summariseSets(exercise: WorkoutExerciseSchema): string {
    if (exercise.sets.length === 0) {
      return 'No sets yet';
    }
    if (exercise.measurement_type === 'reps') {
      const parts = exercise.sets.map(s => (s.reps ?? 0).toString());
      return `${parts.join(' · ')} reps`;
    }
    const parts = exercise.sets.map(s => `${s.duration_seconds ?? 0}s`);
    return parts.join(' · ');
  }
}
