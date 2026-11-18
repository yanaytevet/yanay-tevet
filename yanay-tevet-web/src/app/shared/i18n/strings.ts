import {computed, inject, Signal} from '@angular/core';
import {Language} from '../../../generated-files/api/users';
import {LanguageService} from './language.service';

// One strings object per site language. Each area keeps its English strings in `en.ts`, whose type is the
// contract, and the other languages in files typed against it, so a missing or misspelt key fails the build.
export type Translations<T> = Record<Language, T>;

// The current language's strings for an area, for a component's `t`.
export function injectStrings<T>(table: Translations<T>): Signal<T> {
  const languageService = inject(LanguageService);
  return computed(() => table[languageService.language()]);
}

// Fills `{name}` placeholders: fill('{count} days left', {count: 3}).
export function fill(template: string, values: Record<string, string | number>): string {
  return template.replace(/\{(\w+)\}/g, (match, key: string) => (key in values ? String(values[key]) : match));
}

// A count-dependent string. Only `other` is required; Russian and Arabic need `few`/`many` (and Arabic `two`
// and `zero`) to read right. `{count}` in the chosen form is replaced with the number.
export interface PluralForms {
  zero?: string;
  one?: string;
  two?: string;
  few?: string;
  many?: string;
  other: string;
}

const pluralRules = new Map<Language, Intl.PluralRules>();

export function plural(language: Language, count: number, forms: PluralForms): string {
  let rules = pluralRules.get(language);
  if (!rules) {
    rules = new Intl.PluralRules(language);
    pluralRules.set(language, rules);
  }
  const category = rules.select(count) as keyof PluralForms;
  const template = forms[category] ?? forms.other;
  return fill(template, {count: count.toLocaleString(language)});
}
