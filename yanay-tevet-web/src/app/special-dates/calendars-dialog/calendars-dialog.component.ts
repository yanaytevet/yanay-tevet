import {Component, computed, inject, signal} from '@angular/core';
import {NgIcon} from '@ng-icons/core';
import {featherCheck, featherEdit2, featherLogOut, featherPlus, featherTrash2, featherUserPlus, featherX} from '@ng-icons/feather-icons';
import {
  createSpecialDateCalendarView,
  deleteSpecialDateCalendarView,
  leaveSpecialDateCalendarView,
  listSpecialDateCalendarsView,
  renameSpecialDateCalendarView,
  SpecialDateCalendarSchema,
  updateSpecialDateCalendarPreferencesView,
} from '../../../generated-files/api/special-dates';
import {BaseDialogComponent} from '../../common/dialogs/base-dialog.component';
import {DialogService} from '../../common/dialogs/dialogs.service';
import {CalendarShareDialogComponent, CalendarShareDialogData} from '../calendar-share-dialog/calendar-share-dialog.component';
import {MoveDatesDialogComponent, MoveDatesDialogData} from '../move-dates-dialog/move-dates-dialog.component';
import {calendarColorClass} from '../special-dates.constants';

const CALENDAR_NAME_MAX_LENGTH = 100;

@Component({
  selector: 'app-calendars-dialog',
  standalone: true,
  imports: [NgIcon],
  templateUrl: './calendars-dialog.component.html',
})
export class CalendarsDialogComponent extends BaseDialogComponent<void, boolean> {
  private readonly dialogService = inject(DialogService);

  readonly calendars = signal<SpecialDateCalendarSchema[]>([]);
  readonly isLoading = signal<boolean>(true);

  readonly rows = computed(() => this.calendars().map(c => ({
    calendar: c,
    colorClass: calendarColorClass(c.id),
    subtitle: [
      `${c.event_count} אירועים`,
      c.member_count > 1 ? `${c.member_count} חברים` : 'רק את/ה',
      c.is_owner ? '' : `של ${c.owner_name}`,
    ].filter(Boolean).join(' · '),
  })));

  private changed = false;

  protected readonly featherCheck = featherCheck;
  protected readonly featherEdit2 = featherEdit2;
  protected readonly featherLogOut = featherLogOut;
  protected readonly featherPlus = featherPlus;
  protected readonly featherTrash2 = featherTrash2;
  protected readonly featherUserPlus = featherUserPlus;
  protected readonly featherX = featherX;

  constructor() {
    super();
    void this.load();
  }

  private async load(): Promise<void> {
    try {
      const res = await listSpecialDateCalendarsView();
      if (!res.error) {
        this.calendars.set(res.data.calendars);
      }
    } finally {
      this.isLoading.set(false);
    }
  }

  private async reloadAfterChange(): Promise<void> {
    this.changed = true;
    await this.load();
  }

  private async showError(error: unknown, fallback: string): Promise<void> {
    const err = error as {detail?: string};
    await this.dialogService.showNotificationDialog({title: 'שגיאה', text: err?.detail || fallback});
  }

  async createCalendar(): Promise<void> {
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
      return;
    }
    const res = await createSpecialDateCalendarView({body: {name}});
    if (res.error) {
      await this.showError(res.error, 'יצירת הלוח נכשלה.');
      return;
    }
    await this.reloadAfterChange();
  }

  async share(calendar: SpecialDateCalendarSchema): Promise<void> {
    const changed = await this.dialogService.open<CalendarShareDialogData, boolean>(
      CalendarShareDialogComponent, {calendarId: calendar.id}, 40);
    if (changed) {
      await this.reloadAfterChange();
    }
  }

  async moveInto(calendar: SpecialDateCalendarSchema): Promise<void> {
    const moved = await this.dialogService.open<MoveDatesDialogData, boolean>(
      MoveDatesDialogComponent, {targetCalendarId: calendar.id, isAfterJoin: false}, 40);
    if (moved) {
      await this.reloadAfterChange();
    }
  }

  async rename(calendar: SpecialDateCalendarSchema): Promise<void> {
    const name = (await this.dialogService.getTextFromInputDialog({
      title: 'שינוי שם הלוח',
      text: '',
      label: 'שם הלוח',
      defaultValue: calendar.name,
      confirmActionName: 'שמירה',
      cancelActionName: 'ביטול',
      maxLength: CALENDAR_NAME_MAX_LENGTH,
    }, 40))?.trim();
    if (!name || name === calendar.name) {
      return;
    }
    const res = await renameSpecialDateCalendarView({path: {object_id: calendar.id}, body: {name}});
    if (res.error) {
      await this.showError(res.error, 'שינוי השם נכשל.');
      return;
    }
    await this.reloadAfterChange();
  }

  async toggleShowInUpcoming(calendar: SpecialDateCalendarSchema): Promise<void> {
    const res = await updateSpecialDateCalendarPreferencesView({
      path: {object_id: calendar.id},
      body: {hide_from_upcoming: !calendar.hide_from_upcoming},
    });
    if (!res.error) {
      await this.reloadAfterChange();
    }
  }

  async deleteCalendar(calendar: SpecialDateCalendarSchema): Promise<void> {
    const others = calendar.member_count > 1 ? ' הלוח יימחק גם אצל כל החברים בו.' : '';
    const confirmed = await this.dialogService.getBooleanFromConfirmationDialog({
      title: 'מחיקת לוח',
      text: `למחוק את "${calendar.name}" ואת כל ${calendar.event_count} האירועים שבו?${others} אי אפשר לבטל את זה.`,
      confirmActionName: 'מחיקה',
      cancelActionName: 'ביטול',
    });
    if (!confirmed) {
      return;
    }
    const res = await deleteSpecialDateCalendarView({path: {object_id: calendar.id}});
    if (res.error) {
      await this.showError(res.error, 'המחיקה נכשלה.');
      return;
    }
    await this.reloadAfterChange();
  }

  async leave(calendar: SpecialDateCalendarSchema): Promise<void> {
    const confirmed = await this.dialogService.getBooleanFromConfirmationDialog({
      title: 'יציאה מהלוח',
      text: `לצאת מ"${calendar.name}"? האירועים יישארו בלוח אצל שאר החברים. אפשר לחזור בעזרת קישור ההצטרפות.`,
      confirmActionName: 'יציאה',
      cancelActionName: 'ביטול',
    });
    if (!confirmed) {
      return;
    }
    const res = await leaveSpecialDateCalendarView({path: {object_id: calendar.id}, body: {}});
    if (res.error) {
      await this.showError(res.error, 'היציאה מהלוח נכשלה.');
      return;
    }
    await this.reloadAfterChange();
  }

  onClose(): void {
    this.emitClose(this.changed);
  }
}
