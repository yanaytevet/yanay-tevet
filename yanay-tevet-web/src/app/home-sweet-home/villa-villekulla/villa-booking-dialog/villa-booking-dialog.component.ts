import {Component, inject, signal} from '@angular/core';
import {FormControl, ReactiveFormsModule} from '@angular/forms';
import {NgIcon, provideIcons} from '@ng-icons/core';
import {featherX} from '@ng-icons/feather-icons';
import {
  createUnitBookingView,
  UnitBookingSchema,
} from '../../../../generated-files/api/villa-villekulla';
import {BaseDialogComponent} from '../../../common/dialogs/base-dialog.component';
import {DialogService} from '../../../common/dialogs/dialogs.service';

export interface VillaBookingDialogData {
  unitId: number;
  defaultStart: string;
  bookings: UnitBookingSchema[];
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
  readonly isBooking = signal<boolean>(false);
  readonly errorMsg = signal<string | null>(null);

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
