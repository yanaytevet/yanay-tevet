import {Component, computed, DestroyRef, ElementRef, inject, signal} from '@angular/core';
import {NgTemplateOutlet} from '@angular/common';
import {ActivatedRoute, RouterLink} from '@angular/router';
import {NgIcon} from '@ng-icons/core';
import {
  featherArrowLeft,
  featherArrowRight,
  featherBarChart2,
  featherCheck,
  featherClock,
  featherGlobe,
  featherMoreHorizontal,
  featherPlus,
  featherTrash2,
} from '@ng-icons/feather-icons';
import {
  deleteSetLogView,
  deleteWorkoutSessionView,
  ExerciseSchema,
  getWorkoutSessionView,
  logSetView,
  PlanExerciseSchema,
  SetLogSchema,
  SetSide,
  updateSetLogView,
  updateWorkoutSessionView,
  WorkoutSessionDetailSchema,
} from '../../../generated-files/api/workout-plan';
import {MenuButtonComponent, MenuItem} from '../../common/components/menu-button/menu-button.component';
import {ErrorStateComponent} from '../../common/components/page/error-state/error-state.component';
import {LoadingStateComponent} from '../../common/components/page/loading-state/loading-state.component';
import {PageHeaderComponent} from '../../common/components/page/page-header/page-header.component';
import {DialogService} from '../../common/dialogs/dialogs.service';
import {RoutingService} from '../../shared/services/routing.service';
import {ExercisePickerDialogComponent} from '../dialogs/exercise-picker-dialog/exercise-picker-dialog.component';
import {ExerciseNamePipe} from '../shared/exercise-name.pipe';
import {formatDuration, formatNumber, parseDuration, targetSummary} from '../shared/workout-format';
import {WorkoutI18nService} from '../shared/workout-i18n.service';
import {RestTimerComponent} from './rest-timer/rest-timer.component';
import {RestTimerService} from './rest-timer/rest-timer.service';

type Field = 'reps' | 'weight' | 'duration' | 'distance' | 'laps';
type Values = Partial<Record<Field, string>>;

interface SetRow {
  key: string;
  setNumber: number;
  side: SetSide;
  label: string;
  log: SetLogSchema | null;
  // The logged values, as the inputs show them.
  values: Values;
  // What the inputs show greyed out until typed over, and what ✓ logs if nothing was typed:
  // last session's set, else the plan's target.
  placeholder: Values;
  previousText: string;
}

interface ExerciseCard {
  key: string;
  entry: PlanExerciseSchema | null;
  exercise: ExerciseSchema;
  section: 'every' | 'day' | 'extra';
  fields: Field[];
  rows: SetRow[];
  summary: string;
  notes: string;
  restSeconds: number;
  doneCount: number;
}

interface SummaryLine {
  key: string;
  exercise: ExerciseSchema;
  value: string;
  delta: string;
  direction: 'up' | 'down' | 'same' | 'new';
}

const DEFAULT_REST_SECONDS = 50;

