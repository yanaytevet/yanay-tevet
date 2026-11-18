import {PluralForms} from '../../shared/i18n/strings';

// Dream diary strings. This file is the contract: every other language's file is typed against it.
export const en = {
  // Diary page
  title: 'Dream Diary',
  subtitleEmpty: 'Capture your dreams before they fade.',
  entryCount: {one: '{count} entry', other: '{count} entries'} as PluralForms,
  newEntry: 'New entry',
  lastFourWeeks: 'Last 4 Weeks',
  loadingDreams: 'Loading dreams',
  emptyTitle: 'Log your first dream',
  emptyText: 'Write it down as soon as you wake up, before it fades.',
  generateImage: 'Generate image with AI',
  generating: 'Generating…',
  uploadImage: 'Upload image',
  uploading: 'Uploading…',
  editEntry: 'Edit entry',
  deleteEntry: 'Delete entry',
  viewImage: 'View image',
  dreamImage: 'Dream image',
  close: 'Close',
  loading: 'Loading…',
  loadMore: 'Load More',
  deleteTitle: 'Delete Entry',
  deleteText: 'Are you sure you want to delete this dream diary entry?',
  delete: 'Delete',
  cancel: 'Cancel',
  error: 'Error',
  deleteFailed: 'Failed to delete entry: {error}',
  uploadFailed: 'Failed to upload image: {error}',
  generateFailed: 'Failed to generate image: {error}',

  // New / edit entry page
  form: {
    backToDiary: 'Back to diary',
    editTitle: 'Edit dream',
    newTitle: 'New dream',
    editSubtitle: 'Update the details of this dream.',
    newSubtitle: 'Capture it before it fades.',
    loadingDream: 'Loading dream',
    loadFailed: 'Could not load this dream. It may have been deleted.',
    dream: 'Dream',
    dreamPlaceholder: 'Describe your dream in as much detail as you can remember...',
    dateTime: 'Date & Time',
    dateTimeAria: 'Date and time',
    savingEdit: 'Blaming your mother...',
    savingNew: 'Consulting Freud...',
    saveChanges: 'Save Changes',
    saveDream: 'Save Dream',
    saveFailed: 'Failed to save dream: {error}',
  },
};

export type DreamDiaryStrings = typeof en;
