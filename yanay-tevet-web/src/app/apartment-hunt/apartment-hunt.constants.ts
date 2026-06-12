import {ContactMethod, Currency, ProjectStatus, ProspectStatus} from '../../generated-files/api/apartment-hunt';

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

export const PROJECT_STATUS_LABELS: Record<ProjectStatus, string> = {
  active: 'Active',
  finished: 'Finished',
};

export const PROSPECT_STATUS_LABELS: Record<ProspectStatus, string> = {
  saw: 'Saw',
  contacted: 'Contacted',
  waiting_for_invitation: 'Waiting for invitation',
  saw_waiting_for_them: 'Saw — awaiting them',
  need_to_decide: 'Need to decide',
  declined: 'Declined',
  accepted: 'Accepted',
  signed: 'Signed',
};

export const PROSPECT_STATUS_ORDER: ProspectStatus[] = [
  'saw',
  'contacted',
  'waiting_for_invitation',
  'saw_waiting_for_them',
  'need_to_decide',
  'declined',
  'accepted',
  'signed',
];

export const CONTACT_METHOD_LABELS: Record<ContactMethod, string> = {
  facebook: 'Facebook',
  whatsapp: 'WhatsApp',
  phone: 'Phone',
  email: 'Email',
  agency: 'Agency',
  other: 'Other',
};

export const CONTACT_METHOD_ORDER: ContactMethod[] = [
  'whatsapp',
  'phone',
  'facebook',
  'email',
  'agency',
  'other',
];

export const CURRENCY_ORDER: Currency[] = ['nis', 'usd', 'eur', 'gbp'];

export const LIKED_LEVELS = [1, 2, 3, 4, 5];

export const LIKED_OPTIONS: {value: number; label: string}[] = [
  {value: 1, label: '★☆☆☆☆'},
  {value: 2, label: '★★☆☆☆'},
  {value: 3, label: '★★★☆☆'},
  {value: 4, label: '★★★★☆'},
  {value: 5, label: '★★★★★'},
];

