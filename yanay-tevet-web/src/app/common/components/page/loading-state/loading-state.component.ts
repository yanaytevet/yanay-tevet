import {Component, computed, input} from '@angular/core';
import {COMMON_STRINGS} from '../../../../common/i18n';
import {injectStrings} from '../../../../shared/i18n/strings';

// The line a page shows while its resource loads. Never a card, so the layout doesn't jump when the
// content arrives.
@Component({
  selector: 'app-loading-state',
  templateUrl: './loading-state.component.html',
})
export class LoadingStateComponent {
  // Without a label, the site language's "Loading".
  readonly label = input<string | undefined>(undefined);
  private readonly t = injectStrings(COMMON_STRINGS);
  protected readonly labelText = computed(() => this.label() ?? this.t().loading);
}
