import {Component, computed, inject, signal} from '@angular/core';
import {toSignal} from '@angular/core/rxjs-interop';
import {FormControl, ReactiveFormsModule} from '@angular/forms';
import {ActivatedRoute} from '@angular/router';
import {NgIcon, provideIcons} from '@ng-icons/core';
import {featherArrowLeft} from '@ng-icons/feather-icons';
import {
  createWorkoutRoutineView,
  getWorkoutRoutineView,
  updateWorkoutRoutineView,
} from '../../../generated-files/api/workout-plan';
import {DialogService} from '../../common/dialogs/dialogs.service';
import {RoutingService} from '../../shared/services/routing.service';

@Component({
  selector: 'app-workout-routine-form',
  standalone: true,
  imports: [ReactiveFormsModule, NgIcon],
  providers: [provideIcons({featherArrowLeft})],
  templateUrl: './routine-form.component.html',
})
export class RoutineFormComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly routingService = inject(RoutingService);
  private readonly dialogService = inject(DialogService);

  readonly routineId = signal<number | null>(null);
  readonly isEditMode = computed(() => this.routineId() !== null);
  readonly isLoading = signal<boolean>(false);
  readonly isSaving = signal<boolean>(false);
  readonly loadError = signal<string | null>(null);

  readonly nameCtrl = new FormControl<string>('', {nonNullable: true});

  private readonly nameValue = toSignal(this.nameCtrl.valueChanges, {initialValue: ''});
  readonly canSave = computed(() => !!this.nameValue()?.trim() && !this.isSaving() && !this.isLoading());

  protected readonly featherArrowLeft = featherArrowLeft;

  constructor() {
    this.route.paramMap.subscribe(params => {
      const idStr = params.get('id');
      if (idStr) {
        const id = Number(idStr);
        this.routineId.set(id);
        void this.loadRoutine(id);
      } else {
        this.routineId.set(null);
      }
    });
  }

  private async loadRoutine(id: number): Promise<void> {
    this.isLoading.set(true);
    this.loadError.set(null);
    try {
      const res = await getWorkoutRoutineView({path: {object_id: id}});
      this.nameCtrl.setValue(res.data.name);
    } catch {
      this.loadError.set('Could not load this routine. You may not have access to it.');
    } finally {
      this.isLoading.set(false);
    }
  }

  async onSave(): Promise<void> {
    const name = this.nameCtrl.value.trim();
    if (!name || this.isSaving()) {
      return;
    }
    this.isSaving.set(true);
    try {
      const id = this.routineId();
      if (id !== null) {
        await updateWorkoutRoutineView({body: {name}, path: {object_id: id}});
        await this.routingService.navigateToWorkoutRoutine(id);
      } else {
        const res = await createWorkoutRoutineView({body: {name}});
        await this.routingService.navigateToWorkoutRoutine(res.data.id);
      }
    } catch (err) {
      await this.dialogService.showNotificationDialog({
        title: 'Error',
        text: `Failed to save routine: ${err}`,
      });
    } finally {
      this.isSaving.set(false);
    }
  }

  async onCancel(): Promise<void> {
    const id = this.routineId();
    if (id !== null) {
      await this.routingService.navigateToWorkoutRoutine(id);
    } else {
      await this.routingService.navigateToWorkoutPlan();
    }
  }
}
