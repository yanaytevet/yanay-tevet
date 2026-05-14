import {Component, inject, signal} from '@angular/core';
import {
  bootstrapBell,
  bootstrapCheckSquare,
  bootstrapInputCursorText,
  bootstrapListCheck,
  bootstrapQuestion,
  bootstrapType
} from '@ng-icons/bootstrap-icons';
import { CommonModule, NgClass } from '@angular/common';
import {NgIconComponent} from '@ng-icons/core';
import {BasePageComponent} from '../../common/components/base-page-component';
import {DialogService} from '../../common/dialogs/dialogs.service';
import {Action} from '../../common/interfaces/util/action';

@Component({
  selector: 'app-example-dialogs',
  imports: [
    CommonModule,
    NgClass,
    NgIconComponent
  ],
  templateUrl: './example-dialogs.component.html',
  styleUrl: './example-dialogs.component.css',
  standalone: true
})
export class ExampleDialogsComponent extends BasePageComponent{
  dialogService = inject(DialogService);
  data = signal<string>('');

  constructor() {
    super();
  }

  actions: Action[] = [
    {
      display: 'Confirmation',
      icon: bootstrapQuestion,
      callback: async () => {
        this.setData(await this.dialogService.getBooleanFromConfirmationDialog({
          title: 'Confirmation Dialog',
          text: 'This is a confirmation dialog. Do you want to continue?',
          cancelActionName: 'No',
          confirmActionName: 'Yes',
        }));
      }
    },
    {
      display: 'Notification',
      icon: bootstrapBell,
      callback: async () => {
        await this.dialogService.showNotificationDialog({
          title: 'Notification Dialog',
          text: 'This is a notification dialog with important information.',
          confirmActionName: 'Got it',
          showCopyButton: true,
        });
        this.setData('Notification dialog closed');
      }
    },
    {
      display: 'Number Input',
      icon: bootstrapInputCursorText,
      callback: async () => {
        const result = await this.dialogService.getNumberFromInputDialog({
          title: 'Number Input Dialog',
          text: 'Please enter a number between 1 and 100:',
          label: 'Number',
          minValue: 1,
          maxValue: 100,
          cancelActionName: 'Cancel',
          confirmActionName: 'Submit',
          allowEmpty: false
        });
        this.setData(result !== null ? result : 'Dialog canceled');
      }
    },
    {
      display: 'Text Input',
      icon: bootstrapType,
      callback: async () => {
        const result = await this.dialogService.getTextFromInputDialog({
          title: 'Text Input Dialog',
          text: 'Please enter some text:',
          label: 'Text',
          defaultValue: '',
          maxLength: 100,
          cancelActionName: 'Cancel',
          confirmActionName: 'Submit',
          allowEmpty: false
        });
        this.setData(result !== null ? result : 'Dialog canceled');
      }
    },
    {
      display: 'Text Area Input',
      icon: bootstrapType,
      callback: async () => {
        const result = await this.dialogService.getTextFromInputDialog({
          title: 'Text Area Input Dialog',
          text: 'Please enter a longer text:',
          label: 'Comments',
          defaultValue: '',
          maxLength: 500,
          isTextArea: true,
          textAreaRows: 6,
          cancelActionName: 'Cancel',
          confirmActionName: 'Submit',
          allowEmpty: false
        });
        this.setData(result !== null ? result : 'Dialog canceled');
      }
    },
    {
      display: 'Selection Dropdown',
      icon: bootstrapListCheck,
      callback: async () => {
        const result = await this.dialogService.getValueFromSelectionDialog({
          title: 'Selection Dialog (Dropdown)',
          text: 'Please select an option from the dropdown:',
          label: 'Options',
          options: [
            { display: 'Option 1', value: 'option1' },
            { display: 'Option 2', value: 'option2' },
            { display: 'Option 3', value: 'option3' }
          ],
          defaultValue: 'option1',
          cancelActionName: 'Cancel',
          confirmActionName: 'Submit',
          allowEmpty: false,
          method: 'dropdown'
        });
        this.setData(result !== null ? result : 'Dialog canceled');
      }
    },
    {
      display: 'Selection Buttons',
      icon: bootstrapListCheck,
      callback: async () => {
        const result = await this.dialogService.getValueFromSelectionDialog({
          title: 'Selection Dialog (Buttons)',
          text: 'Please select one of the following options:',
          options: [
            { display: 'Option A', value: 'optionA' },
            { display: 'Option B', value: 'optionB' },
            { display: 'Option C', value: 'optionC' }
          ],
          cancelActionName: 'Cancel',
          allowEmpty: false,
          method: 'buttons'
        });
        this.setData(result !== null ? result : 'Dialog canceled');
      }
    },
    {
      display: 'Multiple Selection',
      icon: bootstrapCheckSquare,
      callback: async () => {
        const result = await this.dialogService.getValuesFromMultipleSelectionDialog({
          title: 'Multiple Selection Dialog',
          text: 'Please select one or more options:',
          options: [
            { display: 'Option 1', value: 'option1', isChecked: true },
            { display: 'Option 2', value: 'option2' },
            { display: 'Option 3', value: 'option3' },
            { display: 'Option 4', value: 'option4' }
          ],
          cancelActionName: 'Cancel',
          confirmActionName: 'Submit',
          allowEmpty: false
        });
        this.setData(result !== null ? JSON.stringify(result) : 'Dialog canceled');
      }
    },
  ]

  private setData(val: string | number | boolean): void {
    this.data.set(val.toString());
  }
}
