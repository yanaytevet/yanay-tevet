import {computed, Injectable, signal} from '@angular/core';
import {getGenresView, getRandomTrackView, TrackSchema} from '../../generated-files/api/genre-trainer';
import {GenreTypeDisplay} from '../shared/string-display/genre-type-display';

export interface GenreFamily {
  name: string;
  genres: string[];
}

export interface GenreStat {
  seen: number;
  correct: number;
}

@Injectable()
export class GenreTrainerService {
  private readonly genreDisplay = new GenreTypeDisplay();

  readonly track = signal<TrackSchema | null>(null);
  readonly genres = signal<string[]>([]);
  readonly displayedGenres = signal<string[]>([]);
  readonly isPlaying = signal(false);
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
  readonly volume = signal(0.8);
  // Per-genre running record (persisted). Drives adaptive track selection so the
  // next track leans toward genres the user keeps missing or hasn't heard yet.
  readonly genreStats = signal<Record<string, GenreStat>>(this.loadStatsFromStorage());

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

  readonly trackGenreDescription = computed(() => {
    const t = this.track();
    return t ? (this.genreDisplay.descriptions[t.genre] ?? '') : '';
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

  readonly selectedGenreLabel = computed(() => {
    const g = this.selectedGenre();
    return g ? this.genreDisplay.get(g) : '';
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
      if (raw) { return JSON.parse(raw) as Record<string, GenreStat>; }
    } catch {
      // ignore malformed storage
    }
    return {};
  }

  private saveStatsToStorage(stats: Record<string, GenreStat>): void {
    localStorage.setItem('genre_trainer_stats', JSON.stringify(stats));
  }

  private recordResult(genre: string, correct: boolean): void {
    this.genreStats.update(prev => {
      const cur = prev[genre] ?? {seen: 0, correct: 0};
      const next = {...prev, [genre]: {seen: cur.seen + 1, correct: cur.correct + (correct ? 1 : 0)}};
      this.saveStatsToStorage(next);
      return next;
    });
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

  // Weighted pick: unseen genres and low-accuracy genres are surfaced more often,
  // while the just-played genre is damped so the same one rarely repeats back-to-back.
  private pickAdaptiveGenre(candidates: string[]): string | undefined {
    if (candidates.length === 0) { return undefined; }
    const stats = this.genreStats();
    const weights = candidates.map(g => {
      const s = stats[g];
      if (!s || s.seen === 0) { return 4; }          // surface unheard genres for coverage
      return 1 + 4 * (1 - s.correct / s.seen);        // 1 (mastered) .. 5 (always missed)
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

  selectGenre(genre: string): void {
    if (this.revealed()) { return; }
    this.selectedGenre.set(genre);
    this.revealed.set(true);
    this.totalAnswered.update(n => n + 1);
    const track = this.track();
    const correct = genre === track?.genre;
    if (track) { this.recordResult(track.genre, correct); }
    if (correct) {
      this.totalCorrect.update(n => n + 1);
      this.streak.update(n => n + 1);
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
  }): void {
    this.easyMode.set(config.easyMode);
    localStorage.setItem('genre_trainer_easy_mode', JSON.stringify(config.easyMode));
    this.focusGenres.set(config.focusGenres);
    this.saveFocusToStorage(config.focusGenres);
    this.focusFamilies.set(config.focusFamilies);
    this.saveFamilyFocusToStorage(config.focusFamilies);
    this.autoStopLoops.set(config.autoStopLoops);
    this.clearTrack();
  }

  private clearTrack(): void {
    this.track.set(null);
    this.selectedGenre.set(null);
    this.selectedFamily.set(null);
    this.revealed.set(false);
  }
}
