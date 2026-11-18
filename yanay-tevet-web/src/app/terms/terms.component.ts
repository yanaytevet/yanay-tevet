import {Component, computed, inject} from '@angular/core';
import {SUPPORT_EMAIL} from '../common/constants/app-constants';
import {LanguageService} from '../shared/i18n/language.service';
import {fill, injectStrings} from '../shared/i18n/strings';
import {TERMS_STRINGS} from './i18n';

// The month these terms last changed (May 2026); shown in the site language.
const LAST_UPDATED = new Date(2026, 4, 1);

@Component({
  selector: 'app-terms',
  standalone: true,
  imports: [],
  templateUrl: './terms.component.html',
})
export class TermsComponent {
  private readonly languageService = inject(LanguageService);
  protected readonly t = injectStrings(TERMS_STRINGS);
  readonly email = SUPPORT_EMAIL;

  readonly lastUpdated = computed(() => fill(this.t().lastUpdated, {
    date: new Intl.DateTimeFormat(this.languageService.language(), {month: 'long', year: 'numeric'}).format(LAST_UPDATED),
  }));
}
