import {effect, Injectable, signal} from '@angular/core';
import * as Tone from 'tone';
import {AutomationSpecSchema, TrackLayerSchema, TrackSchema} from '../../generated-files/api/genre-trainer';

type Transport = ReturnType<typeof Tone.getTransport>;
type SidechainDepth = 'deep' | 'medium' | 'shallow' | 'none';
type DuckDepth = Exclude<SidechainDepth, 'none'>;

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

// Per-role sidechain depth when a layer doesn't set its own. Pads breathe hardest, hats stay solid;
// kick and sub bypass the duck entirely.
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

// The gain each bus drops to on a kick hit at full sidechain depth (0.4 ≈ −8 dB).
const SIDECHAIN_FLOOR: Record<DuckDepth, number> = {
  deep: 0.4,
  medium: 0.6,
  shallow: 0.82,
};
const DUCK_DEPTHS: DuckDepth[] = ['deep', 'medium', 'shallow'];
const DUCK_ATTACK_SECONDS = 0.004;

// The TB-303 slides over a fixed ~60 ms, close to a 32nd note at acid tempos.
const SLIDE_TIME: Tone.Unit.Time = '32n';
const GLIDING_SYNTHS = new Set(['Synth', 'MonoSynth', 'FMSynth', 'AMSynth']);

// Every pattern is two bars; the transport loops over them.
const LOOP: Tone.Unit.Time = '2m';

interface Glider {
  portamento: number;
  setNote(note: string, time: number): unknown;
}

interface Gate {
  entryLoop: number;
  loopModulo: number;
  loopModuloRemainder: number;
  dropout: {prob: number; shouldPlay: boolean};
}

// Everything one playback creates, so stopping (or abandoning a build that a newer play overtook)
// disposes exactly what it made.
interface Playback {
  transport: Transport;
  nodes: Tone.ToneAudioNode[];
  sequences: Tone.Sequence[];
  scheduledIds: number[];
  muteGains: Map<string, Tone.Gain[]>;
  // After the limiter: volume × the genre's level trim.
  output: Tone.Gain;
  trim: number;
  analyser: Tone.Analyser;
  kickMeter: Tone.Meter;
  onLoop: (time: number) => void;
}

/** Plays a generated track with Tone.js. Owns the transport for the page: one track plays at a time. */
@Injectable()
export class GenreTrainerAudioService {
  readonly isPlaying = signal(false);
  // Tone builds an offline render's nodes in a swapped-in global context, so nothing may play while
  // a render is under way: its nodes would land in the render instead of the speakers.
  readonly isRendering = signal(false);
  readonly playingTrackId = signal<string | null>(null);
  readonly volume = signal(0.8);
  // Solo wins over mutes: with a soloed role only that role sounds.
  readonly soloRole = signal<string | null>(null);
  readonly mutedRoles = signal<ReadonlySet<string>>(new Set());
  readonly isAlternating = signal(false);

  private current: Playback | null = null;
  // While comparing: the two tracks, which one plays next, and how many loops each gets per turn.
  private alternation: {tracks: [TrackSchema, TrackSchema]; next: 0 | 1; loopsEach: number} | null = null;
  // Bumped by every play and stop, so a play whose async build was overtaken by a later call
  // abandons itself instead of starting over the newer one.
  private playToken = 0;
  // The build of the latest play, settled or not. An offline render must wait for it: the build's
  // later steps would otherwise create their nodes inside the render's swapped-in context.
  private pendingBuild: Promise<unknown> = Promise.resolve();

  constructor() {
    effect(() => {
      const solo = this.soloRole();
      const muted = this.mutedRoles();
      const playback = this.current;
      if (!playback) { return; }
      for (const [role, gains] of playback.muteGains) {
        const target = this.roleGain(role, solo, muted);
        for (const gain of gains) {
          gain.gain.rampTo(target, 0.03);
        }
      }
    });
  }

  async play(track: TrackSchema, autoStopLoops: number): Promise<void> {
    this.endAlternation();
    await this.start(track, autoStopLoops);
  }

  /** Plays `a` and `b` in turn, `loopsEach` loops at a time, until stopped. */
  async playAlternating(a: TrackSchema, b: TrackSchema, loopsEach: number): Promise<void> {
    this.alternation = {tracks: [a, b], next: 1, loopsEach};
    this.isAlternating.set(true);
    await this.start(a, loopsEach);
  }

