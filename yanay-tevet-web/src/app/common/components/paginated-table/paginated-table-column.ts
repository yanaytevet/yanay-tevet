// import {TableColumn} from '@swimlane/ngx-datatable'; // removed: library dropped, pending replacement
import {PaginatedTableFilter} from './filters/paginated-table-filter';
import {EnumDisplay} from '../../string-display/enum-display';

export type TableColumn = Record<string, any>;

export interface PaginatedTableColumn extends TableColumn {
    filter?: PaginatedTableFilter;
    stringDisplay?: EnumDisplay;
}
