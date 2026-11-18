import {Component, computed, inject, signal} from '@angular/core';
import {NgTemplateOutlet} from '@angular/common';
import {ActivatedRoute, RouterLink} from '@angular/router';
import {NgIcon} from '@ng-icons/core';
import {
  featherArrowDown,
  featherArrowLeft,
  featherArrowUp,
  featherCheck,
  featherEdit,
  featherGlobe,
  featherMoreHorizontal,
  featherPlay,
  featherPlus,
  featherShare2,
  featherTrash2,
} from '@ng-icons/feather-icons';
import {
  createPlanDayView,
  createPlanExerciseView,
  deletePlanDayView,
  deletePlanExerciseView,
  deleteWorkoutPlanView,
  ExerciseSchema,
  getWorkoutPlanView,
  listWorkoutPlanMembersView,
  PlanDaySchema,
  PlanExerciseSchema,
  PlanExerciseTargetsSchema,
  reorderPlanDaysView,
  reorderPlanExercisesView,
  shareWorkoutPlanView,
  startWorkoutSessionView,
  unshareWorkoutPlanView,
  updatePlanDayView,
  updatePlanExerciseView,
  updateWorkoutPlanView,
  WorkoutPlanDetailSchema,
} from '../../../generated-files/api/workout-plan';
import {AuthenticationService} from '../../common/authentication/authentication.service';
import {MenuButtonComponent, MenuItem} from '../../common/components/menu-button/menu-button.component';
import {EmptyStateComponent} from '../../common/components/page/empty-state/empty-state.component';
import {ErrorStateComponent} from '../../common/components/page/error-state/error-state.component';
import {LoadingStateComponent} from '../../common/components/page/loading-state/loading-state.component';
import {PageHeaderComponent} from '../../common/components/page/page-header/page-header.component';
import {DialogService} from '../../common/dialogs/dialogs.service';
import {ShareDialogComponent} from '../../common/dialogs/share-dialog/share-dialog.component';
import {fill, plural} from '../../shared/i18n/strings';
import {RoutingService} from '../../shared/services/routing.service';
import {ExercisePickerDialogComponent} from '../dialogs/exercise-picker-dialog/exercise-picker-dialog.component';
import {
  PlanExerciseDialogComponent,
  PlanExerciseDialogData,
} from '../dialogs/plan-exercise-dialog/plan-exercise-dialog.component';
import {ExerciseNamePipe} from '../shared/exercise-name.pipe';
import {targetSummary} from '../shared/workout-format';
import {WorkoutI18nService} from '../shared/workout-i18n.service';

