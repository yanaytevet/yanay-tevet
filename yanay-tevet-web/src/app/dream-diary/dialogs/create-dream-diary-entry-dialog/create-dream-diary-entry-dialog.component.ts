import {Component} from '@angular/core';
import {FormControl, ReactiveFormsModule} from '@angular/forms';
import {createDreamDiaryEntryView, DreamDiaryEntrySchema} from '../../../../generated-files/api/dream-diary';
import {BaseDialogComponent} from '../../../common/dialogs/base-dialog.component';
import {ConfirmationButtonComponent} from '../../../common/dialogs/confirmation-button/confirmation-button.component';

@Component({
  selector: 'app-create-dream-diary-entry-dialog',
  standalone: true,
  imports: [ReactiveFormsModule, ConfirmationButtonComponent],
  templateUrl: './create-dream-diary-entry-dialog.component.html',
})
export class CreateDreamDiaryEntryDialogComponent extends BaseDialogComponent<void, DreamDiaryEntrySchema | null> {
  titleCtrl = new FormControl<string>('');
  textCtrl = new FormControl<string>('');
  timeCtrl = new FormControl<string>(this.getTodayLocalDatetimeString());
  isSaving = false;

  private getTodayLocalDatetimeString(): string {
    const now = new Date();
    const pad = (n: number) => String(n).padStart(2, '0');
    return `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}T${pad(now.getHours())}:${pad(now.getMinutes())}`;
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
        : new Date().toISOString();
      const res = await createDreamDiaryEntryView({
        body: {
          title: this.titleCtrl.value?.trim() || '',
          text,
          time,
        },
      });
      this.emitClose(res.data);
    } finally {
      this.isSaving = false;
    }
  }
}
