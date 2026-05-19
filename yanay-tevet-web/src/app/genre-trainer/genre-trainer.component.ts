import {afterNextRender, Component, inject, viewChild} from '@angular/core';
import {GenreTrainerService} from './genre-trainer.service';
import {GenreTrainerPlayerComponent} from './genre-trainer-player/genre-trainer-player.component';
import {GenreTrainerGuessComponent} from './genre-trainer-guess/genre-trainer-guess.component';
import {GenreTrainerRevealComponent} from './genre-trainer-reveal/genre-trainer-reveal.component';

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

}
