

export interface PaginationInput {
    query?: {
        page?: number;
        page_size?: number;
        order_by?: string[];
    }
}
