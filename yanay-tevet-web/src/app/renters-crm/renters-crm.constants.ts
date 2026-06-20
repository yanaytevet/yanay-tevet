import {Currency, FamilyStatus, ProjectStatus, RenterStatus} from '../../generated-files/api/renters-crm';

export const CURRENCY_SYMBOLS: Record<Currency, string> = {
  nis: '₪',
  usd: '$',
  eur: '€',
  gbp: '£',
};

export const CURRENCY_LABELS: Record<Currency, string> = {
  nis: 'NIS (₪)',
  usd: 'USD ($)',
  eur: 'EUR (€)',
  gbp: 'GBP (£)',
};

export const CURRENCY_ORDER: Currency[] = ['nis', 'usd', 'eur', 'gbp'];

export const PROJECT_STATUS_LABELS: Record<ProjectStatus, string> = {
  active: 'Active',
  finished: 'Finished',
};

export const RENTER_STATUS_LABELS: Record<RenterStatus, string> = {
  contacted: 'Contacted',
  scheduled_to_see: 'Scheduled to see',
  visited: 'Visited',
  declined: 'Declined',
  want_to_sign: 'Want to sign',
  signed: 'Signed',
};

export const RENTER_STATUS_ORDER: RenterStatus[] = [
  'contacted',
  'scheduled_to_see',
  'visited',
  'declined',
  'want_to_sign',
  'signed',
];

export const FAMILY_STATUS_LABELS: Record<FamilyStatus, string> = {
  family_with_children: 'Family with children',
  couple: 'Couple',
  single: 'Single',
};

export const FAMILY_STATUS_ORDER: FamilyStatus[] = ['family_with_children', 'couple', 'single'];
