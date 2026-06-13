import {Component, computed, inject, signal} from '@angular/core';
import {NgIcon, provideIcons} from '@ng-icons/core';
import {featherPlus} from '@ng-icons/feather-icons';
import {paginateTaskProjectsView, TaskProjectSchema} from '../../../generated-files/api/task-management';
import {RoutingService} from '../../shared/services/routing.service';

@Component({
  selector: 'app-task-projects-list',
  standalone: true,
  imports: [NgIcon],
  providers: [provideIcons({featherPlus})],
  templateUrl: './projects-list.component.html',
})
export class ProjectsListComponent {
  private readonly routingService = inject(RoutingService);

  readonly projects = signal<TaskProjectSchema[]>([]);
  readonly isLoading = signal<boolean>(true);

  readonly activeProjects = computed(() => this.projects().filter(p => p.status === 'active'));
  readonly archivedProjects = computed(() => this.projects().filter(p => p.status === 'archived'));

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

  async openProject(project: TaskProjectSchema): Promise<void> {
    await this.routingService.navigateToTaskProject(project.id);
  }

  async createProject(): Promise<void> {
    await this.routingService.navigateToTaskManagementNewProject();
  }
}
