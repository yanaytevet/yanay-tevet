import {EnumDisplay} from '../../common/string-display/enum-display';

export type GenreFamilyId = 'psy' | 'bass' | 'tek' | 'techno' | 'house';
export type GenreRole = 'kick' | 'snare' | 'hihat' | 'perc' | 'bass' | 'sub' | 'lead' | 'stab' | 'pad';

// Genre names are proper names and stay in English in every language.

export class GenreTypeDisplay extends EnumDisplay {
  override data: Record<string, string> = {
    psytrance: 'Full-On Psytrance',
    progressive_psy: 'Progressive Psy',
    goa: 'Goa Trance',
    psy_bass: 'Psybass',
    dark_psy: 'Dark / Forest Psy',
    tek: 'Tek',
    hightek: 'Hi-Tech Psy',
    techno: 'Techno',
    hard_techno: 'Hard Techno',
    acid_techno: 'Acid Techno',
    minimal_techno: 'Minimal Techno',
    melodic_techno: 'Melodic Techno',
    house: 'House',
    drum_and_bass: 'Drum & Bass',
    jungle: 'Jungle',
    weird_finnish_trance: 'Weird Finnish Trance',
  };

  // The families of the Easy mode. Their names are translated (GENRE_STRINGS.families); the ids are what
  // settings store.
  families: {id: GenreFamilyId; genres: string[]}[] = [
    {id: 'psy', genres: ['psytrance', 'progressive_psy', 'goa', 'dark_psy', 'hightek', 'weird_finnish_trance']},
    {id: 'bass', genres: ['psy_bass', 'drum_and_bass', 'jungle']},
    {id: 'tek', genres: ['tek']},
    {id: 'techno', genres: ['techno', 'hard_techno', 'acid_techno', 'minimal_techno', 'melodic_techno']},
    {id: 'house', genres: ['house']},
  ];

  // Layer roles in mix order (drums first), as the reveal's solo/mute chips show them. Their names are
  // translated (GENRE_STRINGS.roles).
  roleOrder: GenreRole[] = ['kick', 'snare', 'hihat', 'perc', 'bass', 'sub', 'lead', 'stab', 'pad'];
}
