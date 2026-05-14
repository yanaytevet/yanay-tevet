export interface Action {
  display: string;
  icon?: string;
  disabled?: boolean;
  callback: () => void;
}
