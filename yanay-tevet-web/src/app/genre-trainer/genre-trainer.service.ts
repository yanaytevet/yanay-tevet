import {computed, Injectable, signal} from '@angular/core';
import {GenreProfileSchema, getGenresView, getRandomTrackView, TrackSchema} from '../../generated-files/api/genre-trainer';
import {GenreTypeDisplay} from '../shared/string-display/genre-type-display';

export interface GenreFamily {
  name: string;
  genres: string[];
}

export interface GenreStat {
  seen: number;
  correct: number;
}

// actual genre -> the genre it was taken for -> how many times.
export type Confusions = Record<string, Record<string, number>>;

export interface ConfusionPair {
  actual: string;
  guessed: string;
  count: number;
}

export interface RoleChip {
  role: string;
  label: string;
  isKey: boolean;
}

// Which track the reveal is playing: the one being guessed, or one of the genre the user guessed.
export type Listening = 'track' | 'compare';

export type Trait = 'tempo' | 'drums' | 'bass' | 'signature' | 'mood';
export type Verdict = 'Very close' | 'Close' | 'Not close';

export interface TraitRow {
  trait: Trait;
  label: string;
  actual: string;
  other: string;
  // The trait that tells the two genres apart.
  isKey: boolean;
}

// Why the track is its genre and not the one guessed (in easy mode: the closest genre of the guessed
// family), built from the two genres' profiles.
export interface Explanation {
  actualLabel: string;
  otherLabel: string;
  // How the compared genre relates to the answer: the guess itself, or the closest genre of the guessed family.
  otherNote: string;
  verdict: Verdict;
  reason: string;
  rows: TraitRow[];
  tip: string;
}

const TRAITS: Exclude<Trait, 'tempo'>[] = ['drums', 'bass', 'signature', 'mood'];
// A tempo gap this wide is the easiest cue to hear, so it outranks the genre's own defining trait.
const TELLING_TEMPO_GAP_BPM = 5;

// v2 reworked psy_bass (now halftime bass music) and hightek (now hi-tech psytrance) and merged
// forest_psy into dark_psy, so old records for those genres describe different music.
const STATS_VERSION = 2;
const GENRES_CHANGED_IN_V2 = ['psy_bass', 'hightek', 'forest_psy'];

@Injectable()
export class GenreTrainerService {
  private readonly genreDisplay = new GenreTypeDisplay();

  readonly track = signal<TrackSchema | null>(null);
  readonly genres = signal<string[]>([]);
  readonly displayedGenres = signal<string[]>([]);
  readonly isLoading = signal(false);
  readonly selectedGenre = signal<string | null>(null);
  readonly selectedFamily = signal<string | null>(null);
  readonly revealed = signal(false);
  readonly error = signal<string | null>(null);
  readonly autoStart = signal(true);
  readonly autoStopLoops = signal(10);
  readonly streak = signal(0);
  readonly totalAnswered = signal(0);
  readonly totalCorrect = signal(0);
  readonly focusGenres = signal<Set<string>>(this.loadFocusFromStorage());
  readonly focusFamilies = signal<Set<string>>(this.loadFamilyFocusFromStorage());
  readonly easyMode = signal<boolean>(this.loadEasyModeFromStorage());
  // Per-genre running record (persisted). Drives adaptive track selection so the
  // next track leans toward genres the user keeps missing or hasn't heard yet.
  readonly genreStats = signal<Record<string, GenreStat>>(this.loadStatsFromStorage());
  readonly confusions = signal<Confusions>(this.loadConfusionsFromStorage());
  // The last wrong genre guess, so the next pick can bring the genre the user reached for back soon.
  private readonly lastMiss = signal<{actual: string; guessed: string} | null>(null);

  // Each genre's listening profile (tempo, drums, bass, signature sound, mood), from the backend.
  readonly profiles = signal<Record<string, GenreProfileSchema>>({});

  readonly compareTrack = signal<TrackSchema | null>(null);
  readonly isCompareLoading = signal(false);
  readonly listening = signal<Listening>('track');

  readonly allFamilies: GenreFamily[] = this.genreDisplay.families;

  readonly isCorrect = computed(() => {
    const t = this.track();
    if (!t) { return false; }
    if (this.easyMode()) {
      const sf = this.selectedFamily();
      if (!sf) { return false; }
      const family = this.allFamilies.find(f => f.name === sf);
      return family?.genres.includes(t.genre) ?? false;
    } else {
      const s = this.selectedGenre();
      return s !== null && s === t.genre;
    }
  });

