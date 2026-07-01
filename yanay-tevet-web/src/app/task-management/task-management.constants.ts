import {TaskPriority} from '../../generated-files/api/task-management';

export const TASK_PRIORITY_LABELS: Record<TaskPriority, string> = {
  none: 'No priority',
  low: 'Low',
  medium: 'Medium',
  high: 'High',
  urgent: 'Urgent',
};

export const TASK_PRIORITY_ORDER: TaskPriority[] = ['none', 'low', 'medium', 'high', 'urgent'];

// Higher-priority tasks get a stronger accent. "none" renders without a badge.
export const TASK_PRIORITY_CHIP_CLASS: Record<TaskPriority, string> = {
  none: '',
  low: 'bg-layer-3 text-writing-minor',
  medium: 'bg-layer-3 text-notion-blue',
  high: 'bg-layer-3 text-notion-orange',
  urgent: 'bg-notion-red-bg text-notion-red',
};

// Repeating-task weekdays use JS Date.getDay() numbering: 0=Sunday .. 6=Saturday.
// The list order here (Sunday first) is also the display order in the UI.
export interface Weekday {
  value: number;
  short: string;
  label: string;
}

export const WEEKDAYS: Weekday[] = [
  {value: 0, short: 'Su', label: 'Sun'},
  {value: 1, short: 'Mo', label: 'Mon'},
  {value: 2, short: 'Tu', label: 'Tue'},
  {value: 3, short: 'We', label: 'Wed'},
  {value: 4, short: 'Th', label: 'Thu'},
  {value: 5, short: 'Fr', label: 'Fri'},
  {value: 6, short: 'Sa', label: 'Sat'},
];

export const REPEAT_PRESETS: {label: string; days: number[]}[] = [
  {label: 'Every day', days: []},
  {label: 'Work days', days: [0, 1, 2, 3, 4]},
  {label: 'Weekend', days: [5, 6]},
];

// Compact schedule label for chips/badges, e.g. "Daily", "Sun–Thu", "Wed, Fri".
export function formatRepeatDays(days: number[]): string {
  if (days.length === 0 || days.length === 7) {
    return 'Daily';
  }
  const sorted = [...days].sort((a, b) => a - b);
  const key = sorted.join(',');
  if (key === '0,1,2,3,4') {
    return 'Sun–Thu';
  }
  if (key === '5,6') {
    return 'Weekends';
  }
  return sorted.map(d => WEEKDAYS[d].label).join(', ');
}

// Full sentence used in the dialog, e.g. 'Resets to "To do" at 4 AM every Sun, Wed.'
export function describeRepeatSchedule(days: number[]): string {
  if (days.length === 0 || days.length === 7) {
    return 'Resets to "To do" every day at 4 AM.';
  }
  const list = [...days].sort((a, b) => a - b).map(d => WEEKDAYS[d].label).join(', ');
  return `Resets to "To do" at 4 AM every ${list}.`;
}
