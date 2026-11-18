import {Translations} from '../strings';
import {ar} from './ar';
import {de} from './de';
import {ChromeStrings, en} from './en';
import {es} from './es';
import {fr} from './fr';
import {he} from './he';
import {ja} from './ja';
import {ru} from './ru';
import {zhHans} from './zh-hans';

export type {ChromeStrings};

export const CHROME_STRINGS: Translations<ChromeStrings> = {en, he, ar, de, es, fr, ru, ja, 'zh-Hans': zhHans};