  readonly noFocus = computed(() => this.focusGenres().size === 0);
  readonly noFamilyFocus = computed(() => this.focusFamilies().size === 0);

  readonly playDisabled = computed(() =>
    this.easyMode() ? this.focusFamilies().size === 1 : this.focusGenres().size === 1
  );

  readonly playDisabledMessage = computed(() =>
    this.easyMode()
      ? 'Select at least 2 families in settings'
      : 'Select at least 2 genres in settings'
  );

  readonly genreLabelMap = computed(() =>
    Object.fromEntries(this.genres().map(g => [g, this.genreDisplay.get(g)]))
  );

  readonly trackGenreLabel = computed(() => {
    const t = this.track();
    return t ? this.genreDisplay.get(t.genre) : '';
  });

  readonly trackProfileRows = computed(() => {
    const t = this.track();
    const profile = t ? this.profiles()[t.genre] : undefined;
    if (!profile) { return []; }
    return [
      {label: this.genreDisplay.traitLabels['tempo'], text: `${profile.bpm_min}–${profile.bpm_max} BPM`},
      ...TRAITS.map(trait => ({label: this.genreDisplay.traitLabels[trait], text: profile[trait]})),
    ];
  });

  // After a correct answer: the trait that gives the genre away, so a lucky guess still teaches the cue.
  readonly giveaway = computed(() => {
    const t = this.track();
    const profile = t ? this.profiles()[t.genre] : undefined;
    if (!profile || !this.revealed() || !this.isCorrect()) { return null; }
    const trait = profile.key_trait as Exclude<Trait, 'tempo'>;
    return {label: this.genreDisplay.traitLabels[trait], text: profile[trait]};
  });

  readonly trackGenreFamily = computed(() => {
    const genre = this.track()?.genre;
    if (!genre) { return null; }
    return this.genreDisplay.families.find(f => f.genres.includes(genre)) ?? null;
  });

  // Accuracy on the current track's genre, including this answer (recorded on reveal).
  readonly currentGenreStat = computed<GenreStat | null>(() => {
    const t = this.track();
    if (!t) { return null; }
    return this.genreStats()[t.genre] ?? null;
  });

  // What the current track's genre has been taken for, most often first.
  readonly currentConfusions = computed(() => {
    const t = this.track();
    if (!t) { return []; }
    return Object.entries(this.confusions()[t.genre] ?? {})
      .sort(([, a], [, b]) => b - a)
      .slice(0, 3)
      .map(([genre, count]) => ({label: this.genreDisplay.get(genre), count}));
  });

  readonly topConfusions = computed<ConfusionPair[]>(() =>
    Object.entries(this.confusions())
      .flatMap(([actual, guesses]) => Object.entries(guesses).map(([guessed, count]) => ({actual, guessed, count})))
      .sort((a, b) => b.count - a.count)
      .slice(0, 8)
  );

  readonly selectedGenreLabel = computed(() => {
    const g = this.selectedGenre();
    return g ? this.genreDisplay.get(g) : '';
  });

  // After a wrong answer: the genre the track is compared with — the guessed genre, or in easy mode the
  // genre of the guessed family closest in tempo to the real one, since the nearest miss teaches the
  // boundary best.
  readonly compareGenre = computed<string | null>(() => {
    const t = this.track();
    if (!t || !this.revealed() || this.isCorrect()) { return null; }
    if (!this.easyMode()) { return this.selectedGenre(); }
    const family = this.allFamilies.find(f => f.name === this.selectedFamily());
    if (!family) { return null; }
    const profiles = this.profiles();
    const center = (genre: string): number => {
      const p = profiles[genre];
      return p ? (p.bpm_min + p.bpm_max) / 2 : 0;
    };
    const target = center(t.genre);
    return [...family.genres].sort((a, b) => Math.abs(center(a) - target) - Math.abs(center(b) - target))[0] ?? null;
  });

  readonly compareLabel = computed(() => {
    const genre = this.compareGenre();
    if (!genre) { return ''; }
    return this.easyMode() ? this.genreDisplay.get(genre) : `Your guess: ${this.genreDisplay.get(genre)}`;
  });

