import {ItemStatus, ListStatus, TaskStatus} from '../../../generated-files/api/itinerary-lists';
import {PluralForms} from '../../shared/i18n/strings';

// Strings for Itinerary Lists. This file is the contract: every other language's file is typed against it.
export const en = {
  error: 'Error',
  cancel: 'Cancel',
  save: 'Save',
  back: 'Back',
  loadError: 'Could not load this list. You may not have access to it.',
  itemStatuses: {
    need_to_buy: 'Need to buy',
    in_the_house: 'In the house',
    ready: 'Ready',
    in_the_car: 'In the car',
  } satisfies Record<ItemStatus, string>,
  taskStatuses: {
    to_do: 'To do',
    done: 'Done',
  } satisfies Record<TaskStatus, string>,
  listStatuses: {
    standby: 'Standby',
    active: 'Active',
  } satisfies Record<ListStatus, string>,
  itemsCount: {one: '{count} item', other: '{count} items'} as PluralForms,
  tasksCount: {one: '{count} task', other: '{count} tasks'} as PluralForms,
  membersCount: {one: '{count} member', other: '{count} members'} as PluralForms,

  // Lists page
  lists: {
    title: 'Itinerary Lists',
    subtitle: 'Reusable packing & prep lists. Activate one when you head out.',
    newList: 'New list',
    loading: 'Loading lists',
    emptyTitle: 'Start your first list',
    emptyText: 'Write down what to pack and prepare once, then activate the list each time you head out.',
  },

  // New / edit list
  form: {
    editTitle: 'Edit list',
    newTitle: 'New list',
    subtitle: 'A reusable list of things to pack and prepare for a trip or outing.',
    loading: 'Loading list',
    name: 'Name',
    namePlaceholder: 'e.g. Beach day, Camping trip',
    description: 'Description',
    descriptionPlaceholder: 'What is this list for? Any notes…',
    saving: 'Saving…',
    saveChanges: 'Save changes',
    create: 'Create list',
    saveFailed: 'Failed to save list: {error}',
  },

  // List page
  detail: {
    allLists: 'All lists',
    backToLists: 'Back to lists',
    loading: 'Loading list',
    finish: 'Finish',
    activate: 'Activate',
    share: 'Share',
    moreActions: 'More list actions',
    editList: 'Edit list',
    deleteList: 'Delete list',
    // A status chip, e.g. "3 Need to buy".
    statusCount: '{count} {status}',
    tasksDone: {one: '{count} task done', other: '{count} tasks done'} as PluralForms,
    tasksToDo: {one: '{count} task to do', other: '{count} tasks to do'} as PluralForms,
    addItem: 'Add an item',
    itemPlaceholder: 'e.g. Sunscreen, Beach towel',
    add: 'Add',
    statusHint: 'Tap a status to move it forward · long-press (or right-click) to pick any status.',
    itemsEmpty: 'Add what to pack or buy above, then tap its status as you go.',
    edit: 'Edit',
    editItem: 'Edit item',
    delete: 'Delete',
    deleteItem: 'Delete item',
    tasks: 'Tasks',
    addTask: 'Add a task',
    taskPlaceholder: 'e.g. Book parking, Confirm reservation',
    tasksEmpty: 'Add anything to sort out before you go, like booking parking.',
    markDone: 'Mark as done',
    markNotDone: 'Mark as not done',
    editTask: 'Edit task',
    deleteTask: 'Delete task',
    setStatus: 'Set status',
    set: 'Set',
    deleteConfirm: 'Delete “{name}”?',
    finishTitle: 'Finish list',
    finishText: 'Finish this list and return it to standby? Items that are not “Need to buy” will be set back to “In the house”.',
    shareTitle: 'Share list',
    shareSubtitle: 'People you add can view and edit this list and its items.',
    deleteListText: 'This permanently deletes the list and all of its items. This cannot be undone.',
    listName: 'List name',
  },

  // Item / task dialog
  dialog: {
    close: 'Close',
    name: 'Name',
    itemPlaceholder: 'e.g. Sunscreen',
    taskPlaceholder: 'e.g. Book parking',
    description: 'Description',
    itemNotesPlaceholder: 'Optional notes about this item…',
    taskNotesPlaceholder: 'Optional notes about this task…',
  },
};

export type ItineraryStrings = typeof en;
