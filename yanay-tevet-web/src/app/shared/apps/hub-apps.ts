import {
  bootstrapCake2,
  bootstrapCart3,
  bootstrapCheck2Square,
  bootstrapFileEarmarkPdf,
  bootstrapHeadphones,
  bootstrapHeartPulse,
  bootstrapHouseHeart,
  bootstrapLuggage,
  bootstrapMoonStars,
  bootstrapSpeedometer2,
  bootstrapTranslate,
} from '@ng-icons/bootstrap-icons';

// Each key has a pair of accent colours under [data-app="<key>"] in styles.css (DESIGN.md §2, App accents).
export type HubAppKey =
  | 'tasks'
  | 'shopping'
  | 'dates'
  | 'dreams'
  | 'workout'
  | 'itinerary'
  | 'home'
  | 'japanese'
  | 'genre'
  | 'pdf'
  | 'dashboard';

export interface HubApp {
  key: HubAppKey;
  name: string;
  // Shown when the site language is Hebrew (LanguageService).
  nameHe: string;
  icon: string;
  // The first URL segment of every page that belongs to the app.
  rootSegment: string;
}

export const HUB_APPS: Record<HubAppKey, HubApp> = {
  tasks: {key: 'tasks', name: 'Task Management', nameHe: 'ניהול משימות', icon: bootstrapCheck2Square, rootSegment: 'task-management'},
  shopping: {key: 'shopping', name: 'Shopping Lists', nameHe: 'רשימות קניות', icon: bootstrapCart3, rootSegment: 'shopping-lists'},
  dates: {key: 'dates', name: 'תאריכים חשובים', nameHe: 'תאריכים חשובים', icon: bootstrapCake2, rootSegment: 'special-dates'},
  dreams: {key: 'dreams', name: 'Dream Diary', nameHe: 'יומן חלומות', icon: bootstrapMoonStars, rootSegment: 'dream-diary'},
  workout: {key: 'workout', name: 'Workout Plan', nameHe: 'תוכנית אימונים', icon: bootstrapHeartPulse, rootSegment: 'workout-plan'},
  itinerary: {key: 'itinerary', name: 'Itinerary Lists', nameHe: 'רשימות לטיול', icon: bootstrapLuggage, rootSegment: 'itinerary-lists'},
  home: {key: 'home', name: 'Home Sweet Home', nameHe: 'הבית המתוק', icon: bootstrapHouseHeart, rootSegment: 'home-sweet-home'},
  japanese: {key: 'japanese', name: 'Japanese', nameHe: 'יפנית', icon: bootstrapTranslate, rootSegment: 'japanese'},
  genre: {key: 'genre', name: 'Genre Trainer', nameHe: 'מאמן ז׳אנרים', icon: bootstrapHeadphones, rootSegment: 'genre-trainer'},
  pdf: {key: 'pdf', name: 'PDF Editor', nameHe: 'עורך PDF', icon: bootstrapFileEarmarkPdf, rootSegment: 'pdf-editor'},
  dashboard: {key: 'dashboard', name: 'My Dashboard', nameHe: 'הדשבורד שלי', icon: bootstrapSpeedometer2, rootSegment: 'my-dashboard'},
};

export function hubAppForUrl(url: string): HubApp | null {
  const rootSegment = url.split(/[/?#]/).find(segment => segment.length > 0) ?? '';
  return Object.values(HUB_APPS).find(app => app.rootSegment === rootSegment) ?? null;
}

// The registry with each app's name in the given language, for templates that show app names.
export function localizedHubApps(language: 'en' | 'he'): Record<HubAppKey, HubApp> {
  const entries = Object.values(HUB_APPS).map(app => [app.key, {...app, name: language === 'he' ? app.nameHe : app.name}]);
  return Object.fromEntries(entries) as Record<HubAppKey, HubApp>;
}
