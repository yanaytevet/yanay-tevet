import {EnumDisplay} from '../../common/string-display/enum-display';

export class GenreTypeDisplay extends EnumDisplay {
  override data: Record<string, string> = {
    psytrance: 'Psytrance',
    goa: 'Goa Trance',
    psy_bass: 'Psy Bass',
    dark_psy: 'Dark Psy',
    tek: 'Tek',
    hightek: 'High-Tek',
    techno: 'Techno',
    hard_techno: 'Hard Techno',
    house: 'House',
    drum_and_bass: 'Drum & Bass',
    weird_finnish_trance: 'Weird Finnish Trance',
  };
}
