import {Component, computed, inject, signal} from '@angular/core';
import {bootstrapStarFill} from '@ng-icons/bootstrap-icons';
import {NgIcon} from '@ng-icons/core';
import {GenreTrainerService, Listening} from '../genre-trainer.service';
import {GenreTrainerAudioService} from '../genre-trainer-audio.service';

type ChipMode = 'solo' | 'mute';

// Each side of a comparison plays this many loops before switching.
const COMPARE_LOOPS_EACH = 2;

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

  // Which side of the comparison is sounding — it changes on its own while comparing — or, when
  // nothing plays, which one Play would start.
  protected readonly selectedSide = computed<Listening>(() => {
    const playingId = this.audio.playingTrackId();
    if (playingId && playingId === this.service.compareTrack()?.id) { return 'compare'; }
    if (playingId && playingId === this.service.track()?.id) { return 'track'; }
    return this.service.listening();
  });

  async listenTo(which: Listening): Promise<void> {
    if (which === 'compare' && !(await this.service.loadCompareTrack())) { return; }
    this.service.listening.set(which);
    await this.playActive();
  }

  async toggleCompare(): Promise<void> {
    if (this.audio.isAlternating()) {
      this.audio.stop();
      return;
    }
    const track = this.service.track();
    const compare = await this.service.loadCompareTrack();
    if (track && compare) {
      await this.audio.playAlternating(track, compare, COMPARE_LOOPS_EACH);
    }
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