  readonly explanation = computed<Explanation | null>(() => {
    const t = this.track();
    const other = this.compareGenre();
    const profiles = this.profiles();
    const a = t ? profiles[t.genre] : undefined;
    const o = other ? profiles[other] : undefined;
    if (!t || !other || !a || !o) { return null; }

    const actualLabel = this.genreDisplay.get(t.genre);
    const otherLabel = this.genreDisplay.get(other);
    const familyOf = (genre: string): string | undefined => this.allFamilies.find(f => f.genres.includes(genre))?.name;
    const sameFamily = familyOf(t.genre) === familyOf(other);
    const tempoGap = Math.max(o.bpm_min - a.bpm_max, a.bpm_min - o.bpm_max, 0);
    const overlap = a.bpm_min <= o.bpm_max && o.bpm_min <= a.bpm_max;
    const verdict: Verdict = sameFamily && overlap ? 'Very close' : sameFamily || overlap ? 'Close' : 'Not close';
    const decider = this.decidingTrait(a, o, tempoGap);

    const familyPart = sameFamily ? 'Same family' : 'Different families';
    const tempoPart = overlap
      ? ', overlapping tempo'
      : `; ${actualLabel} is ${a.bpm_min > o.bpm_max ? 'faster' : 'slower'} (${a.bpm_min}–${a.bpm_max} vs ${o.bpm_min}–${o.bpm_max} BPM)`;
    const deciderLabel = this.genreDisplay.traitLabels[decider].toLowerCase();
    const gives = decider === 'drums' ? 'give' : 'gives';
    const reason = `${familyPart}${tempoPart} — the ${deciderLabel} ${gives} it away.`;

    const rows: TraitRow[] = [
      {
        trait: 'tempo',
        label: this.genreDisplay.traitLabels['tempo'],
        actual: `${a.bpm_min}–${a.bpm_max} BPM (this track: ${t.bpm})`,
        other: `${o.bpm_min}–${o.bpm_max} BPM`,
        isKey: decider === 'tempo',
      },
      ...TRAITS.map(trait => ({
        trait,
        label: this.genreDisplay.traitLabels[trait],
        actual: a[trait],
        other: o[trait],
        isKey: decider === trait,
      })),
    ];

    const tip = decider === 'tempo'
      ? `Next time, feel the tempo: ${actualLabel} runs at ${a.bpm_min}–${a.bpm_max} BPM, ${otherLabel} at ${o.bpm_min}–${o.bpm_max}.`
      : `Next time, listen for the ${deciderLabel} — ${a[decider as Exclude<Trait, 'tempo'>]}.`;

    const otherNote = this.easyMode() ? 'closest in the family you picked' : 'your guess';
    return {actualLabel, otherLabel, otherNote, verdict, reason, rows, tip};
  });

  readonly activeTrack = computed(() =>
    this.listening() === 'compare' ? this.compareTrack() ?? this.track() : this.track()
  );

  // One chip per part in the track that is playing, in mix order, with the genre's defining part marked.
  readonly roleChips = computed<RoleChip[]>(() => {
    const t = this.activeTrack();
    if (!t) { return []; }
    const roles = new Set(t.layers.map(l => l.role));
    return this.genreDisplay.roleOrder
      .filter(role => roles.has(role))
      .map(role => ({role, label: this.genreDisplay.roleLabels[role] ?? role, isKey: role === t.key_role}));
  });

  readonly keyRoleHint = computed(() => {
    const t = this.activeTrack();
    if (!t?.key_role) { return ''; }
    const part = (this.genreDisplay.roleLabels[t.key_role] ?? t.key_role).toLowerCase();
    return `The ${part} is what gives ${this.genreDisplay.get(t.genre)} away.`;
  });

  readonly genreButtonState = computed(() => {
    const selected = this.selectedGenre();
    const track = this.track();
    const rev = this.revealed();
    return Object.fromEntries(
      this.displayedGenres().map(g => [g, {
        isSelected: g === selected,
        isCorrect: rev && g === track?.genre,
        isWrong: rev && g === selected && g !== track?.genre,
      }])
    );
  });

  readonly familyButtonState = computed(() => {
    const selected = this.selectedFamily();
    const track = this.track();
    const rev = this.revealed();
    return Object.fromEntries(
      this.allFamilies.map(f => [f.name, {
        isSelected: f.name === selected,
        isCorrect: rev && track !== null && f.genres.includes(track.genre),
        isWrong: rev && f.name === selected && (track === null || !f.genres.includes(track.genre)),
      }])
    );
  });

  readonly focusGenreState = computed(() => {
    const focus = this.focusGenres();
    return Object.fromEntries(this.genres().map(g => [g, focus.has(g)]));
  });

