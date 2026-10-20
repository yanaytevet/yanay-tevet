import {EnumDisplay} from '../../common/string-display/enum-display';

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

  families: { name: string; genres: string[] }[] = [
    { name: 'Psychedelic Trance', genres: ['psytrance', 'progressive_psy', 'goa', 'dark_psy', 'hightek', 'weird_finnish_trance'] },
    { name: 'Bass Music', genres: ['psy_bass', 'drum_and_bass', 'jungle'] },
    { name: 'Tek / Free Party', genres: ['tek'] },
    { name: 'Techno', genres: ['techno', 'hard_techno', 'acid_techno', 'minimal_techno', 'melodic_techno'] },
    { name: 'House', genres: ['house'] },
  ];

  // Layer roles in mix order (drums first), as the reveal's solo/mute chips show them.
  roleOrder: string[] = ['kick', 'snare', 'hihat', 'perc', 'bass', 'sub', 'lead', 'stab', 'pad'];

  traitLabels: Record<'tempo' | 'drums' | 'bass' | 'signature' | 'mood', string> = {
    tempo: 'Tempo',
    drums: 'Drums',
    bass: 'Bass',
    signature: 'Signature sound',
    mood: 'Mood',
  };

  roleLabels: Record<string, string> = {
    kick: 'Kick',
    snare: 'Snare / clap',
    hihat: 'Hi-hats',
    perc: 'Percussion',
    bass: 'Bass',
    sub: 'Sub',
    lead: 'Lead',
    stab: 'Stabs',
    pad: 'Pads',
  };
}
