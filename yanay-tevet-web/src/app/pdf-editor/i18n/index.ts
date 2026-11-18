import {Translations} from '../../shared/i18n/strings';
import {ar} from './ar';
import {de} from './de';
import {en, PdfEditorStrings} from './en';
import {es} from './es';
import {fr} from './fr';
import {he} from './he';
import {ja} from './ja';
import {ru} from './ru';
import {zhHans} from './zh-hans';

export type {PdfEditorStrings};

export const PDF_EDITOR_STRINGS: Translations<PdfEditorStrings> = {en, he, ar, de, es, fr, ru, ja, 'zh-Hans': zhHans};
