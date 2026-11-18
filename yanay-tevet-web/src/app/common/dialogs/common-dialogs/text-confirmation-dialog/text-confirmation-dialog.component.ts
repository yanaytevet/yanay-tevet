import {Component, computed, inject, OnInit} from '@angular/core';
import {BaseDialogComponent} from '../../base-dialog.component';
import {FormBuilder, FormGroup, ReactiveFormsModule, Validators, AbstractControl, ValidationErrors} from '@angular/forms';
import {COMMON_STRINGS} from '../../../../common/i18n';
import {injectStrings, fill} from '../../../../shared/i18n/strings';

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
  imports: [ReactiveFormsModule],
  templateUrl: './text-confirmation-dialog.component.html',
  standalone: true
})
export class TextConfirmationDialogComponent extends BaseDialogComponent<
  TextConfirmationDialogInput,
  boolean
> implements OnInit {
  private fb = inject(FormBuilder);
  form: FormGroup;
  protected readonly t = injectStrings(COMMON_STRINGS);
  protected readonly typeToConfirm = computed(() => fill(this.t().typeToConfirm, {text: this.data.validationText}));

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
