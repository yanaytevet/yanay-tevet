import {PluralForms} from '../../shared/i18n/strings';

// Strings for Shopping Lists. This file is the contract: every other language's file is typed against it.
export const en = {
  error: 'Error',
  cancel: 'Cancel',
  save: 'Save',
  name: 'Name',

  // Lists page
  lists: {
    title: 'Shopping Lists',
    subtitle: 'Check things off as you shop — they’re one tap away next time.',
    newList: 'New list',
    loading: 'Loading lists',
    emptyTitle: 'Start your first list',
    emptyText: 'One for groceries, the pharmacy, or anything else you buy regularly. What you check off stays a tap away.',
    nothingToBuy: 'Nothing to buy',
    more: '+ {count} more',
    checkedCount: {one: '{count} checked', other: '{count} checked'} as PluralForms,
    shared: 'Shared',
    create: 'Create',
    createFailed: 'Failed to create list: {error}',
  },

  // List page
  detail: {
    allLists: 'All lists',
    backToLists: 'Back to lists',
    loading: 'Loading list',
    loadError: 'Could not load this list. You may not have access to it.',
    sharedBy: 'Shared by {name}',
    sharedWith: {one: 'Shared with {count} person', other: 'Shared with {count} people'} as PluralForms,
    share: 'Share',
    rename: 'Rename',
    moreActions: 'More list actions',
    deleteList: 'Delete list',
    addItem: 'Add item',
    emptyFirst: 'Add your first item above — what you check off stays here for next time.',
    allChecked: 'Everything’s checked off. Add what you need next above.',
    checkOff: 'Check off',
    edit: 'Edit',
    removeItem: 'Remove item',
    remove: 'Remove',
    checkedItems: {one: '{count} checked item', other: '{count} checked items'} as PluralForms,
    uncheck: 'Uncheck',
    removeFromHistory: 'Remove from history',
    showLess: 'Show less',
    showAll: 'Show all {count}',
    editItem: 'Edit item',
    renameList: 'Rename list',
    shareTitle: 'Share list',
    shareSubtitle: 'People you add can view, add and check off items. Invite someone new by email.',
    deleteListText: 'This permanently deletes the list, its items and its history for everyone it is shared with. This cannot be undone.',
    listName: 'List name',
  },
};

export type ShoppingStrings = typeof en;
