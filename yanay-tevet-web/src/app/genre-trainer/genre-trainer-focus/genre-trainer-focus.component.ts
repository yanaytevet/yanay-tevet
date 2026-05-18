import {Component, inject} from '@angular/core';
import {GenreTrainerService} from '../genre-trainer.service';

@Component({
  selector: 'app-genre-trainer-focus',
  standalone: true,
  imports: [],
  templateUrl: './genre-trainer-focus.component.html',
})
export class GenreTrainerFocusComponent {
  protected readonly service = inject(GenreTrainerService);
}
