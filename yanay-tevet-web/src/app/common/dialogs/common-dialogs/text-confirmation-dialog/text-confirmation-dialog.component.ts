import {Component, inject, OnInit} from '@angular/core';
import {BaseDialogComponent} from '../../base-dialog.component';
import {FormBuilder, FormGroup, ReactiveFormsModule, Validators, AbstractControl, ValidationErrors} from '@angular/forms';
import {ConfirmationButtonComponent} from '../../confirmation-button/confirmation-button.component';

export interface TextConfirmationDialogInput {
  title: string;
  text: string;
  label: string;
  validationText: string;
  cancelActionName?: string;
  confirmActionName?: string;
}

@Component({
  selector: 'app-text-confirmation-dialog',
  imports: [ReactiveFormsModule, ConfirmationButtonComponent],
  templateUrl: './text-confirmation-dialog.component.html',
  standalone: true
})
export class TextConfirmationDialogComponent extends BaseDialogComponent<
  TextConfirmationDialogInput,
  boolean
> implements OnInit {
  private fb = inject(FormBuilder);
  form: FormGroup;

  constructor() {
    super();
  }

  ngOnInit(): void {
    this.form = this.fb.group({
      inputValue: [
        '',
        [Validators.required, this.validateMatch.bind(this)]
      ]
    });
  }

  private validateMatch(control: AbstractControl): ValidationErrors | null {
    if (control.value !== this.data.validationText) {
      return {mismatch: true};
    }
    return null;
  }

  get inputControl() {
    return this.form.get('inputValue');
  }

  onConfirm(): void {
    this.form.markAllAsTouched();

    if (this.form.valid) {
      this.emitClose(true);
    }
  }

  onCancel(): void {
    this.emitClose(false);
  }
}
