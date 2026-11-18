import {PluralForms} from '../../shared/i18n/strings';

// Strings for the shared building blocks every app uses: the common dialogs' default buttons and validation
// messages, page states, menus, tabs, the share dialog, the paginated table and the parts of the layout the
// chrome strings don't cover. This file is the contract: every other language's file is typed against it.
export const en = {
  // Default dialog buttons, used when the caller passes none
  cancel: 'Cancel',
  submit: 'Submit',
  confirm: 'Confirm',
  ok: 'OK',
  apply: 'Apply',
  copy: 'Copy',
  done: 'Done',
  close: 'Close',

  // Dialog fields
  filterOptions: 'Filter options…',
  other: 'Other',
  enterValue: 'Enter value…',
  minimumValue: 'Minimum value',
  maximumValue: 'Maximum value',
  typeToConfirm: 'Type “{text}” below to confirm',

  // Validation messages
  errors: {
    required: 'This field is required',
    atLeast: 'Value must be at least {min}',
    atMost: 'Value must be at most {max}',
    maxLength: {
      one: 'Maximum length is {count} character',
      other: 'Maximum length is {count} characters',
    } as PluralForms,
    invalidRange: 'The minimum must be less than or equal to the maximum',
    selectOption: 'Please select an option',
    selectAtLeastOne: 'Please select at least one option',
  },

  // Share dialog
  share: {
    usernameOrEmail: 'Username or email',
    add: 'Add',
    peopleWithAccess: 'People with access',
    owner: 'Owner',
    collaborator: 'Collaborator',
    pendingInvitations: 'Pending invitations',
    invited: 'Invited',
    remove: 'Remove {name}',
    couldNotShare: 'Could not share',
    couldNotRemove: 'Could not remove',
  },

  // Page states, menus, inputs and tabs
  loading: 'Loading',
  back: 'Back',
  moreActions: 'More actions',
  noValue: 'No value',
  scrollTabsLeft: 'Scroll tabs left',
  scrollTabsRight: 'Scroll tabs right',

  // New-version banner
  newVersion: 'A new version is available',
  refresh: 'Refresh',
  dismiss: 'Dismiss',

  // Paginated table and its column filters
  table: {
    unavailable: 'Table view temporarily unavailable — library update in progress.',
    filter: 'Filter',
    clearFilter: 'Clear filter',
    filterBy: 'Filter by {name}',
    enterText: 'Enter text to filter by:',
    selectValue: 'Select a value:',
    selectOptions: 'Select one or more options:',
    enterRange: 'Enter a range of values:',
    applyFilter: 'Apply filter',
    yes: 'Yes',
    no: 'No',
  },

  // Layout: the top bar and the right panel
  homeLink: 'Yanay Tevet — Home',
  menu: 'Menu',
  closePanel: 'Close panel',
};

export type CommonStrings = typeof en;
