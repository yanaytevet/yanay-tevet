import {Currency, FamilyStatus, RenterStatus} from '../../generated-files/api/renters-crm';
import {Language} from '../../generated-files/api/users';

// Labels for these live in `i18n/`; this file keeps the order and the ISO codes.
export const CURRENCY_CODES: Record<Currency, string> = {
  nis: 'ILS',
  usd: 'USD',
  eur: 'EUR',
  gbp: 'GBP',
};

export const CURRENCY_ORDER: Currency[] = ['nis', 'usd', 'eur', 'gbp'];

export const RENTER_STATUS_ORDER: RenterStatus[] = [
  'contacted',
  'scheduled_to_see',
  'visited',
  'declined',
  'want_to_sign',
  'signed',
];

export const FAMILY_STATUS_ORDER: FamilyStatus[] = ['family_with_children', 'couple', 'single'];

// An amount in the project's currency, in the site language's format ("₪3,500", "3.500 ₪").
export function moneyFormat(language: Language, currency: Currency): Intl.NumberFormat {
  return new Intl.NumberFormat(language, {
    style: 'currency',
    currency: CURRENCY_CODES[currency],
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  });
}
