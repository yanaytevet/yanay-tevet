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
}

function addDays(iso: string, days: number): string {
  const date = new Date(`${iso}T00:00:00`);
  date.setDate(date.getDate() + days);
  return date.toISOString().slice(0, 10);
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

  protected readonly featherX = featherX;

  async onBook(): Promise<void> {
    const start = this.startCtrl.value;
    const end = this.endCtrl.value;
    if (!start || !end || this.isBooking()) {
      return;
    }
    if (end <= start) {
      await this.dialogService.showNotificationDialog({
        title: 'Invalid dates',
        text: 'Check-out must be after check-in.',
      });
      return;
    }
    this.isBooking.set(true);
    try {
      const res = await createUnitBookingView({
        body: {unit_id: this.data.unitId, start_date: start, end_date: end, note: this.noteCtrl.value.trim()},
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
