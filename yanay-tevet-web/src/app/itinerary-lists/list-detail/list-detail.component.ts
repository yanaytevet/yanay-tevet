import {Component, computed, inject, signal} from '@angular/core';
import {FormControl, ReactiveFormsModule} from '@angular/forms';
import {ActivatedRoute, RouterLink} from '@angular/router';
import {NgIcon, provideIcons} from '@ng-icons/core';
import {
  featherArrowLeft,
  featherCheckCircle,
  featherCheckSquare,
  featherEdit,
  featherHome,
  featherMoreHorizontal,
  featherPackage,
  featherPlay,
  featherPlus,
  featherShare2,
  featherShoppingCart,
  featherSquare,
  featherTrash2,
  featherTruck,
} from '@ng-icons/feather-icons';
import {
  activateItineraryListView,
  createItineraryItemView,
  createItineraryTaskView,
  deleteItineraryItemView,
  deleteItineraryListView,
  deleteItineraryTaskView,
  finishItineraryListView,
  getItineraryListView,
  ItemStatus,
  ItineraryItemSchema,
  ItineraryListSchema,
  ItineraryTaskSchema,
  listItineraryListMembersView,
  paginateItineraryItemsView,
  paginateItineraryTasksView,
  shareItineraryListView,
  TaskStatus,
  unshareItineraryListView,
  updateItineraryItemView,
  updateItineraryTaskView,
} from '../../../generated-files/api/itinerary-lists';
import {AuthenticationService} from '../../common/authentication/authentication.service';
import {DialogService} from '../../common/dialogs/dialogs.service';
import {ShareDialogComponent} from '../../common/dialogs/share-dialog/share-dialog.component';
import {RoutingService} from '../../shared/services/routing.service';
import {MenuButtonComponent, MenuItem, SEPARATOR} from '../../common/components/menu-button/menu-button.component';
import {PageHeaderComponent} from '../../common/components/page/page-header/page-header.component';
import {LoadingStateComponent} from '../../common/components/page/loading-state/loading-state.component';
import {ErrorStateComponent} from '../../common/components/page/error-state/error-state.component';
import {ItemDialogComponent, ItemDialogData, ItemDialogResult} from '../dialogs/item-dialog/item-dialog.component';
import {
  ITEM_STATUS_CHIP_CLASS,
  ITEM_STATUS_NEXT,
  ITEM_STATUS_ORDER,
} from '../itinerary-lists.constants';
import {CheckboxMarkComponent} from '../../common/components/inputs/checkbox-mark/checkbox-mark.component';
import {LanguageService} from '../../shared/i18n/language.service';
import {fill, injectStrings, plural} from '../../shared/i18n/strings';
import {ITINERARY_STRINGS} from '../i18n';

