import {Component, computed, inject, input} from '@angular/core';
import {RouterLink} from '@angular/router';
import {NodeSummarySchema} from '../../../../generated-files/api/japanese';
import {RoutingService} from '../../../shared/services/routing.service';
import {FuriganaComponent} from '../furigana/furigana.component';
import {SpeakButtonComponent} from '../speak-button/speak-button.component';

@Component({
  selector: 'app-node-summary-card',
  standalone: true,
  imports: [FuriganaComponent, RouterLink, SpeakButtonComponent],
  templateUrl: './node-summary-card.component.html',
})
export class NodeSummaryCardComponent {
  private readonly routingService = inject(RoutingService);

  node = input.required<NodeSummarySchema>();
  showStatus = input<boolean>(false);

  readonly nodeUrl = computed(() => this.routingService.getJapaneseNodeUrl(this.node().id));

  readonly typeLabel = computed(() => {
    const t = this.node().type;
    return t.charAt(0).toUpperCase() + t.slice(1);
  });

  readonly statusLabel = computed(() => {
    const s = this.node().status;
    return s.replace(/_/g, ' ');
  });

  readonly statusClass = computed(() => {
    switch (this.node().status) {
      case 'published':
        return 'bg-success-soft text-success';
      case 'needs_review':
        return 'bg-warning-soft text-warning';
      case 'generating':
        return 'bg-info-soft text-info';
      case 'stub':
      default:
        return 'bg-secondary-100 text-writing-minor';
    }
  });
}
