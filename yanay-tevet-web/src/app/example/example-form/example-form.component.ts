import {Component, inject} from '@angular/core';
import {FormControl, FormsModule, ReactiveFormsModule} from '@angular/forms';

import {CheckboxInputComponent} from '../../common/components/inputs/checkbox-input/checkbox-input.component';
import {BasePageComponent} from '../../common/components/base-page-component';
import {InputDebounce} from '../../common/data/input-debouncer';
import {Option} from '../../common/interfaces/util/option';

@Component({
  selector: 'app-example-form',
  imports: [FormsModule, ReactiveFormsModule, CheckboxInputComponent],
  templateUrl: './example-form.component.html',
  styleUrl: './example-form.component.css'
})
export class ExampleFormComponent extends BasePageComponent{

  canEditCtrl = new FormControl<boolean>(true);
  inputDebouncer = new InputDebounce<string>();
  textAreaDebouncer = new InputDebounce<string>();
  values: string[] = [];
  options: Option[] = [
    {value: 'test1', display: 'Test 1'},
    {value: 'test2', display: 'Test 2'},
    {value: 'test3', display: 'Test 3'},
  ];

  constructor() {
    super();
    this.inputDebouncer.setValueWithoutTrigger('test');
    this.updateDisabled();

    this.subscriptions.push(this.canEditCtrl.valueChanges.subscribe(() => {
      this.updateDisabled();
    }));

    this.subscriptions.push(this.inputDebouncer.valueChangedFinished$.subscribe(newVal => {
      this.values.push(newVal);
    }));

    this.subscriptions.push(this.textAreaDebouncer.valueChangedFinished$.subscribe(newVal => {
      this.values.push(newVal);
    }));
  }

  updateDisabled() {
    const canEdit = this.canEditCtrl.value;
    if (canEdit) {
      this.inputDebouncer.ctrl.enable({emitEvent: false});
      this.textAreaDebouncer.ctrl.enable({emitEvent: false});
    } else {
      this.inputDebouncer.ctrl.disable({emitEvent: false});
      this.textAreaDebouncer.ctrl.disable({emitEvent: false});
    }
  }
}
