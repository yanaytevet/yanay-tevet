import {Component, computed, effect, input, signal} from '@angular/core';
import {
  getRandomNodesView,
  NodeSummarySchema,
  NodeType,
} from '../../../../generated-files/api/japanese';
import {EmptyStateComponent} from '../../../common/components/page/empty-state/empty-state.component';
import {LoadingStateComponent} from '../../../common/components/page/loading-state/loading-state.component';
import {injectStrings} from '../../../shared/i18n/strings';
import {JAPANESE_STRINGS} from '../../i18n';
import {NodeSummaryCardComponent} from '../node-summary-card/node-summary-card.component';

@Component({
  selector: 'app-japanese-explore-grid',
  standalone: true,
  imports: [NodeSummaryCardComponent, EmptyStateComponent, LoadingStateComponent],
  templateUrl: './japanese-explore-grid.component.html',
})
export class JapaneseExploreGridComponent {
  nodeType = input.required<NodeType>();
  count = input<number>(12);

  protected readonly t = injectStrings(JAPANESE_STRINGS);

  readonly nodes = signal<NodeSummarySchema[]>([]);
  readonly isLoading = signal<boolean>(false);
  readonly failed = signal<boolean>(false);
  readonly emptyTitle = computed(() => this.t().explore.emptyTitles[this.nodeType()]);

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
    this.failed.set(false);
    try {
      const res = await getRandomNodesView({
        query: {types: type, count: this.count()},
      });
      this.nodes.set(res.data.nodes);
    } catch {
      this.failed.set(true);
    } finally {
      this.isLoading.set(false);
    }
  }
}
