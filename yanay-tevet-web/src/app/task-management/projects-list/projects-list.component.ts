import {Component, computed, inject, signal} from '@angular/core';
import {RouterLink} from '@angular/router';
import {NgIcon} from '@ng-icons/core';
import {featherPlus} from '@ng-icons/feather-icons';
import {paginateTaskProjectsView, TaskProjectSchema} from '../../../generated-files/api/task-management';
import {RoutingService} from '../../shared/services/routing.service';
import {PageHeaderComponent} from '../../common/components/page/page-header/page-header.component';
import {EmptyStateComponent} from '../../common/components/page/empty-state/empty-state.component';
import {LoadingStateComponent} from '../../common/components/page/loading-state/loading-state.component';
import {LanguageService} from '../../shared/i18n/language.service';
import {injectStrings, plural} from '../../shared/i18n/strings';
import {TASKS_STRINGS} from '../i18n';

@Component({
  selector: 'app-task-projects-list',
  standalone: true,
  imports: [NgIcon, RouterLink, PageHeaderComponent, EmptyStateComponent, LoadingStateComponent],
  templateUrl: './projects-list.component.html',
})
export class ProjectsListComponent {
  private readonly routingService = inject(RoutingService);
  private readonly languageService = inject(LanguageService);
  protected readonly t = injectStrings(TASKS_STRINGS);

  readonly projects = signal<TaskProjectSchema[]>([]);
  readonly isLoading = signal<boolean>(true);

  readonly activeProjects = computed(() => this.projects().filter(p => p.status === 'active'));
  readonly archivedProjects = computed(() => this.projects().filter(p => p.status === 'archived'));

  readonly subtitle = computed(() => {
    const t = this.t().list;
    const active = this.activeProjects();
    if (this.isLoading() || active.length === 0) {
      return t.subtitle;
    }
    const language = this.languageService.language();
    const openTasks = active.reduce((sum, p) => sum + p.open_task_count, 0);
    return `${plural(language, active.length, t.projectsCount)} · ${plural(language, openTasks, t.openTasksCount)}`;
  });

  // Count labels per project, keyed by project id.
  readonly countLabels = computed(() => {
    const t = this.t().list;
    const language = this.languageService.language();
    return Object.fromEntries(this.projects().map(p => [p.id, {
      openTasks: plural(language, p.open_task_count, t.openTasksLabel),
      openTaskCount: p.open_task_count.toLocaleString(language),
      members: plural(language, p.member_count, t.membersCount),
      tasks: plural(language, p.task_count, t.tasksCount),
    }]));
  });

  readonly projectUrls = computed(() =>
    Object.fromEntries(this.projects().map(p => [p.id, this.routingService.getTaskProjectUrl(p.id)]))
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
