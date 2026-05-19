import {afterNextRender, Component, inject, viewChild} from '@angular/core';
import {GenreTrainerService} from './genre-trainer.service';
import {GenreTrainerPlayerComponent} from './genre-trainer-player/genre-trainer-player.component';
import {GenreTrainerGuessComponent} from './genre-trainer-guess/genre-trainer-guess.component';
import {GenreTrainerRevealComponent} from './genre-trainer-reveal/genre-trainer-reveal.component';
import {DialogService} from '../common/dialogs/dialogs.service';
import {GenreTrainerConfigDialogComponent} from './genre-trainer-config-dialog/genre-trainer-config-dialog.component';

@Component({
  selector: 'app-genre-trainer',
  standalone: true,
  imports: [
    GenreTrainerPlayerComponent,
    GenreTrainerGuessComponent,
    GenreTrainerRevealComponent,
  ],
  providers: [GenreTrainerService],
  templateUrl: './genre-trainer.component.html',
  styleUrl: './genre-trainer.component.css',
})
export class GenreTrainerComponent {
  protected readonly service = inject(GenreTrainerService);
  private readonly player = viewChild.required(GenreTrainerPlayerComponent);
  private readonly dialogService = inject(DialogService);

  constructor() {
    afterNextRender(() => {
      void this.service.loadData();
    });
  }

  async onNextTrack(): Promise<void> {
    await this.player().stop();
    this.service.selectedGenre.set(null);
    this.service.revealed.set(false);
    this.service.track.set(null);
    await this.service.loadData();
    if (this.service.autoStart()) {
      await this.player().start();
    }
  }

  async openConfig(): Promise<void> {
    const result = await this.dialogService.open(GenreTrainerConfigDialogComponent, {
      genres: this.service.genres(),
      focusGenres: new Set(this.service.focusGenres()),
      autoStopLoops: this.service.autoStopLoops(),
      genreLabelMap: this.service.genreLabelMap(),
    }, 60);
    if (result) {
      this.service.applyFocusConfig(result.focusGenres);
      this.service.autoStopLoops.set(result.autoStopLoops);
    }
  }
}
