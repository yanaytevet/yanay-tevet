import {Component} from '@angular/core';
import {BaseDialogComponent} from '../../base-dialog.component';

export interface ConfirmationDialogInput {
  title: string;
  text: string;
  cancelActionName?: string;
  confirmActionName?: string;
}

@Component({
  selector: 'app-confirmation-dialog',
  imports: [],
  templateUrl: './confirmation-dialog.component.html',
  standalone: true
})
export class ConfirmationDialogComponent extends BaseDialogComponent<
    ConfirmationDialogInput,
    boolean
> {
}
