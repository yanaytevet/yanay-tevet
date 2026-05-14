import {Component, inject, OnInit, signal} from '@angular/core';
import {BaseDialogComponent} from '../../base-dialog.component';
import {FormBuilder, FormGroup, FormsModule, ReactiveFormsModule, Validators} from '@angular/forms';
import {bootstrapChevronDown} from '@ng-icons/bootstrap-icons';
import {ConfirmationButtonComponent} from '../../confirmation-button/confirmation-button.component';
import {SelectableBoxComponent} from '../../../components/selectable-box/selectable-box.component';
import {SelectInputComponent} from '../../../components/inputs/select-input/select-input.component';

export interface SingleSelectionOption {
  display: string;
  value: any;
}

export interface SingleSelectionDialogInput {
  title: string;
  text: string;
  options: SingleSelectionOption[];
  defaultValue?: any;
  cancelActionName?: string;
  confirmActionName?: string;
  allowEmpty?: boolean;
  label?: string;
  method?: 'buttons' | 'dropdown'; // the default is dropdown
  filterOptions?: boolean; // whether to show filter input for options
  otherOption?: boolean; // appends an "Other" entry; if selected, shows a text input and returns its value
  otherOptionLabel?: string; // label for the "Other" entry (default: "Other")
  otherOptionPlaceholder?: string; // placeholder for the free-text input (default: "Enter value...")
  otherOptionAllowEmpty?: boolean; // whether the free-text input can be empty (default: false)
  otherOptionDefaultValue?: string; // pre-fills the free-text input when "Other" is the default selection
}

@Component({
  selector: 'app-single-selection-dialog',
  imports: [ReactiveFormsModule, FormsModule, ConfirmationButtonComponent, SelectableBoxComponent, SelectInputComponent],
  templateUrl: './single-selection-dialog.component.html',
  standalone: true
})
export class SingleSelectionDialogComponent extends BaseDialogComponent<
  SingleSelectionDialogInput,
  any
> implements OnInit {
  static readonly OTHER_SENTINEL = '__other__';
  readonly fb = inject(FormBuilder);

  form: FormGroup;
  selectedOption: any = null;
  filterText = '';
  filteredOptions: SingleSelectionOption[] = [];
  otherText = '';
  protected readonly chevronDownIcon = bootstrapChevronDown;

  readonly isOtherSelected = signal(false);

  get allOptions(): SingleSelectionOption[] {
    if (!this.data.otherOption) {
      return this.data.options;
    }
    return [...this.data.options, {display: this.data.otherOptionLabel ?? 'Other', value: SingleSelectionDialogComponent.OTHER_SENTINEL}];
  }

  ngOnInit(): void {
    this.form = this.fb.group({
      selectedValue: [
        this.data.defaultValue ?? null,
        this.buildValidators()
      ],
      otherValue: ['', []],
    });

    if (this.data.defaultValue !== undefined) {
      this.selectedOption = this.data.defaultValue;
      this.form.get('selectedValue')?.setValue(this.data.defaultValue);
    }

    if (this.data.otherOption && this.data.defaultValue === SingleSelectionDialogComponent.OTHER_SENTINEL) {
      this.isOtherSelected.set(true);
      this.otherText = this.data.otherOptionDefaultValue ?? '';
    }

    this.filteredOptions = [...this.allOptions];
  }

  filterOptions(): void {
    if (!this.filterText.trim()) {
      this.filteredOptions = [...this.allOptions];
    } else {
      const searchTerm = this.filterText.toLowerCase().trim();
      this.filteredOptions = this.allOptions.filter(option =>
        option.display.toLowerCase().includes(searchTerm)
      );
    }
  }

  private buildValidators() {
    const validators = [];

    if (this.data.allowEmpty !== true) {
      validators.push(Validators.required);
    }

    return validators;
  }

  get selectionControl() {
    return this.form.get('selectedValue');
  }

  hasError(errorName: string): boolean {
    return this.selectionControl?.errors?.[errorName] &&
           (this.selectionControl.touched || this.selectionControl.dirty);
  }

  getErrorMessage(): string | null {
    if (this.hasError('required')) {
      return 'Please select an option';
    }

    return null;
  }

  onConfirm(): void {
    this.form.markAllAsTouched();

    if (!this.form.valid) {
      return;
    }

    const selected = this.selectionControl?.value;
    if (this.data.otherOption && selected === SingleSelectionDialogComponent.OTHER_SENTINEL) {
      const otherVal = this.otherText.trim();
      if (!this.data.otherOptionAllowEmpty && !otherVal) {
        return;
      }
      this.emitClose(otherVal || null);
    } else {
      this.emitClose(selected);
    }
  }

  toggleValue(value: any): void {
    if (this.selectedOption === value) {
      this.selectedOption = null;
      this.selectionControl?.setValue(null);
      if (this.data.otherOption) {
        this.isOtherSelected.set(false);
      }
    } else {
      this.selectedOption = value;
      this.selectionControl?.setValue(value);
      if (this.data.otherOption) {
        this.isOtherSelected.set(value === SingleSelectionDialogComponent.OTHER_SENTINEL);
      }
    }
  }

  isSelected(value: any): boolean {
    return this.selectedOption === value;
  }
}
