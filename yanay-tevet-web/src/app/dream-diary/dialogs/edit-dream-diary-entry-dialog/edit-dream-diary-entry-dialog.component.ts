import {Component} from '@angular/core';
import {FormControl, ReactiveFormsModule} from '@angular/forms';
import {DreamDiaryEntrySchema, updateDreamDiaryEntryView} from '../../../../generated-files/api/dream-diary';
import {BaseDialogComponent} from '../../../common/dialogs/base-dialog.component';
import {ConfirmationButtonComponent} from '../../../common/dialogs/confirmation-button/confirmation-button.component';

@Component({
  selector: 'app-edit-dream-diary-entry-dialog',
  standalone: true,
  imports: [ReactiveFormsModule, ConfirmationButtonComponent],
  templateUrl: './edit-dream-diary-entry-dialog.component.html',
})
export class EditDreamDiaryEntryDialogComponent extends BaseDialogComponent<DreamDiaryEntrySchema, DreamDiaryEntrySchema | null> {
  titleCtrl = new FormControl<string>(this.data.title ?? '');
  textCtrl = new FormControl<string>(this.data.text);
  timeCtrl = new FormControl<string>(this.toLocalDatetimeString(this.data.time));
  isSaving = false;

  private toLocalDatetimeString(isoString: string): string {
    const d = new Date(isoString);
    const pad = (n: number) => String(n).padStart(2, '0');
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
  }

  get canSave(): boolean {
    return !!this.textCtrl.value?.trim() && !this.isSaving;
  }

  async onConfirm(): Promise<void> {
    const text = this.textCtrl.value?.trim();
    if (!text || this.isSaving) {
      return;
    }
    this.isSaving = true;
    try {
      const time = this.timeCtrl.value
        ? new Date(this.timeCtrl.value).toISOString()
        : this.data.time;
      const res = await updateDreamDiaryEntryView({
        body: {
          title: this.titleCtrl.value?.trim() ?? '',
          text,
          time,
        },
        path: {object_id: this.data.id},
      });
      this.emitClose(res.data);
    } finally {
      this.isSaving = false;
    }
  }
}
