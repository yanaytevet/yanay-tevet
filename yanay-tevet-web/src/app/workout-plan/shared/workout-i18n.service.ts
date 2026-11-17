import {computed, inject, Injectable} from '@angular/core';
import {DialogService} from '../../common/dialogs/dialogs.service';
import {LanguageService} from '../../shared/i18n/language.service';
import {WORKOUT_STRINGS, WorkoutStrings} from './workout-strings';

// The workout app's strings in the site language (LanguageService); its switches change the site setting.
@Injectable({providedIn: 'root'})
export class WorkoutI18nService {
  private readonly languageService = inject(LanguageService);
  private readonly dialogService = inject(DialogService);
  readonly language = this.languageService.language;
  readonly dir = this.languageService.dir;
  readonly t = computed<WorkoutStrings>(() => WORKOUT_STRINGS[this.language()]);

  async toggle(): Promise<void> {
    try {
      await this.languageService.toggle();
    } catch (err) {
      await this.dialogService.showNotificationDialog({title: 'Error', text: `${err}`});
    }
  }
}
