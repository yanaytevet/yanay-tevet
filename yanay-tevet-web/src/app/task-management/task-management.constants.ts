import {TaskPriority} from '../../generated-files/api/task-management';
import {Language} from '../../generated-files/api/users';
import {TasksStrings} from './i18n';
import {fill} from '../shared/i18n/strings';

export const TASK_PRIORITY_ORDER: TaskPriority[] = ['none', 'low', 'medium', 'high', 'urgent'];

// The chip variant added to `chip` for each priority; higher priorities get a stronger colour.
// "none" renders without a chip.
export const TASK_PRIORITY_CHIP_CLASS: Record<TaskPriority, string> = {
  none: '',
  low: '',
  medium: 'chip-accent',
  high: 'chip-warning',
  urgent: 'chip-danger',
};

// Repeating-task weekdays use JS Date.getDay() numbering: 0=Sunday .. 6=Saturday.
// This order (Sunday first) is also the display order in the UI.
export const WEEKDAY_VALUES: number[] = [0, 1, 2, 3, 4, 5, 6];

export type RepeatPresetKey = 'everyDay' | 'workDays' | 'weekend';

export const REPEAT_PRESETS: {key: RepeatPresetKey; days: number[]}[] = [
  {key: 'everyDay', days: []},
  {key: 'workDays', days: [0, 1, 2, 3, 4]},
  {key: 'weekend', days: [5, 6]},
];

// The hour (local time) at which a repeating task resets to "to do"; the backend does the reset.
const RESET_HOUR = 4;

// Short weekday names in the site language, indexed by getDay() value. 1 Jan 2023 was a Sunday.
export function weekdayNames(language: Language): string[] {
  const format = new Intl.DateTimeFormat(language, {weekday: 'short', timeZone: 'UTC'});
  return WEEKDAY_VALUES.map(day => format.format(new Date(Date.UTC(2023, 0, 1 + day))));
}

// The reset time, e.g. "4:00 AM" or "04:00".
export function formatResetTime(language: Language): string {
  return new Intl.DateTimeFormat(language, {hour: 'numeric', minute: '2-digit'})
    .format(new Date(2023, 0, 1, RESET_HOUR, 0));
}

function formatDayList(days: number[], language: Language): string {
  const names = weekdayNames(language);
  return new Intl.ListFormat(language, {style: 'narrow', type: 'conjunction'})
    .format([...days].sort((a, b) => a - b).map(d => names[d]));
}

// Compact schedule label for chips/badges, e.g. "Daily", "Sun–Thu", "Wed, Fri".
export function formatRepeatDays(days: number[], t: TasksStrings, language: Language): string {
  if (days.length === 0 || days.length === 7) {
    return t.repeat.daily;
  }
  const key = [...days].sort((a, b) => a - b).join(',');
  if (key === '0,1,2,3,4') {
    const names = weekdayNames(language);
    return fill(t.repeat.dayRange, {from: names[0], to: names[4]});
  }
  if (key === '5,6') {
    return t.repeat.weekends;
  }
  return formatDayList(days, language);
}

// Full sentence used in the dialog, e.g. 'Resets to "To do" at 4 AM every Sun, Wed.'
export function describeRepeatSchedule(days: number[], t: TasksStrings, language: Language): string {
  const time = formatResetTime(language);
  if (days.length === 0 || days.length === 7) {
    return fill(t.repeat.resetsDaily, {time});
  }
  return fill(t.repeat.resetsOnDays, {time, days: formatDayList(days, language)});
}
