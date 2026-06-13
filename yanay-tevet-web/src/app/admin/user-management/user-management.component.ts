import {Component, computed, inject, signal} from '@angular/core';
import {ReactiveFormsModule} from '@angular/forms';
import {NgIcon, provideIcons} from '@ng-icons/core';
import {featherChevronLeft, featherChevronRight} from '@ng-icons/feather-icons';
import {
  AdminUserOutput,
  adminUsersPaginationView,
  Permissions,
  updateUserPermissionsView,
} from '../../../generated-files/api/users';
import {PermissionsEnum} from '../../../generated-files/api/users/enums.gen';
import {AuthenticationService} from '../../common/authentication/authentication.service';
import {DialogService} from '../../common/dialogs/dialogs.service';
import {InputDebounce} from '../../common/data/input-debouncer';
import {BasePageComponent} from '../../common/components/base-page-component';
import {TooltipDirective} from '../../common/components/tooltip/tooltip.directive';

interface PermissionOption {
  value: Permissions;
  label: string;
  description: string;
}

const PAGE_SIZE = 25;

@Component({
  selector: 'app-user-management',
  standalone: true,
  imports: [ReactiveFormsModule, NgIcon, TooltipDirective],
  providers: [provideIcons({featherChevronLeft, featherChevronRight})],
  templateUrl: './user-management.component.html',
})
export class UserManagementComponent extends BasePageComponent {
  private readonly authService = inject(AuthenticationService);
  private readonly dialogService = inject(DialogService);

  readonly permissionOptions: PermissionOption[] = [
    {value: PermissionsEnum.ADMIN, label: 'Admin', description: 'Full access, including user management'},
    {value: PermissionsEnum.EDITOR, label: 'Editor', description: 'Content editing tools'},
    {value: PermissionsEnum.DREAM_DIARY, label: 'Dream Diary', description: 'Access to Dream Diary'},
    {value: PermissionsEnum.APARTMENT_HUNT, label: 'Apartment Hunt', description: 'Access to Apartment Hunt'},
    {value: PermissionsEnum.ITINERARY_LISTS, label: 'Itinerary Lists', description: 'Access to Itinerary Lists'},
    {value: PermissionsEnum.TASK_MANAGEMENT, label: 'Task Management', description: 'Access to Task Management'},
  ];

  readonly users = signal<AdminUserOutput[]>([]);
  readonly isLoading = signal<boolean>(true);
  readonly page = signal<number>(0);
  readonly pagesAmount = signal<number>(0);
  readonly totalAmount = signal<number>(0);
  readonly savingUserId = signal<number | null>(null);

  readonly searchDebouncer = new InputDebounce<string>('');

  readonly currentUserId = computed<number | null>(() => this.authService.user()?.id ?? null);

  readonly permissionState = computed<Record<string, boolean>>(() => {
    const state: Record<string, boolean> = {};
    for (const user of this.users()) {
      for (const option of this.permissionOptions) {
        state[`${user.id}:${option.value}`] = user.permissions.includes(option.value);
      }
    }
    return state;
  });

  readonly canGoPrev = computed<boolean>(() => this.page() > 0);
  readonly canGoNext = computed<boolean>(() => this.page() < this.pagesAmount() - 1);

  protected readonly featherChevronLeft = featherChevronLeft;
  protected readonly featherChevronRight = featherChevronRight;

  constructor() {
    super();
    void this.loadUsers();
    this.subscriptions.push(
      this.searchDebouncer.valueChangedFinished$.subscribe(() => {
        this.page.set(0);
        void this.loadUsers();
      }),
    );
  }

  private async loadUsers(): Promise<void> {
    this.isLoading.set(true);
    try {
      const result = await adminUsersPaginationView({
        query: {
          page: this.page(),
          page_size: PAGE_SIZE,
          text: this.searchDebouncer.value || undefined,
          order_by: ['username'],
        },
      });
      if (result.error || !result.data) {
        await this.showError(result.error, 'Failed to load users.');
        return;
      }
      this.users.set(result.data.data);
      this.pagesAmount.set(result.data.pages_amount);
      this.totalAmount.set(result.data.total_amount);
    } finally {
      this.isLoading.set(false);
    }
  }

  async goToPage(page: number): Promise<void> {
    if (page < 0 || page > this.pagesAmount() - 1) {
      return;
    }
    this.page.set(page);
    await this.loadUsers();
  }

  async togglePermission(user: AdminUserOutput, option: PermissionOption): Promise<void> {
    if (this.savingUserId() !== null) {
      return;
    }
    const isActive = user.permissions.includes(option.value);

    if (option.value === PermissionsEnum.ADMIN) {
      const confirmed = await this.dialogService.getBooleanFromConfirmationDialog({
        title: isActive ? 'Revoke admin access' : 'Grant admin access',
        text: isActive
          ? `Remove admin permission from ${user.full_name || user.username}? They will lose access to user management and all admin tools.`
          : `Grant admin permission to ${user.full_name || user.username}? They will be able to manage all users and access every admin tool.`,
        confirmActionName: isActive ? 'Revoke' : 'Grant',
        cancelActionName: 'Cancel',
      });
      if (!confirmed) {
        return;
      }
    }

    const newPermissions = isActive
      ? user.permissions.filter(permission => permission !== option.value)
      : [...user.permissions, option.value];

    this.savingUserId.set(user.id);
    try {
      const result = await updateUserPermissionsView({
        body: {user_id: user.id, permissions: newPermissions},
      });
      if (result.error || !result.data) {
        await this.showError(result.error, 'Failed to update permissions.');
        return;
      }
      const updated = result.data;
      this.users.update(users => users.map(u => (u.id === updated.id ? updated : u)));
      if (updated.id === this.currentUserId()) {
        await this.authService.checkAuth();
      }
    } finally {
      this.savingUserId.set(null);
    }
  }

  private async showError(error: unknown, fallback: string): Promise<void> {
    const detail = (error as {detail?: string} | null)?.detail;
    await this.dialogService.showNotificationDialog({
      title: 'Error',
      text: detail ?? fallback,
    });
  }
}
