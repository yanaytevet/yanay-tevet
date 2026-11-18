import {CalendarType, SpecialDateCategory} from '../../generated-files/api/special-dates';
import {Language} from '../../generated-files/api/users';
import {fill, plural} from '../shared/i18n/strings';
import {HebrewMonthKey, SpecialDatesStrings} from './i18n';

export interface SpecialDateCategoryOption {
  value: SpecialDateCategory;
  emoji: string;
}

export const SPECIAL_DATE_CATEGORIES: SpecialDateCategoryOption[] = [
  {value: 'birthday', emoji: '🎂'},
  {value: 'anniversary', emoji: '💍'},
  {value: 'memorial', emoji: '🕯️'},
  {value: 'other', emoji: '📅'},
];

export const SPECIAL_DATE_CATEGORY_BY_VALUE: Record<SpecialDateCategory, SpecialDateCategoryOption> =
  Object.fromEntries(SPECIAL_DATE_CATEGORIES.map(c => [c.value, c])) as Record<SpecialDateCategory, SpecialDateCategoryOption>;

export const CALENDAR_CHIP_CLASSES: Record<CalendarType, string> = {
  hebrew: 'calendar-chip-hebrew',
  gregorian: 'chip-info',
};

type DateFormatKind = 'long' | 'full' | 'fullWithWeekday';

const DATE_FORMAT_OPTIONS: Record<DateFormatKind, Intl.DateTimeFormatOptions> = {
  long: {weekday: 'long', day: 'numeric', month: 'long'},
  full: {day: 'numeric', month: 'long', year: 'numeric'},
  fullWithWeekday: {weekday: 'long', day: 'numeric', month: 'long', year: 'numeric'},
};

const dateFormats = new Map<string, Intl.DateTimeFormat>();

function dateFormat(language: Language, kind: DateFormatKind): Intl.DateTimeFormat {
  const key = `${language}|${kind}`;
  let format = dateFormats.get(key);
  if (!format) {
    format = new Intl.DateTimeFormat(language, DATE_FORMAT_OPTIONS[kind]);
    dateFormats.set(key, format);
  }
  return format;
}

function parseIsoDate(iso: string): Date {
  const [year, month, day] = iso.split('-').map(Number);
  return new Date(year, month - 1, day);
}

export function formatLongDate(iso: string, language: Language): string {
  return dateFormat(language, 'long').format(parseIsoDate(iso));
}

export function formatFullDate(iso: string, language: Language): string {
  return dateFormat(language, 'full').format(parseIsoDate(iso));
}

export function formatFullDateWithWeekday(iso: string, language: Language): string {
  return dateFormat(language, 'fullWithWeekday').format(parseIsoDate(iso));
}

export function formatDaysUntil(days: number, language: Language, t: SpecialDatesStrings): string {
  if (days === 0) {
    return t.today;
  }
  if (days === 1) {
    return t.tomorrow;
  }
  if (days === 2) {
    return t.dayAfterTomorrow;
  }
  return plural(language, days, t.inDays);
}

export function formatYears(category: SpecialDateCategory, years: number, language: Language, t: SpecialDatesStrings): string {
  if (years <= 0) {
    return '';
  }
  return plural(language, years, t.years[category]);
}

// Hebrew-calendar dates outside Hebrew. The backend's own labels (gematria, Hebrew month names) are shown as
// they are in Hebrew; in other languages the date is worked out by the browser's Hebrew calendar (Intl) from
// the Gregorian date, and shown with the month names and order of the strings file. CLDR has no Hebrew month
// names for Japanese or Chinese, so Intl's localized output can't be used directly.

// The months as ICU's English Hebrew calendar names them.
const ICU_HEBREW_MONTHS: Record<string, HebrewMonthKey> = {
  'Tishri': 'tishri',
  'Heshvan': 'heshvan',
  'Kislev': 'kislev',
  'Tevet': 'tevet',
  'Shevat': 'shevat',
  'Adar': 'adar',
  'Adar I': 'adarI',
  'Adar II': 'adarII',
  'Nisan': 'nisan',
  'Iyar': 'iyar',
  'Sivan': 'sivan',
  'Tamuz': 'tamuz',
  'Av': 'av',
  'Elul': 'elul',
};

// The backend numbers months from Nisan (1) to Adar II (13); 12 is Adar I in a leap year.
const BACKEND_HEBREW_MONTHS: Record<number, HebrewMonthKey> = {
  1: 'nisan', 2: 'iyar', 3: 'sivan', 4: 'tamuz', 5: 'av', 6: 'elul',
  7: 'tishri', 8: 'heshvan', 9: 'kislev', 10: 'tevet', 11: 'shevat', 12: 'adar', 13: 'adarII',
};

const HEBREW_CALENDAR_PARTS = new Intl.DateTimeFormat('en-u-ca-hebrew', {
  day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC',
});

export function hebrewMonthName(month: number, isLeapYear: boolean, t: SpecialDatesStrings): string {
  const key = month === 12 && isLeapYear ? 'adarI' : BACKEND_HEBREW_MONTHS[month];
  return key ? t.hebrewMonths[key] : String(month);
}

// `backendLabel` is the backend's Hebrew rendering of the same date, used as is in Hebrew. `afterSunset`
// means the Hebrew date is that of the next Gregorian day (the Hebrew day starts at sunset).
export function formatHebrewDate(
  iso: string, afterSunset: boolean, backendLabel: string, language: Language, t: SpecialDatesStrings,
): string {
  if (language === 'he') {
    return backendLabel;
  }
  const [year, month, day] = iso.split('-').map(Number);
  const date = new Date(Date.UTC(year, month - 1, day + (afterSunset ? 1 : 0)));
  const parts = HEBREW_CALENDAR_PARTS.formatToParts(date);
  const part = (type: Intl.DateTimeFormatPartTypes) => parts.find(p => p.type === type)?.value ?? '';
  const icuMonth = part('month');
  const monthKey = ICU_HEBREW_MONTHS[icuMonth];
  return fill(t.hebrewDateFormat, {
    day: part('day'),
    month: monthKey ? t.hebrewMonths[monthKey] : icuMonth,
    year: part('year'),
  });
}

export function todayIso(): string {
  const now = new Date();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  return `${now.getFullYear()}-${month}-${day}`;
}

const CALENDAR_COLOR_COUNT = 6;
const LAST_CALENDAR_STORAGE_KEY = 'special-dates:last-calendar';

export function calendarColorClass(calendarId: number): string {
  return `calendar-color-${calendarId % CALENDAR_COLOR_COUNT}`;
}

export function buildJoinUrl(joinToken: string): string {
  return `${window.location.origin}/special-dates/join/${joinToken}`;
}

export function readLastCalendarId(): number | null {
  try {
    const value = localStorage.getItem(LAST_CALENDAR_STORAGE_KEY);
    return value ? Number(value) : null;
  } catch {
    return null;
  }
}

export function storeLastCalendarId(calendarId: number): void {
  try {
    localStorage.setItem(LAST_CALENDAR_STORAGE_KEY, String(calendarId));
  } catch {
    // Storage can be unavailable (private mode); remembering the last calendar is only a convenience.
  }
}
