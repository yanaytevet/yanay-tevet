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
        return 'bg-emerald-100 text-emerald-700';
      case 'needs_review':
        return 'bg-amber-100 text-amber-700';
      case 'generating':
        return 'bg-sky-100 text-sky-700';
      case 'stub':
      default:
        return 'bg-secondary-100 text-secondary-500';
    }
  });
}
