import {Component, inject, OnInit} from '@angular/core';
import {BaseDialogComponent} from '../../base-dialog.component';
import {FormBuilder, FormGroup, ReactiveFormsModule, Validators} from '@angular/forms';

import {ConfirmationButtonComponent} from '../../confirmation-button/confirmation-button.component';
import {COMMON_STRINGS} from '../../../../common/i18n';
import {LanguageService} from '../../../../shared/i18n/language.service';
import {injectStrings, plural} from '../../../../shared/i18n/strings';

export interface TextInputDialogInput {
  title: string;
  text: string;
  label: string;
  defaultValue?: string;
  cancelActionName?: string;
  confirmActionName?: string;
  inputType?: string;
  isTextArea?: boolean;
  textAreaRows?: number;
  maxLength?: number;
  allowEmpty?: boolean;
}

@Component({
  selector: 'app-text-input-dialog',
  imports: [ReactiveFormsModule, ConfirmationButtonComponent],
  templateUrl: './text-input-dialog.component.html',
  standalone: true
})
export class TextInputDialogComponent extends BaseDialogComponent<
  TextInputDialogInput,
  string | null
> implements OnInit {
  private fb = inject(FormBuilder);
  protected readonly t = injectStrings(COMMON_STRINGS);
  private readonly languageService = inject(LanguageService);
  form: FormGroup;

  constructor() {
    super();
  }

  ngOnInit(): void {
    this.form = this.fb.group({
      inputValue: [
        this.data.defaultValue ?? '',
        this.buildValidators()
      ]
    });
  }

  private buildValidators() {
    const validators = [];

    if (this.data.allowEmpty !== true) {
      validators.push(Validators.required);
    }

    if (this.data.maxLength !== undefined) {
      validators.push(Validators.maxLength(this.data.maxLength));
    }

    return validators;
  }

  get inputControl() {
    return this.form.get('inputValue');
  }

  hasError(errorName: string): boolean {
    return this.inputControl?.errors?.[errorName] &&
           (this.inputControl.touched || this.inputControl.dirty);
  }

  getErrorMessage(): string | null {
    if (this.hasError('required')) {
      return this.t().errors.required;
    }

    if (this.hasError('maxlength')) {
      return plural(this.languageService.language(), this.data.maxLength, this.t().errors.maxLength);
    }

    return null;
  }

  onConfirm(): void {
    // Mark form as touched to trigger validation messages
    this.form.markAllAsTouched();

    if (this.form.valid) {
      this.emitClose(this.inputControl?.value);
    }
  }
}
