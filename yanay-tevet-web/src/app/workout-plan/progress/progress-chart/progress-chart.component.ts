import {afterNextRender, Component, computed, DestroyRef, ElementRef, inject, input, signal} from '@angular/core';

export interface ChartSeries {
  label: string;
  values: (number | null)[];
  // The second series (left side of a one-sided exercise) is dashed, so the two never rely on colour alone.
  dashed: boolean;
  valueLabels: string[];
}

interface PlottedPoint {
  x: number;
  y: number;
}

const HEIGHT = 220;
const PAD = {top: 16, right: 16, bottom: 28, left: 44};

// A small line chart drawn in SVG on the theme tokens, so it follows the app accent and dark mode.
// One series per line, one y axis; hover or tap shows that workout's values.
@Component({
  selector: 'app-progress-chart',
  host: {class: 'block'},
  templateUrl: './progress-chart.component.html',
})
export class ProgressChartComponent {
  readonly dates = input.required<string[]>();
  readonly series = input.required<ChartSeries[]>();
  readonly axisLabels = input.required<string[]>();
  readonly axisValues = input.required<number[]>();

  readonly hoverIndex = signal<number | null>(null);
  // Measured, so one SVG unit is one CSS pixel and the axis text keeps its size on a phone.
  readonly width = signal<number>(600);

  protected readonly height = HEIGHT;
  protected readonly pad = PAD;

  readonly bounds = computed(() => {
    const ticks = this.axisValues();
    return {min: Math.min(...ticks), max: Math.max(...ticks)};
  });
  readonly xs = computed(() => {
    const count = this.dates().length;
    const inner = this.width() - PAD.left - PAD.right;
    return this.dates().map((_, index) => PAD.left + (count === 1 ? inner / 2 : (inner * index) / (count - 1)));
  });
  readonly gridLines = computed(() => {
    const ticks = this.axisValues();
    return ticks.map((value, index) => ({y: this.yOf(value), label: this.axisLabels()[index]}));
  });
  readonly plotted = computed(() => this.series().map(series => {
    const xs = this.xs();
    const points: (PlottedPoint | null)[] = series.values.map((value, index) =>
      value === null ? null : {x: xs[index], y: this.yOf(value)});
    const path = points.reduce((d, point, index) => {
      if (!point) {
        return d;
      }
      const previous = index > 0 ? points[index - 1] : null;
      return `${d}${previous ? 'L' : 'M'}${point.x.toFixed(1)},${point.y.toFixed(1)} `;
    }, '');
    const last = [...points].reverse().find(point => point !== null) ?? null;
    return {series, points, path, last};
  }));
  readonly xLabels = computed(() => {
    const dates = this.dates();
    const xs = this.xs();
    if (dates.length === 0) {
      return [];
    }
    const indexes = dates.length <= 2 ? dates.map((_, i) => i) : [0, Math.floor((dates.length - 1) / 2), dates.length - 1];
    return [...new Set(indexes)].map(index => ({
      x: xs[index], label: dates[index],
      anchor: index === 0 ? 'start' : index === dates.length - 1 ? 'end' : 'middle',
    }));
  });
  readonly tooltip = computed(() => {
    const index = this.hoverIndex();
    if (index === null) {
      return null;
    }
    const x = this.xs()[index];
    return {
      x,
      leftPercent: (x / this.width()) * 100,
      alignEnd: x > this.width() * 0.6,
      date: this.dates()[index],
      rows: this.series().map(series => ({label: series.label, value: series.valueLabels[index], dashed: series.dashed}))
        .filter(row => row.value),
      dots: this.plotted().map(item => item.points[index]).filter((point): point is PlottedPoint => point !== null),
    };
  });

  constructor() {
    const host = inject(ElementRef<HTMLElement>);
    const destroyRef = inject(DestroyRef);
    afterNextRender(() => {
      const observer = new ResizeObserver(entries => {
        const width = Math.round(entries[0].contentRect.width);
        if (width > 0) {
          this.width.set(width);
        }
      });
      observer.observe(host.nativeElement);
      destroyRef.onDestroy(() => observer.disconnect());
    });
  }

  onPointer(event: PointerEvent): void {
    const svg = event.currentTarget as SVGSVGElement;
    const rect = svg.getBoundingClientRect();
    const x = ((event.clientX - rect.left) / rect.width) * this.width();
    const xs = this.xs();
    let nearest = 0;
    for (let index = 1; index < xs.length; index++) {
      if (Math.abs(xs[index] - x) < Math.abs(xs[nearest] - x)) {
        nearest = index;
      }
    }
    this.hoverIndex.set(xs.length > 0 ? nearest : null);
  }

  private yOf(value: number): number {
    const {min, max} = this.bounds();
    const inner = HEIGHT - PAD.top - PAD.bottom;
    return PAD.top + inner - (max === min ? inner / 2 : ((value - min) / (max - min)) * inner);
  }
}