  stop(): void {
    this.endAlternation();
    this.playToken++;
    this.teardown();
  }

  private endAlternation(): void {
    this.alternation = null;
    this.isAlternating.set(false);
  }

  // Runs when a playback has played its loops: the end of a track, or a turn in a comparison.
  private onLoopsDone(): void {
    const alternation = this.alternation;
    if (!alternation) {
      this.stop();
      return;
    }
    const track = alternation.tracks[alternation.next];
    alternation.next = alternation.next === 0 ? 1 : 0;
    void this.start(track, alternation.loopsEach);
  }

  private async start(track: TrackSchema, autoStopLoops: number): Promise<void> {
    if (this.isRendering()) { return; }
    const token = ++this.playToken;
    this.teardown();
    // Set before the build, so a comparison's switch shows the next side at once rather than nothing.
    this.playingTrackId.set(track.id);
    await Tone.start();

    const transport = Tone.getTransport();
    const solo = this.soloRole();
    const muted = this.mutedRoles();
    const build = this.buildPlayback(track, transport, this.volume(), role => this.roleGain(role, solo, muted), {
      autoStopLoops,
      onAutoStop: time => {
        // Loop events fire ahead of the audio by the scheduler's look-ahead; stop when the loop
        // boundary is actually heard. A timer rather than Tone.Draw, which waits for an animation
        // frame and so never fires in a background tab.
        const delayMs = Math.max(0, (time - Tone.now()) * 1000);
        setTimeout(() => {
          if (token === this.playToken) { this.onLoopsDone(); }
        }, delayMs);
      },
    });
    this.pendingBuild = build.catch(() => null);
    const playback = await build;

    if (token !== this.playToken) {
      this.disposePlayback(playback);
      return;
    }
    this.current = playback;
    transport.start();
    this.isPlaying.set(true);
  }

  setVolume(value: number): void {
    this.volume.set(value);
    if (this.current) {
      this.current.output.gain.value = value * this.current.trim;
    }
  }

  toggleSolo(role: string): void {
    this.soloRole.update(current => current === role ? null : role);
  }

  toggleMute(role: string): void {
    this.soloRole.set(null);
    this.mutedRoles.update(prev => {
      const next = new Set(prev);
      if (next.has(role)) { next.delete(role); } else { next.add(role); }
      return next;
    });
  }

  resetRoles(): void {
    this.soloRole.set(null);
    this.mutedRoles.set(new Set());
  }

  readWaveform(): Float32Array | null {
    return this.current ? this.current.analyser.getValue() as Float32Array : null;
  }

  readKickLevel(): number {
    if (!this.current) { return 0; }
    return Math.max(0, Math.min(1, this.current.kickMeter.getValue() as number));
  }

  /** Renders two loops of the full mix offline, ignoring solo and mute. */
  async renderWav(track: TrackSchema): Promise<Blob> {
    this.stop();
    this.isRendering.set(true);
    try {
      await this.pendingBuild;
      const loopSec = 2 * 4 * 60 / track.bpm;
      const buffer = await Tone.Offline(async ({transport}) => {
        await this.buildPlayback(track, transport, 1, () => 1, null);
        transport.start();
      }, loopSec * 2);
      return this.bufferToWav(buffer);
    } finally {
      this.isRendering.set(false);
    }
  }

  private roleGain(role: string, solo: string | null, muted: ReadonlySet<string>): number {
    if (solo !== null) { return role === solo ? 1 : 0; }
    return muted.has(role) ? 0 : 1;
  }

  private teardown(): void {
    const transport = Tone.getTransport();
    transport.stop();
    transport.cancel(0);
    transport.loop = false;
    if (this.current) {
      this.disposePlayback(this.current);
      this.current = null;
    }
    this.isPlaying.set(false);
    this.playingTrackId.set(null);
  }

  private disposePlayback(playback: Playback): void {
    playback.transport.off('loop', playback.onLoop);
    for (const id of playback.scheduledIds) {
      playback.transport.clear(id);
    }
    for (const seq of playback.sequences) {
      seq.dispose();
    }
    for (const node of playback.nodes) {
      node.dispose();
    }
  }

