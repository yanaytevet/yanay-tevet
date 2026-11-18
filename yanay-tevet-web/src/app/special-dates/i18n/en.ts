import {CalendarType, SpecialDateCategory} from '../../../generated-files/api/special-dates';
import {PluralForms} from '../../shared/i18n/strings';

// The Hebrew months, keyed by their ICU English names (see hebrew-dates.ts). Adar is "adar" in a regular
// year; a leap year has "adarI" and "adarII".
export type HebrewMonthKey =
  'tishri' | 'heshvan' | 'kislev' | 'tevet' | 'shevat' | 'adar' | 'adarI' | 'adarII'
  | 'nisan' | 'iyar' | 'sivan' | 'tamuz' | 'av' | 'elul';

export interface SpecialDateCategoryStrings {
  label: string;
  nameLabel: string;
  namePlaceholder: string;
  // How the event reads with its name: '{name}' is the name the user typed.
  nameTemplate: string;
}

// Strings for the Special Dates app. This file is the contract: every other language's file is typed against it.
export const en = {
  categories: {
    birthday: {label: 'Birthday', nameLabel: 'Whose birthday?', namePlaceholder: 'Grandma Ellie', nameTemplate: '{name}’s birthday'},
    anniversary: {label: 'Anniversary', nameLabel: 'Whose anniversary?', namePlaceholder: 'Dan and Ruth', nameTemplate: '{name}’s anniversary'},
    memorial: {label: 'Memorial', nameLabel: 'In memory of?', namePlaceholder: 'Grandpa Moshe', nameTemplate: 'Memorial for {name}'},
    other: {label: 'Other', nameLabel: 'Event name', namePlaceholder: 'Family reunion day', nameTemplate: '{name}'},
  } as Record<SpecialDateCategory, SpecialDateCategoryStrings>,
  calendarChips: {
    hebrew: 'Hebrew date',
    gregorian: 'Gregorian date',
  } as Record<CalendarType, string>,

  // A Hebrew-calendar date outside Hebrew: '{day}', '{month}' (a name below) and '{year}' (e.g. 5787).
  hebrewDateFormat: '{day} {month} {year}',
  hebrewMonths: {
    tishri: 'Tishrei',
    heshvan: 'Cheshvan',
    kislev: 'Kislev',
    tevet: 'Tevet',
    shevat: 'Shevat',
    adar: 'Adar',
    adarI: 'Adar I',
    adarII: 'Adar II',
    nisan: 'Nisan',
    iyar: 'Iyar',
    sivan: 'Sivan',
    tamuz: 'Tammuz',
    av: 'Av',
    elul: 'Elul',
  } as Record<HebrewMonthKey, string>,

  // How far off an upcoming event is
  today: 'Today',
  tomorrow: 'Tomorrow',
  dayAfterTomorrow: 'In 2 days',
  inDays: {one: 'In {count} day', other: 'In {count} days'} as PluralForms,

  // What the event marks this time
  years: {
    birthday: {other: 'Turns {count}'} as PluralForms,
    anniversary: {one: '{count} year married', other: '{count} years married'} as PluralForms,
    memorial: {one: '{count} year since passing', other: '{count} years since passing'} as PluralForms,
    other: {one: '{count} year', other: '{count} years'} as PluralForms,
  },

  // Shared
  cancel: 'Cancel',
  close: 'Close',
  save: 'Save',
  edit: 'Edit',
  delete: 'Delete',
  error: 'Error',
  loading: 'Loading',
  newCalendar: 'New calendar',
  calendarName: 'Calendar name',
  eventsCount: {one: '{count} event', other: '{count} events'} as PluralForms,
  membersCount: {one: '{count} member', other: '{count} members'} as PluralForms,

  // Creating a calendar
  createCalendar: {
    text: 'For example “Family” or “Work friends”. You can share it once it’s created.',
    confirm: 'Create',
    failed: 'Couldn’t create the calendar.',
  },

  // The main page
  page: {
    title: 'Special Dates',
    share: 'Share',
    calendarsAndSharing: 'Calendars & sharing',
    newEvent: 'New event',
    loadError: 'Couldn’t load your dates. Try refreshing the page.',
    manageCalendars: 'Manage calendars',
    tabUpcoming: 'Next two weeks',
    tabAll: 'All events',
    hiddenHere: 'Not shown here: {names}',
    change: 'Change',
    loadingEvents: 'Loading events',
    noEventsYet: 'No events yet',
    emptyIntro: 'Add birthdays, anniversaries and memorials, and we’ll remind you in time — by both the Hebrew and the Gregorian date.',
    addFirstEvent: 'Add your first event',
    upcomingEmptyTitle: {one: 'No events in the next {count} day', other: 'No events in the next {count} days'} as PluralForms,
    upcomingEmptyText: 'You can see them all under “All events”.',
    todayHeading: 'Today',
    later: 'Later',
    searchPlaceholder: 'Search by name or description…',
    searchLabel: 'Search events',
    allCalendars: 'All calendars',
    noMatches: 'No matching events',
    noMatchesText: 'Try a different search, or clear the filter.',
    todaySubtitle: 'Today is {hebrew} · {gregorian}',
    defaultSubtitle: 'Birthdays, anniversaries and memorials — on the Hebrew and Gregorian calendars.',
    nextHebrew: 'Hebrew: {date}',
    nextGregorian: 'Gregorian: {date}',
    nextLine: 'Next: {dates}',
    afterSunset: 'after sunset',
    betweenSunsetAndMidnight: 'between sunset and midnight',
    addedBy: 'Added by {name}',
    noReminder: 'No reminder',
    deleteTitle: 'Delete event',
    deleteText: 'Delete “{name}”?',
    deleteTextShared: 'Delete “{name}”? It will also be deleted for everyone else in the calendar.',
    deleteFailed: 'Couldn’t delete it. Try again.',
  },

  // Adding or editing an event
  dialog: {
    titleNew: 'New event',
    titleEdit: 'Edit event',
    add: 'Add',
    whichCalendar: 'Which calendar?',
    eventType: 'Event type',
    previewLabel: 'Shows as:',
    nameHint: 'Just the name — the event type is already chosen above.',
    eventDate: 'Date',
    hebrewDate: 'Hebrew date',
    hebrewDateExample: 'e.g. 26 Tishrei',
    gregorianDate: 'Gregorian date',
    gregorianDateExample: 'e.g. October 11',
    day: 'Day',
    month: 'Month',
    year: 'Year',
    betweenSunsetAndMidnight: 'Between sunset and midnight',
    betweenSunsetAndMidnightHint: '(on the Gregorian calendar it was still the previous day)',
    afterSunset: 'After sunset',
    afterSunsetHint: '(the Hebrew day starts at sunset)',
    onGregorianCalendar: 'Gregorian date:',
    onHebrewCalendar: 'Hebrew date:',
    pickDate: 'Pick a date',
    reminders: 'Reminders',
    remindHebrew: 'Remind me by the Hebrew date',
    remindGregorian: 'Remind me by the Gregorian date',
    noRemindersWarning: 'Without a reminder, the event stays in the list but won’t appear in upcoming events.',
    invalidDate: 'That date isn’t valid.',
    saveFailed: 'Couldn’t save. Try again.',
  },

  // Sharing one calendar
  share: {
    title: 'Share calendar',
    joinLink: 'Join link',
    joinLinkHint: 'Anyone who gets the link can see and edit the events in this calendar.',
    copied: 'Copied!',
    copyLink: 'Copy link',
    sendWhatsapp: 'Send on WhatsApp',
    resetLink: 'Reset link',
    inviteLabel: 'Invite by email or username',
    invite: 'Invite',
    onlyOwnerInvites: 'Only the calendar’s owner ({name}) can invite more people.',
    members: 'Members',
    you: '(you)',
    owner: 'Owner',
    removeFromCalendar: 'Remove from calendar',
    awaitingSignup: 'Awaiting sign-up',
    whatsappText: 'Join the “{name}” dates calendar — birthdays, anniversaries and memorials on the Hebrew and Gregorian calendars:\n{url}',
    resetText: 'The current link will stop working, and anyone who already joined stays in the calendar. Continue?',
    resetConfirm: 'Reset',
    inviteFailed: 'Couldn’t send the invite. Try again.',
    added: 'Added to the calendar.',
    invitedByEmail: 'Invite sent by email — they’ll join automatically when they sign up.',
    removeText: 'Remove {name} from the calendar? The events they added stay in it.',
    removeConfirm: 'Remove',
  },

  // Managing calendars
  calendars: {
    title: 'My calendars',
    share: 'Share',
    members: 'Members',
    showInUpcoming: 'Show in upcoming events',
    moveHere: 'Move events here',
    rename: 'Rename',
    deleteCalendar: 'Delete calendar',
    leave: 'Leave calendar',
    onlyYou: 'Just you',
    ownedBy: 'Owned by {name}',
    renameTitle: 'Rename calendar',
    renameFailed: 'Couldn’t rename the calendar.',
    deleteText: {
      one: 'Delete “{name}” and its {count} event? This can’t be undone.',
      other: 'Delete “{name}” and all {count} events in it? This can’t be undone.',
    } as PluralForms,
    deleteTextShared: {
      one: 'Delete “{name}” and its {count} event? It will be deleted for all its members too. This can’t be undone.',
      other: 'Delete “{name}” and all {count} events in it? It will be deleted for all its members too. This can’t be undone.',
    } as PluralForms,
    deleteFailed: 'Couldn’t delete the calendar.',
    leaveText: 'Leave “{name}”? Its events stay for the other members. You can come back with the join link.',
    leaveConfirm: 'Leave',
    leaveFailed: 'Couldn’t leave the calendar.',
  },

  // Moving events into a calendar
  move: {
    title: 'Move events',
    titleAfterJoin: 'You joined the calendar! 🎉',
    afterJoinEmpty: 'The events in “{name}” now show up for you.',
    nothingToMove: 'None of your calendars have events that can be moved to this one.',
    great: 'Great',
    intro: 'Want to move events from your calendars into “{name}”? Then everyone in the calendar will see them. Events that seem to be there already aren’t selected.',
    deselectAll: 'Deselect all',
    selectAll: 'Select all',
    alreadyThere: 'Already in the calendar',
    notNow: 'Not now',
    moveCount: {one: 'Move {count} event', other: 'Move {count} events'} as PluralForms,
    moveFailed: 'Couldn’t move them. Try again.',
  },

  // The join page for a shared link
  join: {
    loadingInvite: 'Loading the invite',
    invalidLink: 'This link isn’t valid. The calendar’s owner may have reset it — ask them for a new one.',
    invitesYou: '{name} invited you to a calendar',
    description: 'Birthdays, anniversaries and memorials — on the Hebrew and Gregorian calendars, with reminders for the next two weeks.',
    loading: 'Loading…',
    joinCalendar: 'Join calendar',
    signInAndJoin: 'Sign in or sign up, and join',
    returnHere: 'Once you sign in, we’ll bring you back here.',
    joinFailed: 'Couldn’t join. Try again.',
  },
};

export type SpecialDatesStrings = typeof en;
