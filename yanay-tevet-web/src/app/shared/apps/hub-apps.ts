import {
  bootstrapCake2,
  bootstrapCart3,
  bootstrapCheck2Square,
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
  | 'dashboard';

export interface HubApp {
  key: HubAppKey;
  name: string;
  icon: string;
  // The first URL segment of every page that belongs to the app.
  rootSegment: string;
}

export const HUB_APPS: Record<HubAppKey, HubApp> = {
  tasks: {key: 'tasks', name: 'Task Management', icon: bootstrapCheck2Square, rootSegment: 'task-management'},
  shopping: {key: 'shopping', name: 'Shopping Lists', icon: bootstrapCart3, rootSegment: 'shopping-lists'},
  dates: {key: 'dates', name: 'תאריכים חשובים', icon: bootstrapCake2, rootSegment: 'special-dates'},
  dreams: {key: 'dreams', name: 'Dream Diary', icon: bootstrapMoonStars, rootSegment: 'dream-diary'},
  workout: {key: 'workout', name: 'Workout Plan', icon: bootstrapHeartPulse, rootSegment: 'workout-plan'},
  itinerary: {key: 'itinerary', name: 'Itinerary Lists', icon: bootstrapLuggage, rootSegment: 'itinerary-lists'},
  home: {key: 'home', name: 'Home Sweet Home', icon: bootstrapHouseHeart, rootSegment: 'home-sweet-home'},
  japanese: {key: 'japanese', name: 'Japanese', icon: bootstrapTranslate, rootSegment: 'japanese'},
  genre: {key: 'genre', name: 'Genre Trainer', icon: bootstrapHeadphones, rootSegment: 'genre-trainer'},
  dashboard: {key: 'dashboard', name: 'My Dashboard', icon: bootstrapSpeedometer2, rootSegment: 'my-dashboard'},
};

export function hubAppForUrl(url: string): HubApp | null {
  const rootSegment = url.split(/[/?#]/).find(segment => segment.length > 0) ?? '';
  return Object.values(HUB_APPS).find(app => app.rootSegment === rootSegment) ?? null;
}
