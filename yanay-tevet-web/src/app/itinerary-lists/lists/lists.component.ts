import {Component, computed, inject, signal} from '@angular/core';
import {NgIcon, provideIcons} from '@ng-icons/core';
import {featherPlus} from '@ng-icons/feather-icons';
import {ItineraryListSchema, paginateItineraryListsView} from '../../../generated-files/api/itinerary-lists';
import {RoutingService} from '../../shared/services/routing.service';

@Component({
  selector: 'app-itinerary-lists',
  standalone: true,
  imports: [NgIcon],
  providers: [provideIcons({featherPlus})],
  templateUrl: './lists.component.html',
})
export class ListsComponent {
  private readonly routingService = inject(RoutingService);

  readonly lists = signal<ItineraryListSchema[]>([]);
  readonly isLoading = signal<boolean>(true);

  readonly activeLists = computed(() => this.lists().filter(l => l.status === 'active'));
  readonly standbyLists = computed(() => this.lists().filter(l => l.status === 'standby'));

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

  async openList(list: ItineraryListSchema): Promise<void> {
    await this.routingService.navigateToItineraryList(list.id);
  }

  async createList(): Promise<void> {
    await this.routingService.navigateToItineraryListsNewList();
  }
}
