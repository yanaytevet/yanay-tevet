import {Component, computed, inject, signal} from '@angular/core';
import {ActivatedRoute, RouterLink} from '@angular/router';
import {NgIcon} from '@ng-icons/core';
import {featherArrowLeft, featherArrowRight} from '@ng-icons/feather-icons';
import {
  ExerciseHistorySummarySchema,
  ExerciseProgressSchema,
  getExerciseProgressView,
  getProgressSummaryView,
  ProgressPointSchema,
} from '../../../generated-files/api/workout-plan';
import {EmptyStateComponent} from '../../common/components/page/empty-state/empty-state.component';
import {LoadingStateComponent} from '../../common/components/page/loading-state/loading-state.component';
import {PageHeaderComponent} from '../../common/components/page/page-header/page-header.component';
import {RoutingService} from '../../shared/services/routing.service';
import {ExerciseNamePipe} from '../shared/exercise-name.pipe';
import {formatDuration, formatNumber} from '../shared/workout-format';
import {WorkoutI18nService} from '../shared/workout-i18n.service';
import {ChartSeries, ProgressChartComponent} from './progress-chart/progress-chart.component';

type Metric = 'top' | 'volume' | 'maxReps' | 'totalReps' | 'maxSeconds' | 'totalSeconds' | 'distance' | 'pace' | 'pace100';

interface MetricSpec {
  label: string;
  // Higher is better, except for pace.
  lowerIsBetter: boolean;
  isTime: boolean;
  unit: string;
  series: {label: string; pick: (point: ProgressPointSchema) => number | null | undefined; dashed: boolean}[];
}

