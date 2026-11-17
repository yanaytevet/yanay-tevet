import {Component, computed, inject, signal} from '@angular/core';
import {RouterLink} from '@angular/router';
import {NgIcon} from '@ng-icons/core';
import {featherBarChart2, featherPlus} from '@ng-icons/feather-icons';
import {
  createWorkoutPlanView,
  paginateWorkoutPlansView,
  paginateWorkoutSessionsView,
  WorkoutPlanSchema,
  WorkoutSessionSchema,
} from '../../../generated-files/api/workout-plan';
import {DialogService} from '../../common/dialogs/dialogs.service';
import {EmptyStateComponent} from '../../common/components/page/empty-state/empty-state.component';
import {LoadingStateComponent} from '../../common/components/page/loading-state/loading-state.component';
import {PageHeaderComponent} from '../../common/components/page/page-header/page-header.component';
import {RoutingService} from '../../shared/services/routing.service';
import {WorkoutI18nService} from '../shared/workout-i18n.service';

@Component({
  selector: 'app-workout-plans-list',
  imports: [NgIcon, RouterLink, PageHeaderComponent, EmptyStateComponent, LoadingStateComponent],
  templateUrl: './plans-list.component.html',
})
export class PlansListComponent {
  private readonly routingService = inject(RoutingService);
  private readonly dialogService = inject(DialogService);
  protected readonly i18n = inject(WorkoutI18nService);

  readonly plans = signal<WorkoutPlanSchema[]>([]);
  readonly sessions = signal<WorkoutSessionSchema[]>([]);
  readonly isLoading = signal<boolean>(true);

  readonly progressUrl = this.routingService.getWorkoutProgressUrl();
  readonly planUrls = computed(() =>
    Object.fromEntries(this.plans().map(plan => [plan.id, this.routingService.getWorkoutPlanDetailUrl(plan.id)])),
  );
  readonly planDaySummaries = computed(() =>
    Object.fromEntries(this.plans().map(plan => [plan.id, plan.day_names.filter(name => name).join(' · ')])),
  );
  readonly sessionUrls = computed(() =>
    Object.fromEntries(this.sessions().map(session => [session.id, this.routingService.getWorkoutSessionUrl(session.id)])),
  );
  readonly sessionDates = computed(() => {
    const format = new Intl.DateTimeFormat(this.i18n.language(), {weekday: 'short', day: 'numeric', month: 'short'});
    return Object.fromEntries(this.sessions().map(session => [session.id, format.format(new Date(session.started_at))]));
  });

  protected readonly featherPlus = featherPlus;
  protected readonly featherBarChart2 = featherBarChart2;

  constructor() {
    void this.i18n.load();
    void this.load();
  }

  private async load(): Promise<void> {
    this.isLoading.set(true);
    try {
      const [plans, sessions] = await Promise.all([
        paginateWorkoutPlansView({query: {page: 0, page_size: 100}}),
        paginateWorkoutSessionsView({query: {page: 0, page_size: 5}}),
      ]);
      this.plans.set(plans.data.data);
      this.sessions.set(sessions.data.data);
    } finally {
      this.isLoading.set(false);
    }
  }

  async createPlan(): Promise<void> {
    const t = this.i18n.t();
    const name = await this.dialogService.getTextFromInputDialog({
      title: t.newPlan, text: '', label: t.planName, confirmActionName: t.createPlan, cancelActionName: t.cancel,
      dir: this.i18n.dir(),
    });
    if (!name?.trim()) {
      return;
    }
    try {
      const res = await createWorkoutPlanView({body: {name: name.trim()}});
      await this.routingService.navigateToWorkoutPlanDetail(res.data.id);
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: 'Error', text: `${err}`});
    }
  }

  async toggleLanguage(): Promise<void> {
    await this.i18n.toggle();
  }
}
