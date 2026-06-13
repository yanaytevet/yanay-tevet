import {Component, effect, ElementRef, HostListener, input, output, signal, ViewChild} from '@angular/core';
import {CommonModule} from '@angular/common';
import {FormsModule} from '@angular/forms';
import {PaginatedTableHandler} from '../../paginated-table/paginated-table-handler';
import {AdminUsersPaginationViewData, AdminUserOutput} from '../../../../../generated-files/api/users';
import {adminUsersPaginationView} from '../../../../../generated-files/api/users';

@Component({
  selector: 'app-admin-all-users-autocomplete',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule
  ],
  templateUrl: './admin-all-users-autocomplete.component.html'
})
export class AdminAllUsersAutocompleteComponent {
  // Input for default user
  defaultUser = input<AdminUserOutput | null>(null);

  // Output for selected user
  selectedUserChanged = output<AdminUserOutput>();

  // Internal signals
  selectedUser = signal<AdminUserOutput | null>(null);
  searchText = signal<string>('');
  isDropdownOpen = signal<boolean>(false);
  highlightedIndex = signal<number>(-1);

  // Pagination handler
  paginationHandler: PaginatedTableHandler<AdminUserOutput, AdminUsersPaginationViewData>;

  // Reference to the input element
  @ViewChild('searchInput') searchInput!: ElementRef<HTMLInputElement>;

  constructor() {
    // Initialize pagination handler
    this.paginationHandler = new PaginatedTableHandler<AdminUserOutput, AdminUsersPaginationViewData>(
      async (options) => {
        const response = await adminUsersPaginationView({
          ...options,
        });
        return response.data;
      }
    );

    // Set page size to 8 as required
    this.paginationHandler.pageSize = 8;

    // Initialize with default user if provided
    effect(() => {
      const user = this.defaultUser();
      if (user) {
        this.selectedUser.set(user);
        this.searchText.set(user.username);
      }
    });

    // Fetch initial data
    this.paginationHandler.fetch();
  }

  // Handle input changes
  onSearchChange(event: Event): void {
    const value = (event.target as HTMLInputElement).value;
    this.searchText.set(value);

    // Set filter and fetch data
    this.paginationHandler.setFilter('text', value);

    // Open dropdown when searching
    if (value) {
      this.isDropdownOpen.set(true);
    }
  }

  // Select a user
  selectUser(user: AdminUserOutput): void {
    this.selectedUser.set(user);
    this.searchText.set(user.username);
    this.isDropdownOpen.set(false);
    this.selectedUserChanged.emit(user);
  }

  // Open dropdown
  openDropdown(): void {
    this.isDropdownOpen.set(true);
    this.paginationHandler.fetch();
    // Reset highlighted index when opening dropdown
    this.highlightedIndex.set(-1);
  }

  // Close dropdown when clicking outside
  @HostListener('document:click', ['$event'])
  onClickOutside(event: MouseEvent): void {
    const target = event.target as HTMLElement;
    const isClickInside = this.searchInput?.nativeElement.contains(target);

    if (!isClickInside) {
      this.isDropdownOpen.set(false);
    }
  }

  // Handle keyboard events
  onKeyDown(event: KeyboardEvent): void {
    if (!this.isDropdownOpen()) {
      if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
        this.openDropdown();
        event.preventDefault();
      }
      return;
    }

    const items = this.paginationHandler.itemsSignal();

    switch (event.key) {
      case 'ArrowDown':
        this.highlightNext(items.length);
        event.preventDefault();
        break;
      case 'ArrowUp':
        this.highlightPrevious(items.length);
        event.preventDefault();
        break;
      case 'Enter':
        this.selectHighlighted(items);
        event.preventDefault();
        break;
      case 'Escape':
        this.isDropdownOpen.set(false);
        event.preventDefault();
        break;
    }
  }

  // Highlight next item
  highlightNext(itemsLength: number): void {
    if (itemsLength === 0) return;

    const currentIndex = this.highlightedIndex();
    if (currentIndex >= itemsLength - 1) {
      // Wrap around to the first item
      this.highlightedIndex.set(0);
    } else {
      this.highlightedIndex.set(currentIndex + 1);
    }
  }

  // Highlight previous item
  highlightPrevious(itemsLength: number): void {
    if (itemsLength === 0) return;

    const currentIndex = this.highlightedIndex();
    if (currentIndex <= 0) {
      // Wrap around to the last item
      this.highlightedIndex.set(itemsLength - 1);
    } else {
      this.highlightedIndex.set(currentIndex - 1);
    }
  }

  // Select highlighted item
  selectHighlighted(items: AdminUserOutput[]): void {
    const index = this.highlightedIndex();
    if (index >= 0 && index < items.length) {
      this.selectUser(items[index]);
    }
  }
}
