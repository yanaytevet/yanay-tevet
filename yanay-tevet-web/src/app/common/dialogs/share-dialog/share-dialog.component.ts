import {Component, inject, signal} from '@angular/core';
import {FormControl, ReactiveFormsModule} from '@angular/forms';
import {NgIcon, provideIcons} from '@ng-icons/core';
import {featherX, featherUserPlus, featherMail} from '@ng-icons/feather-icons';
import {BaseDialogComponent} from '../base-dialog.component';
import {DialogService} from '../dialogs.service';

export interface ShareDialogMember {
  user_id: number;
  username: string;
  full_name: string;
  role: string;
}

export interface ShareDialogPendingInvitation {
  email: string;
}

export interface ShareDialogAccess {
  members: ShareDialogMember[];
  pendingInvitations: ShareDialogPendingInvitation[];
}

export interface ShareDialogData {
  objectId: number;
  isOwner: boolean;
  title: string;
  subtitle: string;
  listMembers: (objectId: number) => Promise<ShareDialogAccess>;
  share: (objectId: number, identifier: string) => Promise<void>;
  unshare: (objectId: number, identifier: string) => Promise<void>;
}

@Component({
  selector: 'app-share-dialog',
  standalone: true,
  imports: [ReactiveFormsModule, NgIcon],
  providers: [provideIcons({featherX, featherUserPlus, featherMail})],
  templateUrl: './share-dialog.component.html',
})
export class ShareDialogComponent extends BaseDialogComponent<ShareDialogData, null> {
  private readonly dialogService = inject(DialogService);

  readonly members = signal<ShareDialogMember[]>([]);
  readonly pendingInvitations = signal<ShareDialogPendingInvitation[]>([]);
  readonly isLoading = signal<boolean>(true);
  readonly isSharing = signal<boolean>(false);
  readonly removingUserId = signal<number | null>(null);

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
      const access = await this.data.listMembers(this.data.objectId);
      this.members.set(access.members);
      this.pendingInvitations.set(access.pendingInvitations);
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
      await this.data.share(this.data.objectId, identifier);
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

  async onRemove(member: ShareDialogMember): Promise<void> {
    this.removingUserId.set(member.user_id);
    try {
      await this.data.unshare(this.data.objectId, member.username);
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
