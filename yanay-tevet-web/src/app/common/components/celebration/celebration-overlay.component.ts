import {Component, inject} from '@angular/core';
import {LottieComponent} from 'ngx-lottie';
import {CelebrationService} from './celebration.service';

@Component({
  selector: 'app-celebration-overlay',
  standalone: true,
  imports: [LottieComponent],
  templateUrl: './celebration-overlay.component.html',
})
export class CelebrationOverlayComponent {
  readonly celebrationService = inject(CelebrationService);
  readonly creatureStyles = {width: '170px', height: '170px'};
  readonly confettiStyles = {width: '100%', height: '100%'};
}
