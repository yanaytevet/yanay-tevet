import {Component, computed, inject, input} from '@angular/core';
import {PaginatedTableFilter} from '../paginated-table-filter';
import {PaginatedTableHandler} from '../../paginated-table-handler';
import {DialogService} from '../../../../dialogs/dialogs.service';

import {NgIcon} from '@ng-icons/core';
import {bootstrapFunnel, bootstrapX} from '@ng-icons/bootstrap-icons';

@Component({
    selector: 'app-column-filter',
    imports: [NgIcon],
    templateUrl: './column-filter.component.html'
})
export class ColumnFilterComponent {
    filter = input<PaginatedTableFilter>();
    paginatedDataHandler = input<PaginatedTableHandler<any, any>>();

    private dialogService = inject(DialogService);

    protected readonly bootstrapFunnel = bootstrapFunnel;
    protected readonly bootstrapX = bootstrapX;

    isActive = computed<boolean>(() => {
        const handler = this.paginatedDataHandler();
        const filterName = this.filter()?.filterName;

        if (!handler || !filterName) {
            return false;
        }

        let keys: string[];
        if (this.filter()?.useDictFilter){
            keys = handler.dictFilterKeysSignal();
        }  else {
            keys = handler.filterKeysSignal();
        }

        return keys.some(key =>
            key === filterName ||
            key === `${filterName}__icontains` ||
            key === `${filterName}__in` ||
            key === `${filterName}__gte` ||
            key === `${filterName}__lte`
        );
    });

    setFilterKey(key: string, value: any, fetch = true): void {
        const handler = this.paginatedDataHandler();

        if (!handler) {
            return;
        }

        if (this.filter()?.useDictFilter) {
            handler.setDictFilter(key, value, fetch);
        } else {
            handler.setFilter(key, value, fetch);
        }
    }

    getFilterValue(key: string): any {
        const handler = this.paginatedDataHandler();

        if (!handler) {
            return null;
        }

        if (this.filter()?.useDictFilter) {
            return handler.getDictFilterValue(key);
        } else {
            return handler.getFilterValue(key);
        }
    }

    clearFilterKey(key: string, fetch = true): void {
        const handler = this.paginatedDataHandler();

        if (!handler) {
            return;
        }

        if (this.filter()?.useDictFilter) {
            handler.clearDictFilter(key, fetch);
        } else {
            handler.clearFilter(key, fetch);
        }
    }

    async openFilterDialog(): Promise<void> {
        const filter = this.filter();

        if (!filter) {
            return;
        }

        switch (filter.filterType) {
            case 'text':
                await this.openTextFilterDialog();
                break;
            case 'boolean':
                await this.openBooleanFilterDialog();
                break;
            case 'options':
                await this.openOptionsFilterDialog();
                break;
            case 'number':
                await this.openNumberFilterDialog();
                break;
        }
    }

    private async openTextFilterDialog(): Promise<void> {
        const filter = this.filter();
        const filterKey = `${filter.filterName}__icontains`;
        const currentValue = this.getFilterValue(filterKey) || '';

        const result = await this.dialogService.getTextFromInputDialog({
            title: `Filter by ${filter.displayName}`,
            text: 'Enter text to filter by:',
            label: filter.displayName,
            defaultValue: currentValue,
            confirmActionName: 'Apply Filter',
            allowEmpty: true
        });

        if (result === null) {
            return; // Dialog was cancelled
        }

        if (result === '') {
            this.clearFilterKey(filterKey);
        } else {
            this.setFilterKey(filterKey, result);
        }
    }

    private async openBooleanFilterDialog(): Promise<void> {
        const filter = this.filter();
        const filterKey = filter.filterName;
        const currentValue = this.getFilterValue(filterKey) ?? null;

        const result = await this.dialogService.getValueFromSelectionDialog({
            title: `Filter by ${filter.displayName}`,
            text: 'Select a value:',
            options: [
                {value: true, display: 'True'},
                {value: false, display: 'False'}
            ],
            defaultValue: currentValue,
            confirmActionName: 'Apply Filter',
            allowEmpty: true
        });

        if (result === null) {
            return; // Dialog was cancelled
        }

        if (result === undefined) {
            this.clearFilterKey(filterKey);
        } else {
            this.setFilterKey(filterKey, result);
        }
    }

    private async openOptionsFilterDialog(): Promise<void> {
        const filter = this.filter();
        if (!filter.options || filter.options.length === 0) {
            return;
        }

        const filterKey = `${filter.filterName}__in`;
        const currentValues = this.getFilterValue(filterKey) || [];

        const options = filter.options.map(option => ({
            value: option,
            display: option,
            isChecked: currentValues.includes(option)
        }));

        const result = await this.dialogService.getValuesFromMultipleSelectionDialog({
            title: `Filter by ${filter.displayName}`,
            text: 'Select one or more options:',
            options: options,
            confirmActionName: 'Apply Filter',
            allowEmpty: true
        });

        if (result === null) {
            return; // Dialog was cancelled
        }

        if (result.length === 0) {
            this.clearFilterKey(filterKey);
        } else {
            this.setFilterKey(filterKey, result);
        }
    }

    private async openNumberFilterDialog(): Promise<void> {
        const filter = this.filter();
        const minFilterKey = `${filter.filterName}__gte`;
        const maxFilterKey = `${filter.filterName}__lte`;

        const currentMinValue = this.getFilterValue(minFilterKey) || null;
        const currentMaxValue = this.getFilterValue(maxFilterKey) || null;

        const result = await this.dialogService.getRangeFromRangeDialog({
            title: `Filter by ${filter.displayName}`,
            text: 'Enter a range of values:',
            minLabel: 'Minimum Value',
            maxLabel: 'Maximum Value',
            defaultMinValue: currentMinValue,
            defaultMaxValue: currentMaxValue,
            confirmActionName: 'Apply Filter',
            allowEmpty: true
        });

        if (result === null) {
            return; // Dialog was cancelled
        }

        // Handle min value
        if (result.min === null) {
            this.clearFilterKey(minFilterKey, false);
        } else {
            this.setFilterKey(minFilterKey, result.min, false);
        }

        // Handle max value
        if (result.max === null) {
            this.clearFilterKey(maxFilterKey, false);
        } else {
            this.setFilterKey(maxFilterKey, result.max, false);
        }

        // Fetch data with both filters applied
        this.paginatedDataHandler().fetch();
    }

    clearFilter(): void {
        const filter = this.filter();

        if (!filter) {
            return;
        }

        switch (filter.filterType) {
            case 'text':
                this.clearFilterKey(`${filter.filterName}__icontains`);
                break;
            case 'boolean':
                this.clearFilterKey(filter.filterName);
                break;
            case 'options':
                this.clearFilterKey(`${filter.filterName}__in`);
                break;
            case 'number':
                this.clearFilterKey(`${filter.filterName}__gte`, false);
                this.clearFilterKey(`${filter.filterName}__lte`);
                break;
        }
    }
}
