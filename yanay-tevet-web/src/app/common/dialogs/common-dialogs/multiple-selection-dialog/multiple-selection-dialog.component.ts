import {Component, OnInit} from '@angular/core';
import {BaseDialogComponent} from '../../base-dialog.component';
import {AbstractControl, FormArray, FormBuilder, FormGroup, ReactiveFormsModule} from '@angular/forms';

import {FormsModule} from '@angular/forms';
import {bootstrapCheck} from '@ng-icons/bootstrap-icons';
import {ConfirmationButtonComponent} from '../../confirmation-button/confirmation-button.component';
import {SelectableBoxComponent} from '../../../components/selectable-box/selectable-box.component';

export interface MultipleSelectionOption {
  display: string;
  value: any;
  isChecked?: boolean;
}

export interface MultipleSelectionDialogInput {
  title: string;
  text: string;
  options: MultipleSelectionOption[];
  cancelActionName?: string;
  confirmActionName?: string;
  allowEmpty?: boolean;
  filterOptions?: boolean; // whether to show filter input for options
}

@Component({
  selector: 'app-multiple-selection-dialog',
  imports: [ReactiveFormsModule, FormsModule, ConfirmationButtonComponent, SelectableBoxComponent],
  templateUrl: './multiple-selection-dialog.component.html',
  standalone: true
})
export class MultipleSelectionDialogComponent extends BaseDialogComponent<
  MultipleSelectionDialogInput,
  any[]
> implements OnInit {
  form: FormGroup;
  filterText = '';
  filteredOptions: MultipleSelectionOption[] = [];
  protected readonly checkIcon = bootstrapCheck;

  constructor(private fb: FormBuilder) {
    super();
  }

  ngOnInit(): void {
    const optionsArray = this.fb.array(
      this.data.options.map(option => this.fb.control(option.isChecked || false))
    );

    this.form = this.fb.group({
      selectedOptions: optionsArray
    });

    // Apply validators to the form array and update the form
    if (this.data.allowEmpty !== true) {
      this.optionsFormArray.setValidators(this.atLeastOneSelectedValidator());
      this.optionsFormArray.updateValueAndValidity();
    }

    // Initialize filteredOptions
    this.filteredOptions = [...this.data.options];
  }

  filterOptions(): void {
    if (!this.filterText.trim()) {
      this.filteredOptions = [...this.data.options];
    } else {
      const searchTerm = this.filterText.toLowerCase().trim();
      this.filteredOptions = this.data.options.filter(option =>
        option.display.toLowerCase().includes(searchTerm)
      );
    }
  }

  get optionsFormArray(): FormArray {
    return this.form.get('selectedOptions') as FormArray;
  }

  private atLeastOneSelectedValidator() {
    return (control: AbstractControl) => {
      const formArray = control as FormArray;
      const selectedCount = formArray.controls.filter(control => control.value === true).length;
      return selectedCount > 0 ? null : { required: true };
    };
  }

  hasError(errorName: string): boolean {
    return this.optionsFormArray.errors?.[errorName] &&
           (this.optionsFormArray.touched || this.optionsFormArray.dirty);
  }

  getErrorMessage(): string | null {
    if (this.hasError('required')) {
      return 'Please select at least one option';
    }

    return null;
  }

  onConfirm(): void {
    // Mark form array as touched to trigger validation messages
    this.optionsFormArray.markAllAsTouched();

    // Update validity
    this.optionsFormArray.updateValueAndValidity();

    if (this.optionsFormArray.valid) {
      const selectedValues = this.data.options
        .filter((_, index) => this.optionsFormArray.at(index).value)
        .map(option => option.value);

      this.emitClose(selectedValues);
    }
  }

  toggleOption(index: number): void {
    const control = this.optionsFormArray.at(index);
    control.setValue(!control.value);
    control.markAsTouched();
  }

  isSelected(index: number): boolean {
    return this.optionsFormArray.at(index).value === true;
  }
}
