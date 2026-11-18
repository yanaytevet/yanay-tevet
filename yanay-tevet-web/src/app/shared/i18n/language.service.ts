import {Directionality} from '@angular/cdk/bidi';
import {DOCUMENT} from '@angular/common';
import {computed, effect, inject, Injectable, signal} from '@angular/core';
import {Language, updateMyLanguageView} from '../../../generated-files/api/users';
import {AuthenticationService} from '../../common/authentication/authentication.service';
import {isLanguage, languageDir, matchLanguage} from './languages';

const STORAGE_KEY = 'language';

// The site language. The account's choice wins, so it follows the user to every device; before sign-in, or
// for someone who never picked one, the last choice in this browser and then the browser's own language.
@Injectable({providedIn: 'root'})
export class LanguageService {
  private readonly authService = inject(AuthenticationService);
  private readonly document = inject(DOCUMENT);
  private readonly directionality = inject(Directionality);
  private readonly localChoice = signal<Language | null>(LanguageService.readLocal());

  readonly language = computed<Language>(() =>
    this.authService.user()?.language ?? this.localChoice() ?? LanguageService.browserLanguage());
  readonly dir = computed<'ltr' | 'rtl'>(() => languageDir(this.language()));

  constructor() {
    // `lang` picks the right fonts and hyphenation (Japanese vs Chinese glyphs share code points); `dir` on
    // <html> flips the whole app for Hebrew and Arabic. The CDK reads the document's direction only once, so
    // its Directionality (menus, overlay positioning) is updated here too.
    effect(() => {
      const root = this.document.documentElement;
      const dir = this.dir();
      root.lang = this.language();
      root.dir = dir;
      if (this.directionality.value !== dir) {
        this.directionality.valueSignal.set(dir);
        this.directionality.change.emit(dir);
      }
    });
  }

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
    // The account's language wins over the local choice, so switch it here first: the site changes at once,
    // and if the save fails it stays changed in this tab (the next load follows the account again).
    this.authService.auth.update(auth => (auth ? {...auth, user: {...auth.user, language}} : auth));
    const {data, error} = await updateMyLanguageView({body: {language}});
    if (data) {
      this.authService.auth.update(auth => (auth ? {...auth, user: data} : auth));
    } else if (error) {
      throw error;
    }
  }

  private static readLocal(): Language | null {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      return isLanguage(stored) ? stored : null;
    } catch {
      return null;
    }
  }

  private static browserLanguage(): Language {
    for (const tag of navigator.languages ?? [navigator.language]) {
      const match = matchLanguage(tag);
      if (match) {
        return match;
      }
    }
    return 'en';
  }
}
