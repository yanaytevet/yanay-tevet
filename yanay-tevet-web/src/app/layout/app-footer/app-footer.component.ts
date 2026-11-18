import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';
import { CHROME_STRINGS } from '../../shared/i18n/chrome';
import {injectStrings} from '../../shared/i18n/strings';

@Component({
  selector: 'app-footer',
  standalone: true,
  imports: [RouterLink],
  templateUrl: './app-footer.component.html',
})
export class AppFooterComponent {
  readonly year = new Date().getFullYear();
  protected readonly t = injectStrings(CHROME_STRINGS);
}
