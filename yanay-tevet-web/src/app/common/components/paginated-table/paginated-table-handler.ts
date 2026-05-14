import {PaginatedData} from './paginated-data';
import {BehaviorSubject, Subscription} from 'rxjs';
import {PaginationInput} from './pagination-input';
import {computed, signal} from '@angular/core';
import {CallbacksDebouncer} from '../../data/callbacks-debouncer';
import {deleteNested, getAllNestedKeys, getNested, setNested} from '../../util-functions/nested-objects-utils';

type SortDirection = 'asc' | 'desc';

interface SortObject {
    direction: SortDirection;
    key: string;
}

export class PaginatedTableHandler<T, S extends PaginationInput> {
    currentPage = 0;
    pageSize = 25;
    isEmpty = true;
    filterObject: Record<string, any> = {};
    filterSignal = signal<Record<string, any>>({});
    filterKeysSignal = computed<string[]>(() => {
        return getAllNestedKeys(this.filterSignal());
    });
    dictFilterSignal = signal<Record<string, any>>({});
    dictFilterKeysSignal = computed<string[]>(() => {
        return getAllNestedKeys(this.dictFilterSignal());
    });

    private _sortObjectsArray: SortObject[] = [];
    sortObjectsArraySignal = signal<SortObject[]>([]);
    fetchesDebouncer = new CallbacksDebouncer();
    isLoading = signal<boolean>(false);

    private readonly _paginationDataSub = new BehaviorSubject<PaginatedData<T>>(null);
    readonly paginationData$ = this._paginationDataSub.asObservable();
    readonly paginationDataSignal = signal<PaginatedData<T>>(null);
    readonly itemsSignal = computed<T[]>(() => this.paginationDataSignal()?.data || []);

    sub: Subscription;

    public get paginationData(): PaginatedData<T> {
        return this._paginationDataSub.getValue();
    }

    public set paginationData(val: PaginatedData<T>) {
        this._paginationDataSub.next(val);
        this.isEmpty = !val || (val.page_size === 0 && val.pages_amount === 0);
    }

    constructor(private fetchPaginatedData: (val: S) => Promise<PaginatedData<T>>) {
        this.sub = this.paginationData$.subscribe((val: PaginatedData<T>) => {
            this.paginationDataSignal.set(val);
        });
    }

    private updateFilterSignal(): void {
        this.filterSignal.set({...this.filterObject});
    }

    public async fetch(): Promise<void> {
        this.fetchesDebouncer.run(async () => {
            this.isLoading.set(true);
            this.currentPage = Math.min(this.currentPage, this.paginationData?.pages_amount - 1 || 0);
            this.currentPage = Math.max(this.currentPage, 0);
            this.paginationData = await this.fetchPaginatedData(this.getData());
            this.isLoading.set(false);
        });
    }

    public getData(): S {
        // @ts-ignore
        return {
            query: {
                page: this.currentPage,
                page_size: this.pageSize,
                order_by: this.getSortArray(),
                ...this.filterObject,
                dict_filter: JSON.stringify(this.dictFilterSignal())
            }
        }
    }

    public fetchPage(page: number, pageSize: number = undefined, fetch = true): void {
        this.currentPage = page;
        if (pageSize !== undefined) {
            this.pageSize = pageSize;
        }
        if (fetch) {
            this.fetch();
        }
    }

    clearAllFilter(fetch = true): void {
        this.filterObject = {};
        this.updateFilterSignal();
        if (fetch) {
            this.fetch();
        }
    }

    setFilter(key: string, value: any, fetch = true): void {
        this.filterObject[key] = value;
        this.updateFilterSignal();
        if (fetch) {
            this.fetch();
        }
    }

    clearFilter(key: string, fetch = true): void {
        delete this.filterObject[key];
        this.updateFilterSignal();
        if (fetch) {
            this.fetch();
        }
    }

    getFilterValue(key: string): any {
        return this.filterObject[key];
    }

    hasFilterValue(key: string): boolean {
        return key in this.filterObject;
    }

    clearAllDictFilter(fetch = true): void {
        this.dictFilterSignal.set({});
        if (fetch) {
            this.fetch();
        }
    }

    setDictFilter(key: string, value: any, fetch = true): void {
        const currentDictFilters = structuredClone(this.dictFilterSignal());
        setNested(currentDictFilters, key, value);
        this.dictFilterSignal.set(currentDictFilters);
        if (fetch) {
            this.fetch();
        }
    }

    clearDictFilter(key: string, fetch = true): void {
        const currentDictFilters = structuredClone(this.dictFilterSignal());
        deleteNested(currentDictFilters, key);
        this.dictFilterSignal.set(currentDictFilters);
        if (fetch) {
            this.fetch();
        }
    }

    getDictFilterValue(key: string): any {
        return getNested(this.dictFilterSignal(), key);
    }

    addSort(key: string, direction: SortDirection, fetch = true): void {
        this.clearSort(key, false);
        this._sortObjectsArray.push({key, direction});
        this.sortObjectsArraySignal.set([...this._sortObjectsArray]);
        if (fetch) {
            this.fetch();
        }
    }

    clearSort(key: string, fetch = true): void {
        this._sortObjectsArray = this._sortObjectsArray.filter(sort => sort.key !== key);
        this.sortObjectsArraySignal.set([...this._sortObjectsArray]);
        if (fetch) {
            this.fetch();
        }
    }

    clearAllSort(fetch = true): void {
        this._sortObjectsArray = [];
        this.sortObjectsArraySignal.set([]);
        if (fetch) {
            this.fetch();
        }
    }

    private getSortArray(): string[] {
        return this._sortObjectsArray.map(sort => `${sort.direction === 'asc' ? '' : '-'}${sort.key}`);
    }

    destroy() {
        this.sub.unsubscribe();
    }

    async updateValues(updatedItems: T[]) {
        this.paginationData = {...this.paginationData, data: updatedItems};
    }

    // State signal that contains the entire pagination state
    readonly stateSignal = computed<Record<string, any>>(() => {
        return {
            currentPage: this.currentPage,
            pageSize: this.pageSize,
            filterObject: this.filterObject,
            dictFilter: this.dictFilterSignal(),
            sortObjectsArray: this._sortObjectsArray
        };
    });

    readonly stateLowerCaseSignal = computed<Record<string, any>>(() => {
        return {
            current_page: this.currentPage,
            page_size: this.pageSize,
            filter_object: this.filterObject,
            dict_filter: this.dictFilterSignal(),
            sort_objects_array: this.sortObjectsArraySignal()
        };
    });

    setState(state: Record<string, any>, fetch = true): void {
        if (state['currentPage'] !== undefined) {
            this.currentPage = state['currentPage'];
        }

        if (state['pageSize'] !== undefined) {
            this.pageSize = state['pageSize'];
        }

        if (state['filterObject'] !== undefined) {
            this.filterObject = {...state['filterObject']};
            this.updateFilterSignal();
        }

        if (state['dictFilter'] !== undefined) {
            this.dictFilterSignal.set(state['dictFilter']);
        }

        if (state['sortObjectsArray'] !== undefined) {
            this._sortObjectsArray = [...state['sortObjectsArray']];
            this.sortObjectsArraySignal.set([...this._sortObjectsArray]);
        }

        if (fetch) {
            this.fetch();
        }
    }
}
