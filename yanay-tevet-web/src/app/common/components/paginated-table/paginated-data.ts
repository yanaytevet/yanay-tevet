
export interface PaginatedData<T> {
    total_amount: number;
    pages_amount: number;
    page: number;
    page_size: number;
    data: T[];
};
