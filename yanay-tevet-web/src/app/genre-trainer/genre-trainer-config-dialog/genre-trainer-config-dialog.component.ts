import {computed, signal, Component} from '@angular/core';
import {BaseDialogComponent} from '../../common/dialogs/base-dialog.component';
import {ConfirmationButtonComponent} from '../../common/dialogs/confirmation-button/confirmation-button.component';
import {GenreFamily} from '../genre-trainer.service';

export interface GenreTrainerConfigDialogInput {
  genres: string[];
  focusGenres: Set<string>;
  focusFamilies: Set<string>;
  easyMode: boolean;
  autoStopLoops: number;
  genreLabelMap: Record<string, string>;
  allFamilies: GenreFamily[];
}

export interface GenreTrainerConfigDialogOutput {
  focusGenres: Set<string>;
  focusFamilies: Set<string>;
  easyMode: boolean;
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
  readonly localEasyMode = signal(this.data.easyMode);
  readonly localFocus = signal<Set<string>>(new Set(this.data.focusGenres));
  readonly localFocusFamilies = signal<Set<string>>(new Set(this.data.focusFamilies));
  readonly localAutoStopLoops = signal(this.data.autoStopLoops);

  readonly localNoFocus = computed(() => this.localFocus().size === 0);
  readonly localNoFamilyFocus = computed(() => this.localFocusFamilies().size === 0);

  readonly canConfirm = computed(() =>
    this.localEasyMode()
      ? this.localFocusFamilies().size !== 1
      : this.localFocus().size !== 1
  );

  readonly localFocusState = computed(() =>
    Object.fromEntries(this.data.genres.map(g => [g, this.localFocus().has(g)]))
  );

  readonly localFocusFamilyState = computed(() =>
    Object.fromEntries(this.data.allFamilies.map(f => [f.name, this.localFocusFamilies().has(f.name)]))
  );

  setEasyMode(value: boolean): void {
    this.localEasyMode.set(value);
  }

  toggleGenre(genre: string): void {
    this.localFocus.update(prev => {
      const next = new Set(prev);
      if (next.has(genre)) { next.delete(genre); } else { next.add(genre); }
      return next;
    });
  }

  clearGenreSelection(): void {
    this.localFocus.set(new Set());
  }

  toggleFamily(familyName: string): void {
    this.localFocusFamilies.update(prev => {
      const next = new Set(prev);
      if (next.has(familyName)) { next.delete(familyName); } else { next.add(familyName); }
      return next;
    });
  }

  clearFamilySelection(): void {
    this.localFocusFamilies.set(new Set());
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
      focusFamilies: this.localFocusFamilies(),
      easyMode: this.localEasyMode(),
      autoStopLoops: this.localAutoStopLoops(),
    });
  }
}
