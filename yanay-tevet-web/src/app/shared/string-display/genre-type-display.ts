import {EnumDisplay} from '../../common/string-display/enum-display';

export class GenreTypeDisplay extends EnumDisplay {
  override data: Record<string, string> = {
    psytrance: 'Psytrance',
    goa: 'Goa Trance',
    psy_bass: 'Psy Bass',
    dark_psy: 'Dark Psy',
    forest_psy: 'Forest Psy',
    tek: 'Tek',
    hightek: 'High-Tek',
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

  descriptions: Record<string, string> = {
    psytrance: '145–150 BPM · Four-on-floor kick · Acid 303-style basslines · Hypnotic, fast-moving leads',
    goa: '136–145 BPM · Melodic layered arpeggios · Mystical lead sequences · Drenched in reverb and delay',
    psy_bass: '138–143 BPM · Very heavy sub bass · Deep wobble or neuro basslines · Psychedelic grooves',
    dark_psy: '148–152 BPM · Dissonant, alien basslines · Heavy FM distortion · Dark, oppressive atmosphere',
    forest_psy: '148–155 BPM · Organic dark atmosphere · Chromatic chromatic basslines · Alien, heavily distorted leads',
    tek: '155–165 BPM · Purely percussive — no melody or bassline · Extremely distorted kick · Minimal and raw',
    hightek: '168–180 BPM · Faster and harsher than Tek · Industrial, chaotic percussion · Maximum aggression',
    techno: '128–140 BPM · Dark, mechanical groove · Four-on-floor with industrial textures · Hypnotic repetition',
    hard_techno: '145–152 BPM · Heavily distorted kick · Aggressive acid basslines · Faster and harder than techno',
    acid_techno: '133–140 BPM · TB-303 squelching acid basslines · Tight filter envelope · Raw and hypnotic',
    minimal_techno: '124–132 BPM · Sparse, hypnotic groove · Very few elements · Power through empty space',
    melodic_techno: '130–138 BPM · Emotional, cinematic feel · Rich AMSynth pads · Driving kick with melodic leads',
    house: '120–130 BPM · Soulful groove · Clap on beats 2 and 4 · Warm bass and chord stabs',
    drum_and_bass: '170–174 BPM · Breakbeat kick — not on every beat · Heavy reese or sub bass · Very fast hi-hats',
    jungle: '160–170 BPM · Syncopated amen-break patterns · Off-beat snares · Raw rave energy',
    weird_finnish_trance: '138–143 BPM · Quirky rhythms and unusual chord choices · Unpredictable structure · Finnish psychedelia',
  };

  families: { name: string; genres: string[] }[] = [
    { name: 'Psychedelic Trance', genres: ['psytrance', 'goa', 'dark_psy', 'forest_psy', 'weird_finnish_trance'] },
    { name: 'Bass Music', genres: ['psy_bass', 'drum_and_bass', 'jungle'] },
    { name: 'Tek / Free Party', genres: ['tek', 'hightek'] },
    { name: 'Techno', genres: ['techno', 'hard_techno', 'acid_techno', 'minimal_techno', 'melodic_techno'] },
    { name: 'House', genres: ['house'] },
  ];
}
