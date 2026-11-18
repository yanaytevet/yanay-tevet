import {Component, computed, inject, signal} from '@angular/core';
import {RouterLink} from '@angular/router';
import {NgIcon} from '@ng-icons/core';
import {featherPlus} from '@ng-icons/feather-icons';
import {paginateRentalProjectsView, RentalProjectSchema} from '../../../generated-files/api/apartment-hunt';
import {RoutingService} from '../../shared/services/routing.service';
import {PageHeaderComponent} from '../../common/components/page/page-header/page-header.component';
import {EmptyStateComponent} from '../../common/components/page/empty-state/empty-state.component';
import {LoadingStateComponent} from '../../common/components/page/loading-state/loading-state.component';
import {injectStrings, plural} from '../../shared/i18n/strings';
import {LanguageService} from '../../shared/i18n/language.service';
import {APARTMENT_HUNT_STRINGS} from '../i18n';

@Component({
  selector: 'app-apartment-hunt-projects-list',
  standalone: true,
  imports: [NgIcon, RouterLink, PageHeaderComponent, EmptyStateComponent, LoadingStateComponent],
  templateUrl: './projects-list.component.html',
})
export class ProjectsListComponent {
  private readonly routingService = inject(RoutingService);
  private readonly languageService = inject(LanguageService);
  protected readonly t = injectStrings(APARTMENT_HUNT_STRINGS);

  readonly projects = signal<RentalProjectSchema[]>([]);
  readonly isLoading = signal<boolean>(true);


  readonly statusFinished = computed(() => {
    return Object.fromEntries(this.projects().map(p => [p.id, p.status === 'finished']));
  });

  readonly memberCounts = computed<Record<number, string>>(() => {
    const language = this.languageService.language();
    const forms = this.t().common.members;
    return Object.fromEntries(this.projects().map(p => [p.id, plural(language, p.member_count, forms)]));
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
