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

  descriptions: Record<string, string> = {
    psytrance: '145–150 BPM · Four-on-floor kick · Acid 303-style basslines · Hypnotic, fast-moving leads',
    goa: '136–145 BPM · Melodic layered arpeggios · Mystical lead sequences · Drenched in reverb and delay',
    psy_bass: '138–145 BPM · Very heavy sub bass · Deep wobble or neuro basslines · Psychedelic grooves',
    dark_psy: '148–152 BPM · Dissonant, alien basslines · Heavy FM distortion · Dark, oppressive atmosphere',
    tek: '155–165 BPM · Purely percussive — no melody or bassline · Extremely distorted kick · Minimal and raw',
    hightek: '168–180 BPM · Faster and harsher than Tek · Industrial, chaotic percussion · Maximum aggression',
    techno: '128–140 BPM · Dark, mechanical groove · Four-on-floor with industrial textures · Hypnotic repetition',
    hard_techno: '145–152 BPM · Heavily distorted kick · Aggressive acid basslines · Faster and harder than techno',
    house: '120–130 BPM · Soulful groove · Clap on beats 2 and 4 · Warm bass and chord stabs',
    drum_and_bass: '170–174 BPM · Breakbeat kick — not on every beat · Heavy reese or sub bass · Very fast hi-hats',
    weird_finnish_trance: '138–145 BPM · Quirky rhythms and unusual chord choices · Unpredictable structure · Finnish psychedelia',
  };

  families: { name: string; genres: string[] }[] = [
    { name: 'Psychedelic Trance', genres: ['psytrance', 'goa', 'dark_psy', 'weird_finnish_trance'] },
    { name: 'Bass Music', genres: ['psy_bass', 'drum_and_bass'] },
    { name: 'Tek / Free Party', genres: ['tek', 'hightek'] },
    { name: 'Techno', genres: ['techno', 'hard_techno'] },
    { name: 'House', genres: ['house'] },
  ];
}
