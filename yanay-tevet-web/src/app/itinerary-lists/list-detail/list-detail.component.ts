import {Component, computed, inject, signal} from '@angular/core';
import {FormControl, ReactiveFormsModule} from '@angular/forms';
import {ActivatedRoute} from '@angular/router';
import {NgIcon, provideIcons} from '@ng-icons/core';
import {
  featherArrowLeft,
  featherCheckCircle,
  featherEdit,
  featherHome,
  featherPackage,
  featherPlay,
  featherPlus,
  featherShare2,
  featherShoppingCart,
  featherTrash2,
  featherTruck,
} from '@ng-icons/feather-icons';
import {
  activateItineraryListView,
  createItineraryItemView,
  deleteItineraryItemView,
  deleteItineraryListView,
  finishItineraryListView,
  getItineraryListView,
  ItemStatus,
  ItineraryItemSchema,
  ItineraryListSchema,
  listItineraryListMembersView,
  paginateItineraryItemsView,
  shareItineraryListView,
  unshareItineraryListView,
  updateItineraryItemView,
} from '../../../generated-files/api/itinerary-lists';
import {AuthenticationService} from '../../common/authentication/authentication.service';
import {DialogService} from '../../common/dialogs/dialogs.service';
import {ShareDialogComponent} from '../../common/dialogs/share-dialog/share-dialog.component';
import {RoutingService} from '../../shared/services/routing.service';
import {ItemDialogComponent, ItemDialogData, ItemDialogResult} from '../dialogs/item-dialog/item-dialog.component';
import {
  ITEM_STATUS_CHIP_CLASS,
  ITEM_STATUS_LABELS,
  ITEM_STATUS_NEXT,
  ITEM_STATUS_ORDER,
} from '../itinerary-lists.constants';

