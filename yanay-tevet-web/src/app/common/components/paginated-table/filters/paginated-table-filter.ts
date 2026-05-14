
export interface PaginatedTableFilter {
    filterName: string;
    displayName: string;
    filterType: 'text' | 'number' | 'boolean' | 'options';
    options?: string[];
    useDictFilter?: boolean;
}
