import {Component, computed, effect, input, signal} from '@angular/core';
import {
  getRandomNodesView,
  NodeSummarySchema,
  NodeType,
} from '../../../../generated-files/api/japanese';
import {EmptyStateComponent} from '../../../common/components/page/empty-state/empty-state.component';
import {LoadingStateComponent} from '../../../common/components/page/loading-state/loading-state.component';
import {NodeSummaryCardComponent} from '../node-summary-card/node-summary-card.component';

const EMPTY_TITLES: Record<NodeType, string> = {
  passage: 'No passages yet',
  sentence: 'No sentences yet',
  word: 'No words yet',
  kanji: 'No kanji yet',
  particle: 'No particles yet',
  rule: 'No rules yet',
};

@Component({
  selector: 'app-japanese-explore-grid',
  standalone: true,
  imports: [NodeSummaryCardComponent, EmptyStateComponent, LoadingStateComponent],
  templateUrl: './japanese-explore-grid.component.html',
})
export class JapaneseExploreGridComponent {
  nodeType = input.required<NodeType>();
  count = input<number>(12);

  readonly nodes = signal<NodeSummarySchema[]>([]);
  readonly isLoading = signal<boolean>(false);
  readonly error = signal<string | null>(null);
  readonly emptyTitle = computed(() => EMPTY_TITLES[this.nodeType()]);

  constructor() {
    effect(() => {
      const type = this.nodeType();
      void this.load(type);
    });
  }

  async shuffle(): Promise<void> {
    await this.load(this.nodeType());
  }

  private async load(type: NodeType): Promise<void> {
    this.isLoading.set(true);
    this.error.set(null);
    try {
      const res = await getRandomNodesView({
        query: {types: type, count: this.count()},
      });
      this.nodes.set(res.data.nodes);
    } catch {
      this.error.set('Failed to load. Is the backend running?');
    } finally {
      this.isLoading.set(false);
    }
  }
}
