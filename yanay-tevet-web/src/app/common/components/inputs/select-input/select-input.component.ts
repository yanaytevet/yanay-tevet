import { Component, input, signal } from '@angular/core';
import { ControlValueAccessor, FormsModule, NG_VALUE_ACCESSOR, ReactiveFormsModule } from '@angular/forms';
import { NgIcon } from '@ng-icons/core';
import { bootstrapChevronDown } from '@ng-icons/bootstrap-icons';
import {NgClass} from '@angular/common';

export interface SelectOption {
  display: string;
  value: any;
}

@Component({
  selector: 'app-select-input',
  standalone: true,
  imports: [ReactiveFormsModule, FormsModule, NgIcon, NgClass],
  templateUrl: './select-input.component.html',
  styleUrl: './select-input.component.css',
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: SelectInputComponent,
      multi: true,
    },
  ],
})
export class SelectInputComponent implements ControlValueAccessor {
  options = input.required<SelectOption[]>();
  allowEmpty = input<boolean>(false);
  emptyValueDisplay = input<string>('No Value');
  className = input<string>('flex-1');
  selectClassName = input<string>('');
  errorClassName = input<string>('border-red-500');
  hasError = input<boolean>(false);
  bgClassName = input<string>('bg-layer-2');

  value = signal<any>(null);
  disabled = signal<boolean>(false);

  protected readonly chevronDownIcon = bootstrapChevronDown;

  // Called by Angular to write a value from the form model into the view
  writeValue(val: any): void {
    this.value.set(val);
  }

  // Register a function to propagate changes
  onChange: (value: any) => void = () => {};

  registerOnChange(fn: (value: any) => void): void {
    this.onChange = fn;
  }

  // Register a function to mark control as touched
  onTouched: () => void = () => {};

  registerOnTouched(fn: () => void): void {
    this.onTouched = fn;
  }

  // Support disabled state
  setDisabledState(isDisabled: boolean): void {
    this.disabled.set(isDisabled);
  }

  // Handle change event from native select
  onValueChange(newValue: any): void {
    this.value.set(newValue);
    this.onChange(newValue);
    this.onTouched();
  }
}
