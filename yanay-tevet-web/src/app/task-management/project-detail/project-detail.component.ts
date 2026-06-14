import {NgTemplateOutlet} from '@angular/common';
import {Component, computed, inject, signal} from '@angular/core';
import {FormControl, ReactiveFormsModule} from '@angular/forms';
import {ActivatedRoute} from '@angular/router';
import {NgIcon, provideIcons} from '@ng-icons/core';
import {
  featherArchive,
  featherArrowLeft,
  featherCheck,
  featherChevronDown,
  featherChevronRight,
  featherClock,
  featherCornerDownRight,
  featherEdit,
  featherLink,
  featherPlus,
  featherRotateCcw,
  featherShare2,
  featherTrash2,
} from '@ng-icons/feather-icons';
import {
  archiveTaskProjectView,
  createTaskView,
  deleteTaskProjectView,
  deleteTaskView,
  getTaskProjectView,
  listTaskProjectMembersView,
  paginateTasksView,
  shareTaskProjectView,
  TaskPriority,
  TaskProjectSchema,
  TaskSchema,
  unarchiveTaskProjectView,
  unshareTaskProjectView,
  updateTaskView,
} from '../../../generated-files/api/task-management';
import {paginateItineraryListsView} from '../../../generated-files/api/itinerary-lists';
import {AuthenticationService} from '../../common/authentication/authentication.service';
import {DialogService} from '../../common/dialogs/dialogs.service';
import {ShareDialogComponent} from '../../common/dialogs/share-dialog/share-dialog.component';
import {RoutingService} from '../../shared/services/routing.service';
import {
  TaskDialogComponent,
  TaskDialogData,
  TaskDialogItineraryList,
  TaskDialogResult,
} from '../dialogs/task-dialog/task-dialog.component';
import {
  TASK_PRIORITY_CHIP_CLASS,
  TASK_PRIORITY_LABELS,
} from '../task-management.constants';

