import {Component, computed, inject, signal} from '@angular/core';
import {takeUntilDestroyed, toSignal} from '@angular/core/rxjs-interop';
import {FormControl, ReactiveFormsModule} from '@angular/forms';
import {ActivatedRoute, RouterLink} from '@angular/router';
import {NgIcon, provideIcons} from '@ng-icons/core';
import {
  featherArrowLeft,
  featherCheckSquare,
  featherChevronDown,
  featherChevronRight,
  featherClock,
  featherEdit,
  featherPlus,
  featherShare2,
  featherSquare,
  featherTrash2,
  featherX,
} from '@ng-icons/feather-icons';
import {fromEvent, interval} from 'rxjs';
import {
  createShoppingItemView,
  deleteShoppingItemView,
  deleteShoppingListView,
  getShoppingListView,
  listShoppingListMembersView,
  paginateShoppingItemsView,
  shareShoppingListView,
  ShoppingItemSchema,
  ShoppingListSchema,
  unshareShoppingListView,
  updateShoppingItemView,
  updateShoppingListView,
} from '../../../generated-files/api/shopping-lists';
import {AuthenticationService} from '../../common/authentication/authentication.service';
import {DialogService} from '../../common/dialogs/dialogs.service';
import {ShareDialogComponent} from '../../common/dialogs/share-dialog/share-dialog.component';
import {RoutingService} from '../../shared/services/routing.service';

const CHECKED_PREVIEW_COUNT = 10;
const MAX_SUGGESTIONS = 6;
const SYNC_INTERVAL_MS = 15000;

