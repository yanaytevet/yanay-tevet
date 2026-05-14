import {Component, input} from '@angular/core';
import {RouterLink, UrlTree} from '@angular/router';
import {CloudinaryImage} from '../cloudinary-image/cloudinary-image';

@Component({
  selector: 'app-entity-card',
  standalone: true,
  imports: [RouterLink, CloudinaryImage],
  templateUrl: './entity-card.html',
  styleUrl: './entity-card.css',
})
export class EntityCard {
  readonly link = input.required<string | any[] | UrlTree>();
  readonly name = input.required<string>();
  readonly imagePublicId = input<string | null>(null);
  readonly subtitle = input<string | null>(null);
}
