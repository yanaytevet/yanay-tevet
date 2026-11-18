import {computed, inject, Injectable} from '@angular/core';
import {LanguageChooserService} from '../../shared/i18n/language-chooser.service';
import {LanguageService} from '../../shared/i18n/language.service';
import {WORKOUT_STRINGS, WorkoutStrings} from '../i18n';

// The workout app's strings in the site language (LanguageService); its language buttons change the site setting.
@Injectable({providedIn: 'root'})
export class WorkoutI18nService {
  private readonly languageService = inject(LanguageService);
  private readonly languageChooser = inject(LanguageChooserService);
  readonly language = this.languageService.language;
  readonly t = computed<WorkoutStrings>(() => WORKOUT_STRINGS[this.language()]);

  async chooseLanguage(): Promise<void> {
    await this.languageChooser.choose();
  }
}
