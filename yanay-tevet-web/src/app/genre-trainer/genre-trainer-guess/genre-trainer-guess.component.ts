import {Component, inject} from '@angular/core';
import {GenreTrainerService} from '../genre-trainer.service';
import {injectStrings} from '../../shared/i18n/strings';
import {GENRE_STRINGS} from '../i18n';

@Component({
  selector: 'app-genre-trainer-guess',
  standalone: true,
  imports: [],
  templateUrl: './genre-trainer-guess.component.html',
})
export class GenreTrainerGuessComponent {
  protected readonly service = inject(GenreTrainerService);
  protected readonly t = injectStrings(GENRE_STRINGS);
}
