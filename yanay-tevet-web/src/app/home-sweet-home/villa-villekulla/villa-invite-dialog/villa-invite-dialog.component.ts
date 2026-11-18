import {Component, computed, inject, signal} from '@angular/core';
import {FormControl, ReactiveFormsModule} from '@angular/forms';
import {NgIcon, provideIcons} from '@ng-icons/core';
import {featherX, featherUserPlus, featherMail} from '@ng-icons/feather-icons';
import {
  listProjectMembersView,
  ProjectMembershipSchema,
  ProjectRole,
  shareVillaVillekullaProjectView,
  unshareRentalProjectView,
} from '../../../../generated-files/api/villa-villekulla';
import {BaseDialogComponent} from '../../../common/dialogs/base-dialog.component';
import {DialogService} from '../../../common/dialogs/dialogs.service';
import {LoadingStateComponent} from '../../../common/components/page/loading-state/loading-state.component';
import {fill, injectStrings} from '../../../shared/i18n/strings';
import {HOME_SWEET_HOME_STRINGS} from '../../i18n';

export interface VillaInviteDialogData {
  projectId: number;
}

@Component({
  selector: 'app-villa-invite-dialog',
  standalone: true,
  imports: [ReactiveFormsModule, NgIcon, LoadingStateComponent],
  providers: [provideIcons({featherX, featherUserPlus, featherMail})],
  templateUrl: './villa-invite-dialog.component.html',
})
export class VillaInviteDialogComponent extends BaseDialogComponent<VillaInviteDialogData, null> {
  private readonly dialogService = inject(DialogService);
  protected readonly t = injectStrings(HOME_SWEET_HOME_STRINGS);

  readonly members = signal<ProjectMembershipSchema[]>([]);
  readonly pendingInvitations = signal<{email: string}[]>([]);
  readonly isLoading = signal<boolean>(true);
  readonly isInviting = signal<boolean>(false);
  readonly removingUserId = signal<number | null>(null);
  readonly role = signal<ProjectRole>('collaborator');

  readonly removeLabels = computed<Record<number, string>>(() => Object.fromEntries(
    this.members().map(m => [m.user_id, fill(this.t().invite.remove, {name: m.full_name || m.username})]),
  ));

  readonly identifierCtrl = new FormControl<string>('', {nonNullable: true});

  protected readonly featherX = featherX;
  protected readonly featherUserPlus = featherUserPlus;
  protected readonly featherMail = featherMail;

  constructor() {
    super();
    void this.loadMembers();
  }

  private async loadMembers(): Promise<void> {
    this.isLoading.set(true);
    try {
      const res = await listProjectMembersView({path: {object_id: this.data.projectId}});
      this.members.set(res.data.members);
      this.pendingInvitations.set(res.data.pending_invitations);
    } finally {
      this.isLoading.set(false);
    }
  }

  setRole(role: ProjectRole): void {
    this.role.set(role);
  }

  async onInvite(): Promise<void> {
    const identifier = this.identifierCtrl.value.trim();
    if (!identifier || this.isInviting()) {
      return;
    }
    this.isInviting.set(true);
    try {
      await shareVillaVillekullaProjectView({
        body: {identifier, role: this.role()},
        path: {object_id: this.data.projectId},
      });
      this.identifierCtrl.setValue('');
      await this.loadMembers();
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: this.t().invite.inviteFailed, text: `${err}`});
    } finally {
      this.isInviting.set(false);
    }
  }

  async onRemove(member: ProjectMembershipSchema): Promise<void> {
    this.removingUserId.set(member.user_id);
    try {
      await unshareRentalProjectView({body: {identifier: member.username}, path: {object_id: this.data.projectId}});
      this.members.update(prev => prev.filter(m => m.user_id !== member.user_id));
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: this.t().invite.removeFailed, text: `${err}`});
    } finally {
      this.removingUserId.set(null);
    }
  }

  onClose(): void {
    this.emitClose(null);
  }
}
