import {inject, Injectable} from '@angular/core';
import {createSpecialDateCalendarView, SpecialDateCalendarSchema} from '../../generated-files/api/special-dates';
import {DialogService} from '../common/dialogs/dialogs.service';
import {LanguageService} from '../shared/i18n/language.service';
import {SPECIAL_DATES_STRINGS} from './i18n';

const CALENDAR_NAME_MAX_LENGTH = 100;

@Injectable({providedIn: 'root'})
export class SpecialDateCalendarsService {
  private readonly dialogService = inject(DialogService);
  private readonly languageService = inject(LanguageService);

  async promptCreateCalendar(): Promise<SpecialDateCalendarSchema | null> {
    const t = SPECIAL_DATES_STRINGS[this.languageService.language()];
    const name = (await this.dialogService.getTextFromInputDialog({
      title: t.newCalendar,
      text: t.createCalendar.text,
      label: t.calendarName,
      defaultValue: '',
      confirmActionName: t.createCalendar.confirm,
      cancelActionName: t.cancel,
      maxLength: CALENDAR_NAME_MAX_LENGTH,
    }, 40))?.trim();
    if (!name) {
      return null;
    }
    const res = await createSpecialDateCalendarView({body: {name}});
    if (res.error) {
      const err = res.error as {detail?: string};
      await this.dialogService.showNotificationDialog({title: t.error, text: err?.detail || t.createCalendar.failed});
      return null;
    }
    return res.data;
  }
}