@Component({
  selector: 'app-shopping-list-detail',
  standalone: true,
  imports: [NgIcon, ReactiveFormsModule, RouterLink],
  providers: [provideIcons({
    featherArrowLeft, featherCheckSquare, featherChevronDown, featherChevronRight, featherClock, featherEdit,
    featherPlus, featherShare2, featherSquare, featherTrash2, featherX,
  })],
  templateUrl: './shopping-list-detail.component.html',
})
export class ShoppingListDetailComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly routingService = inject(RoutingService);
  private readonly dialogService = inject(DialogService);
  private readonly authService = inject(AuthenticationService);

  readonly allListsUrl = this.routingService.getShoppingListsUrl();

  readonly listId = signal<number | null>(null);
  readonly list = signal<ShoppingListSchema | null>(null);
  readonly items = signal<ShoppingItemSchema[]>([]);
  readonly isLoading = signal<boolean>(true);
  readonly loadError = signal<string | null>(null);

  readonly showAllChecked = signal<boolean>(false);
  readonly checkedExpanded = signal<boolean>(true);

  readonly newItemCtrl = new FormControl<string>('', {nonNullable: true});
  private readonly newItemValue = toSignal(this.newItemCtrl.valueChanges, {initialValue: ''});
  readonly suggestionsOpen = signal<boolean>(false);
  readonly highlightedIndex = signal<number>(-1);

  // Background sync must not overwrite optimistic local state: skip it while a write is in flight,
  // and discard a response that was requested before a write started.
  private pendingWrites = 0;
  private writeVersion = 0;

  readonly isOwner = computed(() => {
    const list = this.list();
    return !!list && list.owner_id === this.authService.user()?.id;
  });

  readonly uncheckedItems = computed(() =>
    this.items()
      .filter(i => !i.is_checked)
      .sort((a, b) => a.order - b.order || a.id - b.id),
  );

  readonly checkedItems = computed(() =>
    this.items()
      .filter(i => i.is_checked)
      .sort((a, b) => (b.checked_at ?? '').localeCompare(a.checked_at ?? '') || b.id - a.id),
  );

  readonly visibleCheckedItems = computed(() => {
    const checked = this.checkedItems();
    return this.showAllChecked() ? checked : checked.slice(0, CHECKED_PREVIEW_COUNT);
  });

  readonly hiddenCheckedCount = computed(() => Math.max(0, this.checkedItems().length - CHECKED_PREVIEW_COUNT));

  // Autocomplete is sourced from the checked items: things bought before, not already on the list.
  readonly suggestions = computed(() => {
    const query = this.newItemValue().trim().toLowerCase();
    if (!query) {
      return [];
    }
    const onList = new Set(this.uncheckedItems().map(i => i.name.toLowerCase()));
    const seen = new Set<string>();
    const prefixMatches: ShoppingItemSchema[] = [];
    const otherMatches: ShoppingItemSchema[] = [];
    for (const item of this.checkedItems()) {
      const name = item.name.toLowerCase();
      if (onList.has(name) || seen.has(name) || !name.includes(query)) {
        continue;
      }
      seen.add(name);
      if (name.startsWith(query)) {
        prefixMatches.push(item);
      } else {
        otherMatches.push(item);
      }
    }
    return [...prefixMatches, ...otherMatches].slice(0, MAX_SUGGESTIONS);
  });

  readonly showSuggestions = computed(() => this.suggestionsOpen() && this.suggestions().length > 0);

  readonly suggestionHighlighted = computed(() => {
    const index = this.highlightedIndex();
    return Object.fromEntries(this.suggestions().map((s, i) => [s.id, i === index]));
  });

  protected readonly featherArrowLeft = featherArrowLeft;
  protected readonly featherCheckSquare = featherCheckSquare;
  protected readonly featherChevronDown = featherChevronDown;
  protected readonly featherChevronRight = featherChevronRight;
  protected readonly featherClock = featherClock;
  protected readonly featherEdit = featherEdit;
  protected readonly featherPlus = featherPlus;
  protected readonly featherShare2 = featherShare2;
  protected readonly featherSquare = featherSquare;
  protected readonly featherTrash2 = featherTrash2;
  protected readonly featherX = featherX;

  constructor() {
    this.route.paramMap.pipe(takeUntilDestroyed()).subscribe(params => {
      const idStr = params.get('id');
      if (idStr) {
        const id = Number(idStr);
        this.listId.set(id);
        void this.load(id);
      }
    });

    this.newItemCtrl.valueChanges.pipe(takeUntilDestroyed()).subscribe(() => {
      this.highlightedIndex.set(-1);
      this.suggestionsOpen.set(true);
    });

    // Lists are shared, so pick up changes made by other members while this page is open.
    interval(SYNC_INTERVAL_MS).pipe(takeUntilDestroyed()).subscribe(() => {
      if (document.visibilityState === 'visible') {
        void this.sync();
      }
    });
    fromEvent(document, 'visibilitychange').pipe(takeUntilDestroyed()).subscribe(() => {
      if (document.visibilityState === 'visible') {
        void this.sync();
      }
    });
  }

  private async load(id: number): Promise<void> {
    this.isLoading.set(true);
    this.loadError.set(null);
    try {
      await this.fetch(id);
    } catch {
      this.loadError.set('Could not load this list. You may not have access to it.');
    } finally {
      this.isLoading.set(false);
    }
  }

  private async fetch(id: number): Promise<void> {
    const version = this.writeVersion;
    const [listRes, itemsRes] = await Promise.all([
      getShoppingListView({path: {object_id: id}}),
      paginateShoppingItemsView({path: {list_id: id}, query: {page: 0, page_size: 1000}}),
    ]);
    if (this.pendingWrites > 0 || version !== this.writeVersion) {
      return;
    }
    this.list.set(listRes.data);
    this.items.set(itemsRes.data.data);
  }

  private async sync(): Promise<void> {
    const id = this.listId();
    if (id === null || this.isLoading() || this.loadError() || this.pendingWrites > 0) {
      return;
    }
    try {
      await this.fetch(id);
    } catch {
      // A failed background refresh is not actionable; the next tick retries.
    }
  }

  private upsertItem(item: ShoppingItemSchema): void {
    this.items.update(prev =>
      prev.some(i => i.id === item.id) ? prev.map(i => (i.id === item.id ? item : i)) : [...prev, item],
    );
  }

  private async runWrite<T>(write: () => Promise<T>): Promise<T> {
    this.pendingWrites += 1;
    this.writeVersion += 1;
    try {
      return await write();
    } finally {
      this.pendingWrites -= 1;
    }
  }

  onNewItemKeydown(event: KeyboardEvent): void {
    const suggestions = this.suggestions();
    switch (event.key) {
      case 'ArrowDown':
        if (suggestions.length > 0) {
          event.preventDefault();
          this.suggestionsOpen.set(true);
          this.highlightedIndex.update(i => (i + 1) % suggestions.length);
        }
        break;
      case 'ArrowUp':
        if (suggestions.length > 0) {
          event.preventDefault();
          this.highlightedIndex.update(i => (i <= 0 ? suggestions.length - 1 : i - 1));
        }
        break;
      case 'Enter': {
        event.preventDefault();
        const highlighted = this.showSuggestions() ? suggestions[this.highlightedIndex()] : undefined;
        void this.addItem(highlighted ? highlighted.name : this.newItemCtrl.value);
        break;
      }
      case 'Escape':
        this.suggestionsOpen.set(false);
        this.highlightedIndex.set(-1);
        break;
    }
  }

  onNewItemBlur(): void {
    this.suggestionsOpen.set(false);
    this.highlightedIndex.set(-1);
  }

  onSuggestionMouseDown(event: MouseEvent, suggestion: ShoppingItemSchema): void {
    // mousedown + preventDefault keeps focus in the input so the user can keep typing the next item.
    event.preventDefault();
    void this.addItem(suggestion.name);
  }

  async addItem(rawName: string): Promise<void> {
    const name = rawName.trim();
    const listId = this.listId();
    if (!name || listId === null) {
      return;
    }
    this.newItemCtrl.setValue('');
    this.suggestionsOpen.set(false);
    try {
      const res = await this.runWrite(() => createShoppingItemView({body: {shopping_list_id: listId, name}}));
      this.upsertItem(res.data);
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: 'Error', text: `${err}`});
    }
  }

  async toggleItem(item: ShoppingItemSchema): Promise<void> {
    const isChecked = !item.is_checked;
    const maxOrder = Math.max(-1, ...this.uncheckedItems().map(i => i.order));
    this.upsertItem({
      ...item,
      is_checked: isChecked,
      checked_at: isChecked ? new Date().toISOString() : null,
      order: isChecked ? item.order : maxOrder + 1,
    });
    try {
      const res = await this.runWrite(() =>
        updateShoppingItemView({body: {is_checked: isChecked}, path: {object_id: item.id}}),
      );
      this.upsertItem(res.data);
    } catch (err) {
      this.upsertItem(item);
      await this.dialogService.showNotificationDialog({title: 'Error', text: `${err}`});
    }
  }

  async renameItem(item: ShoppingItemSchema): Promise<void> {
    const name = await this.dialogService.getTextFromInputDialog({
      title: 'Edit item',
      text: '',
      label: 'Name',
      defaultValue: item.name,
      confirmActionName: 'Save',
      cancelActionName: 'Cancel',
      maxLength: 255,
    }, 40);
    const trimmed = name?.trim();
    if (!trimmed || trimmed === item.name) {
      return;
    }
    try {
      const res = await this.runWrite(() =>
        updateShoppingItemView({body: {name: trimmed}, path: {object_id: item.id}}),
      );
      this.upsertItem(res.data);
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: 'Error', text: `${err}`});
    }
  }

  async deleteItem(item: ShoppingItemSchema): Promise<void> {
    this.items.update(prev => prev.filter(i => i.id !== item.id));
    try {
      await this.runWrite(() => deleteShoppingItemView({path: {object_id: item.id}}));
    } catch (err) {
      this.upsertItem(item);
      await this.dialogService.showNotificationDialog({title: 'Error', text: `${err}`});
    }
  }

  toggleCheckedExpanded(): void {
    this.checkedExpanded.update(v => !v);
  }

  toggleShowAllChecked(): void {
    this.showAllChecked.update(v => !v);
  }

  async renameList(): Promise<void> {
    const list = this.list();
    if (list === null) {
      return;
    }
    const name = await this.dialogService.getTextFromInputDialog({
      title: 'Rename list',
      text: '',
      label: 'Name',
      defaultValue: list.name,
      confirmActionName: 'Save',
      cancelActionName: 'Cancel',
      maxLength: 255,
    }, 40);
    const trimmed = name?.trim();
    if (!trimmed || trimmed === list.name) {
      return;
    }
    try {
      const res = await updateShoppingListView({body: {name: trimmed}, path: {object_id: list.id}});
      this.list.set(res.data);
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: 'Error', text: `${err}`});
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
      subtitle: 'People you add can view, add and check off items. Invite someone new by email.',
      listMembers: async (objectId: number) => {
        const data = (await listShoppingListMembersView({path: {object_id: objectId}})).data;
        return {members: data.members, pendingInvitations: data.pending_invitations};
      },
      share: async (objectId: number, identifier: string) => {
        await shareShoppingListView({body: {identifier}, path: {object_id: objectId}});
      },
      unshare: async (objectId: number, identifier: string) => {
        await unshareShoppingListView({body: {identifier}, path: {object_id: objectId}});
      },
    }, 45);
    const res = await getShoppingListView({path: {object_id: id}});
    this.list.set(res.data);
  }

  async deleteList(): Promise<void> {
    const list = this.list();
    if (list === null) {
      return;
    }
    const confirmed = await this.dialogService.getBooleanFromTextConfirmationDialog({
      title: 'Delete list',
      text: 'This permanently deletes the list, its items and its history for everyone it is shared with. This cannot be undone.',
      label: 'List name',
      validationText: list.name,
      confirmActionName: 'Delete list',
      cancelActionName: 'Cancel',
    });
    if (!confirmed) {
      return;
    }
    try {
      await deleteShoppingListView({path: {object_id: list.id}});
      await this.routingService.navigateToShoppingLists();
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: 'Error', text: `${err}`});
    }
  }
}
