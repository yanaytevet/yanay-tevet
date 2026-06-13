import {Component, inject, signal} from '@angular/core';
import {NgIcon, provideIcons} from '@ng-icons/core';
import {featherPlus} from '@ng-icons/feather-icons';
import {paginateWorkoutRoutinesView, WorkoutRoutineSchema} from '../../../generated-files/api/workout-plan';
import {RoutingService} from '../../shared/services/routing.service';

@Component({
  selector: 'app-workout-routines-list',
  standalone: true,
  imports: [NgIcon],
  providers: [provideIcons({featherPlus})],
  templateUrl: './routines-list.component.html',
})
export class RoutinesListComponent {
  private readonly routingService = inject(RoutingService);

  readonly routines = signal<WorkoutRoutineSchema[]>([]);
  readonly isLoading = signal<boolean>(true);

  protected readonly featherPlus = featherPlus;

  constructor() {
    void this.loadRoutines();
  }

  private async loadRoutines(): Promise<void> {
    this.isLoading.set(true);
    try {
      const res = await paginateWorkoutRoutinesView({query: {page: 0, page_size: 100}});
      this.routines.set(res.data.data);
    } finally {
      this.isLoading.set(false);
    }
  }

  async openRoutine(routine: WorkoutRoutineSchema): Promise<void> {
    await this.routingService.navigateToWorkoutRoutine(routine.id);
  }

  async createRoutine(): Promise<void> {
    await this.routingService.navigateToWorkoutPlanNewRoutine();
  }
}
