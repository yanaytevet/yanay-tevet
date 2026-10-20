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

  // What to listen for. The BPM ranges match the generators (genre_trainer/generators/).
  descriptions: Record<string, string> = {
    psytrance: '143–148 BPM · Rolling bass on the three 16ths after every kick · Squelchy, fast-moving leads · Driving and bright',
    progressive_psy: '134–140 BPM · Galloping bass on the last two 16ths of each beat · Deep, minimal and groovy · Sparse delayed plucks',
    goa: '138–145 BPM · Layered modal leads and arpeggios · Eastern-sounding scales · Warm rolling bass, lots of reverb and delay',
    psy_bass: '100–110 BPM · Swung, broken glitch-hop beat · Bass that wobbles in time with the beat · Psychedelic zaps and textures',
    dark_psy: '148–158 BPM · Distorted, squelchy rolling bass · Horror atmospheres or organic forest textures · Chromatic and alien',
    tek: '162–172 BPM · Heavily distorted, relentless kick · Offbeat bass and acid squelches · Raw free-party sound',
    hightek: '180–195 BPM · Very fast, tight rolling bass · Glitchy 32nd-note zaps and stutters · Relentless and bright',
    techno: '130–138 BPM · Offbeat open hi-hat · Rumbling or offbeat bass · Dark, hypnotic repetition',
    hard_techno: '145–155 BPM · Heavily distorted, pounding kick · Distorted rumble bass · Industrial and aggressive',
    acid_techno: '132–140 BPM · Squelching TB-303 line that slides between notes · Resonant filter sweeps · Raw and hypnotic',
    minimal_techno: '124–130 BPM · Sparse clicks, rims and blips · Very few elements · Power through empty space',
    melodic_techno: '120–126 BPM · Rolling offbeat bass · Arpeggiated plucks over minor chords · Big pumping pads, cinematic',
    house: '122–128 BPM · Swung groove with an offbeat open hi-hat · Clap on beats 2 and 4 · Offbeat bass and chord stabs',
    drum_and_bass: '170–176 BPM · Two-step kick, snare on beats 2 and 4 · Reese or growling bass · Fast hi-hats',
    jungle: '160–170 BPM · Busy, chopped amen-style breaks · Deep dub sub bass · Raw rave energy',
    weird_finnish_trance: '142–150 BPM · Bouncy bass, playful leads · Odd intervals and cartoonish sounds · Unpredictable phrasing (suomisaundi)',
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
