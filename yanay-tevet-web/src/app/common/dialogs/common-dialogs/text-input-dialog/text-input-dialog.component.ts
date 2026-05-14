import {Component, inject, OnInit} from '@angular/core';
import {BaseDialogComponent} from '../../base-dialog.component';
import {FormBuilder, FormGroup, ReactiveFormsModule, Validators} from '@angular/forms';

import {ConfirmationButtonComponent} from '../../confirmation-button/confirmation-button.component';

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
      return 'This field is required';
    }

    if (this.hasError('maxlength')) {
      return `Maximum length is ${this.data.maxLength} characters`;
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
