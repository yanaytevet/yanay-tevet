import {computed, Component, DestroyRef, ElementRef, effect, inject, untracked, viewChild} from '@angular/core';
import {GenreTrainerService} from '../genre-trainer.service';
import {GenreTrainerAudioService} from '../genre-trainer-audio.service';
import {DialogService} from '../../common/dialogs/dialogs.service';
import {GenreTrainerConfigDialogComponent} from '../genre-trainer-config-dialog/genre-trainer-config-dialog.component';
import {bootstrapDownload, bootstrapFileMusic, bootstrapGearFill, bootstrapVolumeDownFill, bootstrapVolumeUpFill} from '@ng-icons/bootstrap-icons';
import {NgIcon} from '@ng-icons/core';
import {AuthenticationService} from '../../common/authentication/authentication.service';

@Component({
  selector: 'app-genre-trainer-player',
  standalone: true,
  imports: [NgIcon],
  templateUrl: './genre-trainer-player.component.html',
})
export class GenreTrainerPlayerComponent {
  protected readonly service = inject(GenreTrainerService);
  protected readonly audio = inject(GenreTrainerAudioService);
  private readonly destroyRef = inject(DestroyRef);
  private readonly dialogService = inject(DialogService);
  private readonly authService = inject(AuthenticationService);

  protected readonly bootstrapGearFill = bootstrapGearFill;
  protected readonly bootstrapVolumeDownFill = bootstrapVolumeDownFill;
  protected readonly bootstrapVolumeUpFill = bootstrapVolumeUpFill;
  protected readonly bootstrapDownload = bootstrapDownload;
  protected readonly bootstrapFileMusic = bootstrapFileMusic;

  protected readonly isAdmin = computed(() => this.authService.user()?.is_admin ?? false);

  private readonly canvasEl = viewChild<ElementRef<HTMLCanvasElement>>('vizCanvas');
  private animFrameId: number | null = null;

  constructor() {
    this.destroyRef.onDestroy(() => {
      this.stopAnimation();
      this.audio.stop();
    });
    effect(() => {
      if (!this.service.track() && untracked(() => this.audio.isPlaying())) {
        untracked(() => this.audio.stop());
      }
    });
    effect(() => {
      if (this.audio.isPlaying()) {
        untracked(() => this.startAnimation());
      } else {
        untracked(() => {
          this.stopAnimation();
          this.clearCanvas();
        });
      }
    });
  }

  onCanvasClick(): void {
    if (this.service.isLoading()) { return; }
    if (this.audio.isPlaying()) {
      this.audio.stop();
    } else if (this.service.activeTrack()) {
      void this.playActive();
    }
  }

  async togglePlay(): Promise<void> {
    if (this.audio.isPlaying()) {
      this.audio.stop();
      return;
    }
    if (!this.service.track()) {
      await this.service.loadData();
    }
    await this.playActive();
  }

  toggleAutoStart(): void {
    this.service.autoStart.update(v => !v);
  }

  async openConfig(): Promise<void> {
    const result = await this.dialogService.open(GenreTrainerConfigDialogComponent, {
      genres: this.service.genres(),
      focusGenres: new Set(this.service.focusGenres()),
      focusFamilies: new Set(this.service.focusFamilies()),
      easyMode: this.service.easyMode(),
      autoStopLoops: this.service.autoStopLoops(),
      genreLabelMap: this.service.genreLabelMap(),
      allFamilies: this.service.allFamilies,
      topConfusions: this.service.topConfusions(),
      hasProgress: Object.keys(this.service.genreStats()).length > 0,
    }, 60);
    if (result) {
      this.audio.resetRoles();
      this.service.applyConfig(result);
    }
  }

  downloadJson(): void {
    const track = this.service.activeTrack();
    if (!track) { return; }
    const blob = new Blob([JSON.stringify(track, null, 2)], {type: 'application/json'});
    this.triggerDownload(blob, `track-${track.genre}-${track.id.slice(0, 8)}.json`);
  }

  async downloadAudio(): Promise<void> {
    const track = this.service.activeTrack();
    if (!track || this.audio.isRendering()) { return; }
    const blob = await this.audio.renderWav(track);
    this.triggerDownload(blob, `track-${track.genre}-${track.id.slice(0, 8)}.wav`);
  }

  setVolume(value: number): void {
    this.audio.setVolume(value);
  }

  private async playActive(): Promise<void> {
    const track = this.service.activeTrack();
    if (track) {
      await this.audio.play(track, this.service.autoStopLoops());
    }
  }

  private triggerDownload(blob: Blob, filename: string): void {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  }

  private startAnimation(): void {
    if (this.animFrameId !== null) { return; }

    const draw = (): void => {
      const canvas = this.canvasEl()?.nativeElement;
      const data = this.audio.readWaveform();
      const ctx = canvas?.getContext('2d');
      if (!canvas || !data || !ctx) {
        this.animFrameId = requestAnimationFrame(draw);
        return;
      }

      if (canvas.width !== canvas.clientWidth || canvas.height !== canvas.clientHeight) {
        canvas.width = canvas.clientWidth;
        canvas.height = canvas.clientHeight;
      }

      const w = canvas.width;
      const h = canvas.height;

      ctx.fillStyle = 'rgba(4, 4, 20, 0.2)';
      ctx.fillRect(0, 0, w, h);

      const midY = h / 2;
      // The actual kick-bus amplitude, so the pulse follows off-beat, broken or silent kicks.
      const kick = Math.pow(this.audio.readKickLevel(), 0.6);

      ctx.beginPath();

      for (let i = 0; i < data.length; i++) {
        const x = (i / data.length) * w;
        const amplitude = data[i] * (h * 0.4) * (1 + kick * 0.8);
        const y = midY - amplitude;

        if (i === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
      }

      const gradient = ctx.createLinearGradient(0, 0, w, 0);
      gradient.addColorStop(0, `hsl(220, 90%, ${60 + kick * 30}%)`);
      gradient.addColorStop(0.4, `hsl(270, 85%, ${55 + kick * 30}%)`);
      gradient.addColorStop(0.7, `hsl(300, 80%, ${60 + kick * 30}%)`);
      gradient.addColorStop(1, `hsl(180, 80%, ${55 + kick * 30}%)`);

      ctx.strokeStyle = gradient;
      ctx.lineWidth = 2 + kick * 1.5;
      ctx.shadowColor = `hsl(240, 100%, 70%)`;
      ctx.shadowBlur = 8 + kick * 12;
      ctx.stroke();

      ctx.shadowBlur = 0;

      this.animFrameId = requestAnimationFrame(draw);
    };

    this.animFrameId = requestAnimationFrame(draw);
  }

  private stopAnimation(): void {
    if (this.animFrameId !== null) {
      cancelAnimationFrame(this.animFrameId);
      this.animFrameId = null;
    }
  }

  private clearCanvas(): void {
    const canvas = this.canvasEl()?.nativeElement;
    if (!canvas) {
      return;
    }
    const ctx = canvas.getContext('2d');
    if (!ctx) {
      return;
    }
    ctx.fillStyle = '#040414';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
  }
}
