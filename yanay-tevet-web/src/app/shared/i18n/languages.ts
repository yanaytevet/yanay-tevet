import {Language} from '../../../generated-files/api/users';

export interface LanguageInfo {
  code: Language;
  // The language's name in itself, as the picker shows it.
  nativeName: string;
  dir: 'ltr' | 'rtl';
}

// Every site language, in the order the picker lists them. The codes come from the backend's Language enum.
export const LANGUAGES: readonly LanguageInfo[] = [
  {code: 'en', nativeName: 'English', dir: 'ltr'},
  {code: 'he', nativeName: 'עברית', dir: 'rtl'},
  {code: 'ar', nativeName: 'العربية', dir: 'rtl'},
  {code: 'de', nativeName: 'Deutsch', dir: 'ltr'},
  {code: 'es', nativeName: 'Español', dir: 'ltr'},
  {code: 'fr', nativeName: 'Français', dir: 'ltr'},
  {code: 'ru', nativeName: 'Русский', dir: 'ltr'},
  {code: 'ja', nativeName: '日本語', dir: 'ltr'},
  {code: 'zh-Hans', nativeName: '简体中文', dir: 'ltr'},
];

export const LANGUAGE_CODES: readonly Language[] = LANGUAGES.map(language => language.code);

const RTL_LANGUAGES = new Set<Language>(LANGUAGES.filter(language => language.dir === 'rtl').map(language => language.code));

export function languageDir(language: Language): 'ltr' | 'rtl' {
  return RTL_LANGUAGES.has(language) ? 'rtl' : 'ltr';
}

export function isLanguage(value: string | null | undefined): value is Language {
  return value != null && (LANGUAGE_CODES as readonly string[]).includes(value);
}

// The site language that best matches a BCP 47 tag such as 'de-AT' or 'zh-CN', or null. Chinese is offered
// only in Simplified script, so any zh tag maps to it.
export function matchLanguage(tag: string): Language | null {
  const primary = tag.toLowerCase().split('-')[0];
  if (primary === 'zh') {
    return 'zh-Hans';
  }
  if (primary === 'iw') {
    return 'he';
  }
  return isLanguage(primary) ? primary : null;
}
