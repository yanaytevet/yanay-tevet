import {Language} from '../../../generated-files/api/users';

// A booking's dates ('YYYY-MM-DD', check-in to check-out) as one localized range, e.g. "Nov 18 – 21, 2026".
// Parsed as local midnight so the day never shifts with the time zone.
export function formatDateRange(language: Language, start: string, end: string): string {
  const format = new Intl.DateTimeFormat(language, {dateStyle: 'medium'});
  return format.formatRange(new Date(`${start}T00:00:00`), new Date(`${end}T00:00:00`));
}
