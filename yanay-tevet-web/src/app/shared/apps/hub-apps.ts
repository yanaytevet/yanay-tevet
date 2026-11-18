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
  // English; templates show the site language's name from the chrome strings (localizedHubApps).
  name: string;
  icon: string;
  // The first URL segment of every page that belongs to the app.
  rootSegment: string;
}

export const HUB_APPS: Record<HubAppKey, HubApp> = {
  tasks: {key: 'tasks', name: 'Task Management', icon: bootstrapCheck2Square, rootSegment: 'task-management'},
  shopping: {key: 'shopping', name: 'Shopping Lists', icon: bootstrapCart3, rootSegment: 'shopping-lists'},
  dates: {key: 'dates', name: 'Special Dates', icon: bootstrapCake2, rootSegment: 'special-dates'},
  dreams: {key: 'dreams', name: 'Dream Diary', icon: bootstrapMoonStars, rootSegment: 'dream-diary'},
  workout: {key: 'workout', name: 'Workout Plan', icon: bootstrapHeartPulse, rootSegment: 'workout-plan'},
  itinerary: {key: 'itinerary', name: 'Itinerary Lists', icon: bootstrapLuggage, rootSegment: 'itinerary-lists'},
  home: {key: 'home', name: 'Home Sweet Home', icon: bootstrapHouseHeart, rootSegment: 'home-sweet-home'},
  japanese: {key: 'japanese', name: 'Japanese', icon: bootstrapTranslate, rootSegment: 'japanese'},
  genre: {key: 'genre', name: 'Genre Trainer', icon: bootstrapHeadphones, rootSegment: 'genre-trainer'},
  pdf: {key: 'pdf', name: 'PDF Editor', icon: bootstrapFileEarmarkPdf, rootSegment: 'pdf-editor'},
  dashboard: {key: 'dashboard', name: 'My Dashboard', icon: bootstrapSpeedometer2, rootSegment: 'my-dashboard'},
};

export function hubAppForUrl(url: string): HubApp | null {
  const rootSegment = url.split(/[/?#]/).find(segment => segment.length > 0) ?? '';
  return Object.values(HUB_APPS).find(app => app.rootSegment === rootSegment) ?? null;
}

// The registry with each app's name in the site language (CHROME_STRINGS' appNames), for templates.
export function localizedHubApps(names: Record<HubAppKey, string>): Record<HubAppKey, HubApp> {
  const entries = Object.values(HUB_APPS).map(app => [app.key, {...app, name: names[app.key]}]);
  return Object.fromEntries(entries) as Record<HubAppKey, HubApp>;
}
