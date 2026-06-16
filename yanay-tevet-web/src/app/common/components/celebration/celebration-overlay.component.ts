import {Component, inject} from '@angular/core';
import {CelebrationService} from './celebration.service';

@Component({
  selector: 'app-celebration-overlay',
  standalone: true,
  imports: [],
  templateUrl: './celebration-overlay.component.html',
})
export class CelebrationOverlayComponent {
  readonly celebrationService = inject(CelebrationService);
}
