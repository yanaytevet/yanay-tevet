import {Component, inject, output} from '@angular/core';
import {GenreTrainerService} from '../genre-trainer.service';

@Component({
  selector: 'app-genre-trainer-reveal',
  standalone: true,
  imports: [],
  templateUrl: './genre-trainer-reveal.component.html',
})
export class GenreTrainerRevealComponent {
  protected readonly service = inject(GenreTrainerService);
  readonly nextTrack = output<void>();
}
