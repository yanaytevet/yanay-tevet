import {Component, computed, inject} from '@angular/core';
import {NgIcon} from '@ng-icons/core';
import {featherX} from '@ng-icons/feather-icons';
import {formatDuration} from '../../shared/workout-format';
import {WorkoutI18nService} from '../../shared/workout-i18n.service';
import {RestTimerService} from './rest-timer.service';

// The bar pinned to the bottom of the workout page while resting.
@Component({
  selector: 'app-rest-timer',
  imports: [NgIcon],
  templateUrl: './rest-timer.component.html',
})
export class RestTimerComponent {
  protected readonly timer = inject(RestTimerService);
  protected readonly i18n = inject(WorkoutI18nService);
  protected readonly remainingText = computed(() => formatDuration(this.timer.remaining()));
  protected readonly progressPercent = computed(() => `${Math.round(this.timer.progress() * 100)}%`);
  protected readonly featherX = featherX;
}
