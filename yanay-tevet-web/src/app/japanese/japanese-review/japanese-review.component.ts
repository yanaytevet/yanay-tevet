import {Component, signal} from '@angular/core';
import {
  getReviewQueueView,
  NodeSummarySchema,
} from '../../../generated-files/api/japanese';
import {PageHeaderComponent} from '../../common/components/page/page-header/page-header.component';
import {EmptyStateComponent} from '../../common/components/page/empty-state/empty-state.component';
import {LoadingStateComponent} from '../../common/components/page/loading-state/loading-state.component';
import {ErrorStateComponent} from '../../common/components/page/error-state/error-state.component';
import {JapaneseNavComponent} from '../shared/japanese-nav/japanese-nav.component';
import {NodeSummaryCardComponent} from '../shared/node-summary-card/node-summary-card.component';

@Component({
  selector: 'app-japanese-review',
  standalone: true,
  imports: [
    NodeSummaryCardComponent, JapaneseNavComponent,
    PageHeaderComponent, EmptyStateComponent, LoadingStateComponent, ErrorStateComponent,
  ],
  templateUrl: './japanese-review.component.html',
})
export class JapaneseReviewComponent {
  readonly stubs = signal<NodeSummarySchema[]>([]);
  readonly needsReview = signal<NodeSummarySchema[]>([]);
  readonly isLoading = signal<boolean>(false);
  readonly error = signal<string | null>(null);

  constructor() {
    void this.refresh();
  }

  async refresh(): Promise<void> {
    this.isLoading.set(true);
    this.error.set(null);
    try {
      const res = await getReviewQueueView();
      this.stubs.set(res.data.stubs);
      this.needsReview.set(res.data.needs_review);
    } catch (err) {
      this.error.set(`Failed to load review queue: ${err}`);
    } finally {
      this.isLoading.set(false);
    }
  }
}
