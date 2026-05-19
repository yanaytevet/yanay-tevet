import {computed, Injectable, signal} from '@angular/core';
import {getGenresView, getRandomTrackView, TrackSchema} from '../../generated-files/api/genre-trainer';
import {GenreTypeDisplay} from '../shared/string-display/genre-type-display';

export interface GenreFamily {
  name: string;
  genres: string[];
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
  readonly autoStopLoops = signal(5);
  readonly streak = signal(0);
  readonly totalAnswered = signal(0);
  readonly totalCorrect = signal(0);
  readonly focusGenres = signal<Set<string>>(this.loadFocusFromStorage());
  readonly focusFamilies = signal<Set<string>>(this.loadFamilyFocusFromStorage());
  readonly easyMode = signal<boolean>(this.loadEasyModeFromStorage());
  readonly volume = signal(0.8);

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
    return false;
  }

  async loadData(): Promise<void> {
    this.isLoading.set(true);
    this.error.set(null);
    try {
      let genreFilter: string | undefined;
      if (this.easyMode()) {
        const focusFams = this.focusFamilies();
        if (focusFams.size > 0) {
          const genres = this.allFamilies
            .filter(f => focusFams.has(f.name))
            .flatMap(f => f.genres);
          genreFilter = genres.join(',');
        }
      } else {
        const focus = this.focusGenres();
        if (focus.size > 0) {
          genreFilter = [...focus].join(',');
        }
      }
      const trackOptions = genreFilter ? {query: {genres: genreFilter}} : undefined;

      if (this.genres().length === 0) {
        const [trackRes, genresRes] = await Promise.all([
          getRandomTrackView(trackOptions),
          getGenresView(),
        ]);
        this.track.set(trackRes.data.track);
        this.genres.set(genresRes.data.genres);
      } else {
        const trackRes = await getRandomTrackView(trackOptions);
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
    if (genre === this.track()?.genre) {
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
      if (family?.genres.includes(track.genre)) {
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
