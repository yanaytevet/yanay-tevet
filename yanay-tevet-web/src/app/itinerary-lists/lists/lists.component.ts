import {Component, computed, inject, signal} from '@angular/core';
import {RouterLink} from '@angular/router';
import {NgIcon, provideIcons} from '@ng-icons/core';
import {featherPlus} from '@ng-icons/feather-icons';
import {ItineraryListSchema, paginateItineraryListsView} from '../../../generated-files/api/itinerary-lists';
import {RoutingService} from '../../shared/services/routing.service';
import {PageHeaderComponent} from '../../common/components/page/page-header/page-header.component';
import {EmptyStateComponent} from '../../common/components/page/empty-state/empty-state.component';
import {LoadingStateComponent} from '../../common/components/page/loading-state/loading-state.component';

@Component({
  selector: 'app-itinerary-lists',
  standalone: true,
  imports: [NgIcon, RouterLink, PageHeaderComponent, EmptyStateComponent, LoadingStateComponent],
  providers: [provideIcons({featherPlus})],
  templateUrl: './lists.component.html',
})
export class ListsComponent {
  private readonly routingService = inject(RoutingService);

  readonly lists = signal<ItineraryListSchema[]>([]);
  readonly isLoading = signal<boolean>(true);

  readonly activeLists = computed(() => this.lists().filter(l => l.status === 'active'));
  readonly standbyLists = computed(() => this.lists().filter(l => l.status === 'standby'));

  readonly listUrls = computed(() =>
    Object.fromEntries(this.lists().map(l => [l.id, this.routingService.getItineraryListUrl(l.id)])),
  );

  protected readonly featherPlus = featherPlus;

  constructor() {
    void this.loadLists();
  }

  private async loadLists(): Promise<void> {
    this.isLoading.set(true);
    try {
      const res = await paginateItineraryListsView({query: {page: 0, page_size: 100}});
      this.lists.set(res.data.data);
    } finally {
      this.isLoading.set(false);
    }
  }

  async createList(): Promise<void> {
    await this.routingService.navigateToItineraryListsNewList();
  }
}
