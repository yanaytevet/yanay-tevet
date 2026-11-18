import {Component, computed} from '@angular/core';
import {toSignal} from '@angular/core/rxjs-interop';
import {FormControl, ReactiveFormsModule} from '@angular/forms';
import {NgIcon, provideIcons} from '@ng-icons/core';
import {featherX} from '@ng-icons/feather-icons';
import {BaseDialogComponent} from '../../../common/dialogs/base-dialog.component';
import {injectStrings} from '../../../shared/i18n/strings';
import {ITINERARY_STRINGS} from '../../i18n';

export interface ItemDialogData {
  // Picks the example placeholders: the dialog edits both packing items and tasks.
  kind: 'item' | 'task';
  title: string;
  name: string;
  description: string;
  confirmActionName: string;
}

export interface ItemDialogResult {
  name: string;
  description: string;
}

@Component({
  selector: 'app-item-dialog',
  standalone: true,
  imports: [ReactiveFormsModule, NgIcon],
  providers: [provideIcons({featherX})],
  templateUrl: './item-dialog.component.html',
})
export class ItemDialogComponent extends BaseDialogComponent<ItemDialogData, ItemDialogResult> {
  protected readonly t = injectStrings(ITINERARY_STRINGS);
  readonly isTask = this.data.kind === 'task';

  readonly nameCtrl = new FormControl<string>('', {nonNullable: true});
  readonly descriptionCtrl = new FormControl<string>('', {nonNullable: true});

  private readonly nameValue = toSignal(this.nameCtrl.valueChanges, {initialValue: ''});
  readonly canSave = computed(() => !!this.nameValue()?.trim());

  protected readonly featherX = featherX;

  constructor() {
    super();
    this.nameCtrl.setValue(this.data.name);
    this.descriptionCtrl.setValue(this.data.description);
  }

  onSave(): void {
    const name = this.nameCtrl.value.trim();
    if (!name) {
      return;
    }
    this.emitClose({name, description: this.descriptionCtrl.value.trim()});
  }

  onClose(): void {
    this.emitClose(null);
  }
}
