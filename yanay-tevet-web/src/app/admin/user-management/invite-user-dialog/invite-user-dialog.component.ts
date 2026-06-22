import {Component, computed, inject, signal} from '@angular/core';
import {FormControl, ReactiveFormsModule} from '@angular/forms';
import {NgIcon, provideIcons} from '@ng-icons/core';
import {featherX, featherMail} from '@ng-icons/feather-icons';
import {inviteUserView, Permissions} from '../../../../generated-files/api/users';
import {PermissionsEnum} from '../../../../generated-files/api/users/enums.gen';
import {BaseDialogComponent} from '../../../common/dialogs/base-dialog.component';
import {DialogService} from '../../../common/dialogs/dialogs.service';

interface PermissionOption {
  value: Permissions;
  label: string;
}

@Component({
  selector: 'app-invite-user-dialog',
  standalone: true,
  imports: [ReactiveFormsModule, NgIcon],
  providers: [provideIcons({featherX, featherMail})],
  templateUrl: './invite-user-dialog.component.html',
})
export class InviteUserDialogComponent extends BaseDialogComponent<void, boolean> {
  private readonly dialogService = inject(DialogService);

  readonly permissionOptions: PermissionOption[] = [
    {value: PermissionsEnum.EDITOR, label: 'Editor'},
    {value: PermissionsEnum.DREAM_DIARY, label: 'Dream Diary'},
    {value: PermissionsEnum.APARTMENT_HUNT, label: 'Apartment Hunt'},
    {value: PermissionsEnum.RENTERS_CRM, label: 'Renters CRM'},
    {value: PermissionsEnum.VILLA_VILLEKULLA, label: 'Villa Villekulla'},
    {value: PermissionsEnum.ITINERARY_LISTS, label: 'Itinerary Lists'},
    {value: PermissionsEnum.TASK_MANAGEMENT, label: 'Task Management'},
    {value: PermissionsEnum.WORKOUT_PLAN, label: 'Workout Plan'},
  ];

  readonly emailCtrl = new FormControl<string>('', {nonNullable: true});
  readonly selectedPermissions = signal<Permissions[]>([]);
  readonly isInviting = signal<boolean>(false);

  readonly permissionSelected = computed<Record<string, boolean>>(() => {
    const selected = this.selectedPermissions();
    return Object.fromEntries(this.permissionOptions.map(o => [o.value, selected.includes(o.value)]));
  });

  protected readonly featherX = featherX;
  protected readonly featherMail = featherMail;

  togglePermission(option: PermissionOption): void {
    this.selectedPermissions.update(current =>
      current.includes(option.value)
        ? current.filter(p => p !== option.value)
        : [...current, option.value],
    );
  }

  async onInvite(): Promise<void> {
    const email = this.emailCtrl.value.trim();
    if (this.isInviting()) {
      return;
    }
    if (!email.includes('@')) {
      await this.dialogService.showNotificationDialog({
        title: 'Invalid email',
        text: 'Please enter a valid email address.',
      });
      return;
    }

    this.isInviting.set(true);
    try {
      const result = await inviteUserView({body: {email, permissions: this.selectedPermissions()}});
      if (result.error || !result.data) {
        const detail = (result.error as {detail?: string} | null)?.detail;
        await this.dialogService.showNotificationDialog({
          title: 'Could not invite',
          text: detail ?? 'Failed to send the invitation.',
        });
        return;
      }
      await this.dialogService.showNotificationDialog({
        title: result.data.applied_immediately ? 'Access granted' : 'Invitation sent',
        text: result.data.applied_immediately
          ? `${email} already has an account — their permissions were updated.`
          : `An invitation email was sent to ${email}. Their access will be applied when they sign in.`,
      });
      this.emitClose(true);
    } finally {
      this.isInviting.set(false);
    }
  }

  onClose(): void {
    this.emitClose(null);
  }
}
