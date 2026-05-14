import {Component, OnInit} from '@angular/core';
import {BaseDialogComponent} from '../../base-dialog.component';
import {FormBuilder, FormGroup, ReactiveFormsModule, Validators} from '@angular/forms';

import {ConfirmationButtonComponent} from '../../confirmation-button/confirmation-button.component';

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

  constructor(private fb: FormBuilder) {
    super();
  }

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
      return 'This field is required';
    }

    if (this.hasError('min')) {
      return `Value must be at least ${this.data.minValue}`;
    }

    if (this.hasError('max')) {
      return `Value must be at most ${this.data.maxValue}`;
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
