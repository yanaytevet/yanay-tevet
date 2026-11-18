import {Component, computed, inject, signal} from '@angular/core';
import {FormControl, ReactiveFormsModule} from '@angular/forms';
import {NgIcon, provideIcons} from '@ng-icons/core';
import {featherX} from '@ng-icons/feather-icons';
import {
  createUnitBookingView,
  ProjectMembershipSchema,
  UnitBookingSchema,
} from '../../../../generated-files/api/villa-villekulla';
import {BaseDialogComponent} from '../../../common/dialogs/base-dialog.component';
import {DialogService} from '../../../common/dialogs/dialogs.service';
import {fill, injectStrings} from '../../../shared/i18n/strings';
import {HOME_SWEET_HOME_STRINGS} from '../../i18n';

export interface VillaBookingDialogData {
  unitId: number;
  defaultStart: string;
  bookings: UnitBookingSchema[];
  // When the viewer can book on behalf of others, the project members and the
  // current user so the dialog can offer a "booking for" dropdown.
  canManageAll: boolean;
  members: ProjectMembershipSchema[];
  currentUserId: number;
  currentUserName: string;
}

interface BookForOption {
  id: number;
  name: string;
}

// Date math on the y-m-d parts only — avoids the UTC shift that Date.toISOString() causes.
function addDays(iso: string, days: number): string {
  const date = new Date(`${iso}T00:00:00`);
  date.setDate(date.getDate() + days);
  const year = date.getFullYear();
  const month = `${date.getMonth() + 1}`.padStart(2, '0');
  const day = `${date.getDate()}`.padStart(2, '0');
  return `${year}-${month}-${day}`;
}

@Component({
  selector: 'app-villa-booking-dialog',
  standalone: true,
  imports: [ReactiveFormsModule, NgIcon],
  providers: [provideIcons({featherX})],
  templateUrl: './villa-booking-dialog.component.html',
})
export class VillaBookingDialogComponent extends BaseDialogComponent<VillaBookingDialogData, UnitBookingSchema> {
  private readonly dialogService = inject(DialogService);
  protected readonly t = injectStrings(HOME_SWEET_HOME_STRINGS);

  readonly startCtrl = new FormControl<string>(this.data.defaultStart, {nonNullable: true});
  readonly endCtrl = new FormControl<string>(addDays(this.data.defaultStart, 1), {nonNullable: true});
  readonly noteCtrl = new FormControl<string>('', {nonNullable: true});
  readonly bookForCtrl = new FormControl<number>(this.data.currentUserId, {nonNullable: true});
  readonly isBooking = signal<boolean>(false);
  // Which validation message applies; the text itself follows the site language.
  readonly error = signal<'order' | 'conflict' | null>(null);
  readonly errorMsg = computed<string | null>(() => {
    const error = this.error();
    if (error === null) {
      return null;
    }
    const t = this.t().bookingDialog;
    return error === 'order' ? t.errorOrder : t.errorConflict;
  });

  // The current user first (the default), then every other project member.
  readonly bookForOptions = computed<BookForOption[]>(() => [
    {id: this.data.currentUserId, name: fill(this.t().bookingDialog.youSuffix, {name: this.data.currentUserName})},
    ...this.data.members
      .filter(m => m.user_id !== this.data.currentUserId)
      .map(m => ({id: m.user_id, name: m.full_name || m.username})),
  ]);
  readonly showBookFor = this.data.canManageAll && this.data.members.some(m => m.user_id !== this.data.currentUserId);

  protected readonly featherX = featherX;

  constructor() {
    super();
    this.startCtrl.valueChanges.subscribe(() => this.validate());
    this.endCtrl.valueChanges.subscribe(() => this.validate());
    this.validate();
  }

  private validate(): void {
    const start = this.startCtrl.value;
    const end = this.endCtrl.value;
    if (!start || !end || end <= start) {
      this.error.set('order');
      return;
    }
    // ISO date strings compare chronologically; ranges overlap if each starts before the other ends.
    const conflict = this.data.bookings.some(b => start < b.end_date && end > b.start_date);
    this.error.set(conflict ? 'conflict' : null);
  }

  async onBook(): Promise<void> {
    if (this.isBooking() || this.errorMsg() !== null) {
      return;
    }
    this.isBooking.set(true);
    try {
      const res = await createUnitBookingView({
        body: {
          unit_id: this.data.unitId,
          start_date: this.startCtrl.value,
          end_date: this.endCtrl.value,
          note: this.noteCtrl.value.trim(),
          booked_for_id: this.showBookFor ? this.bookForCtrl.value : null,
        },
      });
      this.emitClose(res.data);
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: this.t().bookingDialog.bookFailed, text: `${err}`});
    } finally {
      this.isBooking.set(false);
    }
  }

  onClose(): void {
    this.emitClose(null);
  }
}
