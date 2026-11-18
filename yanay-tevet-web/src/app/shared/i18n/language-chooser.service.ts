import {inject, Injectable} from '@angular/core';
import {DialogService} from '../../common/dialogs/dialogs.service';
import {CHROME_STRINGS} from './chrome';
import {LanguageService} from './language.service';
import {isLanguage, LANGUAGES} from './languages';

// The language switch as a dialog, for pages that offer it from a button or a menu entry rather than the
// <app-language-picker> dropdown.
@Injectable({providedIn: 'root'})
export class LanguageChooserService {
  private readonly languageService = inject(LanguageService);
  private readonly dialogService = inject(DialogService);

  async choose(): Promise<void> {
    const t = CHROME_STRINGS[this.languageService.language()];
    const value: unknown = await this.dialogService.getValueFromSelectionDialog({
      title: t.language,
      text: '',
      method: 'buttons',
      confirmActionName: t.change,
      options: LANGUAGES.map(language => ({display: language.nativeName, value: language.code})),
      defaultValue: this.languageService.language(),
    });
    if (typeof value !== 'string' || !isLanguage(value) || value === this.languageService.language()) {
      return;
    }
    try {
      await this.languageService.set(value);
    } catch {
      const after = CHROME_STRINGS[value];
      await this.dialogService.showNotificationDialog({title: after.error, text: after.languageSaveFailed});
    }
  }
}
