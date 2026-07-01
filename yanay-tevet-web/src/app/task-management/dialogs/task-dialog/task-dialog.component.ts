import {Component, computed, signal} from '@angular/core';
import {toSignal} from '@angular/core/rxjs-interop';
import {FormControl, ReactiveFormsModule} from '@angular/forms';
import {NgIcon, provideIcons} from '@ng-icons/core';
import {featherCheck, featherRotateCcw, featherX} from '@ng-icons/feather-icons';
import {TaskPriority, TaskStatus} from '../../../../generated-files/api/task-management';
import {BaseDialogComponent} from '../../../common/dialogs/base-dialog.component';
import {
  describeRepeatSchedule,
  formatRepeatDays,
  REPEAT_PRESETS,
  TASK_PRIORITY_LABELS,
  TASK_PRIORITY_ORDER,
  WEEKDAYS,
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
  isRepeating: boolean;
  repeatDays: number[];
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
  isRepeating: boolean;
  repeatDays: number[];
  itineraryListId: number | null;
}

@Component({
  selector: 'app-task-dialog',
  standalone: true,
  imports: [ReactiveFormsModule, NgIcon],
  providers: [provideIcons({featherCheck, featherRotateCcw, featherX})],
  templateUrl: './task-dialog.component.html',
})
export class TaskDialogComponent extends BaseDialogComponent<TaskDialogData, TaskDialogResult> {
  readonly nameCtrl = new FormControl<string>('', {nonNullable: true});
  readonly descriptionCtrl = new FormControl<string>('', {nonNullable: true});
  readonly priorityCtrl = new FormControl<TaskPriority>('none', {nonNullable: true});
  readonly dueAtCtrl = new FormControl<string>('', {nonNullable: true});
  readonly itineraryListCtrl = new FormControl<number | null>(null);

  readonly isDone = signal<boolean>(false);
  readonly isRepeating = signal<boolean>(false);
  readonly repeatDays = signal<number[]>([]);

  readonly priorityOrder = TASK_PRIORITY_ORDER;
  readonly priorityLabels = TASK_PRIORITY_LABELS;
  readonly weekdays = WEEKDAYS;
  readonly repeatPresets = REPEAT_PRESETS;

  readonly daySelected = computed(() => {
    const selected = new Set(this.repeatDays());
    return Object.fromEntries(WEEKDAYS.map(d => [d.value, selected.has(d.value)]));
  });
  readonly repeatSummary = computed(() => formatRepeatDays(this.repeatDays()));
  readonly repeatScheduleText = computed(() => describeRepeatSchedule(this.repeatDays()));

  private readonly nameValue = toSignal(this.nameCtrl.valueChanges, {initialValue: ''});
  readonly canSave = computed(() => !!this.nameValue()?.trim());

  protected readonly featherCheck = featherCheck;
  protected readonly featherRotateCcw = featherRotateCcw;
  protected readonly featherX = featherX;

  constructor() {
    super();
    this.nameCtrl.setValue(this.data.name);
    this.descriptionCtrl.setValue(this.data.description);
    this.isDone.set(this.data.status === 'done');
    this.isRepeating.set(this.data.isRepeating);
    this.repeatDays.set([...this.data.repeatDays]);
    this.priorityCtrl.setValue(this.data.priority);
    this.itineraryListCtrl.setValue(this.data.itineraryListId);
    if (this.data.dueAt) {
      this.dueAtCtrl.setValue(this.toDatetimeLocal(this.data.dueAt));
    }
  }

  toggleDone(): void {
    this.isDone.update(v => !v);
  }

  toggleRepeating(): void {
    this.isRepeating.update(v => !v);
  }

  toggleDay(value: number): void {
    this.repeatDays.update(days =>
      days.includes(value)
        ? days.filter(d => d !== value)
        : [...days, value].sort((a, b) => a - b));
  }

  applyPreset(days: number[]): void {
    this.repeatDays.set([...days]);
  }

  onSave(): void {
    const name = this.nameCtrl.value.trim();
    if (!name) {
      return;
    }
    const local = this.dueAtCtrl.value.trim();
    const status: TaskStatus = this.isDone() ? 'done' : 'todo';
    this.emitClose({
      name,
      description: this.descriptionCtrl.value.trim(),
      status,
      priority: this.priorityCtrl.value,
      dueAt: local ? new Date(local).toISOString() : null,
      isRepeating: this.isRepeating(),
      repeatDays: this.isRepeating() ? this.repeatDays() : [],
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
