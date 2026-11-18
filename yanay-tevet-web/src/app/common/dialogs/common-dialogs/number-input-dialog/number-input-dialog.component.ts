import {Component, inject, OnInit} from '@angular/core';
import {BaseDialogComponent} from '../../base-dialog.component';
import {FormBuilder, FormGroup, ReactiveFormsModule, Validators} from '@angular/forms';

import {ConfirmationButtonComponent} from '../../confirmation-button/confirmation-button.component';
import {COMMON_STRINGS} from '../../../../common/i18n';
import {LanguageService} from '../../../../shared/i18n/language.service';
import {injectStrings, fill} from '../../../../shared/i18n/strings';

export interface NumberInputDialogInput {
  title: string;
  text: string;
  label: string;
  defaultValue?: number;
  cancelActionName?: string;
  confirmActionName?: string;
  allowEmpty?: boolean;
  maxValue?: number;
  minValue?: number;
}

@Component({
  selector: 'app-number-input-dialog',
  imports: [ReactiveFormsModule, ConfirmationButtonComponent],
  templateUrl: './number-input-dialog.component.html',
  standalone: true
})
export class NumberInputDialogComponent extends BaseDialogComponent<
  NumberInputDialogInput,
  number | null
> implements OnInit {
  form: FormGroup;
  readonly fb = inject(FormBuilder)
  protected readonly t = injectStrings(COMMON_STRINGS);
  private readonly languageService = inject(LanguageService);

  ngOnInit(): void {
    this.form = this.fb.group({
      inputValue: [
        this.data.defaultValue ?? null,
        this.buildValidators()
      ]
    });
  }

  private buildValidators() {
    const validators = [];

    if (this.data.allowEmpty !== true) {
      validators.push(Validators.required);
    }

    if (this.data.minValue !== undefined) {
      validators.push(Validators.min(this.data.minValue));
    }

    if (this.data.maxValue !== undefined) {
      validators.push(Validators.max(this.data.maxValue));
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

    if (this.hasError('min')) {
      return fill(this.t().errors.atLeast, {min: this.data.minValue.toLocaleString(this.languageService.language())});
    }

    if (this.hasError('max')) {
      return fill(this.t().errors.atMost, {max: this.data.maxValue.toLocaleString(this.languageService.language())});
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