  readonly focusFamilyState = computed(() => {
    const focus = this.focusFamilies();
    return Object.fromEntries(this.allFamilies.map(f => [f.name, focus.has(f.name)]));
  });

  readonly displayedFamilies = computed(() => {
    const focus = this.focusFamilies();
    if (focus.size === 0) { return this.allFamilies; }
    return this.allFamilies.filter(f => focus.has(f.name));
  });

  // What tells the two genres apart, easiest cue first: a clear tempo gap, then a different kick
  // pattern. Next comes the real genre's own defining trait when it is melodic (melodic techno's
  // arps), then a different bass pattern; when the rhythm is the same (full-on vs goa) it is the
  // guessed genre's melodic trait.
  private decidingTrait(actual: GenreProfileSchema, other: GenreProfileSchema, tempoGap: number): Trait {
    const rhythmic = new Set(['drums', 'bass']);
    if (tempoGap >= TELLING_TEMPO_GAP_BPM) { return 'tempo'; }
    if (actual.kick_pattern !== other.kick_pattern) { return 'drums'; }
    if (!rhythmic.has(actual.key_trait)) { return actual.key_trait as Trait; }
    if (actual.bass_pattern !== other.bass_pattern) { return 'bass'; }
    if (!rhythmic.has(other.key_trait)) { return other.key_trait as Trait; }
    return 'signature';
  }

  private loadFocusFromStorage(): Set<string> {
    try {
      const raw = localStorage.getItem('genre_trainer_focus');
      if (raw) { return new Set(JSON.parse(raw) as string[]); }
    } catch {
      // ignore malformed storage
    }
    return new Set();
  }

  private saveFocusToStorage(focus: Set<string>): void {
    localStorage.setItem('genre_trainer_focus', JSON.stringify([...focus]));
  }

  private loadFamilyFocusFromStorage(): Set<string> {
    try {
      const raw = localStorage.getItem('genre_trainer_family_focus');
      if (raw) { return new Set(JSON.parse(raw) as string[]); }
    } catch {
      // ignore
    }
    return new Set();
  }

  private saveFamilyFocusToStorage(focus: Set<string>): void {
    localStorage.setItem('genre_trainer_family_focus', JSON.stringify([...focus]));
  }

  private loadEasyModeFromStorage(): boolean {
    try {
      const raw = localStorage.getItem('genre_trainer_easy_mode');
      if (raw) { return JSON.parse(raw) as boolean; }
    } catch {
      // ignore
    }
    return true;
  }

  private loadStatsFromStorage(): Record<string, GenreStat> {
    try {
      const raw = localStorage.getItem('genre_trainer_stats');
      if (!raw) { return {}; }
      const stats = JSON.parse(raw) as Record<string, GenreStat>;
      if (Number(localStorage.getItem('genre_trainer_stats_version') ?? 1) < STATS_VERSION) {
        for (const genre of GENRES_CHANGED_IN_V2) {
          delete stats[genre];
        }
        this.saveStatsToStorage(stats);
      }
      return stats;
    } catch {
      // ignore malformed storage
    }
    return {};
  }

  private saveStatsToStorage(stats: Record<string, GenreStat>): void {
    localStorage.setItem('genre_trainer_stats', JSON.stringify(stats));
    localStorage.setItem('genre_trainer_stats_version', String(STATS_VERSION));
  }

  private loadConfusionsFromStorage(): Confusions {
    try {
      const raw = localStorage.getItem('genre_trainer_confusions');
      if (raw) { return JSON.parse(raw) as Confusions; }
    } catch {
      // ignore malformed storage
    }
    return {};
  }

  private recordResult(genre: string, correct: boolean): void {
    this.genreStats.update(prev => {
      const cur = prev[genre] ?? {seen: 0, correct: 0};
      const next = {...prev, [genre]: {seen: cur.seen + 1, correct: cur.correct + (correct ? 1 : 0)}};
      this.saveStatsToStorage(next);
      return next;
    });
  }

  private recordConfusion(actual: string, guessed: string): void {
    this.lastMiss.set({actual, guessed});
    this.confusions.update(prev => {
      const forActual = prev[actual] ?? {};
      const next = {...prev, [actual]: {...forActual, [guessed]: (forActual[guessed] ?? 0) + 1}};
      localStorage.setItem('genre_trainer_confusions', JSON.stringify(next));
      return next;
    });
  }

