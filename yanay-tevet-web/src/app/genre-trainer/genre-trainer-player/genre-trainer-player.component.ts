import {Component, DestroyRef, ElementRef, effect, inject, viewChild} from '@angular/core';
import * as Tone from 'tone';
import {AutomationSpecSchema, TrackLayerSchema} from '../../../generated-files/api/genre-trainer';
import {GenreTrainerService} from '../genre-trainer.service';
import {DialogService} from '../../common/dialogs/dialogs.service';
import {GenreTrainerConfigDialogComponent} from '../genre-trainer-config-dialog/genre-trainer-config-dialog.component';
import {bootstrapGearFill, bootstrapVolumeDownFill, bootstrapVolumeUpFill} from '@ng-icons/bootstrap-icons';
import {NgIcon} from '@ng-icons/core';

// Fields added to the backend schema but not yet regenerated into the typed client.
// Remove once `npm run create-api` has been run against the updated backend.
type ExtendedLayer = TrackLayerSchema & {
  loop_modulo?: number;
  loop_modulo_remainder?: number;
  pan?: number | null;
};

// Role-based stereo defaults applied when a layer has no explicit pan.
// Kick and bass stay centered for energy; hats/percs/leads spread to widen the mix.
const ROLE_PAN_DEFAULTS: Record<string, number> = {
  kick: 0,
  bass: 0,
  snare: 0,
  hihat: 0.22,
  perc: -0.22,
  lead: -0.08,
  stab: 0.12,
  pad: 0,
};

@Component({
  selector: 'app-genre-trainer-player',
  standalone: true,
  imports: [NgIcon],
  templateUrl: './genre-trainer-player.component.html',
})
export class GenreTrainerPlayerComponent {
  protected readonly service = inject(GenreTrainerService);
  private readonly destroyRef = inject(DestroyRef);
  private readonly dialogService = inject(DialogService);

  protected readonly bootstrapGearFill = bootstrapGearFill;
  protected readonly bootstrapVolumeDownFill = bootstrapVolumeDownFill;
  protected readonly bootstrapVolumeUpFill = bootstrapVolumeUpFill;

  private readonly canvasEl = viewChild<ElementRef<HTMLCanvasElement>>('vizCanvas');

  private masterGain: Tone.Gain | null = null;
  private masterCompressor: Tone.Compressor | null = null;
  private masterLimiter: Tone.Limiter | null = null;
  private sidechainBus: Tone.Gain | null = null;
  private sidechainLfo: Tone.LFO | null = null;
  private analyser: Tone.Analyser | null = null;
  private sequences: Tone.Sequence[] = [];
  private nodes: Tone.ToneAudioNode[] = [];
  private animFrameId: number | null = null;
  private loopCount = 0;
  private lastTransportSeconds = -1;

  constructor() {
    this.destroyRef.onDestroy(() => void this.stop());
    effect(() => {
      if (!this.service.track() && this.service.isPlaying()) {
        void this.stop();
      }
    });
  }

  onCanvasClick(): void {
    if (this.service.isLoading()) { return; }
    if (this.service.isPlaying()) {
      void this.stop();
    } else if (this.service.track()) {
      void this.start();
    }
  }

