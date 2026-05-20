import {Component, inject, signal} from '@angular/core';
import {RouterLink} from '@angular/router';
import {
  getReviewQueueView,
  NodeSummarySchema,
} from '../../../generated-files/api/japanese';
import {RoutingService} from '../../shared/services/routing.service';
import {NodeSummaryCardComponent} from '../shared/node-summary-card/node-summary-card.component';

@Component({
  selector: 'app-japanese-review',
  standalone: true,
  imports: [NodeSummaryCardComponent, RouterLink],
  templateUrl: './japanese-review.component.html',
})
export class JapaneseReviewComponent {
  protected readonly routingService = inject(RoutingService);

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
