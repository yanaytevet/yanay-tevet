import {computed, inject, Injectable, signal} from '@angular/core';
import {Language, updateMyLanguageView} from '../../../generated-files/api/users';
import {AuthenticationService} from '../../common/authentication/authentication.service';

const STORAGE_KEY = 'language';

// The site language. The account's choice wins, so it follows the user to every device; before sign-in, or
// for someone who never picked one, the last choice in this browser and then the browser's own language.
// Only translated parts of the site (the chrome and the apps that have strings) follow it; the rest stays
// English, so `dir` is applied per component rather than on <html>.
@Injectable({providedIn: 'root'})
export class LanguageService {
  private readonly authService = inject(AuthenticationService);
  private readonly localChoice = signal<Language | null>(LanguageService.readLocal());

  readonly language = computed<Language>(() =>
    this.authService.user()?.language ?? this.localChoice() ?? LanguageService.browserLanguage());
  readonly dir = computed<'ltr' | 'rtl'>(() => this.language() === 'he' ? 'rtl' : 'ltr');

  async set(language: Language): Promise<void> {
    this.localChoice.set(language);
    try {
      localStorage.setItem(STORAGE_KEY, language);
    } catch {
      // Private mode or blocked storage: the choice still holds for this tab.
    }
    if (!this.authService.isLoggedIn()) {
      return;
    }
    const {data} = await updateMyLanguageView({body: {language}});
    if (data) {
      this.authService.auth.update(auth => (auth ? {...auth, user: data} : auth));
    }
  }

  async toggle(): Promise<void> {
    await this.set(this.language() === 'he' ? 'en' : 'he');
  }

  private static readLocal(): Language | null {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      return stored === 'en' || stored === 'he' ? stored : null;
    } catch {
      return null;
    }
  }

  private static browserLanguage(): Language {
    return navigator.language.toLowerCase().startsWith('he') ? 'he' : 'en';
  }
}
