import {Component, inject} from '@angular/core';
import {GenreTrainerService} from '../genre-trainer.service';

@Component({
  selector: 'app-genre-trainer-guess',
  standalone: true,
  imports: [],
  templateUrl: './genre-trainer-guess.component.html',
})
export class GenreTrainerGuessComponent {
  protected readonly service = inject(GenreTrainerService);
}