@Component({
  selector: 'app-task-project-detail',
  standalone: true,
  imports: [NgIcon, NgTemplateOutlet, ReactiveFormsModule],
  providers: [provideIcons({
    featherArchive, featherArrowLeft, featherCheck, featherChevronDown, featherChevronRight,
    featherClock, featherCornerDownRight, featherEdit, featherLink, featherPlus, featherRotateCcw,
    featherShare2, featherTrash2,
  })],
  templateUrl: './project-detail.component.html',
})
export class ProjectDetailComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly routingService = inject(RoutingService);
  private readonly dialogService = inject(DialogService);
  private readonly authService = inject(AuthenticationService);

  readonly projectId = signal<number | null>(null);
  readonly project = signal<TaskProjectSchema | null>(null);
  readonly tasks = signal<TaskSchema[]>([]);
  readonly isLoading = signal<boolean>(true);
  readonly loadError = signal<string | null>(null);
  readonly isUpdatingStatus = signal<boolean>(false);
  readonly savingTaskId = signal<number | null>(null);
  readonly showDone = signal<boolean>(false);
  readonly itineraryLists = signal<TaskDialogItineraryList[]>([]);

  readonly newTaskCtrl = new FormControl<string>('', {nonNullable: true});
  readonly isAdding = signal<boolean>(false);

  readonly addingSubtaskFor = signal<number | null>(null);
  readonly newSubtaskCtrl = new FormControl<string>('', {nonNullable: true});
  readonly isAddingSubtask = signal<boolean>(false);

  readonly isOwner = computed(() => {
    const project = this.project();
    return !!project && project.owner_id === this.authService.user()?.id;
  });
  readonly isArchived = computed(() => this.project()?.status === 'archived');

  private readonly topLevel = computed(() => this.tasks().filter(t => t.parent_id === null));
  readonly openTasks = computed(() => this.topLevel().filter(t => t.status !== 'done'));
  readonly doneTasks = computed(() => this.topLevel().filter(t => t.status === 'done'));

  readonly subtasksByParent = computed(() => {
    const map: Record<number, TaskSchema[]> = {};
    for (const task of this.tasks()) {
      if (task.parent_id !== null) {
        (map[task.parent_id] ??= []).push(task);
      }
    }
    return map;
  });

  readonly overdueById = computed(() => {
    const now = Date.now();
    return Object.fromEntries(this.tasks().map(t =>
      [t.id, t.status !== 'done' && t.due_at !== null && new Date(t.due_at).getTime() < now]));
  });

  readonly dueLabelById = computed(() =>
    Object.fromEntries(this.tasks()
      .filter(t => t.due_at !== null)
      .map(t => [t.id, this.formatDue(t.due_at as string)])));

  readonly priorityLabels = TASK_PRIORITY_LABELS;
  readonly priorityChipClass = TASK_PRIORITY_CHIP_CLASS;

  protected readonly featherArchive = featherArchive;
  protected readonly featherArrowLeft = featherArrowLeft;
  protected readonly featherCheck = featherCheck;
  protected readonly featherChevronDown = featherChevronDown;
  protected readonly featherChevronRight = featherChevronRight;
  protected readonly featherClock = featherClock;
  protected readonly featherCornerDownRight = featherCornerDownRight;
  protected readonly featherEdit = featherEdit;
  protected readonly featherLink = featherLink;
  protected readonly featherPlus = featherPlus;
  protected readonly featherRotateCcw = featherRotateCcw;
  protected readonly featherShare2 = featherShare2;
  protected readonly featherTrash2 = featherTrash2;

  constructor() {
    this.route.paramMap.subscribe(params => {
      const idStr = params.get('id');
      if (idStr) {
        const id = Number(idStr);
        this.projectId.set(id);
        void this.load(id);
      }
    });
  }

  private async load(id: number): Promise<void> {
    this.isLoading.set(true);
    this.loadError.set(null);
    try {
      const [projectRes, tasksRes] = await Promise.all([
        getTaskProjectView({path: {object_id: id}}),
        paginateTasksView({path: {project_id: id}, query: {page: 0, page_size: 500}}),
      ]);
      this.project.set(projectRes.data);
      this.tasks.set(tasksRes.data.data);
    } catch {
      this.loadError.set('Could not load this project. You may not have access to it.');
    } finally {
      this.isLoading.set(false);
    }
    void this.loadItineraryLists();
  }

  private async loadItineraryLists(): Promise<void> {
    try {
      const res = await paginateItineraryListsView({query: {page: 0, page_size: 100}});
      this.itineraryLists.set(res.data.data.map(l => ({id: l.id, name: l.name})));
    } catch {
      this.itineraryLists.set([]);
    }
  }

  async addTask(): Promise<void> {
    const name = this.newTaskCtrl.value.trim();
    const projectId = this.projectId();
    if (!name || projectId === null || this.isAdding()) {
      return;
    }
    this.isAdding.set(true);
    try {
      const res = await createTaskView({body: {project_id: projectId, name}});
      this.tasks.update(prev => [...prev, res.data]);
      this.newTaskCtrl.setValue('');
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: 'Error', text: `${err}`});
    } finally {
      this.isAdding.set(false);
    }
  }

  toggleAddSubtask(parent: TaskSchema): void {
    this.newSubtaskCtrl.setValue('');
    this.addingSubtaskFor.update(curr => (curr === parent.id ? null : parent.id));
  }

  async addSubtask(parent: TaskSchema): Promise<void> {
    const name = this.newSubtaskCtrl.value.trim();
    const projectId = this.projectId();
    if (!name || projectId === null || this.isAddingSubtask()) {
      return;
    }
    this.isAddingSubtask.set(true);
    try {
      const res = await createTaskView({body: {project_id: projectId, name, parent_id: parent.id}});
      this.tasks.update(prev => [...prev, res.data]);
      this.newSubtaskCtrl.setValue('');
      this.addingSubtaskFor.set(null);
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: 'Error', text: `${err}`});
    } finally {
      this.isAddingSubtask.set(false);
    }
  }

  async toggleDone(task: TaskSchema): Promise<void> {
    if (this.savingTaskId() !== null) {
      return;
    }
    await this.patchTask(task, {status: task.status === 'done' ? 'todo' : 'done'});
  }

  async editTask(task: TaskSchema): Promise<void> {
    const result = await this.dialogService.open<TaskDialogData, TaskDialogResult>(
      TaskDialogComponent,
      {
        title: 'Edit task',
        confirmActionName: 'Save',
        name: task.name,
        description: task.description,
        status: task.status,
        priority: task.priority,
        dueAt: task.due_at,
        itineraryListId: task.itinerary_list_id,
        showStatus: true,
        itineraryLists: this.itineraryLists(),
      },
      50,
    );
    if (!result) {
      return;
    }
    await this.patchTask(task, {
      name: result.name,
      description: result.description,
      status: result.status,
      priority: result.priority,
      due_at: result.dueAt,
      itinerary_list_id: result.itineraryListId,
    });
  }

  async setPriority(task: TaskSchema, priority: TaskPriority): Promise<void> {
    await this.patchTask(task, {priority});
  }

  private async patchTask(task: TaskSchema, body: Parameters<typeof updateTaskView>[0]['body']): Promise<void> {
    this.savingTaskId.set(task.id);
    try {
      const res = await updateTaskView({body, path: {object_id: task.id}});
      this.tasks.update(prev => prev.map(t => (t.id === task.id ? res.data : t)));
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: 'Error', text: `${err}`});
    } finally {
      this.savingTaskId.set(null);
    }
  }

  async deleteTask(task: TaskSchema): Promise<void> {
    const subtaskCount = task.subtask_count;
    const text = subtaskCount > 0
      ? `Delete "${task.name}" and its ${subtaskCount} subtask${subtaskCount === 1 ? '' : 's'}?`
      : `Delete "${task.name}"?`;
    const confirmed = await this.dialogService.getBooleanFromConfirmationDialog({
      title: 'Delete task',
      text,
      confirmActionName: 'Delete',
      cancelActionName: 'Cancel',
    });
    if (!confirmed) {
      return;
    }
    try {
      await deleteTaskView({path: {object_id: task.id}});
      this.tasks.update(prev => prev.filter(t => t.id !== task.id && t.parent_id !== task.id));
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: 'Error', text: `${err}`});
    }
  }

  async openLinkedList(task: TaskSchema): Promise<void> {
    if (task.itinerary_list_id !== null) {
      await this.routingService.navigateToItineraryList(task.itinerary_list_id);
    }
  }

  async toggleArchive(): Promise<void> {
    const id = this.projectId();
    if (id === null || this.isUpdatingStatus()) {
      return;
    }
    this.isUpdatingStatus.set(true);
    try {
      if (this.isArchived()) {
        await unarchiveTaskProjectView({body: {}, path: {object_id: id}});
      } else {
        await archiveTaskProjectView({body: {}, path: {object_id: id}});
      }
      const res = await getTaskProjectView({path: {object_id: id}});
      this.project.set(res.data);
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: 'Error', text: `${err}`});
    } finally {
      this.isUpdatingStatus.set(false);
    }
  }

  async openShareDialog(): Promise<void> {
    const id = this.projectId();
    if (id === null) {
      return;
    }
    await this.dialogService.open(ShareDialogComponent, {
      objectId: id,
      isOwner: this.isOwner(),
      title: 'Share project',
      subtitle: 'People you add can view and edit this project and its tasks.',
      listMembers: async (objectId: number) =>
        (await listTaskProjectMembersView({path: {object_id: objectId}})).data.members,
      share: async (objectId: number, identifier: string) => {
        await shareTaskProjectView({body: {identifier, role: 'collaborator'}, path: {object_id: objectId}});
      },
      unshare: async (objectId: number, identifier: string) => {
        await unshareTaskProjectView({body: {identifier}, path: {object_id: objectId}});
      },
    }, 45);
    const res = await getTaskProjectView({path: {object_id: id}});
    this.project.set(res.data);
  }

  async editProject(): Promise<void> {
    const id = this.projectId();
    if (id !== null) {
      await this.routingService.navigateToTaskProjectEdit(id);
    }
  }

  async deleteProject(): Promise<void> {
    const project = this.project();
    if (project === null) {
      return;
    }
    const confirmed = await this.dialogService.getBooleanFromTextConfirmationDialog({
      title: 'Delete project',
      text: 'This permanently deletes the project and all of its tasks. This cannot be undone.',
      label: 'Project name',
      validationText: project.name,
      confirmActionName: 'Delete project',
      cancelActionName: 'Cancel',
    });
    if (!confirmed) {
      return;
    }
    try {
      await deleteTaskProjectView({path: {object_id: project.id}});
      await this.routingService.navigateToTaskManagement();
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: 'Error', text: `${err}`});
    }
  }

  toggleShowDone(): void {
    this.showDone.update(v => !v);
  }

  async back(): Promise<void> {
    await this.routingService.navigateToTaskManagement();
  }

  private formatDue(iso: string): string {
    const date = new Date(iso);
    return date.toLocaleString(undefined, {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  }
}
