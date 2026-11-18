import {Translations} from '../../shared/i18n/strings';
import {ar} from './ar';
import {de} from './de';
import {ApartmentHuntStrings, en} from './en';
import {es} from './es';
import {fr} from './fr';
import {he} from './he';
import {ja} from './ja';
import {ru} from './ru';
import {zhHans} from './zh-hans';

export type {ApartmentHuntStrings};

export const APARTMENT_HUNT_STRINGS: Translations<ApartmentHuntStrings> = {
  en, he, ar, de, es, fr, ru, ja, 'zh-Hans': zhHans,
};
