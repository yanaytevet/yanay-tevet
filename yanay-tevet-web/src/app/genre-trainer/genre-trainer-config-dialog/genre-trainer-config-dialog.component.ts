import {computed, signal, Component} from '@angular/core';
import {BaseDialogComponent} from '../../common/dialogs/base-dialog.component';
import {ConfirmationButtonComponent} from '../../common/dialogs/confirmation-button/confirmation-button.component';

export interface GenreTrainerConfigDialogInput {
  genres: string[];
  focusGenres: Set<string>;
  autoStopLoops: number;
  genreLabelMap: Record<string, string>;
}

export interface GenreTrainerConfigDialogOutput {
  focusGenres: Set<string>;
  autoStopLoops: number;
}

@Component({
  selector: 'app-genre-trainer-config-dialog',
  standalone: true,
  imports: [ConfirmationButtonComponent],
  templateUrl: './genre-trainer-config-dialog.component.html',
})
export class GenreTrainerConfigDialogComponent extends BaseDialogComponent<
  GenreTrainerConfigDialogInput,
  GenreTrainerConfigDialogOutput
> {
  readonly localFocus = signal<Set<string>>(new Set(this.data.focusGenres));
  readonly localAutoStopLoops = signal(this.data.autoStopLoops);

  readonly localNoFocus = computed(() => this.localFocus().size === 0);
  readonly localFocusState = computed(() =>
    Object.fromEntries(this.data.genres.map(g => [g, this.localFocus().has(g)]))
  );

  toggleGenre(genre: string): void {
    this.localFocus.update(prev => {
      const next = new Set(prev);
      if (next.has(genre)) {
        next.delete(genre);
      } else {
        next.add(genre);
      }
      return next;
    });
  }

  clearGenreSelection(): void {
    this.localFocus.set(new Set());
  }

  incrementLoops(): void {
    this.localAutoStopLoops.update(v => Math.min(v + 1, 20));
  }

  decrementLoops(): void {
    this.localAutoStopLoops.update(v => Math.max(v - 1, 0));
  }

  confirm(): void {
    this.emitClose({
      focusGenres: this.localFocus(),
      autoStopLoops: this.localAutoStopLoops(),
    });
  }
}