  private async buildPlayback(
    track: TrackSchema,
    transport: Transport,
    volume: number,
    initialRoleGain: (role: string) => number,
    autoStop: {autoStopLoops: number; onAutoStop: (time: number) => void} | null,
  ): Promise<Playback> {
    transport.bpm.value = track.bpm;
    // Swing on 16th notes — Tone applies a shuffle offset to every other 16n.
    transport.swing = track.swing ?? 0;
    transport.swingSubdivision = '16n';
    transport.loop = true;
    transport.loopStart = 0;
    transport.loopEnd = LOOP;

    // Master chain: bus -> compressor -> limiter -> output -> destination. The limiter keeps layered
    // distorted kicks, bass and leads from clipping; the compressor adds glue without audible pumping
    // (the kick-triggered duck below does that on purpose). Volume and the genre's level trim come
    // after both, where a gain change is exact and doesn't change how hard the mix is compressed.
    const master = new Tone.Gain(1);
    const compressor = new Tone.Compressor({threshold: -12, ratio: 3.5, attack: 0.005, release: 0.12, knee: 6});
    const limiter = new Tone.Limiter(-1);
    const trim = Tone.dbToGain(track.gain_db ?? 0);
    const output = new Tone.Gain(volume * trim);
    master.connect(compressor);
    compressor.connect(limiter);
    limiter.connect(output);
    output.toDestination();
    const analyser = new Tone.Analyser('waveform', 512);
    limiter.connect(analyser);

    // Kick layers bypass the duck. A meter on the kick bus lets the visualizer react to the actual kick.
    const kickBus = new Tone.Gain(1);
    kickBus.connect(master);
    const kickMeter = new Tone.Meter({normalRange: true, smoothing: 0.4});
    kickBus.connect(kickMeter);

    const duckBuses = new Map<DuckDepth, Tone.Gain>();
    for (const depth of DUCK_DEPTHS) {
      const bus = new Tone.Gain(1);
      bus.connect(master);
      duckBuses.set(depth, bus);
    }

    const nodes: Tone.ToneAudioNode[] = [master, compressor, limiter, output, analyser, kickBus, kickMeter, ...duckBuses.values()];
    const sequences: Tone.Sequence[] = [];
    const scheduledIds: number[] = [];
    const muteGains = new Map<string, Tone.Gain[]>();
    const loopState = {count: 0};
    const gates: Gate[] = [];

    // The duck is triggered by each main-kick hit rather than by a free-running LFO, so it always
    // lands on the kick — whatever the pattern (broken DnB kicks, half-time psybass) and however long
    // the reverbs took to build before the transport started.
    const beatSec = 60 / track.bpm;
    const duckScale = track.sidechain_depth ?? 1;
    const releaseSec = (track.sidechain_release ?? 0.5) * beatSec;
    const duck = (time: number): void => {
      if (duckScale <= 0) { return; }
      for (const [depth, bus] of duckBuses) {
        const floor = 1 - duckScale * (1 - SIDECHAIN_FLOOR[depth]);
        bus.gain.cancelAndHoldAtTime(time);
        bus.gain.linearRampToValueAtTime(floor, time + DUCK_ATTACK_SECONDS);
        bus.gain.exponentialRampToValueAtTime(1, time + DUCK_ATTACK_SECONDS + releaseSec);
      }
    };

    // Reverbs render their impulse responses asynchronously; build every layer at once.
    const built = await Promise.all(track.layers.map(async layer => ({
      layer,
      synth: this.buildSynth(layer),
      effects: await Promise.all(layer.effects.map(e => this.buildEffect(e))),
    })));

    for (const {layer, synth, effects} of built) {
      const depth = (layer.sidechain as SidechainDepth | null | undefined) ?? ROLE_SIDECHAIN[layer.role] ?? 'medium';
      const bus = layer.role === 'kick' ? kickBus : depth === 'none' ? master : duckBuses.get(depth) ?? master;

      const muteGain = new Tone.Gain(initialRoleGain(layer.role));
      muteGain.connect(bus);
      muteGains.set(layer.role, [...(muteGains.get(layer.role) ?? []), muteGain]);

      const vol = new Tone.Volume(layer.volume);
      vol.connect(muteGain);
      const panner = new Tone.Panner(layer.pan ?? ROLE_PAN_DEFAULTS[layer.role] ?? 0);
      panner.connect(vol);

      let lastNode: Tone.ToneAudioNode = synth;
      for (const fx of effects) {
        lastNode.connect(fx);
        lastNode = fx;
      }
      lastNode.connect(panner);
      nodes.push(muteGain, vol, panner, synth, ...effects);

      scheduledIds.push(...this.setupLayerAutomation(layer.automation ?? [], effects, transport));

      const gate: Gate = {
        entryLoop: layer.entry_loop ?? 0,
        loopModulo: layer.loop_modulo ?? 0,
        loopModuloRemainder: layer.loop_modulo_remainder ?? 0,
        dropout: {prob: layer.dropout_prob ?? 0, shouldPlay: true},
      };
      gates.push(gate);
      const seq = this.buildSequence(layer, synth, gate, loopState, layer.id === 'kick' ? duck : null);
      seq.start(0);
      sequences.push(seq);
    }

    // Counted on the transport's own loop event, which fires before the new loop's first notes are
    // scheduled and keeps running in a background tab (an animation frame does neither). A repeat
    // scheduled at '2m' never fires here: the transport wraps to 0 when it reaches loopEnd.
    const onLoop = (time: number): void => {
      loopState.count++;
      for (const gate of gates) {
        if (gate.dropout.prob > 0) {
          gate.dropout.shouldPlay = Math.random() >= gate.dropout.prob;
        }
      }
      if (autoStop && autoStop.autoStopLoops > 0 && loopState.count === autoStop.autoStopLoops) {
        autoStop.onAutoStop(time);
      }
    };
    transport.on('loop', onLoop);

    return {transport, nodes, sequences, scheduledIds, muteGains, output, trim, analyser, kickMeter, onLoop};
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
      case 'PingPongDelay': {
        const d = new Tone.PingPongDelay(
          (opts['delayTime'] as Tone.Unit.Time) ?? '8n',
          (opts['feedback'] as number) ?? 0.3,
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
      case 'AutoFilter': {
        // Synced to the transport so a wobble at '8n' stays on the eighth notes.
        const wobble = new Tone.AutoFilter(config.options as unknown as Tone.AutoFilterOptions);
        wobble.sync().start(0);
        wobble.wet.value = config.wet;
        return wobble;
      }
      case 'Chorus': {
        const ch = new Tone.Chorus(config.options as unknown as Tone.ChorusOptions);
        ch.start();
        ch.wet.value = config.wet;
        return ch;
      }
      default:
        // An effect this player doesn't know passes the signal through untouched.
        return new Tone.Gain(1);
    }
  }

  private buildSequence(
    layer: TrackLayerSchema,
    synth: Tone.ToneAudioNode,
    gate: Gate,
    loopState: {count: number},
    onHit: ((time: number) => void) | null,
  ): Tone.Sequence {
    const synthType = layer.instrument.type;
    const steps = layer.pattern.steps;
    const velocities = layer.pattern.velocities;
    const slides = GLIDING_SYNTHS.has(synthType) ? layer.pattern.slides : null;
    const isHihat = layer.role === 'hihat';
    const totalSteps = steps.length;
    const stepSec = Tone.Time(layer.pattern.subdivision as Tone.Unit.Time).toSeconds();
    const noteSec = Tone.Time(layer.note_duration as Tone.Unit.Time).toSeconds();
    const slideSec = Tone.Time(SLIDE_TIME).toSeconds();
    let stepIdx = 0;
    // A note that starts a slide chain is held until the chain ends; slide steps inside that window
    // glide the held note instead of retriggering it.
    let holdUntil = 0;

    interface TwoArgTAR {triggerAttackRelease: (d: Tone.Unit.Time, t: number, v?: number) => void}
    interface ThreeArgTAR {triggerAttackRelease: (n: string | number, d: Tone.Unit.Time, t: number, v?: number) => void}
    interface ChordTAR {triggerAttackRelease: (n: string[], d: Tone.Unit.Time, t: number, v?: number) => void}

    // A MetalSynth is pitched by the note it is triggered with, so a step's note name (only a trigger for
    // percussion) would override the frequency the layer was designed at; trigger it at that frequency.
    const metalFrequency = (layer.instrument.options as {frequency?: number}).frequency ?? 200;

    const fire = (note: string, vel: number, time: number, duration: Tone.Unit.Time): void => {
      // ±7% velocity jitter humanizes successive loops so they don't feel mechanically identical.
      const jittered = Math.max(0, Math.min(1, vel * (0.93 + Math.random() * 0.14)));
      try {
        if (synthType === 'NoiseSynth') {
          (synth as unknown as TwoArgTAR).triggerAttackRelease(duration, time, jittered);
        } else if (synthType === 'MetalSynth') {
          (synth as unknown as ThreeArgTAR).triggerAttackRelease(metalFrequency, duration, time, jittered);
        } else if (synthType === 'PolySynth' && note.includes(',')) {
          (synth as unknown as ChordTAR).triggerAttackRelease(note.split(','), duration, time, jittered);
        } else {
          (synth as unknown as ThreeArgTAR).triggerAttackRelease(note, duration, time, jittered);
        }
      } catch {
        // Tone.js throws "time must be >= last scheduled time" at loop boundaries when
        // a note's duration extends past the loop end. Silently skip — the audio is fine.
      }
    };

    const glide = (note: string, time: number): void => {
      const glider = synth as unknown as Glider;
      glider.portamento = slideSec;
      glider.setNote(note, time);
      glider.portamento = 0;
    };

    // A slide chain never runs past the loop end: the next loop may be gated off.
    const slideChainLength = (idx: number): number => {
      let length = 0;
      while (slides && idx + length + 1 < totalSteps && slides[idx + length + 1] && steps[idx + length + 1]) {
        length++;
      }
      return length;
    };

    return new Tone.Sequence(
      (time: number, note: string | null) => {
        const idx = stepIdx;
        stepIdx = (stepIdx + 1) % totalSteps;

        if (loopState.count < gate.entryLoop) { return; }
        if (gate.loopModulo > 0 && loopState.count % gate.loopModulo !== gate.loopModuloRemainder) { return; }
        if (!gate.dropout.shouldPlay) { return; }

        if (!note) {
          // Occasional quiet ghost hit on hi-hat null steps for rhythmic instability
          if (isHihat && Math.random() < 0.04) {
            fire('C4', 0.12 + Math.random() * 0.12, time, layer.note_duration as Tone.Unit.Time);
          }
          return;
        }

        onHit?.(time);
        if (slides?.[idx] && time < holdUntil) {
          glide(note, time);
          return;
        }
        const chain = slideChainLength(idx);
        let duration = layer.note_duration as Tone.Unit.Time;
        if (chain > 0) {
          duration = chain * stepSec + noteSec;
          // Half a step of slack so a slightly late (swung) slide step still finds the note held.
          holdUntil = time + (chain + 0.5) * stepSec;
        }
        fire(note, velocities?.[idx] ?? 0.75, time, duration);
      },
      steps as (string | null)[],
      layer.pattern.subdivision as Tone.Unit.Time,
    );
  }

  /** Returns the transport event ids, so a playback can clear its own repeats when it is disposed. */
  private setupLayerAutomation(specs: AutomationSpecSchema[], effects: Tone.ToneAudioNode[], transport: Transport): number[] {
    const loopSec = Tone.Time(LOOP).toSeconds();
    const ids: number[] = [];
    for (const spec of specs) {
      const parts = spec.target.split(':');
      if (parts[0] !== 'effect' || parts.length !== 3) { continue; }
      const fx = effects[parseInt(parts[1])];
      if (!fx) { continue; }
      const prop = (fx as unknown as Record<string, unknown>)[parts[2]];
      if (!prop || typeof (prop as {setValueAtTime?: unknown}).setValueAtTime !== 'function') { continue; }

      const param = prop as {
        setValueAtTime(v: number, t: number): void;
        linearRampToValueAtTime(v: number, t: number): void;
        cancelScheduledValues(t: number): void;
      };

      // Scheduled at 0, not at loopEnd, so it fires on every pass of the looping transport.
      ids.push(transport.scheduleRepeat((time: number) => {
        param.cancelScheduledValues(time);
        if (spec.waveform === 'ramp') {
          param.setValueAtTime(spec.from_val, time);
          param.linearRampToValueAtTime(spec.to_val, time + loopSec * 0.98);
        } else {
          param.setValueAtTime(spec.from_val, time);
          param.linearRampToValueAtTime(spec.to_val, time + loopSec * 0.5);
          param.linearRampToValueAtTime(spec.from_val, time + loopSec * 0.98);
        }
      }, LOOP, 0));
    }
    return ids;
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
}
