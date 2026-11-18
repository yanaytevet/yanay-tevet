import {ChangeDetectionStrategy, Component, inject, input} from '@angular/core';
import {DialogService} from '../../../common/dialogs/dialogs.service';
import {CHROME_STRINGS} from '../chrome';
import {LanguageService} from '../language.service';
import {isLanguage, LANGUAGES} from '../languages';
import {injectStrings} from '../strings';

// The site-language dropdown, each language named in itself. Used in account settings, the drawer and any
// app that wants the switch on its own pages.
@Component({
  selector: 'app-language-picker',
  changeDetection: ChangeDetectionStrategy.OnPush,
  template: `
    <select class="main-input w-full" [attr.aria-label]="label()" [value]="languageService.language()"
            (change)="onChange($event)">
      @for (option of languages; track option.code) {
        <option [value]="option.code" [attr.lang]="option.code"
                [selected]="option.code === languageService.language()">{{ option.nativeName }}</option>
      }
    </select>
  `,
})
export class LanguagePickerComponent {
  protected readonly languageService = inject(LanguageService);
  private readonly dialogService = inject(DialogService);
  private readonly t = injectStrings(CHROME_STRINGS);
  protected readonly languages = LANGUAGES;
  readonly label = input.required<string>();

  protected async onChange(event: Event): Promise<void> {
    const value = (event.target as HTMLSelectElement).value;
    if (!isLanguage(value)) {
      return;
    }
    try {
      await this.languageService.set(value);
    } catch {
      // set() switches the site before saving, so the strings below are already in the new language.
      const t = this.t();
      await this.dialogService.showNotificationDialog({title: t.error, text: t.languageSaveFailed});
    }
  }
}