@Component({
  selector: 'app-workout-plan-detail',
  imports: [
    NgIcon, NgTemplateOutlet, RouterLink, MenuButtonComponent, PageHeaderComponent, EmptyStateComponent, LoadingStateComponent,
    ErrorStateComponent, ExerciseNamePipe,
  ],
  templateUrl: './plan-detail.component.html',
})
export class PlanDetailComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly routingService = inject(RoutingService);
  private readonly dialogService = inject(DialogService);
  private readonly authService = inject(AuthenticationService);
  protected readonly i18n = inject(WorkoutI18nService);

  readonly plan = signal<WorkoutPlanDetailSchema | null>(null);
  readonly isLoading = signal<boolean>(true);
  readonly loadError = signal<boolean>(false);
  readonly isEditing = signal<boolean>(false);

  readonly plansUrl = this.routingService.getWorkoutPlanUrl();
  readonly isOwner = computed(() => this.plan()?.owner_id === this.authService.user()?.id);
  readonly subtitle = computed(() => {
    const plan = this.plan();
    if (!plan) {
      return null;
    }
    const t = this.i18n.t();
    const days = plural(this.i18n.language(), plan.days.length, t.dayCount);
    return plan.member_count > 1 ? `${days} · ${t.sharedWith}` : days;
  });
  readonly summaries = computed(() => {
    const plan = this.plan();
    const t = this.i18n.t();
    const language = this.i18n.language();
    const entries = plan ? [...(plan.every_day?.exercises ?? []), ...plan.days.flatMap(day => day.exercises)] : [];
    return Object.fromEntries(entries.map(entry => [entry.id, targetSummary(entry, t, language)]));
  });
  readonly dayMuscles = computed(() => {
    const plan = this.plan();
    const t = this.i18n.t();
    return Object.fromEntries((plan?.days ?? []).map(day => {
      const groups = [...new Set(day.exercises.map(entry => entry.exercise.muscle_group))];
      return [day.id, groups.map(group => t.muscle[group]).join(' · ')];
    }));
  });
  readonly menuItems = computed<MenuItem[]>(() => {
    const t = this.i18n.t();
    const items: MenuItem[] = [
      {display: t.language, icon: featherGlobe, callback: () => void this.i18n.chooseLanguage()},
      {display: t.renamePlan, icon: featherEdit, callback: () => void this.renamePlan()},
      {display: t.poolLength, icon: featherEdit, callback: () => void this.changePoolLength()},
    ];
    if (this.isOwner()) {
      items.push({display: t.deletePlan, icon: featherTrash2, danger: true, callback: () => void this.deletePlan()});
    }
    return items;
  });

  protected readonly featherArrowLeft = featherArrowLeft;
  protected readonly featherArrowUp = featherArrowUp;
  protected readonly featherArrowDown = featherArrowDown;
  protected readonly featherCheck = featherCheck;
  protected readonly featherEdit = featherEdit;
  protected readonly featherMoreHorizontal = featherMoreHorizontal;
  protected readonly featherPlay = featherPlay;
  protected readonly featherPlus = featherPlus;
  protected readonly featherShare2 = featherShare2;
  protected readonly featherTrash2 = featherTrash2;

  constructor() {
    this.route.paramMap.subscribe(params => void this.load(Number(params.get('id'))));
  }

  private async load(planId: number): Promise<void> {
    this.isLoading.set(this.plan()?.id !== planId);
    this.loadError.set(false);
    try {
      const res = await getWorkoutPlanView({path: {object_id: planId}});
      this.plan.set(res.data);
    } catch {
      this.loadError.set(true);
    } finally {
      this.isLoading.set(false);
    }
  }

  private async reload(): Promise<void> {
    const plan = this.plan();
    if (plan) {
      await this.load(plan.id);
    }
  }

  private async run(action: () => Promise<unknown>): Promise<void> {
    try {
      await action();
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: this.i18n.t().error, text: `${err}`});
    }
    await this.reload();
  }

  async start(day: PlanDaySchema | null): Promise<void> {
    const plan = this.plan();
    if (!plan) {
      return;
    }
    try {
      const res = await startWorkoutSessionView({body: day ? {day_id: day.id} : {plan_id: plan.id}});
      await this.routingService.navigateToWorkoutSession(res.data.id);
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: this.i18n.t().error, text: `${err}`});
    }
  }

  // --- Plan ---

  async renamePlan(): Promise<void> {
    const plan = this.plan();
    const t = this.i18n.t();
    if (!plan) {
      return;
    }
    const name = await this.dialogService.getTextFromInputDialog({
      title: t.renamePlan, text: '', label: t.planName, defaultValue: plan.name, confirmActionName: t.save,
      cancelActionName: t.cancel
    });
    if (name?.trim()) {
      await this.run(() => updateWorkoutPlanView({path: {object_id: plan.id}, body: {name: name.trim()}}));
    }
  }

  async changePoolLength(): Promise<void> {
    const plan = this.plan();
    const t = this.i18n.t();
    if (!plan) {
      return;
    }
    const length = await this.dialogService.getNumberFromInputDialog({
      title: t.poolLength, text: t.poolLengthText, label: t.poolLengthLabel, defaultValue: plan.pool_length_m, minValue: 1,
      confirmActionName: t.save, cancelActionName: t.cancel
    });
    if (length) {
      await this.run(() => updateWorkoutPlanView({path: {object_id: plan.id}, body: {pool_length_m: length}}));
    }
  }

  async deletePlan(): Promise<void> {
    const plan = this.plan();
    const t = this.i18n.t();
    if (!plan) {
      return;
    }
    const confirmed = await this.dialogService.getBooleanFromConfirmationDialog({
      title: t.deletePlan, text: t.deletePlanText, confirmActionName: t.delete, cancelActionName: t.cancel,
      danger: true
    });
    if (!confirmed) {
      return;
    }
    try {
      await deleteWorkoutPlanView({path: {object_id: plan.id}});
      await this.routingService.navigateToWorkoutPlan();
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: this.i18n.t().error, text: `${err}`});
    }
  }

  async openShareDialog(): Promise<void> {
    const plan = this.plan();
    const t = this.i18n.t();
    if (!plan) {
      return;
    }
    await this.dialogService.open(ShareDialogComponent, {
      objectId: plan.id,
      isOwner: this.isOwner(),
      title: t.shareTitle,
      subtitle: t.shareSubtitle,
      listMembers: async (objectId: number) => {
        const data = (await listWorkoutPlanMembersView({path: {object_id: objectId}})).data;
        return {members: data.members, pendingInvitations: data.pending_invitations};
      },
      share: async (objectId: number, identifier: string) => {
        await shareWorkoutPlanView({body: {identifier}, path: {object_id: objectId}});
      },
      unshare: async (objectId: number, identifier: string) => {
        await unshareWorkoutPlanView({body: {identifier}, path: {object_id: objectId}});
      },
    }, 45);
    await this.reload();
  }

  // --- Days ---

  async addDay(): Promise<void> {
    const plan = this.plan();
    const t = this.i18n.t();
    if (!plan) {
      return;
    }
    const name = await this.dialogService.getTextFromInputDialog({
      title: t.addDay, text: '', label: t.dayName, defaultValue: fill(t.defaultDayName, {number: plan.days.length + 1}),
      confirmActionName: t.add, cancelActionName: t.cancel
    });
    if (name?.trim()) {
      await this.run(() => createPlanDayView({body: {plan_id: plan.id, name: name.trim()}}));
    }
  }

  async renameDay(day: PlanDaySchema): Promise<void> {
    const t = this.i18n.t();
    const name = await this.dialogService.getTextFromInputDialog({
      title: t.renameDay, text: '', label: t.dayName, defaultValue: day.name, confirmActionName: t.save,
      cancelActionName: t.cancel
    });
    if (name?.trim()) {
      await this.run(() => updatePlanDayView({path: {object_id: day.id}, body: {name: name.trim()}}));
    }
  }

  async deleteDay(day: PlanDaySchema): Promise<void> {
    const t = this.i18n.t();
    const confirmed = await this.dialogService.getBooleanFromConfirmationDialog({
      title: t.deleteDay, text: t.deleteDayText, confirmActionName: t.delete, cancelActionName: t.cancel,
      danger: true
    });
    if (confirmed) {
      await this.run(() => deletePlanDayView({path: {object_id: day.id}}));
    }
  }

  async moveDay(day: PlanDaySchema, offset: -1 | 1): Promise<void> {
    const plan = this.plan();
    if (!plan) {
      return;
    }
    const ids = this.moved(plan.days.map(d => d.id), day.id, offset);
    if (ids) {
      await this.run(() => reorderPlanDaysView({path: {plan_id: plan.id}, body: {ordered_ids: ids}}));
    }
  }

  // --- Exercises in a day ---

  async addExercise(day: PlanDaySchema): Promise<void> {
    const exercise = await this.dialogService.open<void, ExerciseSchema>(ExercisePickerDialogComponent, undefined, 50);
    if (!exercise) {
      return;
    }
    const targets = await this.dialogService.open<PlanExerciseDialogData, PlanExerciseTargetsSchema>(
      PlanExerciseDialogComponent, {exercise}, 45,
    );
    if (targets) {
      await this.run(() => createPlanExerciseView({body: {...targets, day_id: day.id, exercise_id: exercise.id}}));
    }
  }

  async editExercise(entry: PlanExerciseSchema): Promise<void> {
    const targets = await this.dialogService.open<PlanExerciseDialogData, PlanExerciseTargetsSchema>(
      PlanExerciseDialogComponent, {exercise: entry.exercise, entry}, 45,
    );
    if (targets) {
      await this.run(() => updatePlanExerciseView({path: {object_id: entry.id}, body: targets}));
    }
  }

  async removeExercise(entry: PlanExerciseSchema): Promise<void> {
    const t = this.i18n.t();
    const confirmed = await this.dialogService.getBooleanFromConfirmationDialog({
      title: t.removeExercise, text: t.removeExerciseText, confirmActionName: t.remove, cancelActionName: t.cancel,
      danger: true
    });
    if (confirmed) {
      await this.run(() => deletePlanExerciseView({path: {object_id: entry.id}}));
    }
  }

  async moveExercise(day: PlanDaySchema, entry: PlanExerciseSchema, offset: -1 | 1): Promise<void> {
    const ids = this.moved(day.exercises.map(e => e.id), entry.id, offset);
    if (ids) {
      await this.run(() => reorderPlanExercisesView({path: {day_id: day.id}, body: {ordered_ids: ids}}));
    }
  }

  private moved(ids: number[], id: number, offset: -1 | 1): number[] | null {
    const index = ids.indexOf(id);
    const target = index + offset;
    if (index < 0 || target < 0 || target >= ids.length) {
      return null;
    }
    const next = [...ids];
    [next[index], next[target]] = [next[target], next[index]];
    return next;
  }
}
