import {CalendarType, SpecialDateCategory, SpecialDateRecurrence} from '../../generated-files/api/special-dates';

export interface SpecialDateCategoryOption {
  value: SpecialDateCategory;
  label: string;
  emoji: string;
}

export const SPECIAL_DATE_CATEGORIES: SpecialDateCategoryOption[] = [
  {value: 'birthday', label: 'יום הולדת', emoji: '🎂'},
  {value: 'anniversary', label: 'יום נישואין', emoji: '💍'},
  {value: 'memorial', label: 'אזכרה', emoji: '🕯️'},
  {value: 'other', label: 'אחר', emoji: '📅'},
];

export const SPECIAL_DATE_CATEGORY_BY_VALUE: Record<SpecialDateCategory, SpecialDateCategoryOption> =
  Object.fromEntries(SPECIAL_DATE_CATEGORIES.map(c => [c.value, c])) as Record<SpecialDateCategory, SpecialDateCategoryOption>;

export const SPECIAL_DATE_RECURRENCES: {value: SpecialDateRecurrence; label: string}[] = [
  {value: 'both', label: 'לפי שני הלוחות'},
  {value: 'hebrew', label: 'לפי התאריך העברי בלבד'},
  {value: 'gregorian', label: 'לפי התאריך הלועזי בלבד'},
];

export const DEFAULT_RECURRENCE_BY_CATEGORY: Record<SpecialDateCategory, SpecialDateRecurrence> = {
  birthday: 'both',
  anniversary: 'both',
  memorial: 'hebrew',
  other: 'both',
};

export const CALENDAR_LABELS: Record<CalendarType, string> = {
  gregorian: 'לפי הלוח הלועזי',
  hebrew: 'לפי הלוח העברי',
};

const LONG_DATE_FORMAT = new Intl.DateTimeFormat('he-IL', {weekday: 'long', day: 'numeric', month: 'long'});
const FULL_DATE_FORMAT = new Intl.DateTimeFormat('he-IL', {day: 'numeric', month: 'long', year: 'numeric'});

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

export function formatCalendars(calendars: CalendarType[]): string {
  if (calendars.length > 1) {
    return 'חל באותו יום בשני הלוחות';
  }
  return CALENDAR_LABELS[calendars[0]];
}

export function todayIso(): string {
  const now = new Date();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  return `${now.getFullYear()}-${month}-${day}`;
}
