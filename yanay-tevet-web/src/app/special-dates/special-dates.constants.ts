import {CalendarType, SpecialDateCategory} from '../../generated-files/api/special-dates';

export interface SpecialDateCategoryOption {
  value: SpecialDateCategory;
  label: string;
  emoji: string;
  nameLabel: string;
  namePlaceholder: string;
  namePrefix: string;
}

export const SPECIAL_DATE_CATEGORIES: SpecialDateCategoryOption[] = [
  {
    value: 'birthday', label: 'יום הולדת', emoji: '🎂',
    nameLabel: 'של מי יום ההולדת?', namePlaceholder: 'סבתא חלי', namePrefix: 'יום ההולדת של',
  },
  {
    value: 'anniversary', label: 'יום נישואין', emoji: '💍',
    nameLabel: 'של מי יום הנישואין?', namePlaceholder: 'דני ורותי', namePrefix: 'יום הנישואין של',
  },
  {
    value: 'memorial', label: 'אזכרה', emoji: '🕯️',
    nameLabel: 'לזכר מי?', namePlaceholder: 'סבא משה', namePrefix: 'האזכרה של',
  },
  {
    value: 'other', label: 'אחר', emoji: '📅',
    nameLabel: 'שם האירוע', namePlaceholder: 'יום העלייה של המשפחה', namePrefix: '',
  },
];

export const SPECIAL_DATE_CATEGORY_BY_VALUE: Record<SpecialDateCategory, SpecialDateCategoryOption> =
  Object.fromEntries(SPECIAL_DATE_CATEGORIES.map(c => [c.value, c])) as Record<SpecialDateCategory, SpecialDateCategoryOption>;

export const CALENDAR_CHIPS: Record<CalendarType, {label: string; cssClass: string}> = {
  hebrew: {label: 'לפי הלוח העברי', cssClass: 'calendar-chip-hebrew'},
  gregorian: {label: 'לפי הלוח הלועזי', cssClass: 'calendar-chip-gregorian'},
};

const LONG_DATE_FORMAT = new Intl.DateTimeFormat('he-IL', {weekday: 'long', day: 'numeric', month: 'long'});
const FULL_DATE_FORMAT = new Intl.DateTimeFormat('he-IL', {day: 'numeric', month: 'long', year: 'numeric'});
const FULL_DATE_WITH_WEEKDAY_FORMAT = new Intl.DateTimeFormat('he-IL', {weekday: 'long', day: 'numeric', month: 'long', year: 'numeric'});

function parseIsoDate(iso: string): Date {
  const [year, month, day] = iso.split('-').map(Number);
  return new Date(year, month - 1, day);
}

export function formatLongDate(iso: string): string {
  return LONG_DATE_FORMAT.format(parseIsoDate(iso));
}

export function formatFullDate(iso: string): string {
  return FULL_DATE_FORMAT.format(parseIsoDate(iso));
}

export function formatFullDateWithWeekday(iso: string): string {
  return FULL_DATE_WITH_WEEKDAY_FORMAT.format(parseIsoDate(iso));
}

export function formatDaysUntil(days: number): string {
  if (days === 0) {
    return 'היום';
  }
  if (days === 1) {
    return 'מחר';
  }
  if (days === 2) {
    return 'מחרתיים';
  }
  return `בעוד ${days} ימים`;
}

export function formatYears(category: SpecialDateCategory, years: number): string {
  if (years <= 0) {
    return '';
  }
  const yearsText = years === 1 ? 'שנה' : `${years} שנים`;
  switch (category) {
    case 'birthday':
      return `יום הולדת ${years}`;
    case 'anniversary':
      return `${yearsText} לנישואין`;
    case 'memorial':
      return `${yearsText} לפטירה`;
    default:
      return yearsText;
  }
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
