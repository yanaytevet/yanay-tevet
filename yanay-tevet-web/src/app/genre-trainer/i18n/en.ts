import {PluralForms} from '../../shared/i18n/strings';

// Genre trainer strings. This file is the contract: every other language's file is typed against it.
// Genre and family names are proper names and stay in English (`shared/string-display/genre-type-display.ts`);
// the genres' listening profiles come from the backend and are shown as they are.
export const en = {
  // Page
  title: 'Genre Trainer',
  subtitle: 'Listen and identify the electronic music genre',
  streak: 'Streak',
  correct: 'Correct',
  nextTrack: 'Next Track',
  errors: {
    loadTrack: 'Failed to load track. Is the backend running?',
    loadCompare: 'Failed to load the comparison track.',
  },

  // Player
  player: {
    clickToStop: 'Click to stop',
    pressPlay: 'Press Play to start',
    loadingTrack: 'Loading track...',
    auto: 'Auto',
    volume: 'Volume',
    play: 'Play',
    stop: 'Stop',
    settings: 'Training settings',
    selectFamilies: 'Select at least 2 families in settings',
    selectGenres: 'Select at least 2 genres in settings',
  },

  // Guessing and focus
  whatFamily: 'What family of genres is this?',
  whatGenre: 'What genre is this?',
  trainOn: 'Train on',
  all: 'All',

  // Settings dialog
  config: {
    title: 'Training Configuration',
    difficulty: 'Difficulty',
    hard: 'Hard',
    easy: 'Easy',
    autoStop: 'Auto-stop',
    fewerRepetitions: 'Fewer repetitions',
    moreRepetitions: 'More repetitions',
    // Shown after the number, which sits in its own box.
    repetitions: {one: 'repetition', other: 'repetitions'} as PluralForms,
    repetitionsNeverStops: 'repetitions (never stops)',
    mixUps: 'Genres you mix up',
    resetProgress: 'Reset progress',
    resetPending: 'Your record and mix-ups will be cleared when you apply.',
    confusionRow: '{actual} taken for {guessed}',
    noMixUps: 'No mix-ups yet. Wrong guesses in Hard mode show up here.',
    cancel: 'Cancel',
    apply: 'Apply',
    resetTitle: 'Reset your progress?',
    resetText: 'Your per-genre record and the list of genres you mix up are cleared when you apply.',
    reset: 'Reset',
  },

  // The reveal after a guess
  reveal: {
    correct: 'Correct!',
    notQuite: 'Not quite.',
    youGuessed: 'You guessed {genre}.',
    familyLabel: 'Family:',
    genreLabel: 'Genre:',
    giveaway: 'What gave it away — {trait}:',
    whyNot: 'Why it’s {actual}, not {other}',
    verdicts: {
      veryClose: 'Very close',
      close: 'Close',
      notClose: 'Not close',
    },
    // The first sentence of the explanation: how the two genres relate.
    sameFamilyOverlap: 'Same family, overlapping tempo.',
    sameFamilyFaster: 'Same family, but {actual} is faster ({actualRange} vs {otherRange} BPM).',
    sameFamilySlower: 'Same family, but {actual} is slower ({actualRange} vs {otherRange} BPM).',
    differentFamiliesOverlap: 'Different families, overlapping tempo.',
    differentFamiliesFaster: 'Different families; {actual} is faster ({actualRange} vs {otherRange} BPM).',
    differentFamiliesSlower: 'Different families; {actual} is slower ({actualRange} vs {otherRange} BPM).',
    // The second sentence: the trait that tells them apart.
    givesItAway: {
      tempo: 'The tempo gives it away.',
      drums: 'The drums give it away.',
      bass: 'The bass gives it away.',
      signature: 'The signature sound gives it away.',
      mood: 'The mood gives it away.',
    },
    // Joins the two sentences above.
    sentenceSeparator: ' ',
    columnThisTrack: '{genre} · this track',
    columnOther: '{genre} · {note}',
    noteYourGuess: 'your guess',
    noteClosest: 'closest in the family you picked',
    tempoThisTrack: '{range} BPM (this track: {bpm})',
    tipTempo: 'Next time, feel the tempo: {actual} runs at {actualRange} BPM, {other} at {otherRange}.',
    // {description} is the genre's profile text from the backend.
    tipListenFor: {
      drums: 'Next time, listen for the drums — {description}.',
      bass: 'Next time, listen for the bass — {description}.',
      signature: 'Next time, listen for the signature sound — {description}.',
      mood: 'Next time, listen for the mood — {description}.',
    },
    compare: 'Compare A/B',
    stopComparing: 'Stop comparing',
    whichTrack: 'Which track to play',
    thisTrack: 'This track',
    loading: 'Loading…',
    yourGuess: 'Your guess: {genre}',
    switching: 'Switching every two loops, both in the same key.',
    listenCloser: 'Listen closer',
    tapMode: 'What tapping a part does',
    solo: 'Solo',
    mute: 'Mute',
    fullMix: 'Full mix',
    keyRoleHint: 'The part that gives {genre} away: {part}',
    thisTrackBpm: 'This track:',
    guessTrackBpm: 'your guess’s track:',
    record: 'Your record on {genre}:',
    takenFor: 'You’ve taken it for',
    familyHeading: '{family} family',
  },

  // The families of the Easy mode.
  families: {
    psy: 'Psychedelic Trance',
    bass: 'Bass Music',
    tek: 'Tek / Free Party',
    techno: 'Techno',
    house: 'House',
  },

  traits: {
    tempo: 'Tempo',
    drums: 'Drums',
    bass: 'Bass',
    signature: 'Signature sound',
    mood: 'Mood',
  },

  // Layer roles, as the reveal's solo/mute chips show them.
  roles: {
    kick: 'Kick',
    snare: 'Snare / clap',
    hihat: 'Hi-hats',
    perc: 'Percussion',
    bass: 'Bass',
    sub: 'Sub',
    lead: 'Lead',
    stab: 'Stabs',
    pad: 'Pads',
  },
};

export type GenreStrings = typeof en;
