import {Component, computed, inject, signal} from '@angular/core';
import {RouterLink} from '@angular/router';
import {NgIcon, provideIcons} from '@ng-icons/core';
import {featherPlus} from '@ng-icons/feather-icons';
import {paginateWorkoutRoutinesView, WorkoutRoutineSchema} from '../../../generated-files/api/workout-plan';
import {RoutingService} from '../../shared/services/routing.service';
import {PageHeaderComponent} from '../../common/components/page/page-header/page-header.component';
import {EmptyStateComponent} from '../../common/components/page/empty-state/empty-state.component';
import {LoadingStateComponent} from '../../common/components/page/loading-state/loading-state.component';

@Component({
  selector: 'app-workout-routines-list',
  standalone: true,
  imports: [NgIcon, RouterLink, PageHeaderComponent, EmptyStateComponent, LoadingStateComponent],
  providers: [provideIcons({featherPlus})],
  templateUrl: './routines-list.component.html',
})
export class RoutinesListComponent {
  private readonly routingService = inject(RoutingService);

  readonly routines = signal<WorkoutRoutineSchema[]>([]);
  readonly isLoading = signal<boolean>(true);

  readonly routineUrls = computed(() =>
    Object.fromEntries(this.routines().map(r => [r.id, this.routingService.getWorkoutRoutineUrl(r.id)])),
  );

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

  async createRoutine(): Promise<void> {
    await this.routingService.navigateToWorkoutPlanNewRoutine();
  }
}
