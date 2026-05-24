import {computed, Component, DestroyRef, ElementRef, effect, inject, signal, viewChild} from '@angular/core';
import * as Tone from 'tone';
import {AutomationSpecSchema, TrackLayerSchema} from '../../../generated-files/api/genre-trainer';
import {GenreTrainerService} from '../genre-trainer.service';
import {DialogService} from '../../common/dialogs/dialogs.service';
import {GenreTrainerConfigDialogComponent} from '../genre-trainer-config-dialog/genre-trainer-config-dialog.component';
import {bootstrapDownload, bootstrapFileMusic, bootstrapGearFill, bootstrapVolumeDownFill, bootstrapVolumeUpFill} from '@ng-icons/bootstrap-icons';
import {NgIcon} from '@ng-icons/core';
import {AuthenticationService} from '../../common/authentication/authentication.service';

// Role-based stereo defaults applied when a layer has no explicit pan.
// Kick and bass stay centered for energy; hats/percs/leads spread to widen the mix.
const ROLE_PAN_DEFAULTS: Record<string, number> = {
  kick: 0,
  sub: 0,
  bass: 0,
  snare: 0,
  hihat: 0.22,
  perc: -0.22,
  lead: -0.08,
  stab: 0.12,
  pad: 0,
};

// Per-role sidechain depth. Pads "breathe" hardest, hats stay solid. Kick and sub bypass entirely.
// Values are the LFO floor (1.0 = no duck, 0.4 = -8 dB duck at the kick).
type SidechainDepth = 'deep' | 'medium' | 'shallow' | 'none';

const ROLE_SIDECHAIN: Record<string, SidechainDepth> = {
  kick: 'none',
  sub: 'none',
  bass: 'medium',
  snare: 'shallow',
  hihat: 'shallow',
  perc: 'shallow',
  lead: 'medium',
  stab: 'medium',
  pad: 'deep',
};

