import {Component, computed, inject, input} from '@angular/core';
import {RouterLink} from '@angular/router';
import {NodeSummarySchema} from '../../../../generated-files/api/japanese';
import {RoutingService} from '../../../shared/services/routing.service';
import {injectStrings} from '../../../shared/i18n/strings';
import {JAPANESE_STRINGS} from '../../i18n';
import {FuriganaComponent} from '../furigana/furigana.component';
import {nodeDisplay} from '../node-display';
import {SpeakButtonComponent} from '../speak-button/speak-button.component';

@Component({
  selector: 'app-node-summary-card',
  standalone: true,
  imports: [FuriganaComponent, RouterLink, SpeakButtonComponent],
  templateUrl: './node-summary-card.component.html',
})
export class NodeSummaryCardComponent {
  private readonly routingService = inject(RoutingService);
  private readonly t = injectStrings(JAPANESE_STRINGS);

  node = input.required<NodeSummarySchema>();
  showStatus = input<boolean>(false);

  readonly nodeUrl = computed(() => this.routingService.getJapaneseNodeUrl(this.node().id));
  readonly display = computed(() => nodeDisplay(this.node(), this.t()));
}
