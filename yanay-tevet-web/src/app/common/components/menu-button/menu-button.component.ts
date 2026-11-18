import {Component, computed, input} from '@angular/core';
import {CdkMenuModule} from '@angular/cdk/menu';
import {Action} from '../../interfaces/util/action';
import {NgIcon} from '@ng-icons/core';
import {COMMON_STRINGS} from '../../../common/i18n';
import {injectStrings} from '../../../shared/i18n/strings';

export const SEPARATOR = 'SEPARATOR';
export type MenuItem = Action | typeof SEPARATOR;

@Component({
  selector: 'app-menu-button',
  imports: [
    CdkMenuModule,
    NgIcon,
  ],
  templateUrl: './menu-button.component.html',
  styleUrl: './menu-button.component.css'
})
export class MenuButtonComponent {
  text = input<string>('');
  color = input<string>('writing');
  icon = input<string>(null);
  // Read by screen readers when the button shows only an icon.
  ariaLabel = input<string | undefined>(undefined);
  private readonly t = injectStrings(COMMON_STRINGS);
  protected readonly ariaLabelText = computed(() => this.ariaLabel() ?? this.t().moreActions);
  actions= input<MenuItem[]>();

  // Make SEPARATOR constant accessible in the template
  readonly SEPARATOR = SEPARATOR;
}
