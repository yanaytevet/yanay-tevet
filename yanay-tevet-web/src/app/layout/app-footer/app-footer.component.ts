import { Component, computed, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { CHROME_STRINGS } from '../../shared/i18n/chrome-strings';
import { LanguageService } from '../../shared/i18n/language.service';

@Component({
  selector: 'app-footer',
  standalone: true,
  imports: [RouterLink],
  templateUrl: './app-footer.component.html',
})
export class AppFooterComponent {
  readonly year = new Date().getFullYear();
  protected readonly languageService = inject(LanguageService);
  protected readonly t = computed(() => CHROME_STRINGS[this.languageService.language()]);
}