@Component({
  selector: 'app-workout-progress',
  imports: [NgIcon, RouterLink, PageHeaderComponent, EmptyStateComponent, LoadingStateComponent, ExerciseNamePipe, ProgressChartComponent],
  templateUrl: './progress.component.html',
})
export class ProgressComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly routingService = inject(RoutingService);
  protected readonly i18n = inject(WorkoutI18nService);

  readonly summary = signal<ExerciseHistorySummarySchema[]>([]);
  readonly progress = signal<ExerciseProgressSchema | null>(null);
  readonly selectedId = signal<number | null>(null);
  readonly metric = signal<Metric | null>(null);
  readonly isLoading = signal<boolean>(true);

  readonly plansUrl = this.routingService.getWorkoutPlanUrl();
  readonly backIcon = computed(() => this.i18n.dir() === 'rtl' ? featherArrowRight : featherArrowLeft);
  readonly exerciseUrls = computed(() => Object.fromEntries(
    this.summary().map(item => [item.exercise.id, this.routingService.getWorkoutProgressUrl(item.exercise.id)]),
  ));
  readonly sessionUrls = computed(() => Object.fromEntries(
    (this.progress()?.points ?? []).map(point => [point.session_id, this.routingService.getWorkoutSessionUrl(point.session_id)]),
  ));

  readonly metrics = computed<Metric[]>(() => {
    switch (this.progress()?.exercise.tracking_type) {
      case 'weight_reps': return ['top', 'volume'];
      case 'reps': return ['maxReps', 'totalReps'];
      case 'time': return ['maxSeconds', 'totalSeconds'];
      case 'distance': return ['distance', 'pace'];
      case 'laps': return ['distance', 'pace100'];
      default: return [];
    }
  });
  readonly activeMetric = computed<Metric | null>(() => {
    const chosen = this.metric();
    return chosen && this.metrics().includes(chosen) ? chosen : this.metrics()[0] ?? null;
  });
  readonly specs = computed<Record<Metric, MetricSpec>>(() => {
    const t = this.i18n.t();
    const perSide = this.progress()?.exercise.per_side ?? false;
    return {
      top: {
        label: t.topWeight, lowerIsBetter: false, isTime: false, unit: t.weightKg,
        series: perSide
          ? [
            {label: t.right, pick: p => p.top_weight_right_kg, dashed: false},
            {label: t.left, pick: p => p.top_weight_left_kg, dashed: true},
          ]
          : [{label: t.topWeight, pick: p => p.top_weight_kg, dashed: false}],
      },
      volume: {label: t.volume, lowerIsBetter: false, isTime: false, unit: t.weightKg, series: [{label: t.volume, pick: p => p.volume_kg, dashed: false}]},
      maxReps: {label: t.maxReps, lowerIsBetter: false, isTime: false, unit: t.reps, series: [{label: t.maxReps, pick: p => p.max_reps, dashed: false}]},
      totalReps: {label: t.totalReps, lowerIsBetter: false, isTime: false, unit: t.reps, series: [{label: t.totalReps, pick: p => p.total_reps, dashed: false}]},
      maxSeconds: {label: t.longestHold, lowerIsBetter: false, isTime: true, unit: '', series: [{label: t.longestHold, pick: p => p.max_seconds, dashed: false}]},
      totalSeconds: {label: t.time, lowerIsBetter: false, isTime: true, unit: '', series: [{label: t.time, pick: p => p.total_seconds, dashed: false}]},
      distance: {label: t.distance, lowerIsBetter: false, isTime: false, unit: t.distanceKm, series: [{label: t.distance, pick: p => p.distance_km, dashed: false}]},
      pace: {label: t.pace, lowerIsBetter: true, isTime: true, unit: t.perKm, series: [{label: t.pace, pick: p => p.pace_seconds_per_km, dashed: false}]},
      pace100: {label: t.pace, lowerIsBetter: true, isTime: true, unit: t.per100m, series: [{label: t.pace, pick: p => p.pace_seconds_per_100m, dashed: false}]},
    };
  });

  readonly chart = computed(() => {
    const progress = this.progress();
    const metric = this.activeMetric();
    if (!progress || !metric) {
      return null;
    }
    const spec = this.specs()[metric];
    const points = progress.points;
    const dateFormat = new Intl.DateTimeFormat(this.i18n.language(), {day: 'numeric', month: 'short'});
    const series: ChartSeries[] = spec.series.map(s => {
      const values = points.map(point => s.pick(point) ?? null);
      return {
        label: s.label, dashed: s.dashed, values,
        valueLabels: values.map(value => value === null ? '' : this.format(value, spec)),
      };
    }).filter(s => s.values.some(value => value !== null));
    const all = series.flatMap(s => s.values).filter((value): value is number => value !== null);
    if (all.length === 0) {
      return null;
    }
    const ticks = this.niceTicks(Math.min(...all), Math.max(...all));
    return {
      dates: points.map(point => dateFormat.format(new Date(point.date))),
      series,
      axisValues: ticks,
      axisLabels: ticks.map(tick => spec.isTime ? formatDuration(tick) : formatNumber(tick)),
    };
  });

  // The headline: where the exercise stands now, and how far it moved since the first logged workout.
  readonly headline = computed(() => {
    const progress = this.progress();
    const metric = this.activeMetric();
    if (!progress || !metric) {
      return null;
    }
    const spec = this.specs()[metric];
    const pick = spec.series[0].pick;
    const values = progress.points.map(point => pick(point)).filter((value): value is number => value !== null && value !== undefined);
    if (values.length === 0) {
      return null;
    }
    const latest = values[values.length - 1];
    const diff = latest - values[0];
    const better = spec.lowerIsBetter ? diff < 0 : diff > 0;
    return {
      value: this.format(latest, spec),
      delta: values.length > 1 && Math.abs(diff) > 1e-9 ? `${diff > 0 ? '+' : '−'}${this.format(Math.abs(diff), spec)}` : null,
      better,
    };
  });

  readonly rows = computed(() => {
    const progress = this.progress();
    const metric = this.activeMetric();
    if (!progress || !metric) {
      return [];
    }
    const spec = this.specs()[metric];
    const dateFormat = new Intl.DateTimeFormat(this.i18n.language(), {weekday: 'short', day: 'numeric', month: 'short', year: 'numeric'});
    return [...progress.points].reverse().map(point => ({
      sessionId: point.session_id,
      date: dateFormat.format(new Date(point.date)),
      value: spec.series
        .map(s => {
          const value = s.pick(point);
          return value === null || value === undefined ? null : `${spec.series.length > 1 ? `${s.label} ` : ''}${this.format(value, spec)}`;
        })
        .filter(text => text !== null).join(' · '),
    }));
  });

  constructor() {
    void this.i18n.load();
    this.route.queryParamMap.subscribe(params => {
      const id = Number(params.get('exercise'));
      void this.load(Number.isNaN(id) || id <= 0 ? null : id);
    });
  }

  private async load(exerciseId: number | null): Promise<void> {
    if (this.summary().length === 0) {
      this.isLoading.set(true);
      try {
        const res = await getProgressSummaryView();
        this.summary.set(res.data.exercises);
      } finally {
        this.isLoading.set(false);
      }
    }
    const id = exerciseId ?? this.summary()[0]?.exercise.id ?? null;
    this.selectedId.set(id);
    this.metric.set(null);
    if (id === null) {
      this.progress.set(null);
      return;
    }
    const res = await getExerciseProgressView({path: {exercise_id: id}});
    this.progress.set(res.data);
  }

  private format(value: number, spec: MetricSpec): string {
    const text = spec.isTime ? formatDuration(value) : formatNumber(value);
    return spec.unit ? `${text} ${spec.unit}` : text;
  }

  // Four round-numbered gridlines that cover the data, so the axis reads 30 · 35 · 40 · 45, not 31.7 · 36.2.
  private niceTicks(min: number, max: number): number[] {
    if (min === max) {
      const pad = Math.abs(min) * 0.1 || 1;
      min -= pad;
      max += pad;
    }
    const rough = (max - min) / 3;
    const magnitude = Math.pow(10, Math.floor(Math.log10(rough)));
    const step = [1, 2, 2.5, 5, 10].map(m => m * magnitude).find(s => s >= rough) ?? 10 * magnitude;
    const start = Math.floor(min / step) * step;
    const end = Math.ceil(max / step) * step;
    const ticks: number[] = [];
    for (let value = start; value <= end + step / 2; value += step) {
      ticks.push(Math.max(0, Math.round(value * 1000) / 1000));
    }
    return [...new Set(ticks)];
  }
}
