import {Currency, FamilyStatus, ProjectStatus, RenterStatus} from '../../../generated-files/api/renters-crm';
import {PluralForms} from '../../shared/i18n/strings';

// Strings for Renters CRM. This file is the contract: every other language's file is typed against it.
const currencies: Record<Currency, string> = {
  nis: 'NIS (₪)',
  usd: 'USD ($)',
  eur: 'EUR (€)',
  gbp: 'GBP (£)',
};

const projectStatuses: Record<ProjectStatus, string> = {
  active: 'Active',
  finished: 'Finished',
};

const renterStatuses: Record<RenterStatus, string> = {
  contacted: 'Contacted',
  scheduled_to_see: 'Scheduled to see',
  visited: 'Visited',
  declined: 'Declined',
  want_to_sign: 'Want to sign',
  signed: 'Signed',
};

const familyStatuses: Record<FamilyStatus, string> = {
  family_with_children: 'Family with children',
  couple: 'Couple',
  single: 'Single',
};

const members: PluralForms = {one: '{count} member', other: '{count} members'};

export const en = {
  currencies,
  projectStatuses,
  renterStatuses,
  familyStatuses,
  common: {
    back: 'Back',
    backToProject: 'Back to project',
    cancel: 'Cancel',
    delete: 'Delete',
    edit: 'Edit',
    error: 'Error',
    saving: 'Saving…',
    saveChanges: 'Save changes',
    status: 'Status',
    name: 'Name',
    notes: 'Notes',
    familyStatus: 'Family status',
    timeOfVisit: 'Time of visit',
    agreedRent: 'Agreed rent (monthly)',
    askingRent: 'Asking {amount}/mo',
    unnamed: 'Unnamed',
    members,
    loadProjectError: 'Could not load this project. You may not have access to it.',
  },
  list: {
    title: 'Renters CRM',
    subtitle: 'Track the renters who came to see your apartment.',
    newProject: 'New project',
    loading: 'Loading projects',
    emptyTitle: 'Start tracking renters',
    emptyText: 'A project holds the renters who come to see one apartment — their visit, family and where they stand.',
  },
  projectForm: {
    newTitle: 'New project',
    editTitle: 'Edit project',
    subtitle: 'A project groups the renters who came to see one apartment.',
    loading: 'Loading project',
    namePlaceholder: 'e.g. Allenby 12 — 2nd floor',
    description: 'Description',
    descriptionPlaceholder: 'The apartment you’re renting out, terms, must-haves for a renter…',
    currency: 'Currency',
    initialAskedRent: 'Initial asked rent (monthly)',
    create: 'Create project',
    saveFailed: 'Failed to save project: {error}',
  },
  detail: {
    allProjects: 'All projects',
    backToProjects: 'Back to projects',
    loading: 'Loading project',
    owner: 'Owner: {name}',
    share: 'Share',
    moreActions: 'More project actions',
    renters: 'Renters',
    addRenter: 'Add renter',
    emptyTitle: 'Add the first renter',
    emptyText: 'Note who came to see the apartment — when they visited, their family, and where they stand.',
    columns: {
      renter: 'Renter',
      status: 'Status',
      family: 'Family',
      visit: 'Visit',
      agreedRent: 'Agreed rent',
      saw: 'Saw',
      actions: 'Actions',
    },
    animals: 'animals',
    longTerm: 'long term',
    saw: 'saw',
    yes: 'Yes',
    editRenter: 'Edit renter',
    deleteRenter: 'Delete renter',
    editFullDetails: 'Edit full details',
    finish: 'Finish',
    reopen: 'Reopen',
    finishTitle: 'Finish project',
    reopenTitle: 'Reopen project',
    finishText: 'Mark this project as finished? You can reopen it later.',
    reopenText: 'Reopen this project and mark it active again?',
    deleteProject: 'Delete project',
    deleteProjectText: 'This permanently deletes the project and all of its renters. This cannot be undone.',
    projectName: 'Project name',
    shareTitle: 'Share project',
    shareSubtitle: 'People you add can view and edit this project’s renters.',
    deleteRenterText: 'Delete “{name}”?',
    thisRenter: 'this renter',
  },
  panel: {
    sawApartment: 'Saw apartment',
    yes: 'Yes',
    no: 'No',
    animals: 'Animals',
    hasAnimals: 'Has animals',
    noAnimals: 'No animals',
    term: 'Term',
    longTerm: 'Long term',
    notLongTerm: 'Not long term',
  },
  renterForm: {
    newTitle: 'New renter',
    editTitle: 'Edit renter',
    subtitle: 'Track who came to see the apartment and where they stand.',
    loading: 'Loading renter',
    loadError: 'Could not load this renter. It may have been deleted.',
    namePlaceholder: 'e.g. Dana & Yossi',
    visit: 'Visit',
    sawApartment: 'Saw the apartment',
    preferences: 'Preferences',
    hasAnimals: 'Has animals',
    longTerm: 'Long term',
    create: 'Create renter',
    saveFailed: 'Failed to save renter: {error}',
  },
};

export type RentersCrmStrings = typeof en;
