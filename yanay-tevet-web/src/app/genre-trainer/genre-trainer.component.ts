import {afterNextRender, Component, inject} from '@angular/core';
import {GenreTrainerService} from './genre-trainer.service';
import {GenreTrainerAudioService} from './genre-trainer-audio.service';
import {GenreTrainerPlayerComponent} from './genre-trainer-player/genre-trainer-player.component';
import {GenreTrainerGuessComponent} from './genre-trainer-guess/genre-trainer-guess.component';
import {GenreTrainerRevealComponent} from './genre-trainer-reveal/genre-trainer-reveal.component';
import {PageHeaderComponent} from '../common/components/page/page-header/page-header.component';

@Component({
  selector: 'app-genre-trainer',
  standalone: true,
  imports: [
    GenreTrainerPlayerComponent,
    GenreTrainerGuessComponent,
    GenreTrainerRevealComponent,
    PageHeaderComponent,
  ],
  providers: [GenreTrainerService, GenreTrainerAudioService],
  templateUrl: './genre-trainer.component.html',
  styleUrl: './genre-trainer.component.css',
})
export class GenreTrainerComponent {
  protected readonly service = inject(GenreTrainerService);
  private readonly audio = inject(GenreTrainerAudioService);

  constructor() {
    afterNextRender(() => {
      void this.service.loadData();
    });
  }

  async onNextTrack(): Promise<void> {
    this.audio.stop();
    this.audio.resetRoles();
    this.service.clearTrack();
    await this.service.loadData();
    const track = this.service.track();
    if (this.service.autoStart() && track) {
      await this.audio.play(track, this.service.autoStopLoops());
    }
  }

}
