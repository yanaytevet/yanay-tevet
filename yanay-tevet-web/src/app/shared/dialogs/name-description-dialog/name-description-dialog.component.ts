import {Component} from '@angular/core';
import {BaseDialogComponent} from '../../../common/dialogs/base-dialog.component';
import {FormControl, FormGroup, ReactiveFormsModule, Validators} from '@angular/forms';
import {ConfirmationButtonComponent} from '../../../common/dialogs/confirmation-button/confirmation-button.component';
import {COMMON_STRINGS} from '../../../common/i18n';
import {injectStrings} from '../../../shared/i18n/strings';

export interface NameDescriptionDialogInput {
  title: string;
  text: string;
  nameLabel: string;
  descriptionLabel: string;
  defaultName?: string;
  defaultDescription?: string;
  cancelActionName?: string;
  confirmActionName?: string;
}

export interface NameDescriptionDialogOutput {
  name: string;
  description: string;
}

@Component({
  selector: 'app-name-description-dialog',
  imports: [
    ReactiveFormsModule,
    ConfirmationButtonComponent
  ],
  templateUrl: './name-description-dialog.component.html',
  standalone: true
})
export class NameDescriptionDialogComponent extends BaseDialogComponent<
    NameDescriptionDialogInput,
    NameDescriptionDialogOutput
> {
  protected readonly t = injectStrings(COMMON_STRINGS);
  form = new FormGroup({
    name: new FormControl(this.data.defaultName ?? '', Validators.required),
    description: new FormControl(this.data.defaultDescription ?? ''),
  });

  protected emitSubmit() {
    if (!this.form.valid) {
      return;
    }
    this.emitClose({
      name: this.form.value.name,
      description: this.form.value.description,
    });
  }
}
