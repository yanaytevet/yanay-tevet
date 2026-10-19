import {Component, computed, inject, signal} from '@angular/core';
import {RouterLink} from '@angular/router';
import {NgIcon} from '@ng-icons/core';
import {featherPlus} from '@ng-icons/feather-icons';
import {paginateRentalProjectsView, RentalProjectSchema} from '../../../generated-files/api/apartment-hunt';
import {RoutingService} from '../../shared/services/routing.service';
import {PageHeaderComponent} from '../../common/components/page/page-header/page-header.component';
import {EmptyStateComponent} from '../../common/components/page/empty-state/empty-state.component';
import {LoadingStateComponent} from '../../common/components/page/loading-state/loading-state.component';
import {CURRENCY_LABELS, PROJECT_STATUS_LABELS} from '../apartment-hunt.constants';

@Component({
  selector: 'app-apartment-hunt-projects-list',
  standalone: true,
  imports: [NgIcon, RouterLink, PageHeaderComponent, EmptyStateComponent, LoadingStateComponent],
  templateUrl: './projects-list.component.html',
})
export class ProjectsListComponent {
  private readonly routingService = inject(RoutingService);

  readonly projects = signal<RentalProjectSchema[]>([]);
  readonly isLoading = signal<boolean>(true);

  readonly currencyLabels = CURRENCY_LABELS;
  readonly statusLabels = PROJECT_STATUS_LABELS;

  readonly statusFinished = computed(() => {
    return Object.fromEntries(this.projects().map(p => [p.id, p.status === 'finished']));
  });

  readonly projectUrls = computed(() =>
    Object.fromEntries(this.projects().map(p => [p.id, this.routingService.getApartmentHuntProjectUrl(p.id)]))
  );

  protected readonly featherPlus = featherPlus;

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

  async createProject(): Promise<void> {
    await this.routingService.navigateToApartmentHuntNewProject();
  }
}
