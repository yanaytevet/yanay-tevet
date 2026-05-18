import {afterNextRender, Component, computed, DestroyRef, ElementRef, inject, signal, viewChild} from '@angular/core';
import * as Tone from 'tone';
import {getGenresView, getRandomTrackView, TrackLayerSchema, TrackSchema} from '../../generated-files/api/genre-trainer';
import {GenreTypeDisplay} from '../shared/string-display/genre-type-display';

@Component({
  selector: 'app-genre-trainer',
  standalone: true,
  imports: [],
  templateUrl: './genre-trainer.component.html',
  styleUrl: './genre-trainer.component.css',
})
export class GenreTrainerComponent {
  private destroyRef = inject(DestroyRef);

  readonly genreDisplay = new GenreTypeDisplay();

  track = signal<TrackSchema | null>(null);
  genres = signal<string[]>([]);
  isPlaying = signal(false);
  isLoading = signal(false);
  selectedGenre = signal<string | null>(null);
  revealed = signal(false);
  error = signal<string | null>(null);
  autoStart = signal(false);

  streak = signal(0);
  totalAnswered = signal(0);
  totalCorrect = signal(0);
  focusGenres = signal<Set<string>>(this.loadFocusFromStorage());
  volume = signal(0.8);

  isCorrect = computed(() => {
    const s = this.selectedGenre();
    const t = this.track();
    return s !== null && t !== null && s === t.genre;
  });

  noFocus = computed(() => this.focusGenres().size === 0);

  genreLabelMap = computed(() =>
    Object.fromEntries(this.genres().map(g => [g, this.genreDisplay.get(g)]))
  );

  trackGenreLabel = computed(() => {
    const t = this.track();
    return t ? this.genreDisplay.get(t.genre) : '';
  });

  trackGenreDescription = computed(() => {
    const t = this.track();
    return t ? (this.genreDisplay.descriptions[t.genre] ?? '') : '';
  });

  trackGenreFamily = computed(() => {
    const genre = this.track()?.genre;
    if (!genre) return null;
    return this.genreDisplay.families.find(f => f.genres.includes(genre)) ?? null;
  });

  genreButtonState = computed(() => {
    const selected = this.selectedGenre();
    const track = this.track();
    const rev = this.revealed();
    return Object.fromEntries(
      this.genres().map(g => [g, {
        isSelected: g === selected,
        isCorrect: rev && g === track?.genre,
        isWrong: rev && g === selected && g !== track?.genre,
      }])
    );
  });

  focusGenreState = computed(() => {
    const focus = this.focusGenres();
    return Object.fromEntries(this.genres().map(g => [g, focus.has(g)]));
  });

  private canvasEl = viewChild<ElementRef<HTMLCanvasElement>>('vizCanvas');

  private masterGain: Tone.Gain | null = null;
  private analyser: Tone.Analyser | null = null;
  private sequences: Tone.Sequence[] = [];
  private nodes: Tone.ToneAudioNode[] = [];
  private animFrameId: number | null = null;

  constructor() {
    this.destroyRef.onDestroy(() => void this.stopPlayback());
    afterNextRender(() => {
      void this.loadData();
    });
  }

  private loadFocusFromStorage(): Set<string> {
    try {
      const raw = localStorage.getItem('genre_trainer_focus');
      if (raw) {
        return new Set(JSON.parse(raw) as string[]);
      }
    } catch {}
    return new Set();
  }

  private saveFocusToStorage(focus: Set<string>): void {
    localStorage.setItem('genre_trainer_focus', JSON.stringify([...focus]));
  }

  private async loadData(): Promise<void> {
    this.isLoading.set(true);
    this.error.set(null);
    try {
      const focus = this.focusGenres();
      const trackOptions = focus.size > 0 ? {query: {genres: [...focus].join(',')}} : undefined;

      if (this.genres().length === 0) {
        const [trackRes, genresRes] = await Promise.all([
          getRandomTrackView(trackOptions),
          getGenresView(),
        ]);
        this.track.set(trackRes.data.track);
        this.genres.set(genresRes.data.genres);
      } else {
        const trackRes = await getRandomTrackView(trackOptions);
        this.track.set(trackRes.data.track);
      }
    } catch {
      this.error.set('Failed to load track. Is the backend running?');
    } finally {
      this.isLoading.set(false);
    }
  }

  async togglePlay(): Promise<void> {
    if (this.isPlaying()) {
      await this.stopPlayback();
    } else {
      await this.startPlayback();
    }
  }

  toggleAutoStart(): void {
    this.autoStart.update(v => !v);
  }

  toggleFocusGenre(genre: string): void {
    this.focusGenres.update(prev => {
      const next = new Set(prev);
      if (next.has(genre)) {
        next.delete(genre);
      } else {
        next.add(genre);
      }
      this.saveFocusToStorage(next);
      return next;
    });
  }

  clearFocus(): void {
    this.focusGenres.set(new Set());
    localStorage.removeItem('genre_trainer_focus');
  }

  setVolume(value: number): void {
    this.volume.set(value);
    if (this.masterGain) {
      this.masterGain.gain.value = value;
    }
  }

  private async startPlayback(): Promise<void> {
    const track = this.track();
    if (!track) {
      return;
    }
    await Tone.start();

    this.masterGain = new Tone.Gain(this.volume()).toDestination();
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
    this.isPlaying.set(true);
    this.startAnimation();
  }

  private async stopPlayback(): Promise<void> {
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

    this.isPlaying.set(false);
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
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const s = synth as any;
        if (synthType === 'MetalSynth' || synthType === 'NoiseSynth') {
          s.triggerAttackRelease(duration, time);
        } else {
          s.triggerAttackRelease(note, duration, time);
        }
      },
      layer.pattern.steps as (string | null)[],
      layer.pattern.subdivision as Tone.Unit.Time,
    );
  }

  private startAnimation(): void {
    const draw = (): void => {
      if (!this.isPlaying()) {
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
      const bpm = this.track()?.bpm ?? 128;
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

  selectGenre(genre: string): void {
    if (this.revealed()) {
      return;
    }
    this.selectedGenre.set(genre);
    this.revealed.set(true);
    this.totalAnswered.update(n => n + 1);
    if (genre === this.track()?.genre) {
      this.totalCorrect.update(n => n + 1);
      this.streak.update(n => n + 1);
    } else {
      this.streak.set(0);
    }
  }

  async nextTrack(): Promise<void> {
    await this.stopPlayback();
    this.selectedGenre.set(null);
    this.revealed.set(false);
    this.track.set(null);
    await this.loadData();
    if (this.autoStart()) {
      await this.startPlayback();
    }
  }
}
