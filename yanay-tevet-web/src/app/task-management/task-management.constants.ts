import {TaskPriority, TaskStatus} from '../../generated-files/api/task-management';

export const TASK_STATUS_LABELS: Record<TaskStatus, string> = {
  todo: 'To do',
  in_progress: 'In progress',
  done: 'Done',
};

export const TASK_STATUS_ORDER: TaskStatus[] = ['todo', 'in_progress', 'done'];

// Tap-to-cycle advances forward and wraps back to the start.
export const TASK_STATUS_NEXT: Record<TaskStatus, TaskStatus> = {
  todo: 'in_progress',
  in_progress: 'done',
  done: 'todo',
};

export const TASK_STATUS_CHIP_CLASS: Record<TaskStatus, string> = {
  todo: 'bg-layer-3 text-writing-minor',
  in_progress: 'bg-layer-3 text-notion-blue',
  done: 'bg-layer-3 text-notion-green',
};

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
