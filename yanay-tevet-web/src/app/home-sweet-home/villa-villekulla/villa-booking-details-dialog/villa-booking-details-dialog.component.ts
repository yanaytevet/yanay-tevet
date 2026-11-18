import {Component, computed, inject, signal} from '@angular/core';
import {FormControl, ReactiveFormsModule} from '@angular/forms';
import {NgIcon, provideIcons} from '@ng-icons/core';
import {featherX, featherTrash2} from '@ng-icons/feather-icons';
import {
  deleteUnitBookingView,
  updateUnitBookingView,
  UnitBookingSchema,
} from '../../../../generated-files/api/villa-villekulla';
import {BaseDialogComponent} from '../../../common/dialogs/base-dialog.component';
import {DialogService} from '../../../common/dialogs/dialogs.service';
import {fill, injectStrings} from '../../../shared/i18n/strings';
import {LanguageService} from '../../../shared/i18n/language.service';
import {HOME_SWEET_HOME_STRINGS} from '../../i18n';
import {formatDateRange} from '../villa-dates';

export interface VillaBookingDetailsDialogData {
  booking: UnitBookingSchema;
}

@Component({
  selector: 'app-villa-booking-details-dialog',
  standalone: true,
  imports: [ReactiveFormsModule, NgIcon],
  providers: [provideIcons({featherX, featherTrash2})],
  templateUrl: './villa-booking-details-dialog.component.html',
})
export class VillaBookingDetailsDialogComponent extends BaseDialogComponent<VillaBookingDetailsDialogData, boolean> {
  private readonly dialogService = inject(DialogService);
  private readonly languageService = inject(LanguageService);
  protected readonly t = injectStrings(HOME_SWEET_HOME_STRINGS);

  readonly booking = this.data.booking;
  // Show who made the booking only when it differs from who it is for (admin booked on their behalf).
  readonly bookedByOther =
    this.data.booking.created_by_name !== '' &&
    this.data.booking.created_by_id !== this.data.booking.booked_for_id;
  readonly dates = computed<string>(() =>
    formatDateRange(this.languageService.language(), this.booking.start_date, this.booking.end_date));
  readonly createdByLabel = computed<string>(() =>
    fill(this.t().bookingDetails.createdBy, {name: this.booking.created_by_name}));
  readonly noteCtrl = new FormControl<string>(this.data.booking.note, {nonNullable: true});
  readonly isSaving = signal<boolean>(false);
  readonly isDeleting = signal<boolean>(false);

  protected readonly featherX = featherX;
  protected readonly featherTrash2 = featherTrash2;

  async onSave(): Promise<void> {
    if (this.isSaving()) {
      return;
    }
    this.isSaving.set(true);
    try {
      await updateUnitBookingView({body: {note: this.noteCtrl.value.trim()}, path: {object_id: this.booking.id}});
      this.emitClose(true);
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: this.t().bookingDetails.saveFailed, text: `${err}`});
    } finally {
      this.isSaving.set(false);
    }
  }

  async onCancelBooking(): Promise<void> {
    if (this.isDeleting()) {
      return;
    }
    const t = this.t().bookingDetails;
    const confirmed = await this.dialogService.getBooleanFromConfirmationDialog({
      title: t.cancelBooking,
      text: fill(t.cancelConfirmText, {dates: this.dates()}),
      confirmActionName: t.cancelBooking,
      danger: true,
      cancelActionName: t.keep,
    });
    if (!confirmed) {
      return;
    }
    this.isDeleting.set(true);
    try {
      await deleteUnitBookingView({path: {object_id: this.booking.id}});
      this.emitClose(true);
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: this.t().common.error, text: `${err}`});
    } finally {
      this.isDeleting.set(false);
    }
  }

  onClose(): void {
    this.emitClose(false);
  }
}