  resetProgress(): void {
    this.genreStats.set({});
    this.confusions.set({});
    this.lastMiss.set(null);
    localStorage.removeItem('genre_trainer_stats');
    localStorage.removeItem('genre_trainer_confusions');
  }

  // The pool of genres the next track may be drawn from, honoring focus + mode.
  // Falls back to the full genre list (empty until the first load resolves it).
  private candidateGenres(): string[] {
    if (this.easyMode()) {
      const fams = this.focusFamilies();
      if (fams.size > 0) {
        return this.allFamilies.filter(f => fams.has(f.name)).flatMap(f => f.genres);
      }
      return this.genres();
    }
    const focus = this.focusGenres();
    return focus.size > 0 ? [...focus] : this.genres();
  }

  // Weighted pick: unseen genres and low-accuracy genres are surfaced more often, and so are genres
  // the user mixes up with others; the genre just reached for in a wrong guess comes back soon, so the
  // pair is heard close together. The just-played genre is damped so it rarely repeats back-to-back.
  private pickAdaptiveGenre(candidates: string[]): string | undefined {
    if (candidates.length === 0) { return undefined; }
    const stats = this.genreStats();
    const involvement = this.confusionInvolvement();
    const miss = this.lastMiss();
    const weights = candidates.map(g => {
      const s = stats[g];
      let weight = !s || s.seen === 0 ? 4 : 1 + 4 * (1 - s.correct / s.seen);
      weight *= 1 + Math.min(1, (involvement[g] ?? 0) / 6);
      if (miss && g === miss.guessed) { weight *= 2; }
      return weight;
    });
    const last = this.track()?.genre;
    if (candidates.length > 1 && last) {
      const i = candidates.indexOf(last);
      if (i >= 0) { weights[i] *= 0.25; }
    }
    const total = weights.reduce((a, b) => a + b, 0);
    let r = Math.random() * total;
    for (let i = 0; i < candidates.length; i++) {
      r -= weights[i];
      if (r <= 0) { return candidates[i]; }
    }
    return candidates[candidates.length - 1];
  }

  // How many confusions each genre is part of, on either side.
  private confusionInvolvement(): Record<string, number> {
    const counts: Record<string, number> = {};
    for (const pair of Object.entries(this.confusions()).flatMap(([actual, guesses]) =>
      Object.entries(guesses).map(([guessed, count]) => ({actual, guessed, count})))) {
      counts[pair.actual] = (counts[pair.actual] ?? 0) + pair.count;
      counts[pair.guessed] = (counts[pair.guessed] ?? 0) + pair.count;
    }
    return counts;
  }

  // Broad comma-separated focus filter used only for the very first load, before
  // the genre list is known and adaptive single-genre selection is possible.
  private broadGenreFilter(): string | undefined {
    if (this.easyMode()) {
      const fams = this.focusFamilies();
      if (fams.size > 0) {
        return this.allFamilies.filter(f => fams.has(f.name)).flatMap(f => f.genres).join(',');
      }
      return undefined;
    }
    const focus = this.focusGenres();
    return focus.size > 0 ? [...focus].join(',') : undefined;
  }

  // A focus saved before a genre was renamed or merged would keep asking for a genre that no longer exists.
  private pruneFocus(known: string[]): void {
    const focus = this.focusGenres();
    const kept = new Set([...focus].filter(g => known.includes(g)));
    if (kept.size !== focus.size) {
      this.focusGenres.set(kept);
      this.saveFocusToStorage(kept);
    }
  }

  async loadData(): Promise<void> {
    this.isLoading.set(true);
    this.error.set(null);
    try {
      if (this.genres().length === 0) {
        // First load: the genre list isn't known yet, so we can't pick adaptively.
        // Fetch the list alongside a track, honoring focus as a broad filter.
        const broad = this.broadGenreFilter();
        const options = broad ? {query: {genres: broad}} : undefined;
        const [trackRes, genresRes] = await Promise.all([
          getRandomTrackView(options),
          getGenresView(),
        ]);
        this.track.set(trackRes.data.track);
        this.genres.set(genresRes.data.genres);
        this.profiles.set(Object.fromEntries(genresRes.data.profiles.map(p => [p.genre, p])));
        this.pruneFocus(genresRes.data.genres);
      } else {
        // Subsequent loads: weight selection toward the genres the user struggles with.
        const picked = this.pickAdaptiveGenre(this.candidateGenres());
        const options = picked ? {query: {genres: picked}} : undefined;
        const trackRes = await getRandomTrackView(options);
        this.track.set(trackRes.data.track);
      }

      if (!this.easyMode()) {
        const focus = this.focusGenres();
        this.displayedGenres.set(focus.size > 0 ? [...focus] : this.genres());
      }
    } catch {
      this.error.set('Failed to load track. Is the backend running?');
    } finally {
      this.isLoading.set(false);
    }
  }

