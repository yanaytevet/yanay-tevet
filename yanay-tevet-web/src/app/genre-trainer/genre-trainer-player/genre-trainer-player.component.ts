import {Component, DestroyRef, ElementRef, inject, viewChild} from '@angular/core';
import * as Tone from 'tone';
import {TrackLayerSchema} from '../../../generated-files/api/genre-trainer';
import {GenreTrainerService} from '../genre-trainer.service';

@Component({
  selector: 'app-genre-trainer-player',
  standalone: true,
  imports: [],
  templateUrl: './genre-trainer-player.component.html',
})
export class GenreTrainerPlayerComponent {
  protected readonly service = inject(GenreTrainerService);
  private readonly destroyRef = inject(DestroyRef);

  private readonly canvasEl = viewChild<ElementRef<HTMLCanvasElement>>('vizCanvas');

  private masterGain: Tone.Gain | null = null;
  private analyser: Tone.Analyser | null = null;
  private sequences: Tone.Sequence[] = [];
  private nodes: Tone.ToneAudioNode[] = [];
  private animFrameId: number | null = null;

  constructor() {
    this.destroyRef.onDestroy(() => void this.stop());
  }

  onCanvasClick(): void {
    if (!this.service.isPlaying() && !this.service.isLoading() && this.service.track()) {
      void this.start();
    }
  }

  async togglePlay(): Promise<void> {
    if (this.service.isPlaying()) {
      await this.stop();
    } else {
      await this.start();
    }
  }

  toggleAutoStart(): void {
    this.service.autoStart.update(v => !v);
  }

  setVolume(value: number): void {
    this.service.volume.set(value);
    if (this.masterGain) {
      this.masterGain.gain.value = value;
    }
  }

  async start(): Promise<void> {
    const track = this.service.track();
    if (!track) {
      return;
    }
    await Tone.start();

    this.masterGain = new Tone.Gain(this.service.volume()).toDestination();
    this.analyser = new Tone.Analyser('waveform', 512);
    this.masterGain.connect(this.analyser as unknown as Tone.ToneAudioNode);

    Tone.getTransport().bpm.value = track.bpm;

    for (const layer of track.layers) {
      const vol = new Tone.Volume(layer.volume);
      vol.connect(this.masterGain);
      this.nodes.push(vol);

      const synth = this.buildSynth(layer);
      const effects = await Promise.all(layer.effects.map(e => this.buildEffect(e)));

      let lastNode: Tone.ToneAudioNode = synth;
      for (const effect of effects) {
        lastNode.connect(effect);
        lastNode = effect;
      }
      lastNode.connect(vol);

      this.nodes.push(synth, ...effects);

      const seq = this.buildSequence(layer, synth);
      seq.start(0);
      this.sequences.push(seq);
    }

    Tone.getTransport().loop = true;
    Tone.getTransport().loopEnd = '2m';
    Tone.getTransport().start();
    this.service.isPlaying.set(true);
    this.startAnimation();
  }

  async stop(): Promise<void> {
    if (this.animFrameId !== null) {
      cancelAnimationFrame(this.animFrameId);
      this.animFrameId = null;
    }
    Tone.getTransport().stop();
    Tone.getTransport().cancel(0);
    Tone.getTransport().loop = false;

    for (const seq of this.sequences) {
      seq.dispose();
    }
    this.sequences = [];

    for (const node of this.nodes) {
      node.dispose();
    }
    this.nodes = [];

    this.analyser?.dispose();
    this.analyser = null;
    this.masterGain?.dispose();
    this.masterGain = null;

    this.service.isPlaying.set(false);
    this.clearCanvas();
  }

