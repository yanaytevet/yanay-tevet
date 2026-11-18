import {ContactMethod, Currency, ProspectStatus} from '../../generated-files/api/apartment-hunt';
import {Language} from '../../generated-files/api/users';

// Labels for these live in `i18n/`; this file keeps the order and the ISO codes.
export const CURRENCY_CODES: Record<Currency, string> = {
  nis: 'ILS',
  usd: 'USD',
  eur: 'EUR',
  gbp: 'GBP',
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

// An amount in the project's currency, in the site language's format ("₪3,500", "3.500 ₪").
export function moneyFormat(language: Language, currency: Currency): Intl.NumberFormat {
  return new Intl.NumberFormat(language, {
    style: 'currency',
    currency: CURRENCY_CODES[currency],
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  });
}

// A 'YYYY-MM-DD' date or an ISO timestamp, as local time ('YYYY-MM-DD' alone would parse as UTC midnight).
export function parseDate(value: string): Date {
  return new Date(value.length === 10 ? `${value}T00:00:00` : value);
}