  async togglePlay(): Promise<void> {
    if (this.service.isPlaying()) {
      await this.stop();
    } else if (!this.service.track()) {
      await this.service.loadData();
      await this.start();
    } else {
      await this.start();
    }
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
    }, 60);
    if (result) {
      this.service.applyConfig({
        focusGenres: result.focusGenres,
        focusFamilies: result.focusFamilies,
        easyMode: result.easyMode,
        autoStopLoops: result.autoStopLoops,
      });
    }
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

    this.loopCount = 0;
    this.lastTransportSeconds = -1;

    // Master chain: masterGain -> compressor -> limiter -> destination.
    // The limiter prevents clipping when layered distorted kicks + bass + leads peak together;
    // the compressor adds gentle glue without obvious pumping (the sidechain LFO handles that).
    this.masterGain = new Tone.Gain(this.service.volume());
    this.masterCompressor = new Tone.Compressor({threshold: -12, ratio: 3.5, attack: 0.005, release: 0.12, knee: 6});
    this.masterLimiter = new Tone.Limiter(-1);
    this.masterGain.connect(this.masterCompressor);
    this.masterCompressor.connect(this.masterLimiter);
    this.masterLimiter.toDestination();

    this.analyser = new Tone.Analyser('waveform', 512);
    this.masterLimiter.connect(this.analyser as unknown as Tone.ToneAudioNode);

    Tone.getTransport().bpm.value = track.bpm;

    // Sidechain bus: every non-kick layer routes through this gain, which is modulated by
    // a transport-locked sawtooth LFO (low at each beat, ramping back to unity before the next).
    // The kick connects directly to masterGain so it triggers the "pump" without ducking itself.
    this.sidechainBus = new Tone.Gain(1);
    this.sidechainBus.connect(this.masterGain);
    this.sidechainLfo = new Tone.LFO({frequency: '4n', type: 'sawtooth', min: 0.55, max: 1.0});
    this.sidechainLfo.connect(this.sidechainBus.gain);
    this.sidechainLfo.start(0);

    for (const layer of track.layers) {
      const extended = layer as ExtendedLayer;
      const isKick = layer.role === 'kick';
      const bus = isKick ? this.masterGain : this.sidechainBus;

      const vol = new Tone.Volume(layer.volume);
      vol.connect(bus);

      const panValue = extended.pan ?? ROLE_PAN_DEFAULTS[layer.role] ?? 0;
      const panner = new Tone.Panner(panValue);
      panner.connect(vol);

      this.nodes.push(vol, panner);

      const synth = this.buildSynth(layer);
      const effects = await Promise.all(layer.effects.map(e => this.buildEffect(e)));

      let lastNode: Tone.ToneAudioNode = synth;
      for (const effect of effects) {
        lastNode.connect(effect);
        lastNode = effect;
      }
      lastNode.connect(panner);

      this.nodes.push(synth, ...effects);

      const dropoutRef = {shouldPlay: true};
      const dropoutProb = layer.dropout_prob ?? 0;
      if (dropoutProb > 0) {
        Tone.getTransport().scheduleRepeat(() => {
          dropoutRef.shouldPlay = Math.random() >= dropoutProb;
        }, '2m', '2m');
      }

      this.setupLayerAutomation(layer.automation ?? [], effects);

      const seq = this.buildSequence(layer, synth, dropoutRef);
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
    this.sidechainLfo?.dispose();
    this.sidechainLfo = null;
    this.sidechainBus?.dispose();
    this.sidechainBus = null;
    this.masterLimiter?.dispose();
    this.masterLimiter = null;
    this.masterCompressor?.dispose();
    this.masterCompressor = null;
    this.masterGain?.dispose();
    this.masterGain = null;

    this.loopCount = 0;
    this.lastTransportSeconds = -1;
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

  private buildSequence(
    layer: TrackLayerSchema,
    synth: Tone.ToneAudioNode,
    dropoutRef: {shouldPlay: boolean},
  ): Tone.Sequence {
    const extended = layer as ExtendedLayer;
    const synthType = layer.instrument.type;
    const duration = layer.note_duration as Tone.Unit.Time;
    const velocities = layer.pattern.velocities;
    const entryLoop = layer.entry_loop ?? 0;
    const loopModulo = extended.loop_modulo ?? 0;
    const loopModuloRem = extended.loop_modulo_remainder ?? 0;
    const isHihat = layer.role === 'hihat';
    const totalSteps = layer.pattern.steps.length;
    let stepIdx = 0;

    interface TwoArgTAR {triggerAttackRelease: (d: Tone.Unit.Time, t: number, v?: number) => void}
    interface ThreeArgTAR {triggerAttackRelease: (n: string, d: Tone.Unit.Time, t: number, v?: number) => void}

    const fire = (note: string, vel: number, time: number): void => {
      // ±7% velocity jitter humanizes successive loops so they don't feel mechanically identical.
      const jittered = Math.max(0, Math.min(1, vel * (0.93 + Math.random() * 0.14)));
      if (synthType === 'MetalSynth' || synthType === 'NoiseSynth') {
        (synth as unknown as TwoArgTAR).triggerAttackRelease(duration, time, jittered);
      } else {
        (synth as unknown as ThreeArgTAR).triggerAttackRelease(note, duration, time, jittered);
      }
    };

    return new Tone.Sequence(
      (time: number, note: string | null) => {
        const idx = stepIdx;
        stepIdx = (stepIdx + 1) % totalSteps;

        if (this.loopCount < entryLoop) { return; }
        if (loopModulo > 0 && this.loopCount % loopModulo !== loopModuloRem) { return; }
        if (!dropoutRef.shouldPlay) { return; }

        if (!note) {
          // Occasional quiet ghost hit on hi-hat null steps for rhythmic instability
          if (isHihat && Math.random() < 0.04) {
            fire('C4', 0.12 + Math.random() * 0.12, time);
          }
          return;
        }

        const vel = velocities?.[idx] ?? 0.75;
        fire(note, vel, time);
      },
      layer.pattern.steps as (string | null)[],
      layer.pattern.subdivision as Tone.Unit.Time,
    );
  }

  private setupLayerAutomation(specs: AutomationSpecSchema[], effects: Tone.ToneAudioNode[]): void {
    const loopSec = Tone.Time('2m' as Tone.Unit.Time).toSeconds();
    for (const spec of specs) {
      const parts = spec.target.split(':');
      if (parts[0] !== 'effect' || parts.length !== 3) { continue; }
      const effect = effects[parseInt(parts[1])];
      if (!effect) { continue; }
      const prop = (effect as unknown as Record<string, unknown>)[parts[2]];
      if (!prop || typeof (prop as {setValueAtTime?: unknown}).setValueAtTime !== 'function') { continue; }

      const signal = prop as {
        setValueAtTime(v: number, t: number): void;
        linearRampToValueAtTime(v: number, t: number): void;
        cancelScheduledValues(t: number): void;
      };

      Tone.getTransport().scheduleRepeat((time: number) => {
        signal.cancelScheduledValues(time);
        if (spec.waveform === 'ramp') {
          signal.setValueAtTime(spec.from_val, time);
          signal.linearRampToValueAtTime(spec.to_val, time + loopSec * 0.98);
        } else {
          signal.setValueAtTime(spec.from_val, time);
          signal.linearRampToValueAtTime(spec.to_val, time + loopSec * 0.5);
          signal.linearRampToValueAtTime(spec.from_val, time + loopSec * 0.98);
        }
      }, '2m' as Tone.Unit.Time, 0);
    }
  }

  private startAnimation(): void {
    const autoStopLoops = this.service.autoStopLoops();
    const bpm = this.service.track()?.bpm ?? 128;
    const loopDurationMs = (2 * 4 * 60 / bpm) * 1000;
    const stopAfterMs = autoStopLoops > 0 ? autoStopLoops * loopDurationMs : null;
    const startMs = performance.now();

    const draw = (): void => {
      if (!this.service.isPlaying()) {
        return;
      }
      if (stopAfterMs !== null && performance.now() - startMs >= stopAfterMs) {
        void this.stop();
        return;
      }

      // Detect transport loop restarts to maintain loop count for arrangement logic
      const currentTransportSec = Tone.getTransport().seconds;
      if (this.lastTransportSeconds >= 0 && currentTransportSec < this.lastTransportSeconds - 0.1) {
        this.loopCount++;
      }
      this.lastTransportSeconds = currentTransportSec;

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
