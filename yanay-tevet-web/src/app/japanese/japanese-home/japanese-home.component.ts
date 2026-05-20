import {Component, inject, signal} from '@angular/core';
import {RouterLink} from '@angular/router';
import {
  getRandomNodesView,
  NodeSummarySchema,
} from '../../../generated-files/api/japanese';
import {AuthenticationService} from '../../common/authentication/authentication.service';
import {RoutingService} from '../../shared/services/routing.service';
import {NodeSummaryCardComponent} from '../shared/node-summary-card/node-summary-card.component';

@Component({
  selector: 'app-japanese-home',
  standalone: true,
  imports: [NodeSummaryCardComponent, RouterLink],
  templateUrl: './japanese-home.component.html',
})
export class JapaneseHomeComponent {
  protected readonly authService = inject(AuthenticationService);
  protected readonly routingService = inject(RoutingService);

  readonly sentences = signal<NodeSummarySchema[]>([]);
  readonly rules = signal<NodeSummarySchema[]>([]);
  readonly isLoading = signal<boolean>(false);
  readonly error = signal<string | null>(null);

  constructor() {
    void this.refresh();
  }

  async refresh(): Promise<void> {
    this.isLoading.set(true);
    this.error.set(null);
    try {
      const [sentencesRes, rulesRes] = await Promise.all([
        getRandomNodesView({query: {types: 'sentence', count: 6}}),
        getRandomNodesView({query: {types: 'rule', count: 6}}),
      ]);
      this.sentences.set(sentencesRes.data.nodes);
      this.rules.set(rulesRes.data.nodes);
    } catch {
      this.error.set('Failed to load. Is the backend running?');
    } finally {
      this.isLoading.set(false);
    }
  }
}
