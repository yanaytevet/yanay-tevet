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
