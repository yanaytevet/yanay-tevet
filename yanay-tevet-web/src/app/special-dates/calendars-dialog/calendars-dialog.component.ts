import {Component, computed, inject, signal} from '@angular/core';
import {NgIcon} from '@ng-icons/core';
import {featherEdit, featherLogOut, featherPlus, featherTrash2, featherUserPlus, featherX} from '@ng-icons/feather-icons';
import {
  deleteSpecialDateCalendarView,
  leaveSpecialDateCalendarView,
  listSpecialDateCalendarsView,
  renameSpecialDateCalendarView,
  SpecialDateCalendarSchema,
  updateSpecialDateCalendarPreferencesView,
} from '../../../generated-files/api/special-dates';
import {LoadingStateComponent} from '../../common/components/page/loading-state/loading-state.component';
import {BaseDialogComponent} from '../../common/dialogs/base-dialog.component';
import {DialogService} from '../../common/dialogs/dialogs.service';
import {LanguageService} from '../../shared/i18n/language.service';
import {fill, injectStrings, plural} from '../../shared/i18n/strings';
import {SPECIAL_DATES_STRINGS} from '../i18n';
import {CalendarShareDialogComponent, CalendarShareDialogData} from '../calendar-share-dialog/calendar-share-dialog.component';
import {MoveDatesDialogComponent, MoveDatesDialogData} from '../move-dates-dialog/move-dates-dialog.component';
import {SpecialDateCalendarsService} from '../special-date-calendars.service';
import {calendarColorClass} from '../special-dates.constants';
import {CheckboxMarkComponent} from '../../common/components/inputs/checkbox-mark/checkbox-mark.component';

const CALENDAR_NAME_MAX_LENGTH = 100;

@Component({
  selector: 'app-calendars-dialog',
  standalone: true,
  imports: [CheckboxMarkComponent, NgIcon, LoadingStateComponent],
  templateUrl: './calendars-dialog.component.html',
})
export class CalendarsDialogComponent extends BaseDialogComponent<void, boolean> {
  private readonly dialogService = inject(DialogService);
  private readonly calendarsService = inject(SpecialDateCalendarsService);
  private readonly language = inject(LanguageService).language;
  protected readonly t = injectStrings(SPECIAL_DATES_STRINGS);

  readonly calendars = signal<SpecialDateCalendarSchema[]>([]);
  readonly isLoading = signal<boolean>(true);

  readonly rows = computed(() => {
    const language = this.language();
    const t = this.t();
    const ownedCount = this.calendars().filter(c => c.is_owner).length;
    return this.calendars().map(c => ({
      calendar: c,
      canDelete: c.is_owner && ownedCount > 1,
      colorClass: calendarColorClass(c.id),
      subtitle: [
        plural(language, c.event_count, t.eventsCount),
        c.member_count > 1 ? plural(language, c.member_count, t.membersCount) : t.calendars.onlyYou,
        c.is_owner ? '' : fill(t.calendars.ownedBy, {name: c.owner_name}),
      ].filter(Boolean).join(' · '),
    }));
  });

  private changed = false;

  protected readonly featherEdit = featherEdit;
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
    await this.dialogService.showNotificationDialog({title: this.t().error, text: err?.detail || fallback});
  }

  async createCalendar(): Promise<void> {
    if (await this.calendarsService.promptCreateCalendar()) {
      await this.reloadAfterChange();
    }
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
      title: this.t().calendars.renameTitle,
      text: '',
      label: this.t().calendarName,
      defaultValue: calendar.name,
      confirmActionName: this.t().save,
      cancelActionName: this.t().cancel,
      maxLength: CALENDAR_NAME_MAX_LENGTH,
    }, 40))?.trim();
    if (!name || name === calendar.name) {
      return;
    }
    const res = await renameSpecialDateCalendarView({path: {object_id: calendar.id}, body: {name}});
    if (res.error) {
      await this.showError(res.error, this.t().calendars.renameFailed);
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
    const t = this.t();
    const forms = calendar.member_count > 1 ? t.calendars.deleteTextShared : t.calendars.deleteText;
    const confirmed = await this.dialogService.getBooleanFromConfirmationDialog({
      title: t.calendars.deleteCalendar,
      text: fill(plural(this.language(), calendar.event_count, forms), {name: calendar.name}),
      confirmActionName: t.delete,
      danger: true,
      cancelActionName: t.cancel,
    });
    if (!confirmed) {
      return;
    }
    const res = await deleteSpecialDateCalendarView({path: {object_id: calendar.id}});
    if (res.error) {
      await this.showError(res.error, this.t().calendars.deleteFailed);
      return;
    }
    await this.reloadAfterChange();
  }

  async leave(calendar: SpecialDateCalendarSchema): Promise<void> {
    const confirmed = await this.dialogService.getBooleanFromConfirmationDialog({
      title: this.t().calendars.leave,
      text: fill(this.t().calendars.leaveText, {name: calendar.name}),
      confirmActionName: this.t().calendars.leaveConfirm,
      danger: true,
      cancelActionName: this.t().cancel,
    });
    if (!confirmed) {
      return;
    }
    const res = await leaveSpecialDateCalendarView({path: {object_id: calendar.id}, body: {}});
    if (res.error) {
      await this.showError(res.error, this.t().calendars.leaveFailed);
      return;
    }
    await this.reloadAfterChange();
  }

  onClose(): void {
    this.emitClose(this.changed);
  }
}
