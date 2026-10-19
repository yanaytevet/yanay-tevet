export interface Action {
  display: string;
  icon?: string;
  disabled?: boolean;
  // Destructive: shown in the danger colour.
  danger?: boolean;
  callback: () => void;
}
