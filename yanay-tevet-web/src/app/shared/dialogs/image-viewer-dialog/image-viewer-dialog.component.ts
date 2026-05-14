import {Component, inject, signal} from '@angular/core';
import {BaseDialogComponent} from '../../../common/dialogs/base-dialog.component';
import {CloudinaryImage} from '../../components/cloudinary-image/cloudinary-image';
import {NgIcon, provideIcons} from '@ng-icons/core';
import {bootstrapChatDots} from '@ng-icons/bootstrap-icons';
import {postAddImageLogItemView} from '../../../../generated-files/api/campaign-sessions';
import {DialogService} from '../../../common/dialogs/dialogs.service';

export interface ImageForViewer {
  id: number;
  name: string;
  description: string;
  image_public_id: string;
  is_visible?: boolean;
}

export interface ImageViewerDialogInput {
  image: ImageForViewer;
  sessionId: number | null;
}

@Component({
  selector: 'app-image-viewer-dialog',
  standalone: true,
  imports: [CloudinaryImage, NgIcon],
  providers: [provideIcons({bootstrapChatDots})],
  templateUrl: './image-viewer-dialog.component.html',
})
export class ImageViewerDialogComponent extends BaseDialogComponent<ImageViewerDialogInput, void> {
  private readonly dialogService = inject(DialogService);

  readonly isSending = signal(false);
  protected readonly bootstrapChatDots = bootstrapChatDots;

  readonly image = this.data.image;
  readonly sessionId = this.data.sessionId;
  readonly isHidden = this.data.image.is_visible === false;
  readonly canSendToChat = this.data.sessionId !== null && !this.isHidden;

  async onSendToChat() {
    if (!this.sessionId || this.isSending()) {
      return;
    }
    this.isSending.set(true);
    try {
      await postAddImageLogItemView({
        path: {object_id: this.sessionId},
        body: {image_id: this.image.id},
      });
      this.emitClose();
    } catch (error: any) {
      const errorCode = error?.response?.data?.error_code;
      if (errorCode === 'image_not_visible') {
        await this.dialogService.showNotificationDialog({
          title: 'Cannot Send',
          text: 'Only visible images can be sent to chat.',
        });
      } else {
        await this.dialogService.showNotificationDialog({
          title: 'Error',
          text: 'Failed to send image to chat.',
        });
      }
    } finally {
      this.isSending.set(false);
    }
  }
}
