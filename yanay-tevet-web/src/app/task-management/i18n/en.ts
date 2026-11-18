import {TaskPriority, TaskStatus} from '../../../generated-files/api/task-management';
import {PluralForms} from '../../shared/i18n/strings';

// Strings for Task Management. This file is the contract: every other language's file is typed against it.
export const en = {
  error: 'Error',
  cancel: 'Cancel',
  save: 'Save',
  back: 'Back',
  loadError: 'Could not load this project. You may not have access to it.',
  priorities: {
    none: 'No priority',
    low: 'Low',
    medium: 'Medium',
    high: 'High',
    urgent: 'Urgent',
  } satisfies Record<TaskPriority, string>,
  statuses: {
    todo: 'To do',
    in_progress: 'In progress',
    done: 'Done',
  } satisfies Record<TaskStatus, string>,

  // Repeating tasks
  repeat: {
    daily: 'Daily',
    weekends: 'Weekends',
    // A run of weekdays, e.g. "Sun–Thu".
    dayRange: '{from}–{to}',
    everyDay: 'Every day',
    workDays: 'Work days',
    weekend: 'Weekend',
    resetsDaily: 'Resets to “To do” every day at {time}.',
    resetsOnDays: 'Resets to “To do” at {time} every {days}.',
    tooltip: 'Resets to “To do” at {time}',
  },

  // Projects list
  list: {
    title: 'Task Management',
    subtitle: 'Projects, tasks and subtasks — with due dates, priorities and sharing.',
    projectsCount: {one: '{count} project', other: '{count} projects'} as PluralForms,
    openTasksCount: {one: '{count} open task', other: '{count} open tasks'} as PluralForms,
    // Shown under a large number, so it has no {count}.
    openTasksLabel: {one: 'open task', other: 'open tasks'} as PluralForms,
    membersCount: {one: '{count} member', other: '{count} members'} as PluralForms,
    tasksCount: {one: '{count} task', other: '{count} tasks'} as PluralForms,
    newProject: 'New project',
    loading: 'Loading projects',
    emptyTitle: 'Start your first project',
    emptyText: 'A project holds tasks and subtasks, with due dates, priorities and the people you share it with.',
    allDone: 'All done',
    noTasksYet: 'No tasks yet',
    archived: 'Archived',
  },

  // New / edit project
  form: {
    editTitle: 'Edit project',
    newTitle: 'New project',
    subtitle: 'A project groups related tasks together.',
    loading: 'Loading project',
    name: 'Name',
    namePlaceholder: 'Trip to Japan',
    description: 'Description',
    descriptionPlaceholder: 'What this project is about, and anything worth remembering',
    saving: 'Saving…',
    saveChanges: 'Save changes',
    create: 'Create project',
    saveFailed: 'Failed to save project: {error}',
  },

  // Project page
  detail: {
    allProjects: 'All projects',
    backToProjects: 'Back to projects',
    loading: 'Loading project',
    noTasksYet: 'No tasks yet',
    progress: '{done} of {total} done · {pct}%',
    archived: 'Archived',
    share: 'Share',
    edit: 'Edit',
    moreActions: 'More project actions',
    archive: 'Archive',
    unarchive: 'Unarchive',
    deleteProject: 'Delete project',
    tasksDone: 'Tasks done',
    newTask: 'New task',
    addTaskPlaceholder: 'Add a task',
    add: 'Add',
    everythingDone: 'Everything is done',
    emptyText: 'Add a task above. Tick its box when it’s done; open it to set a due date, priority, subtasks or a linked list.',
    completed: 'Completed ({count})',
    subtaskPlaceholder: 'Subtask name',
    newSubtask: 'New subtask',
    dragToReorder: 'Drag to reorder',
    markDone: 'Mark as done',
    markNotDone: 'Mark as not done',
    dueOverdue: '{date} · overdue',
    subtasksDone: '{done} of {total} subtasks done',
    addSubtask: 'Add subtask',
    editTask: 'Edit task',
    delete: 'Delete',
    deleteTask: 'Delete task',
    taskActions: 'Task actions',
    deleteTaskConfirm: 'Delete “{name}”?',
    deleteTaskWithSubtasks: {
      one: 'Delete “{name}” and its {count} subtask?',
      other: 'Delete “{name}” and its {count} subtasks?',
    } as PluralForms,
    shareTitle: 'Share project',
    shareSubtitle: 'People you add can view and edit this project and its tasks.',
    deleteProjectText: 'This permanently deletes the project and all of its tasks. This cannot be undone.',
    projectName: 'Project name',
  },

  // Task dialog
  dialog: {
    close: 'Close',
    name: 'Name',
    namePlaceholder: 'e.g. Book flights',
    description: 'Description',
    descriptionPlaceholder: 'Optional notes about this task…',
    status: 'Status',
    priority: 'Priority',
    dueDate: 'Due date',
    repeat: 'Repeat',
    repeats: 'Repeats · {days}',
    doesNotRepeat: 'Does not repeat',
    linkedList: 'Linked itinerary list',
    none: 'None',
  },
};

export type TasksStrings = typeof en;
