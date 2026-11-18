import {Component, inject} from '@angular/core';
import {GenreTrainerService} from '../genre-trainer.service';
import {injectStrings} from '../../shared/i18n/strings';
import {GENRE_STRINGS} from '../i18n';

@Component({
  selector: 'app-genre-trainer-focus',
  standalone: true,
  imports: [],
  templateUrl: './genre-trainer-focus.component.html',
})
export class GenreTrainerFocusComponent {
  protected readonly service = inject(GenreTrainerService);
  protected readonly t = injectStrings(GENRE_STRINGS);
}
