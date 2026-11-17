import {computed, Injectable, signal} from '@angular/core';
import {getWorkoutPreferencesView, updateWorkoutPreferencesView} from '../../../generated-files/api/workout-plan';
import {WORKOUT_STRINGS, WorkoutLanguage, WorkoutStrings} from './workout-strings';

// The language lives on the account (so it follows the user to the phone); until it has loaded, or for a
// user who never picked one, the browser's language decides.
@Injectable({providedIn: 'root'})
export class WorkoutI18nService {
  readonly language = signal<WorkoutLanguage>(WorkoutI18nService.browserLanguage());
  readonly t = computed<WorkoutStrings>(() => WORKOUT_STRINGS[this.language()]);
  readonly dir = computed<'ltr' | 'rtl'>(() => this.language() === 'he' ? 'rtl' : 'ltr');
  private loaded = false;

  async load(): Promise<void> {
    if (this.loaded) {
      return;
    }
    this.loaded = true;
    try {
      const res = await getWorkoutPreferencesView();
      if (res.data.language) {
        this.language.set(res.data.language);
      }
    } catch {
      // Keep the browser's language; the toggle still works and saves.
      this.loaded = false;
    }
  }

  async toggle(): Promise<void> {
    const next: WorkoutLanguage = this.language() === 'he' ? 'en' : 'he';
    this.language.set(next);
    await updateWorkoutPreferencesView({body: {language: next}});
  }

  private static browserLanguage(): WorkoutLanguage {
    return navigator.language.toLowerCase().startsWith('he') ? 'he' : 'en';
  }
}
