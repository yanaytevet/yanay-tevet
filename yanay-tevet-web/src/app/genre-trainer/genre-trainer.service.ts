import {computed, Injectable, signal} from '@angular/core';
import {getGenresView, getRandomTrackView, TrackSchema} from '../../generated-files/api/genre-trainer';
import {GenreTypeDisplay} from '../shared/string-display/genre-type-display';

@Injectable()
export class GenreTrainerService {
  private readonly genreDisplay = new GenreTypeDisplay();

  readonly track = signal<TrackSchema | null>(null);
  readonly genres = signal<string[]>([]);
  readonly isPlaying = signal(false);
  readonly isLoading = signal(false);
  readonly selectedGenre = signal<string | null>(null);
  readonly revealed = signal(false);
  readonly error = signal<string | null>(null);
  readonly autoStart = signal(false);
  readonly streak = signal(0);
  readonly totalAnswered = signal(0);
  readonly totalCorrect = signal(0);
  readonly focusGenres = signal<Set<string>>(this.loadFocusFromStorage());
  readonly volume = signal(0.8);

  readonly isCorrect = computed(() => {
    const s = this.selectedGenre();
    const t = this.track();
    return s !== null && t !== null && s === t.genre;
  });

  readonly noFocus = computed(() => this.focusGenres().size === 0);

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
    if (!genre) {
      return null;
    }
    return this.genreDisplay.families.find(f => f.genres.includes(genre)) ?? null;
  });

  readonly genreButtonState = computed(() => {
    const selected = this.selectedGenre();
    const track = this.track();
    const rev = this.revealed();
    return Object.fromEntries(
      this.genres().map(g => [g, {
        isSelected: g === selected,
        isCorrect: rev && g === track?.genre,
        isWrong: rev && g === selected && g !== track?.genre,
      }])
    );
  });

  readonly focusGenreState = computed(() => {
    const focus = this.focusGenres();
    return Object.fromEntries(this.genres().map(g => [g, focus.has(g)]));
  });

  private loadFocusFromStorage(): Set<string> {
    try {
      const raw = localStorage.getItem('genre_trainer_focus');
      if (raw) {
        return new Set(JSON.parse(raw) as string[]);
      }
    } catch {
      // ignore malformed storage
    }
    return new Set();
  }

  private saveFocusToStorage(focus: Set<string>): void {
    localStorage.setItem('genre_trainer_focus', JSON.stringify([...focus]));
  }

  async loadData(): Promise<void> {
    this.isLoading.set(true);
    this.error.set(null);
    try {
      const focus = this.focusGenres();
      const trackOptions = focus.size > 0 ? {query: {genres: [...focus].join(',')}} : undefined;

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
    } catch {
      this.error.set('Failed to load track. Is the backend running?');
    } finally {
      this.isLoading.set(false);
    }
  }

  selectGenre(genre: string): void {
    if (this.revealed()) {
      return;
    }
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

  toggleFocusGenre(genre: string): void {
    this.focusGenres.update(prev => {
      const next = new Set(prev);
      if (next.has(genre)) {
        next.delete(genre);
      } else {
        next.add(genre);
      }
      this.saveFocusToStorage(next);
      return next;
    });
  }

  clearFocus(): void {
    this.focusGenres.set(new Set());
    localStorage.removeItem('genre_trainer_focus');
  }
}
