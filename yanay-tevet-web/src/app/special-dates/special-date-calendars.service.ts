import {inject, Injectable} from '@angular/core';
import {createSpecialDateCalendarView, SpecialDateCalendarSchema} from '../../generated-files/api/special-dates';
import {DialogService} from '../common/dialogs/dialogs.service';

const CALENDAR_NAME_MAX_LENGTH = 100;

@Injectable({providedIn: 'root'})
export class SpecialDateCalendarsService {
  private readonly dialogService = inject(DialogService);

  async promptCreateCalendar(): Promise<SpecialDateCalendarSchema | null> {
    const name = (await this.dialogService.getTextFromInputDialog({
      title: 'לוח חדש',
      text: 'למשל "משפחה" או "חברים מהעבודה". אחרי היצירה אפשר לשתף אותו.',
      label: 'שם הלוח',
      defaultValue: '',
      confirmActionName: 'יצירה',
      cancelActionName: 'ביטול',
      maxLength: CALENDAR_NAME_MAX_LENGTH,
    }, 40))?.trim();
    if (!name) {
      return null;
    }
    const res = await createSpecialDateCalendarView({body: {name}});
    if (res.error) {
      const err = res.error as {detail?: string};
      await this.dialogService.showNotificationDialog({title: 'שגיאה', text: err?.detail || 'יצירת הלוח נכשלה.'});
      return null;
    }
    return res.data;
  }
}
