import {Component, computed, DestroyRef, inject, signal} from '@angular/core';
import {toSignal} from '@angular/core/rxjs-interop';
import {FormControl, ReactiveFormsModule} from '@angular/forms';
import {NgIcon} from '@ng-icons/core';
import {featherCheck, featherCopy, featherRefreshCw, featherUserMinus, featherX} from '@ng-icons/feather-icons';
import {
  listSpecialDateCalendarMembersView,
  listSpecialDateCalendarsView,
  removeSpecialDateCalendarMemberView,
  resetSpecialDateCalendarLinkView,
  shareSpecialDateCalendarView,
  SpecialDateCalendarMembersSchema,
  SpecialDateCalendarSchema,
} from '../../../generated-files/api/special-dates';
import {LoadingStateComponent} from '../../common/components/page/loading-state/loading-state.component';
import {BaseDialogComponent} from '../../common/dialogs/base-dialog.component';
import {DialogService} from '../../common/dialogs/dialogs.service';
import {fill, injectStrings} from '../../shared/i18n/strings';
import {SPECIAL_DATES_STRINGS} from '../i18n';
import {buildJoinUrl} from '../special-dates.constants';

export interface CalendarShareDialogData {
  calendarId: number;
}

const COPIED_FEEDBACK_MS = 2000;

@Component({
  selector: 'app-calendar-share-dialog',
  standalone: true,
  imports: [ReactiveFormsModule, NgIcon, LoadingStateComponent],
  templateUrl: './calendar-share-dialog.component.html',
})
export class CalendarShareDialogComponent extends BaseDialogComponent<CalendarShareDialogData, boolean> {
  private readonly dialogService = inject(DialogService);
  protected readonly t = injectStrings(SPECIAL_DATES_STRINGS);

  readonly calendar = signal<SpecialDateCalendarSchema | null>(null);
  readonly members = signal<SpecialDateCalendarMembersSchema | null>(null);
  readonly copied = signal<boolean>(false);
  readonly isInviting = signal<boolean>(false);
  readonly inviteMessage = signal<string>('');
  readonly inviteError = signal<string>('');

  readonly identifierCtrl = new FormControl<string>('', {nonNullable: true});
  private readonly identifierValue = toSignal(this.identifierCtrl.valueChanges, {initialValue: ''});

  readonly isOwner = computed(() => this.calendar()?.is_owner ?? false);
  readonly joinUrl = computed(() => {
    const token = this.calendar()?.join_token;
    return token ? buildJoinUrl(token) : '';
  });
  readonly whatsappUrl = computed(() => {
    const calendar = this.calendar();
    const url = this.joinUrl();
    if (!calendar || !url) {
      return '';
    }
    const text = fill(this.t().share.whatsappText, {name: calendar.name, url});
    return `https://wa.me/?text=${encodeURIComponent(text)}`;
  });
  readonly onlyOwnerText = computed(() => fill(this.t().share.onlyOwnerInvites, {name: this.calendar()?.owner_name ?? ''}));
  readonly canInvite = computed(() => !!this.identifierValue().trim() && !this.isInviting());

  private changed = false;
  private copiedTimeout: ReturnType<typeof setTimeout> | null = null;

  protected readonly featherCheck = featherCheck;
  protected readonly featherCopy = featherCopy;
  protected readonly featherRefreshCw = featherRefreshCw;
  protected readonly featherUserMinus = featherUserMinus;
  protected readonly featherX = featherX;

  constructor() {
    super();
    inject(DestroyRef).onDestroy(() => {
      if (this.copiedTimeout !== null) {
        clearTimeout(this.copiedTimeout);
      }
    });
    void this.load();
  }

  private async load(): Promise<void> {
    const [calendarsRes, membersRes] = await Promise.all([
      listSpecialDateCalendarsView(),
      listSpecialDateCalendarMembersView({path: {object_id: this.data.calendarId}}),
    ]);
    if (!calendarsRes.error) {
      this.calendar.set(calendarsRes.data.calendars.find(c => c.id === this.data.calendarId) ?? null);
    }
    if (!membersRes.error) {
      this.members.set(membersRes.data);
    }
  }

  async copyLink(): Promise<void> {
    const url = this.joinUrl();
    if (!url) {
      return;
    }
    try {
      await navigator.clipboard.writeText(url);
    } catch {
      await this.dialogService.showNotificationDialog({title: this.t().share.joinLink, text: url});
      return;
    }
    this.copied.set(true);
    if (this.copiedTimeout !== null) {
      clearTimeout(this.copiedTimeout);
    }
    this.copiedTimeout = setTimeout(() => this.copied.set(false), COPIED_FEEDBACK_MS);
  }

  async resetLink(): Promise<void> {
    const confirmed = await this.dialogService.getBooleanFromConfirmationDialog({
      title: this.t().share.resetLink,
      text: this.t().share.resetText,
      confirmActionName: this.t().share.resetConfirm,
      danger: true,
      cancelActionName: this.t().cancel,
    });
    if (!confirmed) {
      return;
    }
    const res = await resetSpecialDateCalendarLinkView({path: {object_id: this.data.calendarId}, body: {}});
    if (!res.error) {
      this.calendar.set(res.data);
    }
  }

  async invite(): Promise<void> {
    const identifier = this.identifierCtrl.value.trim();
    if (!identifier || this.isInviting()) {
      return;
    }
    this.isInviting.set(true);
    this.inviteError.set('');
    this.inviteMessage.set('');
    try {
      const res = await shareSpecialDateCalendarView({path: {object_id: this.data.calendarId}, body: {identifier}});
      if (res.error) {
        const err = res.error as {detail?: string};
        this.inviteError.set(err?.detail || this.t().share.inviteFailed);
        return;
      }
      this.changed = true;
      this.identifierCtrl.setValue('');
      await this.load();
      const joined = this.members()?.members.some(m => m.email.toLowerCase() === identifier.toLowerCase()
        || m.name.toLowerCase() === identifier.toLowerCase());
      this.inviteMessage.set(joined ? this.t().share.added : this.t().share.invitedByEmail);
    } finally {
      this.isInviting.set(false);
    }
  }

  async removeMember(userId: number, name: string): Promise<void> {
    const confirmed = await this.dialogService.getBooleanFromConfirmationDialog({
      title: this.t().share.removeFromCalendar,
      text: fill(this.t().share.removeText, {name}),
      confirmActionName: this.t().share.removeConfirm,
      danger: true,
      cancelActionName: this.t().cancel,
    });
    if (!confirmed) {
      return;
    }
    const res = await removeSpecialDateCalendarMemberView({path: {object_id: this.data.calendarId}, body: {user_id: userId}});
    if (!res.error) {
      this.changed = true;
      await this.load();
    }
  }

  onClose(): void {
    this.emitClose(this.changed);
  }
}