@Component({
  selector: 'app-itinerary-list-detail',
  standalone: true,
  imports: [NgIcon, ReactiveFormsModule],
  providers: [provideIcons({
    featherArrowLeft, featherCheckCircle, featherEdit, featherHome, featherPackage, featherPlay,
    featherPlus, featherShare2, featherShoppingCart, featherTrash2, featherTruck,
  })],
  templateUrl: './list-detail.component.html',
})
export class ListDetailComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly routingService = inject(RoutingService);
  private readonly dialogService = inject(DialogService);
  private readonly authService = inject(AuthenticationService);

  readonly listId = signal<number | null>(null);
  readonly list = signal<ItineraryListSchema | null>(null);
  readonly items = signal<ItineraryItemSchema[]>([]);
  readonly isLoading = signal<boolean>(true);
  readonly loadError = signal<string | null>(null);
  readonly isUpdatingStatus = signal<boolean>(false);
  readonly savingItemId = signal<number | null>(null);

  readonly newItemCtrl = new FormControl<string>('', {nonNullable: true});
  readonly isAdding = signal<boolean>(false);

  readonly isOwner = computed(() => {
    const list = this.list();
    return !!list && list.owner_id === this.authService.user()?.id;
  });
  readonly isActive = computed(() => this.list()?.status === 'active');

  readonly statusCounts = computed(() => {
    const counts: Record<ItemStatus, number> = {need_to_buy: 0, in_the_house: 0, ready: 0, in_the_car: 0};
    for (const item of this.items()) {
      counts[item.status] += 1;
    }
    return counts;
  });

  readonly statusLabels = ITEM_STATUS_LABELS;
  readonly statusOrder = ITEM_STATUS_ORDER;
  readonly statusChipClass = ITEM_STATUS_CHIP_CLASS;
  readonly statusIcon: Record<ItemStatus, string> = {
    need_to_buy: featherShoppingCart,
    in_the_house: featherHome,
    ready: featherPackage,
    in_the_car: featherTruck,
  };

  protected readonly featherArrowLeft = featherArrowLeft;
  protected readonly featherCheckCircle = featherCheckCircle;
  protected readonly featherEdit = featherEdit;
  protected readonly featherPlay = featherPlay;
  protected readonly featherPlus = featherPlus;
  protected readonly featherShare2 = featherShare2;
  protected readonly featherTrash2 = featherTrash2;

  constructor() {
    this.route.paramMap.subscribe(params => {
      const idStr = params.get('id');
      if (idStr) {
        const id = Number(idStr);
        this.listId.set(id);
        void this.load(id);
      }
    });
  }

  private async load(id: number): Promise<void> {
    this.isLoading.set(true);
    this.loadError.set(null);
    try {
      const [listRes, itemsRes] = await Promise.all([
        getItineraryListView({path: {object_id: id}}),
        paginateItineraryItemsView({path: {list_id: id}, query: {page: 0, page_size: 500}}),
      ]);
      this.list.set(listRes.data);
      this.items.set(itemsRes.data.data);
    } catch {
      this.loadError.set('Could not load this list. You may not have access to it.');
    } finally {
      this.isLoading.set(false);
    }
  }

  async addItem(): Promise<void> {
    const name = this.newItemCtrl.value.trim();
    const listId = this.listId();
    if (!name || listId === null || this.isAdding()) {
      return;
    }
    this.isAdding.set(true);
    try {
      const res = await createItineraryItemView({body: {itinerary_list_id: listId, name}});
      this.items.update(prev => [...prev, res.data]);
      this.newItemCtrl.setValue('');
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: 'Error', text: `${err}`});
    } finally {
      this.isAdding.set(false);
    }
  }

  async cycleStatus(item: ItineraryItemSchema): Promise<void> {
    const next = ITEM_STATUS_NEXT[item.status];
    if (next === item.status || this.savingItemId() !== null) {
      return;
    }
    await this.patchItemStatus(item, next);
  }

  async openStatusPicker(event: Event, item: ItineraryItemSchema): Promise<void> {
    event.preventDefault();
    if (this.savingItemId() !== null) {
      return;
    }
    const value = await this.dialogService.getValueFromSelectionDialog({
      title: 'Set status',
      text: item.name,
      method: 'buttons',
      options: this.statusOrder.map(status => ({display: this.statusLabels[status], value: status})),
      defaultValue: item.status,
      confirmActionName: 'Set',
      cancelActionName: 'Cancel',
    }, 40);
    if (value && value !== item.status) {
      await this.patchItemStatus(item, value as ItemStatus);
    }
  }

  private async patchItemStatus(item: ItineraryItemSchema, status: ItemStatus): Promise<void> {
    this.savingItemId.set(item.id);
    try {
      const res = await updateItineraryItemView({body: {status}, path: {object_id: item.id}});
      this.items.update(prev => prev.map(i => (i.id === item.id ? res.data : i)));
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: 'Error', text: `${err}`});
    } finally {
      this.savingItemId.set(null);
    }
  }

  async editItem(item: ItineraryItemSchema): Promise<void> {
    const result = await this.dialogService.open<ItemDialogData, ItemDialogResult>(
      ItemDialogComponent,
      {title: 'Edit item', name: item.name, description: item.description, confirmActionName: 'Save'},
      45,
    );
    if (!result) {
      return;
    }
    this.savingItemId.set(item.id);
    try {
      const res = await updateItineraryItemView({
        body: {name: result.name, description: result.description},
        path: {object_id: item.id},
      });
      this.items.update(prev => prev.map(i => (i.id === item.id ? res.data : i)));
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: 'Error', text: `${err}`});
    } finally {
      this.savingItemId.set(null);
    }
  }

  async deleteItem(item: ItineraryItemSchema): Promise<void> {
    const confirmed = await this.dialogService.getBooleanFromConfirmationDialog({
      title: 'Delete item',
      text: `Delete "${item.name}"?`,
      confirmActionName: 'Delete',
      cancelActionName: 'Cancel',
    });
    if (!confirmed) {
      return;
    }
    try {
      await deleteItineraryItemView({path: {object_id: item.id}});
      this.items.update(prev => prev.filter(i => i.id !== item.id));
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: 'Error', text: `${err}`});
    }
  }

  async toggleActive(): Promise<void> {
    const id = this.listId();
    if (id === null || this.isUpdatingStatus()) {
      return;
    }
    const active = this.isActive();
    if (active) {
      const confirmed = await this.dialogService.getBooleanFromConfirmationDialog({
        title: 'Finish list',
        text: 'Finish this list and return it to standby? Items that are not "need to buy" will be set back to "in the house".',
        confirmActionName: 'Finish',
        cancelActionName: 'Cancel',
      });
      if (!confirmed) {
        return;
      }
    }
    this.isUpdatingStatus.set(true);
    try {
      if (active) {
        await finishItineraryListView({body: {}, path: {object_id: id}});
      } else {
        await activateItineraryListView({body: {}, path: {object_id: id}});
      }
      await this.load(id);
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: 'Error', text: `${err}`});
    } finally {
      this.isUpdatingStatus.set(false);
    }
  }

  async openShareDialog(): Promise<void> {
    const id = this.listId();
    if (id === null) {
      return;
    }
    await this.dialogService.open(ShareDialogComponent, {
      objectId: id,
      isOwner: this.isOwner(),
      title: 'Share list',
      subtitle: 'People you add can view and edit this list and its items.',
      listMembers: async (objectId: number) =>
        (await listItineraryListMembersView({path: {object_id: objectId}})).data.members,
      share: async (objectId: number, identifier: string) => {
        await shareItineraryListView({body: {identifier, role: 'collaborator'}, path: {object_id: objectId}});
      },
      unshare: async (objectId: number, identifier: string) => {
        await unshareItineraryListView({body: {identifier}, path: {object_id: objectId}});
      },
    }, 45);
    const res = await getItineraryListView({path: {object_id: id}});
    this.list.set(res.data);
  }

  async editList(): Promise<void> {
    const id = this.listId();
    if (id !== null) {
      await this.routingService.navigateToItineraryListEdit(id);
    }
  }

  async deleteList(): Promise<void> {
    const list = this.list();
    if (list === null) {
      return;
    }
    const confirmed = await this.dialogService.getBooleanFromTextConfirmationDialog({
      title: 'Delete list',
      text: 'This permanently deletes the list and all of its items. This cannot be undone.',
      label: 'List name',
      validationText: list.name,
      confirmActionName: 'Delete list',
      cancelActionName: 'Cancel',
    });
    if (!confirmed) {
      return;
    }
    try {
      await deleteItineraryListView({path: {object_id: list.id}});
      await this.routingService.navigateToItineraryLists();
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: 'Error', text: `${err}`});
    }
  }

  async back(): Promise<void> {
    await this.routingService.navigateToItineraryLists();
  }
}
