import {Component, OnInit} from '@angular/core';
import {BaseDialogComponent} from '../../base-dialog.component';
import {FormBuilder, FormGroup, ReactiveFormsModule, Validators} from '@angular/forms';

import {ConfirmationButtonComponent} from '../../confirmation-button/confirmation-button.component';

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

  constructor(private fb: FormBuilder) {
    super();
  }

  ngOnInit(): void {
    this.form = this.fb.group({
      minValue: [
        this.data.defaultMinValue ?? null,
        this.buildValidators('min')
      ],
      maxValue: [
        this.data.defaultMaxValue ?? null,
        this.buildValidators('max')
      ]
    }, { validators: this.rangeValidator });
  }

  private buildValidators(type: 'min' | 'max') {
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
      return 'This field is required';
    }

    if (this.hasError(control, 'min')) {
      return `Value must be at least ${this.data.globalMinValue}`;
    }

    if (this.hasError(control, 'max')) {
      return `Value must be at most ${this.data.globalMaxValue}`;
    }

    return null;
  }

  getFormErrorMessage(): string | null {
    if (this.form.errors?.['invalidRange']) {
      return 'Minimum value must be less than or equal to maximum value';
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
