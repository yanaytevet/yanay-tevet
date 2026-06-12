import {Component, computed, inject, signal} from '@angular/core';
import {NgIcon, provideIcons} from '@ng-icons/core';
import {featherPlus, featherHome} from '@ng-icons/feather-icons';
import {paginateRentalProjectsView, RentalProjectSchema} from '../../../generated-files/api/apartment-hunt';
import {RoutingService} from '../../shared/services/routing.service';
import {CURRENCY_SYMBOLS, PROJECT_STATUS_LABELS} from '../apartment-hunt.constants';

@Component({
  selector: 'app-apartment-hunt-projects-list',
  standalone: true,
  imports: [NgIcon],
  providers: [provideIcons({featherPlus, featherHome})],
  templateUrl: './projects-list.component.html',
})
export class ProjectsListComponent {
  private readonly routingService = inject(RoutingService);

  readonly projects = signal<RentalProjectSchema[]>([]);
  readonly isLoading = signal<boolean>(true);

  readonly currencySymbols = CURRENCY_SYMBOLS;
  readonly statusLabels = PROJECT_STATUS_LABELS;

  readonly statusFinished = computed(() => {
    return Object.fromEntries(this.projects().map(p => [p.id, p.status === 'finished']));
  });

  protected readonly featherPlus = featherPlus;
  protected readonly featherHome = featherHome;

  constructor() {
    void this.loadProjects();
  }

  private async loadProjects(): Promise<void> {
    this.isLoading.set(true);
    try {
      const res = await paginateRentalProjectsView({query: {page: 0, page_size: 100}});
      this.projects.set(res.data.data);
    } finally {
      this.isLoading.set(false);
    }
  }

  async openProject(project: RentalProjectSchema): Promise<void> {
    await this.routingService.navigateToApartmentHuntProject(project.id);
  }

  async createProject(): Promise<void> {
    await this.routingService.navigateToApartmentHuntNewProject();
  }
}
