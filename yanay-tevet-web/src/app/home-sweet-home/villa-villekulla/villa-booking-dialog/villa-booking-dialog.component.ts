import {Component, inject, signal} from '@angular/core';
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

  readonly startCtrl = new FormControl<string>(this.data.defaultStart, {nonNullable: true});
  readonly endCtrl = new FormControl<string>(addDays(this.data.defaultStart, 1), {nonNullable: true});
  readonly noteCtrl = new FormControl<string>('', {nonNullable: true});
  readonly bookForCtrl = new FormControl<number>(this.data.currentUserId, {nonNullable: true});
  readonly isBooking = signal<boolean>(false);
  readonly errorMsg = signal<string | null>(null);

  // The current user first (the default), then every other project member.
  readonly bookForOptions: BookForOption[] = [
    {id: this.data.currentUserId, name: `${this.data.currentUserName} (you)`},
    ...this.data.members
      .filter(m => m.user_id !== this.data.currentUserId)
      .map(m => ({id: m.user_id, name: m.full_name || m.username})),
  ];
  readonly showBookFor = this.data.canManageAll && this.bookForOptions.length > 1;

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
      this.errorMsg.set('Check-out must be after check-in.');
      return;
    }
    // ISO date strings compare chronologically; ranges overlap if each starts before the other ends.
    const conflict = this.data.bookings.some(b => start < b.end_date && end > b.start_date);
    this.errorMsg.set(conflict ? 'Some of those nights are already booked.' : null);
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
      await this.dialogService.showNotificationDialog({title: 'Could not book', text: `${err}`});
    } finally {
      this.isBooking.set(false);
    }
  }

  onClose(): void {
    this.emitClose(null);
  }
}
