// import {ColumnMode, NgxDatatableModule, PageEvent, SortEvent, SortType, TableColumn} from '@swimlane/ngx-datatable'; // removed: library dropped, pending replacement
import {Component, computed, inject, input, TemplateRef, ViewChild} from '@angular/core';
import {PaginatedTableHandler} from './paginated-table-handler';
import {PaginationInput} from './pagination-input';
import {PaginatedData} from './paginated-data';
import {MenuButtonComponent} from '../menu-button/menu-button.component';
import {TableAction} from './table-action';
import {Action} from '../../interfaces/util/action';
import {bootstrapThreeDotsVertical} from '@ng-icons/bootstrap-icons';
import {DarkModeService} from '../../services/dark-mode.service';
import {PaginatedTableColumn, TableColumn} from './paginated-table-column';
import {ColumnFilterComponent} from './filters/column-filter/column-filter.component';
import {TooltipDirective} from '../tooltip/tooltip.directive';

// type ColumnMode = any;
// type SortType = any;
type PageEvent = any;
type SortEvent = any;

const ColumnMode: any = {};
const SortType: any = {};

@Component({
    selector: 'app-paginated-table',
    imports: [
        // NgxDatatableModule, // removed: library dropped, pending replacement
        MenuButtonComponent,
        ColumnFilterComponent,
        TooltipDirective
    ],
    templateUrl: './paginated-table.component.html',
    styleUrls: ['./paginated-table.component.css']
})
export class PaginatedTableComponent<T, S extends PaginationInput> {
    @ViewChild('actionTmpl', {static: true}) actionTmpl: TemplateRef<any>;
    @ViewChild('colHeader', {static: true}) colHeaderTpl!: TemplateRef<any>;
    themeService = inject(DarkModeService);

    paginatedDataHandler = input<PaginatedTableHandler<T, S>>();

    paginationDataSignal = computed<PaginatedData<T>>(() => {
        if (!this.paginatedDataHandler()) {
            return null;
        }
        return this.paginatedDataHandler().paginationDataSignal();
    });
    columns = input<PaginatedTableColumn[]>();
    actions = input<TableAction[]>();
    realColumns = computed<TableColumn[]>(() => {
        const columns = this.columns().map((column => {
          const newColumn: TableColumn = {...column}
            if (column.filter) {
                newColumn['headerTemplate'] = this.colHeaderTpl;
            }
            if (column.stringDisplay) {
              newColumn['pipe'] = {
                transform: (value: string) => {
                  return column.stringDisplay.get(value)
                }
              }
            }
            return newColumn;
        }));

        const actions = this.actions();
        if (actions) {
            const actionColumn: PaginatedTableColumn = {
                prop: 'action',
                name: ' ',
                sortable: false,
                width: 60,
                cellTemplate: this.actionTmpl,
                frozenRight: true,
                cellClass: 'datatable-body',
            }
            columns.push(actionColumn);
        }
        return columns;
    });

    setPage($event: PageEvent) {
        const paginatedDataHandler = this.paginatedDataHandler()
        if (paginatedDataHandler && paginatedDataHandler.pageSize === $event.pageSize && paginatedDataHandler.currentPage === $event.offset) {
            return;
        }
        this.paginatedDataHandler()?.fetchPage($event.offset, $event.limit);
    }

    setSort($event: SortEvent) {
        const paginatedDataHandler = this.paginatedDataHandler()
        paginatedDataHandler.clearAllSort(false)
        $event.sorts.forEach((sortProp: any) => {
            paginatedDataHandler.addSort(sortProp.prop as string, sortProp.dir, false)
        });
        paginatedDataHandler.fetch();
    }

    getActions(row: any): Action[] {
        return this.actions().map((tableAction) => {
            return {
                display: tableAction.display,
                icon: tableAction.icon,
                callback: () => {
                    tableAction.callback(row);
                },
            }
        });
    }

    protected readonly ColumnMode = ColumnMode;
    protected readonly SortType = SortType;
    protected readonly bootstrapThreeDotsVertical = bootstrapThreeDotsVertical;
}
