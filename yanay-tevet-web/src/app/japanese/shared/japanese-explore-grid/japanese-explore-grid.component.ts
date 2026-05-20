import {Component, effect, input, signal} from '@angular/core';
import {
  getRandomNodesView,
  NodeSummarySchema,
  NodeType,
} from '../../../../generated-files/api/japanese';
import {NodeSummaryCardComponent} from '../node-summary-card/node-summary-card.component';

@Component({
  selector: 'app-japanese-explore-grid',
  standalone: true,
  imports: [NodeSummaryCardComponent],
  templateUrl: './japanese-explore-grid.component.html',
})
export class JapaneseExploreGridComponent {
  nodeType = input.required<NodeType>();
  count = input<number>(12);

  readonly nodes = signal<NodeSummarySchema[]>([]);
  readonly isLoading = signal<boolean>(false);
  readonly error = signal<string | null>(null);

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
