import {Component, computed, inject, signal} from '@angular/core';
import {RouterLink} from '@angular/router';
import {NgIcon} from '@ng-icons/core';
import {featherPlus} from '@ng-icons/feather-icons';
import {paginateTaskProjectsView, TaskProjectSchema} from '../../../generated-files/api/task-management';
import {RoutingService} from '../../shared/services/routing.service';
import {PageHeaderComponent} from '../../common/components/page/page-header/page-header.component';
import {EmptyStateComponent} from '../../common/components/page/empty-state/empty-state.component';
import {LoadingStateComponent} from '../../common/components/page/loading-state/loading-state.component';

@Component({
  selector: 'app-task-projects-list',
  standalone: true,
  imports: [NgIcon, RouterLink, PageHeaderComponent, EmptyStateComponent, LoadingStateComponent],
  templateUrl: './projects-list.component.html',
})
export class ProjectsListComponent {
  private readonly routingService = inject(RoutingService);

  readonly projects = signal<TaskProjectSchema[]>([]);
  readonly isLoading = signal<boolean>(true);

  readonly activeProjects = computed(() => this.projects().filter(p => p.status === 'active'));
  readonly archivedProjects = computed(() => this.projects().filter(p => p.status === 'archived'));

  readonly subtitle = computed(() => {
    const active = this.activeProjects();
    if (this.isLoading() || active.length === 0) {
      return 'Projects, tasks and subtasks — with due dates, priorities and sharing.';
    }
    const openTasks = active.reduce((sum, p) => sum + p.open_task_count, 0);
    const projectsLabel = `${active.length} project${active.length === 1 ? '' : 's'}`;
    return `${projectsLabel} · ${openTasks} open task${openTasks === 1 ? '' : 's'}`;
  });

  readonly projectUrls = computed(() =>
    Object.fromEntries(this.projects().map(p => [p.id, this.routingService.getTaskProjectUrl(p.id)]))
  );

  readonly donePercent = computed(() =>
    Object.fromEntries(this.projects().map(p => [
      p.id,
      p.task_count === 0 ? 0 : Math.round(100 * (p.task_count - p.open_task_count) / p.task_count),
    ]))
  );

  protected readonly featherPlus = featherPlus;

  constructor() {
    void this.loadProjects();
  }

  private async loadProjects(): Promise<void> {
    this.isLoading.set(true);
    try {
      const res = await paginateTaskProjectsView({query: {page: 0, page_size: 100}});
      this.projects.set(res.data.data);
    } finally {
      this.isLoading.set(false);
    }
  }

  async createProject(): Promise<void> {
    await this.routingService.navigateToTaskManagementNewProject();
  }
}