@Component({
  selector: 'app-itinerary-list-detail',
  standalone: true,
  imports: [CheckboxMarkComponent, 
    NgIcon, ReactiveFormsModule, RouterLink, MenuButtonComponent,
    PageHeaderComponent, LoadingStateComponent, ErrorStateComponent,
  ],
  providers: [provideIcons({
  featherArrowLeft,
  featherCheckCircle,
  featherCheckSquare,
  featherEdit,
  featherHome,
  featherMoreHorizontal,
  featherPackage,
  featherPlay,
  featherPlus,
  featherShare2,
  featherShoppingCart,
  featherSquare,
  featherTrash2,
  featherTruck,
})],
  templateUrl: './list-detail.component.html',
})
export class ListDetailComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly routingService = inject(RoutingService);
  private readonly dialogService = inject(DialogService);
  private readonly authService = inject(AuthenticationService);
  private readonly languageService = inject(LanguageService);
  protected readonly t = injectStrings(ITINERARY_STRINGS);

  readonly allListsUrl = this.routingService.getItineraryListsUrl();

  readonly listId = signal<number | null>(null);
  readonly list = signal<ItineraryListSchema | null>(null);
  readonly items = signal<ItineraryItemSchema[]>([]);
  readonly tasks = signal<ItineraryTaskSchema[]>([]);
  readonly isLoading = signal<boolean>(true);
  readonly loadError = signal<boolean>(false);
  readonly isUpdatingStatus = signal<boolean>(false);
  readonly savingItemId = signal<number | null>(null);
  readonly savingTaskId = signal<number | null>(null);

  readonly newItemCtrl = new FormControl<string>('', {nonNullable: true});
  readonly isAdding = signal<boolean>(false);
  readonly newTaskCtrl = new FormControl<string>('', {nonNullable: true});
  readonly isAddingTask = signal<boolean>(false);

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

  readonly taskCounts = computed(() => {
    const tasks = this.tasks();
    const done = tasks.filter(t => t.status === 'done').length;
    return {done, toDo: tasks.length - done, total: tasks.length};
  });

  readonly headerSubtitle = computed(() => {
    const list = this.list();
    if (list === null) {
      return null;
    }
    const t = this.t();
    const language = this.languageService.language();
    return [
      plural(language, this.items().length, t.itemsCount),
      plural(language, this.tasks().length, t.tasksCount),
      plural(language, list.member_count, t.membersCount),
    ].join(' · ');
  });

  // Summary chip text per item status, e.g. "3 Need to buy".
  readonly statusCountLabels = computed(() => {
    const t = this.t();
    const language = this.languageService.language();
    const counts = this.statusCounts();
    return Object.fromEntries(ITEM_STATUS_ORDER.map(status => [status,
      fill(t.detail.statusCount, {count: counts[status].toLocaleString(language), status: t.itemStatuses[status]})]));
  });
  readonly tasksDoneLabel = computed(() =>
    plural(this.languageService.language(), this.taskCounts().done, this.t().detail.tasksDone));
  readonly tasksToDoLabel = computed(() =>
    plural(this.languageService.language(), this.taskCounts().toDo, this.t().detail.tasksToDo));

  // Activate/Finish and Share sit in the header; editing and deleting the list live behind "more".
  readonly overflowActions = computed<MenuItem[]>(() => {
    const t = this.t().detail;
    const actions: MenuItem[] = [
      {display: t.editList, icon: featherEdit, callback: () => void this.editList()},
    ];
    if (this.isOwner()) {
      actions.push(SEPARATOR);
      actions.push({display: t.deleteList, icon: featherTrash2, danger: true, callback: () => void this.deleteList()});
    }
    return actions;
  });

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
  protected readonly featherCheckSquare = featherCheckSquare;
  protected readonly featherEdit = featherEdit;
  protected readonly featherMoreHorizontal = featherMoreHorizontal;
  protected readonly featherPlay = featherPlay;
  protected readonly featherPlus = featherPlus;
  protected readonly featherShare2 = featherShare2;
  protected readonly featherSquare = featherSquare;
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
    this.loadError.set(false);
    try {
      const [listRes, itemsRes, tasksRes] = await Promise.all([
        getItineraryListView({path: {object_id: id}}),
        paginateItineraryItemsView({path: {list_id: id}, query: {page: 0, page_size: 500}}),
        paginateItineraryTasksView({path: {list_id: id}, query: {page: 0, page_size: 500}}),
      ]);
      this.list.set(listRes.data);
      this.items.set(itemsRes.data.data);
      this.tasks.set(tasksRes.data.data);
    } catch {
      this.loadError.set(true);
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
      await this.dialogService.showNotificationDialog({title: this.t().error, text: `${err}`});
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
    const t = this.t();
    const value = await this.dialogService.getValueFromSelectionDialog({
      title: t.detail.setStatus,
      text: item.name,
      method: 'buttons',
      options: this.statusOrder.map(status => ({display: t.itemStatuses[status], value: status})),
      defaultValue: item.status,
      confirmActionName: t.detail.set,
      cancelActionName: t.cancel,
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
      await this.dialogService.showNotificationDialog({title: this.t().error, text: `${err}`});
    } finally {
      this.savingItemId.set(null);
    }
  }

  async editItem(item: ItineraryItemSchema): Promise<void> {
    const result = await this.dialogService.open<ItemDialogData, ItemDialogResult>(
      ItemDialogComponent,
      {
        kind: 'item',
        title: this.t().detail.editItem,
        name: item.name,
        description: item.description,
        confirmActionName: this.t().save,
      },
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
      await this.dialogService.showNotificationDialog({title: this.t().error, text: `${err}`});
    } finally {
      this.savingItemId.set(null);
    }
  }

  async deleteItem(item: ItineraryItemSchema): Promise<void> {
    const t = this.t();
    const confirmed = await this.dialogService.getBooleanFromConfirmationDialog({
      title: t.detail.deleteItem,
      text: fill(t.detail.deleteConfirm, {name: item.name}),
      confirmActionName: t.detail.delete,
      danger: true,
      cancelActionName: t.cancel,
    });
    if (!confirmed) {
      return;
    }
    try {
      await deleteItineraryItemView({path: {object_id: item.id}});
      this.items.update(prev => prev.filter(i => i.id !== item.id));
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: this.t().error, text: `${err}`});
    }
  }

  async addTask(): Promise<void> {
    const name = this.newTaskCtrl.value.trim();
    const listId = this.listId();
    if (!name || listId === null || this.isAddingTask()) {
      return;
    }
    this.isAddingTask.set(true);
    try {
      const res = await createItineraryTaskView({body: {itinerary_list_id: listId, name}});
      this.tasks.update(prev => [...prev, res.data]);
      this.newTaskCtrl.setValue('');
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: this.t().error, text: `${err}`});
    } finally {
      this.isAddingTask.set(false);
    }
  }

  async toggleTask(task: ItineraryTaskSchema): Promise<void> {
    if (this.savingTaskId() !== null) {
      return;
    }
    const next: TaskStatus = task.status === 'done' ? 'to_do' : 'done';
    this.savingTaskId.set(task.id);
    try {
      const res = await updateItineraryTaskView({body: {status: next}, path: {object_id: task.id}});
      this.tasks.update(prev => prev.map(t => (t.id === task.id ? res.data : t)));
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: this.t().error, text: `${err}`});
    } finally {
      this.savingTaskId.set(null);
    }
  }

  async editTask(task: ItineraryTaskSchema): Promise<void> {
    const result = await this.dialogService.open<ItemDialogData, ItemDialogResult>(
      ItemDialogComponent,
      {
        kind: 'task',
        title: this.t().detail.editTask,
        name: task.name,
        description: task.description,
        confirmActionName: this.t().save,
      },
      45,
    );
    if (!result) {
      return;
    }
    this.savingTaskId.set(task.id);
    try {
      const res = await updateItineraryTaskView({
        body: {name: result.name, description: result.description},
        path: {object_id: task.id},
      });
      this.tasks.update(prev => prev.map(t => (t.id === task.id ? res.data : t)));
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: this.t().error, text: `${err}`});
    } finally {
      this.savingTaskId.set(null);
    }
  }

  async deleteTask(task: ItineraryTaskSchema): Promise<void> {
    const t = this.t();
    const confirmed = await this.dialogService.getBooleanFromConfirmationDialog({
      title: t.detail.deleteTask,
      text: fill(t.detail.deleteConfirm, {name: task.name}),
      confirmActionName: t.detail.delete,
      danger: true,
      cancelActionName: t.cancel,
    });
    if (!confirmed) {
      return;
    }
    try {
      await deleteItineraryTaskView({path: {object_id: task.id}});
      this.tasks.update(prev => prev.filter(t => t.id !== task.id));
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: this.t().error, text: `${err}`});
    }
  }

  async toggleActive(): Promise<void> {
    const id = this.listId();
    if (id === null || this.isUpdatingStatus()) {
      return;
    }
    const active = this.isActive();
    if (active) {
      const t = this.t();
      const confirmed = await this.dialogService.getBooleanFromConfirmationDialog({
        title: t.detail.finishTitle,
        text: t.detail.finishText,
        confirmActionName: t.detail.finish,
        cancelActionName: t.cancel,
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
      await this.dialogService.showNotificationDialog({title: this.t().error, text: `${err}`});
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
      title: this.t().detail.shareTitle,
      subtitle: this.t().detail.shareSubtitle,
      listMembers: async (objectId: number) => {
        const data = (await listItineraryListMembersView({path: {object_id: objectId}})).data;
        return {members: data.members, pendingInvitations: data.pending_invitations};
      },
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
    const t = this.t();
    const confirmed = await this.dialogService.getBooleanFromTextConfirmationDialog({
      title: t.detail.deleteList,
      text: t.detail.deleteListText,
      label: t.detail.listName,
      validationText: list.name,
      confirmActionName: t.detail.deleteList,
      cancelActionName: t.cancel,
    });
    if (!confirmed) {
      return;
    }
    try {
      await deleteItineraryListView({path: {object_id: list.id}});
      await this.routingService.navigateToItineraryLists();
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: this.t().error, text: `${err}`});
    }
  }

}
