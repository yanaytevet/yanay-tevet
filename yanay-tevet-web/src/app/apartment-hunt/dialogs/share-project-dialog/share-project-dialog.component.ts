import {Component, inject, signal} from '@angular/core';
import {FormControl, ReactiveFormsModule} from '@angular/forms';
import {NgIcon, provideIcons} from '@ng-icons/core';
import {featherX, featherUserPlus} from '@ng-icons/feather-icons';
import {
  listProjectMembersView,
  ProjectMembershipSchema,
  shareRentalProjectView,
  unshareRentalProjectView,
} from '../../../../generated-files/api/apartment-hunt';
import {BaseDialogComponent} from '../../../common/dialogs/base-dialog.component';
import {DialogService} from '../../../common/dialogs/dialogs.service';

export interface ShareProjectDialogData {
  projectId: number;
  isOwner: boolean;
}

@Component({
  selector: 'app-share-project-dialog',
  standalone: true,
  imports: [ReactiveFormsModule, NgIcon],
  providers: [provideIcons({featherX, featherUserPlus})],
  templateUrl: './share-project-dialog.component.html',
})
export class ShareProjectDialogComponent extends BaseDialogComponent<ShareProjectDialogData, null> {
  private readonly dialogService = inject(DialogService);

  readonly members = signal<ProjectMembershipSchema[]>([]);
  readonly isLoading = signal<boolean>(true);
  readonly isSharing = signal<boolean>(false);
  readonly removingUserId = signal<number | null>(null);

  readonly identifierCtrl = new FormControl<string>('', {nonNullable: true});

  protected readonly featherX = featherX;
  protected readonly featherUserPlus = featherUserPlus;

  constructor() {
    super();
    void this.loadMembers();
  }

  private async loadMembers(): Promise<void> {
    this.isLoading.set(true);
    try {
      const res = await listProjectMembersView({path: {object_id: this.data.projectId}});
      this.members.set(res.data.members);
    } finally {
      this.isLoading.set(false);
    }
  }

  async onShare(): Promise<void> {
    const identifier = this.identifierCtrl.value.trim();
    if (!identifier || this.isSharing()) {
      return;
    }
    this.isSharing.set(true);
    try {
      await shareRentalProjectView({
        body: {identifier, role: 'collaborator'},
        path: {object_id: this.data.projectId},
      });
      this.identifierCtrl.setValue('');
      await this.loadMembers();
    } catch (err) {
      await this.dialogService.showNotificationDialog({
        title: 'Could not share',
        text: `${err}`,
      });
    } finally {
      this.isSharing.set(false);
    }
  }

  async onRemove(member: ProjectMembershipSchema): Promise<void> {
    this.removingUserId.set(member.user_id);
    try {
      await unshareRentalProjectView({
        body: {identifier: member.username},
        path: {object_id: this.data.projectId},
      });
      this.members.update(prev => prev.filter(m => m.user_id !== member.user_id));
    } catch (err) {
      await this.dialogService.showNotificationDialog({
        title: 'Could not remove',
        text: `${err}`,
      });
    } finally {
      this.removingUserId.set(null);
    }
  }

  onClose(): void {
    this.emitClose(null);
  }
}
