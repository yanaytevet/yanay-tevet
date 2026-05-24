import {Component, afterNextRender, computed, effect, inject, signal} from '@angular/core';
import {NgIcon} from '@ng-icons/core';
import {bootstrapArrowClockwise, bootstrapCurrencyDollar} from '@ng-icons/bootstrap-icons';
import {getOpenAiCostsView, OpenAiCostsOutput} from '../../../generated-files/api/my-dashboard';
import {MyDashboardService} from '../my-dashboard.service';

@Component({
  selector: 'app-openai-credits-card',
  standalone: true,
  imports: [NgIcon],
  templateUrl: './openai-credits-card.component.html',
})
export class OpenAiCreditsCardComponent {
  private readonly dashboard = inject(MyDashboardService);

  protected readonly bootstrapArrowClockwise = bootstrapArrowClockwise;
  protected readonly bootstrapCurrencyDollar = bootstrapCurrencyDollar;

  protected readonly data = signal<OpenAiCostsOutput | null>(null);
  protected readonly isLoading = signal(false);
  protected readonly error = signal<string | null>(null);

  protected readonly currencySymbol = computed(() => {
    const code = (this.data()?.currency ?? 'usd').toLowerCase();
    if (code === 'usd') { return '$'; }
    if (code === 'eur') { return '€'; }
    return code.toUpperCase() + ' ';
  });

  protected readonly fetchedLabel = computed(() => {
    const iso = this.data()?.fetched_at;
    if (!iso) { return ''; }
    const d = new Date(iso);
    return d.toLocaleString();
  });

  constructor() {
    afterNextRender(() => void this.load());
    effect(() => {
      // Re-fetch when the dashboard global refresh fires.
      const tick = this.dashboard.refreshTick();
      if (tick > 0) { void this.load(); }
    });
  }

  async refresh(): Promise<void> {
    await this.load();
  }

  private async load(): Promise<void> {
    this.isLoading.set(true);
    this.error.set(null);
    try {
      const res = await getOpenAiCostsView();
      this.data.set(res.data);
    } catch (e) {
      const detail = (e as {response?: {data?: {detail?: string}}})?.response?.data?.detail;
      this.error.set(detail ?? 'Failed to load OpenAI costs.');
    } finally {
      this.isLoading.set(false);
    }
  }
}
