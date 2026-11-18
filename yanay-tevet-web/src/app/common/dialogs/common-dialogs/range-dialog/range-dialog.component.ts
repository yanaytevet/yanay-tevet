import {Component, inject, OnInit} from '@angular/core';
import {BaseDialogComponent} from '../../base-dialog.component';
import {FormBuilder, FormGroup, ReactiveFormsModule, Validators} from '@angular/forms';

import {ConfirmationButtonComponent} from '../../confirmation-button/confirmation-button.component';
import {COMMON_STRINGS} from '../../../../common/i18n';
import {LanguageService} from '../../../../shared/i18n/language.service';
import {injectStrings, fill} from '../../../../shared/i18n/strings';

export interface RangeDialogInput {
  title: string;
  text: string;
  minLabel?: string;
  maxLabel?: string;
  defaultMinValue?: number;
  defaultMaxValue?: number;
  cancelActionName?: string;
  confirmActionName?: string;
  allowEmpty?: boolean;
  globalMaxValue?: number;
  globalMinValue?: number;
}

export interface RangeDialogOutput {
  min: number | null;
  max: number | null;
}

@Component({
  selector: 'app-range-dialog',
  imports: [ReactiveFormsModule, ConfirmationButtonComponent],
  templateUrl: './range-dialog.component.html',
  standalone: true
})
export class RangeDialogComponent extends BaseDialogComponent<
  RangeDialogInput,
  RangeDialogOutput | null
> implements OnInit {
  form: FormGroup;
  readonly fb = inject(FormBuilder)
  protected readonly t = injectStrings(COMMON_STRINGS);
  private readonly languageService = inject(LanguageService);

  ngOnInit(): void {
    this.form = this.fb.group({
      minValue: [
        this.data.defaultMinValue ?? null,
        this.buildValidators()
      ],
      maxValue: [
        this.data.defaultMaxValue ?? null,
        this.buildValidators()
      ]
    }, { validators: this.rangeValidator });
  }

  private buildValidators() {
    const validators = [];

    if (this.data.allowEmpty !== true) {
      // At least one of min or max should be provided, but not necessarily both
      // This is handled by the form-level validator
    }

    if (this.data.globalMinValue !== undefined) {
      validators.push(Validators.min(this.data.globalMinValue));
    }

    if (this.data.globalMaxValue !== undefined) {
      validators.push(Validators.max(this.data.globalMaxValue));
    }

    return validators;
  }

  private rangeValidator(form: FormGroup) {
    const minValue = form.get('minValue')?.value;
    const maxValue = form.get('maxValue')?.value;

    // If both values are provided, ensure min <= max
    if (minValue !== null && maxValue !== null && minValue > maxValue) {
      return { invalidRange: true };
    }

    return null;
  }

  get minControl() {
    return this.form.get('minValue');
  }

  get maxControl() {
    return this.form.get('maxValue');
  }

  hasError(control: 'min' | 'max', errorName: string): boolean {
    const formControl = control === 'min' ? this.minControl : this.maxControl;
    return formControl?.errors?.[errorName] &&
           (formControl.touched || formControl.dirty);
  }

  getErrorMessage(control: 'min' | 'max'): string | null {
    if (this.hasError(control, 'required')) {
      return this.t().errors.required;
    }

    if (this.hasError(control, 'min')) {
      return fill(this.t().errors.atLeast, {min: this.data.globalMinValue.toLocaleString(this.languageService.language())});
    }

    if (this.hasError(control, 'max')) {
      return fill(this.t().errors.atMost, {max: this.data.globalMaxValue.toLocaleString(this.languageService.language())});
    }

    return null;
  }

  getFormErrorMessage(): string | null {
    if (this.form.errors?.['invalidRange']) {
      return this.t().errors.invalidRange;
    }

    return null;
  }

  onConfirm(): void {
    // Mark form as touched to trigger validation messages
    this.form.markAllAsTouched();

    if (this.form.valid) {
      // If both values are null and allowEmpty is false, don't close
      if (!this.data.allowEmpty &&
          this.minControl?.value === null &&
          this.maxControl?.value === null) {
        return;
      }

      this.emitClose({
        min: this.minControl?.value,
        max: this.maxControl?.value
      });
    }
  }
}