  /** Loads (once per reveal) a track of the compared genre, in the real track's key, so switching
   * between the two changes the genre and nothing else. */
  async loadCompareTrack(): Promise<TrackSchema | null> {
    const existing = this.compareTrack();
    if (existing) { return existing; }
    const genre = this.compareGenre();
    const root = this.track()?.root;
    if (!genre) { return null; }
    this.isCompareLoading.set(true);
    this.error.set(null);
    try {
      const res = await getRandomTrackView({query: {genres: genre, root: root ?? undefined}});
      this.compareTrack.set(res.data.track);
      return res.data.track;
    } catch {
      this.error.set('Failed to load the comparison track.');
      return null;
    } finally {
      this.isCompareLoading.set(false);
    }
  }

  selectGenre(genre: string): void {
    if (this.revealed()) { return; }
    this.selectedGenre.set(genre);
    this.revealed.set(true);
    this.totalAnswered.update(n => n + 1);
    const track = this.track();
    const correct = genre === track?.genre;
    if (track) {
      this.recordResult(track.genre, correct);
      if (!correct) { this.recordConfusion(track.genre, genre); }
    }
    if (correct) {
      this.totalCorrect.update(n => n + 1);
      this.streak.update(n => n + 1);
      this.lastMiss.set(null);
    } else {
      this.streak.set(0);
    }
  }

  selectFamily(familyName: string): void {
    if (this.revealed()) { return; }
    this.selectedFamily.set(familyName);
    this.revealed.set(true);
    this.totalAnswered.update(n => n + 1);
    const track = this.track();
    if (track) {
      const family = this.allFamilies.find(f => f.name === familyName);
      const correct = family?.genres.includes(track.genre) ?? false;
      this.recordResult(track.genre, correct);
      if (correct) {
        this.totalCorrect.update(n => n + 1);
        this.streak.update(n => n + 1);
      } else {
        this.streak.set(0);
      }
    }
  }

  toggleFocusGenre(genre: string): void {
    this.focusGenres.update(prev => {
      const next = new Set(prev);
      if (next.has(genre)) { next.delete(genre); } else { next.add(genre); }
      this.saveFocusToStorage(next);
      return next;
    });
    this.clearTrack();
  }

  clearFocus(): void {
    this.focusGenres.set(new Set());
    localStorage.removeItem('genre_trainer_focus');
    this.clearTrack();
  }

  toggleFocusFamily(familyName: string): void {
    this.focusFamilies.update(prev => {
      const next = new Set(prev);
      if (next.has(familyName)) { next.delete(familyName); } else { next.add(familyName); }
      this.saveFamilyFocusToStorage(next);
      return next;
    });
    this.clearTrack();
  }

  clearFamilyFocus(): void {
    this.focusFamilies.set(new Set());
    localStorage.removeItem('genre_trainer_family_focus');
    this.clearTrack();
  }

  setEasyMode(value: boolean): void {
    this.easyMode.set(value);
    localStorage.setItem('genre_trainer_easy_mode', JSON.stringify(value));
    this.clearTrack();
  }

  applyConfig(config: {
    focusGenres: Set<string>;
    focusFamilies: Set<string>;
    easyMode: boolean;
    autoStopLoops: number;
    resetProgress: boolean;
  }): void {
    this.easyMode.set(config.easyMode);
    localStorage.setItem('genre_trainer_easy_mode', JSON.stringify(config.easyMode));
    this.focusGenres.set(config.focusGenres);
    this.saveFocusToStorage(config.focusGenres);
    this.focusFamilies.set(config.focusFamilies);
    this.saveFamilyFocusToStorage(config.focusFamilies);
    this.autoStopLoops.set(config.autoStopLoops);
    if (config.resetProgress) { this.resetProgress(); }
    this.clearTrack();
  }

  clearTrack(): void {
    this.track.set(null);
    this.selectedGenre.set(null);
    this.selectedFamily.set(null);
    this.revealed.set(false);
    this.compareTrack.set(null);
    this.listening.set('track');
  }
}