  private buildSynth(layer: TrackLayerSchema): Tone.ToneAudioNode {
    const opts = layer.instrument.options as unknown;
    switch (layer.instrument.type) {
      case 'MembraneSynth':
        return new Tone.MembraneSynth(opts as Tone.MembraneSynthOptions);
      case 'MetalSynth':
        return new Tone.MetalSynth(opts as Tone.MetalSynthOptions);
      case 'NoiseSynth':
        return new Tone.NoiseSynth(opts as Tone.NoiseSynthOptions);
      case 'MonoSynth':
        return new Tone.MonoSynth(opts as Tone.MonoSynthOptions);
      case 'AMSynth':
        return new Tone.AMSynth(opts as Tone.AMSynthOptions);
      case 'FMSynth':
        return new Tone.FMSynth(opts as Tone.FMSynthOptions);
      default:
        return new Tone.Synth(opts as Tone.SynthOptions);
    }
  }

  private async buildEffect(config: TrackLayerSchema['effects'][0]): Promise<Tone.ToneAudioNode> {
    const opts = config.options as Record<string, unknown>;
    switch (config.type) {
      case 'Reverb': {
        const r = new Tone.Reverb(config.options as unknown as Tone.ReverbOptions);
        await r.ready;
        r.wet.value = config.wet;
        return r;
      }
      case 'FeedbackDelay': {
        const d = new Tone.FeedbackDelay(
          (opts['delayTime'] as Tone.Unit.Time) ?? '8n',
          (opts['feedback'] as number) ?? 0.4,
        );
        d.wet.value = config.wet;
        return d;
      }
      case 'Distortion': {
        const dist = new Tone.Distortion((opts['distortion'] as number) ?? 0.5);
        dist.wet.value = config.wet;
        return dist;
      }
      case 'Filter':
        return new Tone.Filter(config.options as unknown as Tone.FilterOptions);
      case 'Chorus': {
        const ch = new Tone.Chorus(config.options as unknown as Tone.ChorusOptions);
        ch.start();
        ch.wet.value = config.wet;
        return ch;
      }
      default:
        return new Tone.Reverb({decay: 0.1});
    }
  }

  private buildSequence(layer: TrackLayerSchema, synth: Tone.ToneAudioNode): Tone.Sequence {
    const synthType = layer.instrument.type;
    const duration = layer.note_duration as Tone.Unit.Time;

    return new Tone.Sequence(
      (time: number, note: string | null) => {
        if (!note) {
          return;
        }
        type TwoArgTAR = {triggerAttackRelease: (d: Tone.Unit.Time, t: number) => void};
        type ThreeArgTAR = {triggerAttackRelease: (n: string, d: Tone.Unit.Time, t: number) => void};
        if (synthType === 'MetalSynth' || synthType === 'NoiseSynth') {
          (synth as unknown as TwoArgTAR).triggerAttackRelease(duration, time);
        } else {
          (synth as unknown as ThreeArgTAR).triggerAttackRelease(note, duration, time);
        }
      },
      layer.pattern.steps as (string | null)[],
      layer.pattern.subdivision as Tone.Unit.Time,
    );
  }

  private startAnimation(): void {
    const draw = (): void => {
      if (!this.service.isPlaying()) {
        return;
      }
      const canvas = this.canvasEl()?.nativeElement;
      if (!canvas || !this.analyser) {
        this.animFrameId = requestAnimationFrame(draw);
        return;
      }

      const ctx = canvas.getContext('2d');
      if (!ctx) {
        this.animFrameId = requestAnimationFrame(draw);
        return;
      }

      if (canvas.width !== canvas.clientWidth || canvas.height !== canvas.clientHeight) {
        canvas.width = canvas.clientWidth;
        canvas.height = canvas.clientHeight;
      }

      const w = canvas.width;
      const h = canvas.height;
      const data = this.analyser.getValue() as Float32Array;

      ctx.fillStyle = 'rgba(4, 4, 20, 0.2)';
      ctx.fillRect(0, 0, w, h);

      const midY = h / 2;
      const transport = Tone.getTransport();
      const bpm = this.service.track()?.bpm ?? 128;
      const beatPhaseSec = transport.seconds % (60 / bpm);
      const beatPhase = beatPhaseSec / (60 / bpm);
      const kick = beatPhase < 0.12 ? Math.sin(Math.PI * beatPhase / 0.12) : 0;

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
