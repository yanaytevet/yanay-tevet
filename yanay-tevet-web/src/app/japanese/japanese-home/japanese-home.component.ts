import {Component, computed, inject, signal} from '@angular/core';
import {
  getRandomNodesView,
  NodeSummarySchema,
  NodeType,
} from '../../../generated-files/api/japanese';
import {RoutingService} from '../../shared/services/routing.service';
import {NodeSummaryCardComponent} from '../shared/node-summary-card/node-summary-card.component';

const TAB_ORDER: NodeType[] = ['sentence', 'word', 'kanji', 'particle', 'rule'];

const TAB_LABELS: Record<NodeType, string> = {
  sentence: 'Sentences',
  word: 'Words',
  kanji: 'Kanji',
  particle: 'Particles',
  rule: 'Rules',
};

@Component({
  selector: 'app-japanese-home',
  standalone: true,
  imports: [NodeSummaryCardComponent],
  templateUrl: './japanese-home.component.html',
})
export class JapaneseHomeComponent {
  protected readonly routingService = inject(RoutingService);

  readonly tabs = TAB_ORDER;
  readonly tabLabels = TAB_LABELS;

  readonly activeTab = signal<NodeType>('sentence');
  readonly nodes = signal<NodeSummarySchema[]>([]);
  readonly isLoading = signal<boolean>(false);
  readonly error = signal<string | null>(null);

  readonly activeTabLabel = computed(() => TAB_LABELS[this.activeTab()]);

  readonly tabActive = computed(() => {
    const t = this.activeTab();
    return Object.fromEntries(this.tabs.map(tab => [tab, tab === t]));
  });

  constructor() {
    void this.load();
  }

  async setTab(tab: NodeType): Promise<void> {
    if (tab === this.activeTab()) {
      return;
    }
    this.activeTab.set(tab);
    this.nodes.set([]);
    await this.load();
  }

  async load(): Promise<void> {
    this.isLoading.set(true);
    this.error.set(null);
    try {
      const res = await getRandomNodesView({
        query: {types: this.activeTab(), count: 12},
      });
      this.nodes.set(res.data.nodes);
    } catch {
      this.error.set('Failed to load. Is the backend running?');
    } finally {
      this.isLoading.set(false);
    }
  }
}
