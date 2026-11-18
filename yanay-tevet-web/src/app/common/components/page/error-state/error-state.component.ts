import {Component, computed, input} from '@angular/core';
import {RouterLink, UrlTree} from '@angular/router';
import {NgIcon} from '@ng-icons/core';
import {featherAlertCircle, featherArrowLeft} from '@ng-icons/feather-icons';
import {COMMON_STRINGS} from '../../../../common/i18n';
import {injectStrings} from '../../../../shared/i18n/strings';

// Shown when a page's resource fails to load or no longer exists, with a way back.
@Component({
  selector: 'app-error-state',
  imports: [NgIcon, RouterLink],
  templateUrl: './error-state.component.html',
})
export class ErrorStateComponent {
  readonly text = input.required<string>();
  readonly backUrl = input<UrlTree | null>(null);
  // Without a label, the site language's "Back".
  readonly backLabel = input<string | undefined>(undefined);
  private readonly t = injectStrings(COMMON_STRINGS);
  protected readonly backText = computed(() => this.backLabel() ?? this.t().back);

  protected readonly featherAlertCircle = featherAlertCircle;
  protected readonly featherArrowLeft = featherArrowLeft;
}