const SIDECHAIN_FLOOR: Record<Exclude<SidechainDepth, 'none'>, number> = {
  deep: 0.4,
  medium: 0.6,
  shallow: 0.82,
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
  private readonly authService = inject(AuthenticationService);

  protected readonly bootstrapGearFill = bootstrapGearFill;
  protected readonly bootstrapVolumeDownFill = bootstrapVolumeDownFill;
  protected readonly bootstrapVolumeUpFill = bootstrapVolumeUpFill;
  protected readonly bootstrapDownload = bootstrapDownload;
  protected readonly bootstrapFileMusic = bootstrapFileMusic;

  protected readonly isAdmin = computed(() => this.authService.user()?.is_admin ?? false);
  protected readonly isRecording = signal(false);

  private readonly canvasEl = viewChild<ElementRef<HTMLCanvasElement>>('vizCanvas');

  private masterGain: Tone.Gain | null = null;
  private masterCompressor: Tone.Compressor | null = null;
  private masterLimiter: Tone.Limiter | null = null;
  private kickBus: Tone.Gain | null = null;
  private kickMeter: Tone.Meter | null = null;
  private sidechainBuses: Map<Exclude<SidechainDepth, 'none'>, Tone.Gain> = new Map();
  private sidechainLfos: Tone.LFO[] = [];
  private analyser: Tone.Analyser | null = null;
  private sequences: Tone.Sequence[] = [];
  private nodes: Tone.ToneAudioNode[] = [];
  private animFrameId: number | null = null;
  private readonly loopCountRef = {value: 0};
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

  downloadJson(): void {
    const track = this.service.track();
    if (!track) { return; }
    const blob = new Blob([JSON.stringify(track, null, 2)], {type: 'application/json'});
    this.triggerDownload(blob, `track-${track.genre}-${track.id.slice(0, 8)}.json`);
  }

  async downloadAudio(): Promise<void> {
    const track = this.service.track();
    if (!track || this.isRecording()) { return; }

    if (this.service.isPlaying()) {
      await this.stop();
    }
    await Tone.start();

    this.isRecording.set(true);
    try {
      const loopSec = 2 * 4 * 60 / track.bpm;
      const durationSec = loopSec * 2;

      const buffer = await Tone.Offline(async ({transport}) => {
        transport.bpm.value = track.bpm;
        transport.swing = track.swing ?? 0;
        transport.swingSubdivision = '16n';

        const masterGain = new Tone.Gain(1);
        const compressor = new Tone.Compressor({threshold: -12, ratio: 3.5, attack: 0.005, release: 0.12, knee: 6});
        const limiter = new Tone.Limiter(-1);
        masterGain.connect(compressor);
        compressor.connect(limiter);
        limiter.toDestination();

        const kickBus = new Tone.Gain(1);
        kickBus.connect(masterGain);

        const sidechainBuses = new Map<Exclude<SidechainDepth, 'none'>, Tone.Gain>();
        for (const depth of ['deep', 'medium', 'shallow'] as const) {
          const bus = new Tone.Gain(1);
          bus.connect(masterGain);
          const lfo = new Tone.LFO({frequency: '4n', type: 'sawtooth', min: SIDECHAIN_FLOOR[depth], max: 1.0});
          lfo.connect(bus.gain);
          lfo.start(0);
          sidechainBuses.set(depth, bus);
        }

        const loopCountRef = {value: 0};
        transport.scheduleRepeat(() => { loopCountRef.value++; }, '2m', '2m');

        await this.buildLayers(track.layers, masterGain, kickBus, sidechainBuses, loopCountRef, [], []);

        transport.loop = true;
        transport.loopEnd = '2m';
        transport.start();
      }, durationSec);

      const blob = this.bufferToWav(buffer);
      this.triggerDownload(blob, `track-${track.genre}-${track.id.slice(0, 8)}.wav`);
    } finally {
      this.isRecording.set(false);
    }
  }

  private bufferToWav(buffer: Tone.ToneAudioBuffer): Blob {
    const channelCount = buffer.numberOfChannels;
    const sampleRate = buffer.sampleRate;
    const length = buffer.length;

    const channels: Float32Array[] = [];
    for (let i = 0; i < channelCount; i++) {
      channels.push(buffer.getChannelData(i));
    }

    const bytesPerSample = 2;
    const dataSize = length * channelCount * bytesPerSample;
    const totalSize = 44 + dataSize;
    const arrayBuffer = new ArrayBuffer(totalSize);
    const view = new DataView(arrayBuffer);

    const writeString = (offset: number, str: string): void => {
      for (let i = 0; i < str.length; i++) {
        view.setUint8(offset + i, str.charCodeAt(i));
      }
    };

    writeString(0, 'RIFF');
    view.setUint32(4, totalSize - 8, true);
    writeString(8, 'WAVE');
    writeString(12, 'fmt ');
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true);
    view.setUint16(22, channelCount, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, sampleRate * channelCount * bytesPerSample, true);
    view.setUint16(32, channelCount * bytesPerSample, true);
    view.setUint16(34, 16, true);
    writeString(36, 'data');
    view.setUint32(40, dataSize, true);

    let offset = 44;
    for (let i = 0; i < length; i++) {
      for (let ch = 0; ch < channelCount; ch++) {
        const s = Math.max(-1, Math.min(1, channels[ch][i]));
        view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
        offset += 2;
      }
    }

    return new Blob([arrayBuffer], {type: 'audio/wav'});
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

    this.loopCountRef.value = 0;
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
    // Swing on 16th notes — Tone applies a shuffle offset to every other 16n.
    Tone.getTransport().swing = track.swing ?? 0;
    Tone.getTransport().swingSubdivision = '16n';

    // Kick bus: kick role layers route here, then to masterGain. A Tone.Meter taps the bus so the
    // visualizer can react to the actual kick amplitude instead of guessing from transport phase.
    this.kickBus = new Tone.Gain(1);
    this.kickBus.connect(this.masterGain);
    this.kickMeter = new Tone.Meter({normalRange: true, smoothing: 0.4});
    this.kickBus.connect(this.kickMeter as unknown as Tone.ToneAudioNode);

    // Per-role sidechain buses (deep / medium / shallow). Each has its own LFO with a different
    // floor value, so pads breathe hard, basses pump moderately, hats stay solid.
    // All LFOs share the same '4n' period and are started together so they remain phase-locked.
    this.sidechainBuses.clear();
    this.sidechainLfos = [];
    for (const depth of ['deep', 'medium', 'shallow'] as const) {
      const bus = new Tone.Gain(1);
      bus.connect(this.masterGain);
      const lfo = new Tone.LFO({frequency: '4n', type: 'sawtooth', min: SIDECHAIN_FLOOR[depth], max: 1.0});
      lfo.connect(bus.gain);
      lfo.start(0);
      this.sidechainBuses.set(depth, bus);
      this.sidechainLfos.push(lfo);
    }

    await this.buildLayers(
      track.layers,
      this.masterGain,
      this.kickBus,
      this.sidechainBuses,
      this.loopCountRef,
      this.sequences,
      this.nodes,
    );

    Tone.getTransport().loop = true;
    Tone.getTransport().loopEnd = '2m';
    Tone.getTransport().start();
    this.service.isPlaying.set(true);
    this.startAnimation();
  }

  private async buildLayers(
    layers: TrackLayerSchema[],
    masterGain: Tone.ToneAudioNode,
    kickBus: Tone.Gain,
    sidechainBuses: Map<Exclude<SidechainDepth, 'none'>, Tone.Gain>,
    loopCountRef: {value: number},
    sequencesOut: Tone.Sequence[],
    nodesOut: Tone.ToneAudioNode[],
  ): Promise<void> {
    for (const layer of layers) {
      const sidechainDepth = ROLE_SIDECHAIN[layer.role] ?? 'medium';
      const bus = this.selectBusForLayer(layer.role, sidechainDepth, kickBus, sidechainBuses, masterGain);

      const vol = new Tone.Volume(layer.volume);
      vol.connect(bus);

      const panValue = layer.pan ?? ROLE_PAN_DEFAULTS[layer.role] ?? 0;
      const panner = new Tone.Panner(panValue);
      panner.connect(vol);

      nodesOut.push(vol, panner);

      const synth = this.buildSynth(layer);
      const effects = await Promise.all(layer.effects.map(e => this.buildEffect(e)));

      let lastNode: Tone.ToneAudioNode = synth;
      for (const effect of effects) {
        lastNode.connect(effect);
        lastNode = effect;
      }
      lastNode.connect(panner);

      nodesOut.push(synth, ...effects);

      const dropoutRef = {shouldPlay: true};
      const dropoutProb = layer.dropout_prob ?? 0;
      if (dropoutProb > 0) {
        Tone.getTransport().scheduleRepeat(() => {
          dropoutRef.shouldPlay = Math.random() >= dropoutProb;
        }, '2m', '2m');
      }

      this.setupLayerAutomation(layer.automation ?? [], effects);

      const seq = this.buildSequence(layer, synth, dropoutRef, loopCountRef);
      seq.start(0);
      sequencesOut.push(seq);
    }
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
    for (const lfo of this.sidechainLfos) {
      lfo.dispose();
    }
    this.sidechainLfos = [];
    for (const bus of this.sidechainBuses.values()) {
      bus.dispose();
    }
    this.sidechainBuses.clear();
    this.kickMeter?.dispose();
    this.kickMeter = null;
    this.kickBus?.dispose();
    this.kickBus = null;
    this.masterLimiter?.dispose();
    this.masterLimiter = null;
    this.masterCompressor?.dispose();
    this.masterCompressor = null;
    this.masterGain?.dispose();
    this.masterGain = null;

    this.loopCountRef.value = 0;
    this.lastTransportSeconds = -1;
    this.service.isPlaying.set(false);
    this.clearCanvas();
  }

  private selectBusForLayer(
    role: string,
    depth: SidechainDepth,
    kickBus: Tone.Gain,
    sidechainBuses: Map<Exclude<SidechainDepth, 'none'>, Tone.Gain>,
    masterGain: Tone.ToneAudioNode,
  ): Tone.ToneAudioNode {
    if (depth === 'none') {
      if (role === 'kick') { return kickBus; }
      return masterGain;
    }
    return sidechainBuses.get(depth) ?? masterGain;
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
      case 'PolySynth':
        // Chord-capable voice. Layers using PolySynth encode chords as comma-separated
        // step strings (e.g. "C4,Eb4,G4") which `fire()` splits before triggering.
        return new Tone.PolySynth(Tone.Synth, opts as Partial<Tone.SynthOptions>);
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
    loopCountRef: {value: number},
  ): Tone.Sequence {
    const synthType = layer.instrument.type;
    const duration = layer.note_duration as Tone.Unit.Time;
    const velocities = layer.pattern.velocities;
    const entryLoop = layer.entry_loop ?? 0;
    const loopModulo = layer.loop_modulo ?? 0;
    const loopModuloRem = layer.loop_modulo_remainder ?? 0;
    const isHihat = layer.role === 'hihat';
    const totalSteps = layer.pattern.steps.length;
    let stepIdx = 0;

    interface TwoArgTAR {triggerAttackRelease: (d: Tone.Unit.Time, t: number, v?: number) => void}
    interface ThreeArgTAR {triggerAttackRelease: (n: string, d: Tone.Unit.Time, t: number, v?: number) => void}
    interface ChordTAR {triggerAttackRelease: (n: string[], d: Tone.Unit.Time, t: number, v?: number) => void}

    const fire = (note: string, vel: number, time: number): void => {
      // ±7% velocity jitter humanizes successive loops so they don't feel mechanically identical.
      const jittered = Math.max(0, Math.min(1, vel * (0.93 + Math.random() * 0.14)));
      try {
        if (synthType === 'MetalSynth' || synthType === 'NoiseSynth') {
          (synth as unknown as TwoArgTAR).triggerAttackRelease(duration, time, jittered);
        } else if (synthType === 'PolySynth' && note.includes(',')) {
          const notes = note.split(',');
          (synth as unknown as ChordTAR).triggerAttackRelease(notes, duration, time, jittered);
        } else {
          (synth as unknown as ThreeArgTAR).triggerAttackRelease(note, duration, time, jittered);
        }
      } catch {
        // Tone.js throws "time must be >= last scheduled time" at loop boundaries when
        // a note's duration extends past the loop end. Silently skip — the audio is fine.
      }
    };

    return new Tone.Sequence(
      (time: number, note: string | null) => {
        const idx = stepIdx;
        stepIdx = (stepIdx + 1) % totalSteps;

        if (loopCountRef.value < entryLoop) { return; }
        if (loopModulo > 0 && loopCountRef.value % loopModulo !== loopModuloRem) { return; }
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
        this.loopCountRef.value++;
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
      // Use the actual kick-bus amplitude (Tone.Meter, normalRange) rather than guessing from
      // transport phase. Reacts correctly to off-beat / triplet / silent-kick patterns.
      const kickLevel = this.kickMeter ? Math.max(0, Math.min(1, this.kickMeter.getValue() as number)) : 0;
      const kick = Math.pow(kickLevel, 0.6);

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
