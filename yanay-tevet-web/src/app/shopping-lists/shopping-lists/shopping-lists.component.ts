import {Component, computed, inject, signal} from '@angular/core';
import {NgIcon, provideIcons} from '@ng-icons/core';
import {featherPlus, featherSquare, featherUsers} from '@ng-icons/feather-icons';
import {
  createShoppingListView,
  paginateShoppingListsView,
  ShoppingListSchema,
} from '../../../generated-files/api/shopping-lists';
import {DialogService} from '../../common/dialogs/dialogs.service';
import {RoutingService} from '../../shared/services/routing.service';

@Component({
  selector: 'app-shopping-lists',
  standalone: true,
  imports: [NgIcon],
  providers: [provideIcons({featherPlus, featherSquare, featherUsers})],
  templateUrl: './shopping-lists.component.html',
})
export class ShoppingListsComponent {
  private readonly routingService = inject(RoutingService);
  private readonly dialogService = inject(DialogService);

  readonly lists = signal<ShoppingListSchema[]>([]);
  readonly isLoading = signal<boolean>(true);
  readonly isCreating = signal<boolean>(false);

  readonly moreCount = computed(() =>
    Object.fromEntries(this.lists().map(l => [l.id, l.unchecked_count - l.preview_items.length])),
  );

  protected readonly featherPlus = featherPlus;
  protected readonly featherSquare = featherSquare;
  protected readonly featherUsers = featherUsers;

  constructor() {
    void this.loadLists();
  }

  private async loadLists(): Promise<void> {
    this.isLoading.set(true);
    try {
      const res = await paginateShoppingListsView({query: {page: 0, page_size: 100}});
      this.lists.set(res.data.data);
    } finally {
      this.isLoading.set(false);
    }
  }

  async openList(list: ShoppingListSchema): Promise<void> {
    await this.routingService.navigateToShoppingList(list.id);
  }

  async createList(): Promise<void> {
    if (this.isCreating()) {
      return;
    }
    const name = await this.dialogService.getTextFromInputDialog({
      title: 'New shopping list',
      text: '',
      label: 'Name',
      defaultValue: '',
      confirmActionName: 'Create',
      cancelActionName: 'Cancel',
      maxLength: 255,
    }, 40);
    const trimmed = name?.trim();
    if (!trimmed) {
      return;
    }
    this.isCreating.set(true);
    try {
      const res = await createShoppingListView({body: {name: trimmed}});
      await this.routingService.navigateToShoppingList(res.data.id);
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: 'Error', text: `Failed to create list: ${err}`});
    } finally {
      this.isCreating.set(false);
    }
  }
}
