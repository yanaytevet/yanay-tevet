import {Component, inject} from '@angular/core';
import {UploadFilesSumSizeResponse, uploadFilesSumSizeView} from '../../../generated-files/api/blocks';
import {BasePageComponent} from '../../common/components/base-page-component';
import {FileDownloadService} from '../../common/services/file-download.service';
import {FilesUploadService} from '../../common/services/files-upload.service';
import {DialogService} from '../../common/dialogs/dialogs.service';

@Component({
  selector: 'app-example-files',
  standalone: true,
  imports: [
  ],
  templateUrl: './example-files.component.html',
  styleUrl: './example-files.component.css'
})
export class ExampleFilesComponent extends BasePageComponent {
  fileDownloadService = inject(FileDownloadService);
  filesUploadService = inject(FilesUploadService);
  dialogService = inject(DialogService);

  constructor() {
    super();
  }

  downloadBlocksCount(): void {
    try {
      this.fileDownloadService.downloadAndSave('/api/blocks/download-count/', 'blocks_count.xlsx');
    } catch (error) {
      this.dialogService.showNotificationDialog({
        title: 'Download Error',
        text: `Failed to download blocks count: ${error}`
      });
    }
  }

  async uploadFilesAndCalculateSize(): Promise<void> {
    try {
      const result = await this.filesUploadService.uploadFile<UploadFilesSumSizeResponse>('.xlsx,.pdf', async (files: File[]) => {
        const formData = new FormData();
        files.forEach(file => {
          formData.append('files', file);
        });

        const res = await uploadFilesSumSizeView({
          body: {
            files
          }
        });
        return res?.data;
      });
      await this.dialogService.showNotificationDialog({
        title: 'Upload Successful',
        text: `Total size of uploaded files: ${result.total_size} bytes`
      });
    } catch (error) {
      await this.dialogService.showNotificationDialog({
        title: 'Upload Error',
        text: `Failed to upload files: ${error}`
      });
    }
  }
}