@Component({
  selector: 'app-workout-session',
  imports: [
    NgIcon, NgTemplateOutlet, RouterLink, PageHeaderComponent, LoadingStateComponent, ErrorStateComponent, MenuButtonComponent,
    ExerciseNamePipe, RestTimerComponent,
  ],
  templateUrl: './workout-session.component.html',
})
export class WorkoutSessionComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly routingService = inject(RoutingService);
  private readonly dialogService = inject(DialogService);
  private readonly host = inject(ElementRef<HTMLElement>);
  protected readonly i18n = inject(WorkoutI18nService);
  protected readonly timer = inject(RestTimerService);

  readonly session = signal<WorkoutSessionDetailSchema | null>(null);
  readonly logs = signal<SetLogSchema[]>([]);
  readonly isLoading = signal<boolean>(true);
  readonly loadError = signal<boolean>(false);
  readonly drafts = signal<Record<string, Values>>({});
  readonly extraSets = signal<Record<string, number>>({});
  readonly addedExercises = signal<ExerciseSchema[]>([]);
  readonly busyKeys = signal<Record<string, boolean>>({});

  readonly plansUrl = this.routingService.getWorkoutPlanUrl();
  readonly backUrl = computed(() => {
    const planId = this.session()?.plan_id;
    return planId ? this.routingService.getWorkoutPlanDetailUrl(planId) : this.plansUrl;
  });
  readonly backIcon = computed(() => this.i18n.dir() === 'rtl' ? featherArrowRight : featherArrowLeft);
  readonly isFinished = computed(() => !!this.session()?.finished_at);
  readonly title = computed(() => {
    const session = this.session();
    return session?.day_name || (session?.plan_name ? this.i18n.t().everyDay : this.i18n.t().freeWorkout);
  });
  readonly subtitle = computed(() => {
    const session = this.session();
    if (!session) {
      return null;
    }
    const date = new Intl.DateTimeFormat(this.i18n.language(), {weekday: 'long', day: 'numeric', month: 'long'})
      .format(new Date(session.started_at));
    return session.plan_name ? `${session.plan_name} · ${date}` : date;
  });

  readonly cards = computed<ExerciseCard[]>(() => {
    const session = this.session();
    if (!session) {
      return [];
    }
    const t = this.i18n.t();
    const logs = this.logs();
    const extraSets = this.extraSets();
    const cards: ExerciseCard[] = [];
    const seenExerciseIds = new Set<number>();

    for (const entry of session.plan_exercises) {
      seenExerciseIds.add(entry.exercise.id);
      const entryLogs = logs.filter(log => log.plan_exercise_id === entry.id);
      const key = `p${entry.id}`;
      cards.push(this.buildCard({
        key, entry, exercise: entry.exercise,
        section: entry.day_id === session.day_id ? 'day' : 'every',
        logs: entryLogs, targetSets: entry.target_sets + (extraSets[key] ?? 0),
        summary: targetSummary(entry, t), notes: entry.notes, restSeconds: entry.rest_seconds,
      }, session));
    }
    const extras = [...session.extra_exercises, ...this.addedExercises()];
    for (const exercise of extras) {
      if (seenExerciseIds.has(exercise.id)) {
        continue;
      }
      seenExerciseIds.add(exercise.id);
      const key = `x${exercise.id}`;
      const entryLogs = logs.filter(log => log.exercise_id === exercise.id && log.plan_exercise_id === null);
      const isCardio = exercise.tracking_type === 'distance' || exercise.tracking_type === 'laps';
      cards.push(this.buildCard({
        key, entry: null, exercise, section: 'extra', logs: entryLogs,
        targetSets: (isCardio ? 1 : 3) + (extraSets[key] ?? 0),
        summary: '', notes: '', restSeconds: DEFAULT_REST_SECONDS,
      }, session));
    }
    return cards;
  });
  readonly everyDayCards = computed(() => this.cards().filter(card => card.section === 'every'));
  readonly dayCards = computed(() => this.cards().filter(card => card.section === 'day'));
  readonly extraCards = computed(() => this.cards().filter(card => card.section === 'extra'));
  readonly progressUrls = computed(() => Object.fromEntries(
    this.cards().map(card => [card.key, this.routingService.getWorkoutProgressUrl(card.exercise.id)]),
  ));

  // How each exercise went against the last time it was done: the "did I go up?" answer at the end.
  readonly summary = computed<SummaryLine[]>(() => {
    const session = this.session();
    if (!session) {
      return [];
    }
    const t = this.i18n.t();
    const lines: SummaryLine[] = [];
    for (const card of this.cards()) {
      const current = card.rows.map(row => row.log).filter((log): log is SetLogSchema => log !== null);
      if (current.length === 0) {
        continue;
      }
      const previous = session.previous_logs.filter(log => log.exercise_id === card.exercise.id);
      const now = this.headline(card.exercise, current, session.pool_length_m);
      const before = previous.length > 0 ? this.headline(card.exercise, previous, session.pool_length_m) : null;
      const unit = this.headlineUnit(card.exercise, t);
      let direction: SummaryLine['direction'] = 'new';
      let delta = '';
      if (before !== null) {
        const diff = now - before;
        direction = Math.abs(diff) < 1e-9 ? 'same' : diff > 0 ? 'up' : 'down';
        delta = direction === 'same' ? '=' : `${diff > 0 ? '+' : '−'}${this.formatHeadline(card.exercise, Math.abs(diff))}`;
      }
      lines.push({
        key: card.key, exercise: card.exercise, value: `${this.formatHeadline(card.exercise, now)} ${unit}`.trim(),
        delta, direction,
      });
    }
    return lines;
  });

  readonly menuItems = computed<MenuItem[]>(() => {
    const t = this.i18n.t();
    const items: MenuItem[] = [
      {display: t.languageToggle, icon: featherGlobe, callback: () => void this.i18n.toggle()},
    ];
    if (this.isFinished()) {
      items.push({display: t.reopenWorkout, icon: featherClock, callback: () => void this.setFinished(false)});
    }
    items.push({display: t.deleteWorkout, icon: featherTrash2, danger: true, callback: () => void this.deleteSession()});
    return items;
  });

  protected readonly featherBarChart2 = featherBarChart2;
  protected readonly featherCheck = featherCheck;
  protected readonly featherClock = featherClock;
  protected readonly featherMoreHorizontal = featherMoreHorizontal;
  protected readonly featherPlus = featherPlus;

  private wakeLock: WakeLockSentinel | null = null;
  // An edit is saved on blur, which fires just before a tap on the row's ✓; that tap waits for the save.
  private readonly pendingSaves = new Map<string, Promise<void>>();

  constructor() {
    this.route.paramMap.subscribe(params => void this.load(Number(params.get('id'))));
    void this.keepScreenOn();
    inject(DestroyRef).onDestroy(() => void this.wakeLock?.release());
  }

  private async load(sessionId: number): Promise<void> {
    this.isLoading.set(true);
    this.loadError.set(false);
    try {
      const res = await getWorkoutSessionView({path: {object_id: sessionId}});
      this.session.set(res.data);
      this.logs.set(res.data.set_logs);
      this.drafts.set({});
      this.extraSets.set({});
      this.addedExercises.set([]);
    } catch {
      this.loadError.set(true);
    } finally {
      this.isLoading.set(false);
    }
  }

  // The phone sits on a bench between sets; a sleeping screen would hide the rest timer.
  private async keepScreenOn(): Promise<void> {
    try {
      this.wakeLock = await navigator.wakeLock?.request('screen') ?? null;
    } catch {
      this.wakeLock = null;
    }
  }

  // --- Building the rows ---

  private buildCard(
    source: {
      key: string; entry: PlanExerciseSchema | null; exercise: ExerciseSchema; section: ExerciseCard['section'];
      logs: SetLogSchema[]; targetSets: number; summary: string; notes: string; restSeconds: number;
    },
    session: WorkoutSessionDetailSchema,
  ): ExerciseCard {
    const t = this.i18n.t();
    const exercise = source.exercise;
    const sides: SetSide[] = exercise.per_side ? ['right', 'left'] : ['both'];
    const previous = session.previous_logs.filter(log => log.exercise_id === exercise.id);
    const loggedMax = Math.max(0, ...source.logs.map(log => log.set_number));
    const setCount = Math.max(1, source.targetSets, loggedMax);
    const fields = this.fieldsFor(exercise);
    const rows: SetRow[] = [];
    for (let setNumber = 1; setNumber <= setCount; setNumber++) {
      for (const side of sides) {
        const log = source.logs.find(l => l.set_number === setNumber && l.side === side) ?? null;
        const previousSet = previous.find(l => l.set_number === setNumber && l.side === side)
          ?? [...previous].reverse().find(l => l.side === side) ?? null;
        const sideLabel = side === 'left' ? ` ${t.left}` : side === 'right' ? ` ${t.right}` : '';
        rows.push({
          key: `${source.key}:${setNumber}:${side}`,
          setNumber, side,
          label: `${setNumber}${sideLabel}`,
          log,
          values: log ? this.valuesOf(log) : {},
          placeholder: previousSet ? this.valuesOf(previousSet) : this.targetValues(source.entry),
          previousText: previousSet ? this.describe(previousSet, exercise, t) : '',
        });
      }
    }
    return {
      key: source.key, entry: source.entry, exercise, section: source.section, fields, rows,
      summary: source.summary, notes: source.notes, restSeconds: source.restSeconds,
      doneCount: rows.filter(row => row.log !== null).length,
    };
  }

  private fieldsFor(exercise: ExerciseSchema): Field[] {
    switch (exercise.tracking_type) {
      case 'weight_reps': return ['weight', 'reps'];
      case 'reps': return ['reps'];
      case 'time': return ['duration'];
      case 'distance': return ['distance', 'duration'];
      case 'laps': return ['laps', 'duration'];
    }
  }

  private valuesOf(log: SetLogSchema): Values {
    return {
      reps: log.reps !== null ? String(log.reps) : undefined,
      weight: log.weight_kg !== null ? formatNumber(log.weight_kg) : undefined,
      duration: log.duration_seconds !== null ? formatDuration(log.duration_seconds) : undefined,
      distance: log.distance_km !== null ? formatNumber(log.distance_km) : undefined,
      laps: log.laps !== null ? String(log.laps) : undefined,
    };
  }

  private targetValues(entry: PlanExerciseSchema | null): Values {
    if (!entry) {
      return {};
    }
    return {
      reps: entry.target_reps !== null ? String(entry.target_reps) : undefined,
      weight: entry.target_weight_kg !== null ? formatNumber(entry.target_weight_kg) : undefined,
      duration: entry.target_seconds !== null ? formatDuration(entry.target_seconds) : undefined,
      distance: entry.target_distance_km !== null ? formatNumber(entry.target_distance_km) : undefined,
      laps: entry.target_laps !== null ? String(entry.target_laps) : undefined,
    };
  }

  private describe(log: SetLogSchema, exercise: ExerciseSchema, t: ReturnType<WorkoutI18nService['t']>): string {
    switch (exercise.tracking_type) {
      case 'weight_reps':
        return `${formatNumber(log.weight_kg)} ${t.weightKg} × ${log.reps ?? '–'}`;
      case 'reps':
        return `× ${log.reps ?? '–'}`;
      case 'time':
        return formatDuration(log.duration_seconds);
      case 'distance':
        return `${formatNumber(log.distance_km)} ${t.distanceKm}${log.duration_seconds ? ` · ${formatDuration(log.duration_seconds)}` : ''}`;
      case 'laps':
        return `${log.laps ?? '–'} ${t.laps}${log.duration_seconds ? ` · ${formatDuration(log.duration_seconds)}` : ''}`;
    }
  }

  // --- Logging ---

  onDraft(row: SetRow, field: Field, event: Event): void {
    const value = (event.target as HTMLInputElement).value;
    this.drafts.update(drafts => ({...drafts, [row.key]: {...drafts[row.key], [field]: value}}));
  }

  async toggle(card: ExerciseCard, row: SetRow): Promise<void> {
    if (this.busyKeys()[row.key]) {
      return;
    }
    this.timer.unlockSound();
    this.setBusy(row.key, true);
    try {
      await this.pendingSaves.get(row.key);
      if (row.log) {
        await deleteSetLogView({path: {object_id: row.log.id}});
        const removedId = row.log.id;
        this.logs.update(logs => logs.filter(log => log.id !== removedId));
        return;
      }
      const session = this.session();
      if (!session) {
        return;
      }
      const values = this.parsed(card, {...row.placeholder, ...this.drafts()[row.key]});
      const res = await logSetView({body: {
        ...values,
        session_id: session.id,
        exercise_id: card.exercise.id,
        plan_exercise_id: card.entry?.id ?? null,
        set_number: row.setNumber,
        side: row.side,
      }});
      this.logs.update(logs => [...logs.filter(log => log.id !== res.data.id), res.data]);
      this.drafts.update(drafts => {
        const next = {...drafts};
        delete next[row.key];
        return next;
      });
      if (!this.isCardio(card.exercise)) {
        this.timer.start(card.restSeconds);
      }
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: 'Error', text: `${err}`});
    } finally {
      this.setBusy(row.key, false);
    }
  }

  // A logged set edited in place is saved when the field is left.
  async saveEdit(card: ExerciseCard, row: SetRow): Promise<void> {
    const save = this.saveEditNow(card, row);
    this.pendingSaves.set(row.key, save);
    try {
      await save;
    } finally {
      if (this.pendingSaves.get(row.key) === save) {
        this.pendingSaves.delete(row.key);
      }
    }
  }

  private async saveEditNow(card: ExerciseCard, row: SetRow): Promise<void> {
    const draft = this.drafts()[row.key];
    if (!row.log || !draft) {
      return;
    }
    try {
      const res = await updateSetLogView({
        path: {object_id: row.log.id},
        body: this.parsed(card, {...this.valuesOf(row.log), ...draft}),
      });
      this.logs.update(logs => logs.map(log => log.id === res.data.id ? res.data : log));
      this.drafts.update(drafts => {
        const next = {...drafts};
        delete next[row.key];
        return next;
      });
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: 'Error', text: `${err}`});
    }
  }

  private parsed(card: ExerciseCard, values: Values): {
    reps?: number | null; weight_kg?: number | null; duration_seconds?: number | null;
    distance_km?: number | null; laps?: number | null;
  } {
    const toInt = (text: string | undefined) => {
      const value = parseInt(text ?? '', 10);
      return Number.isNaN(value) ? null : value;
    };
    const toFloat = (text: string | undefined) => {
      const value = parseFloat((text ?? '').replace(',', '.'));
      return Number.isNaN(value) ? null : value;
    };
    switch (card.exercise.tracking_type) {
      case 'weight_reps':
        return {weight_kg: toFloat(values.weight), reps: toInt(values.reps)};
      case 'reps':
        return {reps: toInt(values.reps)};
      case 'time':
        return {duration_seconds: parseDuration(values.duration ?? '')};
      case 'distance':
        return {distance_km: toFloat(values.distance), duration_seconds: parseDuration(values.duration ?? '')};
      case 'laps':
        return {laps: toInt(values.laps), duration_seconds: parseDuration(values.duration ?? '')};
    }
  }

  addSet(card: ExerciseCard): void {
    this.extraSets.update(sets => ({...sets, [card.key]: (sets[card.key] ?? 0) + 1}));
  }

  async addExercise(): Promise<void> {
    const exercise = await this.dialogService.open<void, ExerciseSchema>(ExercisePickerDialogComponent, undefined, 50);
    if (exercise) {
      this.addedExercises.update(list => [...list, exercise]);
    }
  }

  startRest(): void {
    this.timer.unlockSound();
    this.timer.start(DEFAULT_REST_SECONDS);
  }

  // --- Session ---

  async setFinished(finished: boolean): Promise<void> {
    const session = this.session();
    if (!session) {
      return;
    }
    try {
      const res = await updateWorkoutSessionView({path: {object_id: session.id}, body: {finished}});
      this.session.set(res.data);
      this.logs.set(res.data.set_logs);
      if (finished) {
        this.timer.stop();
        // The page scrolls inside the layout's container, not the window: bring the summary into view.
        (this.host.nativeElement as HTMLElement).scrollIntoView({behavior: 'smooth', block: 'start'});
      }
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: 'Error', text: `${err}`});
    }
  }

  async deleteSession(): Promise<void> {
    const session = this.session();
    const t = this.i18n.t();
    if (!session) {
      return;
    }
    const confirmed = await this.dialogService.getBooleanFromConfirmationDialog({
      title: t.deleteWorkout, text: t.deleteWorkoutText, confirmActionName: t.delete, cancelActionName: t.cancel,
      danger: true, dir: this.i18n.dir(),
    });
    if (!confirmed) {
      return;
    }
    try {
      await deleteWorkoutSessionView({path: {object_id: session.id}});
      this.timer.stop();
      if (session.plan_id) {
        await this.routingService.navigateToWorkoutPlanDetail(session.plan_id);
      } else {
        await this.routingService.navigateToWorkoutPlan();
      }
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: 'Error', text: `${err}`});
    }
  }

  // --- Summary helpers ---

  private headline(exercise: ExerciseSchema, logs: SetLogSchema[], poolLength: number): number {
    switch (exercise.tracking_type) {
      case 'weight_reps': return Math.max(0, ...logs.map(log => log.weight_kg ?? 0));
      case 'reps': return Math.max(0, ...logs.map(log => log.reps ?? 0));
      case 'time': return Math.max(0, ...logs.map(log => log.duration_seconds ?? 0));
      case 'distance': return logs.reduce((sum, log) => sum + (log.distance_km ?? 0), 0);
      case 'laps': return logs.reduce((sum, log) => sum + (log.laps ?? 0), 0) * poolLength / 1000;
    }
  }

  private formatHeadline(exercise: ExerciseSchema, value: number): string {
    return exercise.tracking_type === 'time' ? formatDuration(value) : formatNumber(value);
  }

  private headlineUnit(exercise: ExerciseSchema, t: ReturnType<WorkoutI18nService['t']>): string {
    switch (exercise.tracking_type) {
      case 'weight_reps': return t.weightKg;
      case 'reps': return t.reps;
      case 'time': return '';
      case 'distance':
      case 'laps': return t.distanceKm;
    }
  }

  private isCardio(exercise: ExerciseSchema): boolean {
    return exercise.tracking_type === 'distance' || exercise.tracking_type === 'laps';
  }

  private setBusy(key: string, busy: boolean): void {
    this.busyKeys.update(keys => ({...keys, [key]: busy}));
  }

}
