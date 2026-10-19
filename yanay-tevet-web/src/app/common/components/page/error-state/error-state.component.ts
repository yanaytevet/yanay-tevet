import {Component, input} from '@angular/core';
import {RouterLink, UrlTree} from '@angular/router';
import {NgIcon} from '@ng-icons/core';
import {featherAlertCircle, featherArrowLeft} from '@ng-icons/feather-icons';

// Shown when a page's resource fails to load or no longer exists, with a way back.
@Component({
  selector: 'app-error-state',
  imports: [NgIcon, RouterLink],
  templateUrl: './error-state.component.html',
})
export class ErrorStateComponent {
  readonly text = input.required<string>();
  readonly backUrl = input<UrlTree | null>(null);
  readonly backLabel = input<string>('Back');

  protected readonly featherAlertCircle = featherAlertCircle;
  protected readonly featherArrowLeft = featherArrowLeft;
}
