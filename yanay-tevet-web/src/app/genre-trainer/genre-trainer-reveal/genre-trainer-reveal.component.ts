import {Component, computed, inject, signal} from '@angular/core';
import {bootstrapStarFill} from '@ng-icons/bootstrap-icons';
import {NgIcon} from '@ng-icons/core';
import {GenreTrainerService, Listening} from '../genre-trainer.service';
import {GenreTrainerAudioService} from '../genre-trainer-audio.service';

type ChipMode = 'solo' | 'mute';

@Component({
  selector: 'app-genre-trainer-reveal',
  standalone: true,
  imports: [NgIcon],
  templateUrl: './genre-trainer-reveal.component.html',
})
export class GenreTrainerRevealComponent {
  protected readonly service = inject(GenreTrainerService);
  protected readonly audio = inject(GenreTrainerAudioService);

  protected readonly bootstrapStarFill = bootstrapStarFill;

  protected readonly chipMode = signal<ChipMode>('solo');

  protected readonly isFullMix = computed(() => this.audio.soloRole() === null && this.audio.mutedRoles().size === 0);

  protected readonly chipState = computed(() => {
    const solo = this.audio.soloRole();
    const muted = this.audio.mutedRoles();
    return Object.fromEntries(this.service.roleChips().map(chip => [chip.role, {
      soloed: solo === chip.role,
      muted: solo === null && muted.has(chip.role),
    }]));
  });

  async listenTo(which: Listening): Promise<void> {
    if (which === 'compare' && !(await this.service.loadCompareTrack())) { return; }
    this.service.listening.set(which);
    await this.playActive();
  }

  async onChip(role: string): Promise<void> {
    if (this.chipMode() === 'solo') {
      this.audio.toggleSolo(role);
    } else {
      this.audio.toggleMute(role);
    }
    if (!this.audio.isPlaying()) {
      await this.playActive();
    }
  }

  private async playActive(): Promise<void> {
    const track = this.service.activeTrack();
    if (track) {
      await this.audio.play(track, this.service.autoStopLoops());
    }
  }
}
