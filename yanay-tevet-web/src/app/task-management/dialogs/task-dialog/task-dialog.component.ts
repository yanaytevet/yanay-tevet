import {Component, computed} from '@angular/core';
import {toSignal} from '@angular/core/rxjs-interop';
import {FormControl, ReactiveFormsModule} from '@angular/forms';
import {NgIcon, provideIcons} from '@ng-icons/core';
import {featherX} from '@ng-icons/feather-icons';
import {TaskPriority, TaskStatus} from '../../../../generated-files/api/task-management';
import {BaseDialogComponent} from '../../../common/dialogs/base-dialog.component';
import {
  TASK_PRIORITY_LABELS,
  TASK_PRIORITY_ORDER,
  TASK_STATUS_LABELS,
  TASK_STATUS_ORDER,
} from '../../task-management.constants';

export interface TaskDialogItineraryList {
  id: number;
  name: string;
}

export interface TaskDialogData {
  title: string;
  confirmActionName: string;
  name: string;
  description: string;
  status: TaskStatus;
  priority: TaskPriority;
  dueAt: string | null;
  itineraryListId: number | null;
  showStatus: boolean;
  itineraryLists: TaskDialogItineraryList[];
}

export interface TaskDialogResult {
  name: string;
  description: string;
  status: TaskStatus;
  priority: TaskPriority;
  dueAt: string | null;
  itineraryListId: number | null;
}

@Component({
  selector: 'app-task-dialog',
  standalone: true,
  imports: [ReactiveFormsModule, NgIcon],
  providers: [provideIcons({featherX})],
  templateUrl: './task-dialog.component.html',
})
export class TaskDialogComponent extends BaseDialogComponent<TaskDialogData, TaskDialogResult> {
  readonly nameCtrl = new FormControl<string>('', {nonNullable: true});
  readonly descriptionCtrl = new FormControl<string>('', {nonNullable: true});
  readonly statusCtrl = new FormControl<TaskStatus>('todo', {nonNullable: true});
  readonly priorityCtrl = new FormControl<TaskPriority>('none', {nonNullable: true});
  readonly dueAtCtrl = new FormControl<string>('', {nonNullable: true});
  readonly itineraryListCtrl = new FormControl<number | null>(null);

  readonly statusOrder = TASK_STATUS_ORDER;
  readonly statusLabels = TASK_STATUS_LABELS;
  readonly priorityOrder = TASK_PRIORITY_ORDER;
  readonly priorityLabels = TASK_PRIORITY_LABELS;

  private readonly nameValue = toSignal(this.nameCtrl.valueChanges, {initialValue: ''});
  readonly canSave = computed(() => !!this.nameValue()?.trim());

  protected readonly featherX = featherX;

  constructor() {
    super();
    this.nameCtrl.setValue(this.data.name);
    this.descriptionCtrl.setValue(this.data.description);
    this.statusCtrl.setValue(this.data.status);
    this.priorityCtrl.setValue(this.data.priority);
    this.itineraryListCtrl.setValue(this.data.itineraryListId);
    if (this.data.dueAt) {
      this.dueAtCtrl.setValue(this.toDatetimeLocal(this.data.dueAt));
    }
  }

  onSave(): void {
    const name = this.nameCtrl.value.trim();
    if (!name) {
      return;
    }
    const local = this.dueAtCtrl.value.trim();
    this.emitClose({
      name,
      description: this.descriptionCtrl.value.trim(),
      status: this.statusCtrl.value,
      priority: this.priorityCtrl.value,
      dueAt: local ? new Date(local).toISOString() : null,
      itineraryListId: this.itineraryListCtrl.value ?? null,
    });
  }

  onClose(): void {
    this.emitClose(null);
  }

  private toDatetimeLocal(iso: string): string {
    const date = new Date(iso);
    const offsetMs = date.getTimezoneOffset() * 60000;
    return new Date(date.getTime() - offsetMs).toISOString().slice(0, 16);
  }
}
