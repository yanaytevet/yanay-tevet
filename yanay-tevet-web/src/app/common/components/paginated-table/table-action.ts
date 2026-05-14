export interface TableAction {
  display: string;
  icon?: string;
  callback: (item: any) => void;
}
