import {Component, inject} from '@angular/core';
import {
  BlockSchema,
  deleteBlockItemView,
  paginationBlockView,
  PaginationBlockViewData,
  postCreateBlockItemView,
  readBlockItemView,
  runActionBuildBlockItemView,
  updateBlockItemView,
  uploadDataToBlockByIdView
} from '../../../generated-files/api/blocks';
import {BlockTypesEnum} from '../../../generated-files/api/blocks/enums.gen';
import {
  generateRandomBoolean,
  generateRandomInteger,
  generateRandomString,
  getRandomFromEnum
} from '../../common/util-functions/random-utils';
import {
  featherActivity,
  featherBookOpen,
  featherDelete,
  featherDownload,
  featherEdit,
  featherUpload
} from '@ng-icons/feather-icons';
import {ReactiveFormsModule} from '@angular/forms';
import {BasePageComponent} from '../../common/components/base-page-component';
import {StringUtilsService} from '../../common/services/string-utils.service';
import {DialogService} from '../../common/dialogs/dialogs.service';
import {FileDownloadService} from '../../common/services/file-download.service';
import {FilesUploadService} from '../../common/services/files-upload.service';
import {PaginatedTableColumn} from '../../common/components/paginated-table/paginated-table-column';
import {TableAction} from '../../common/components/paginated-table/table-action';
import {InputDebounce} from '../../common/data/input-debouncer';
import {PaginatedTableHandler} from '../../common/components/paginated-table/paginated-table-handler';
import {PaginatedTableComponent} from '../../common/components/paginated-table/paginated-table.component';
import {BlockTypeDisplay} from '../../shared/string-display/block-type-display';

@Component({
  selector: 'app-example-table',
  imports: [PaginatedTableComponent, ReactiveFormsModule],
  templateUrl: './example-table.component.html',
  styleUrl: './example-table.component.css'
})
export class ExampleTableComponent extends BasePageComponent {
  stringUtilsService = inject(StringUtilsService);
  dialogsService = inject(DialogService);
  fileDownloadService = inject(FileDownloadService);
  filesUploadService = inject(FilesUploadService);

  columns: PaginatedTableColumn[] = [
    {prop: 'id'},
    {prop: 'a'},
    {prop: 'b'},
    {prop: 'c'},
    {
      prop: 'block_type', name: 'Block Type', sortable: false,
      stringDisplay: new BlockTypeDisplay()
    }
  ]

  actions: TableAction[] = [
    {
      display: 'Show Details', icon: featherBookOpen, callback: async (block: BlockSchema) => {
        const fullBlock = await readBlockItemView({
          path: {object_id: block.id}
        });
        await this.dialogsService.showNotificationDialog({
          title: `Block ${block.id}`,
          text: JSON.stringify(fullBlock, null, 2),
        });
      }
    },
    {
      display: 'Delete', icon: featherDelete, callback: async (block: BlockSchema) => {
        await deleteBlockItemView({
          path: {object_id: block.id}
        });
        await this.paginatedDataHandler.fetch();
      }
    },
    {
      display: 'Update', icon: featherEdit, callback: async (block: BlockSchema) => {
        await updateBlockItemView({
          body: {
            a: this.stringUtilsService.generateRandomString(10),
            b: Math.floor(Math.random() * 11),
            c: Math.random() < 0.5,
          },
          path: {
            object_id: block.id,
          }
        });
        await this.paginatedDataHandler.fetch();
      }
    },
    {
      display: 'Build', icon: featherActivity, callback: async (block: BlockSchema) => {
        await runActionBuildBlockItemView({
          body: {
            should_build: true,
          },
          path: {
            object_id: block.id,
          }
        });
        await this.paginatedDataHandler.fetch();
      }
    },
    {
      display: 'Download', icon: featherDownload, callback: async (block: BlockSchema) => {
        try {
          this.fileDownloadService.downloadAndSave(`/api/blocks/${block.id}/download/`, 'block.json')
        } catch (error) {
          await this.dialogsService.showNotificationDialog({
            title: 'Download Error',
            text: `Failed to download data for block ${block.id}: ${error}`,
          });
        }
      }
    },
    {
      display: 'Upload', icon: featherUpload, callback: async (block: BlockSchema) => {
        try {
          await this.filesUploadService.uploadFile('.xlsx', async (files: File[]) => {
            await uploadDataToBlockByIdView({
              body: {
                files: Array.from(files)
              },
              path: {
                object_id: block.id
              }
            })
          })
          await this.dialogsService.showNotificationDialog({
            title: 'Upload Successful',
            text: `File successfully uploaded to block ${block.id}`,
          });
        } catch (error) {
          await this.dialogsService.showNotificationDialog({
            title: 'Upload Error',
            text: `Failed to initiate upload for block ${block.id}: ${error}`,
          });
        }
      }
    },
  ];

  paginatedDataHandler: PaginatedTableHandler<BlockSchema, PaginationBlockViewData> = null;
  searchDebouncer = new InputDebounce('');

  constructor() {
    super();
    this.paginatedDataHandler = new PaginatedTableHandler<BlockSchema, PaginationBlockViewData>(async (options) => {
      return (await paginationBlockView(options)).data;
    });
    this.paginatedDataHandler.fetch();
    this.subscriptions.push(this.searchDebouncer.valueChangedFinished$.subscribe(
      value => {
        this.paginatedDataHandler.setFilter('search', value)
      }
    ))
  }

  override ngOnDestroy() {
    super.ngOnDestroy();
    this.paginatedDataHandler.destroy();
  }

  generateRandomBlockData() {
    return {
      a: generateRandomString(10),
      b: generateRandomInteger(0, 100),
      c: generateRandomBoolean(),
      block_type: getRandomFromEnum(BlockTypesEnum)
    };
  }

  async createBlock(): Promise<void> {
    try {
      const randomData = this.generateRandomBlockData();
      await postCreateBlockItemView({
        body: randomData
      });
      await this.paginatedDataHandler.fetch();
    } catch (error) {
      await this.dialogsService.showNotificationDialog({
        title: 'Error',
        text: `Failed to create block: ${error}`,
      });
    }
  }
}
