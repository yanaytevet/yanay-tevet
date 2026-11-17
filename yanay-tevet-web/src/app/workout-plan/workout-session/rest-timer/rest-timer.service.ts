import {computed, Injectable, signal} from '@angular/core';

// The rest countdown between sets. In root so it keeps running while the user glances at another page.
@Injectable({providedIn: 'root'})
export class RestTimerService {
  readonly endsAt = signal<number | null>(null);
  readonly total = signal<number>(0);
  readonly now = signal<number>(Date.now());
  readonly justFinished = signal<boolean>(false);

  readonly remaining = computed(() => {
    const endsAt = this.endsAt();
    return endsAt === null ? 0 : Math.max(0, Math.ceil((endsAt - this.now()) / 1000));
  });
  readonly progress = computed(() => {
    const total = this.total();
    return total > 0 ? Math.min(1, 1 - this.remaining() / total) : 0;
  });
  readonly isRunning = computed(() => this.endsAt() !== null);

  private intervalId: ReturnType<typeof setInterval> | null = null;
  private finishedTimeoutId: ReturnType<typeof setTimeout> | null = null;
  private audio: AudioContext | null = null;

  start(seconds: number): void {
    this.justFinished.set(false);
    this.total.set(seconds);
    this.now.set(Date.now());
    this.endsAt.set(Date.now() + seconds * 1000);
    this.ensureTicking();
  }

  adjust(seconds: number): void {
    const endsAt = this.endsAt();
    if (endsAt === null) {
      return;
    }
    const next = Math.max(Date.now(), endsAt + seconds * 1000);
    this.endsAt.set(next);
    this.total.set(Math.max(this.total() + seconds, Math.ceil((next - Date.now()) / 1000)));
  }

  stop(): void {
    this.endsAt.set(null);
    this.justFinished.set(false);
    if (this.intervalId !== null) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
  }

  // Browsers only let a page make sound after a tap; called from the tap that logs a set.
  unlockSound(): void {
    if (this.audio === null) {
      try {
        this.audio = new AudioContext();
      } catch {
        this.audio = null;
      }
    }
    void this.audio?.resume();
  }

  private ensureTicking(): void {
    if (this.intervalId !== null) {
      return;
    }
    this.intervalId = setInterval(() => {
      this.now.set(Date.now());
      if (this.endsAt() !== null && this.remaining() === 0) {
        this.finish();
      }
    }, 250);
  }

  private finish(): void {
    this.stop();
    this.justFinished.set(true);
    this.alert();
    if (this.finishedTimeoutId !== null) {
      clearTimeout(this.finishedTimeoutId);
    }
    this.finishedTimeoutId = setTimeout(() => this.justFinished.set(false), 4000);
  }

  private alert(): void {
    navigator.vibrate?.([200, 100, 200]);
    const audio = this.audio;
    if (!audio) {
      return;
    }
    for (const offset of [0, 0.25, 0.5]) {
      const oscillator = audio.createOscillator();
      const gain = audio.createGain();
      oscillator.frequency.value = 880;
      gain.gain.setValueAtTime(0.0001, audio.currentTime + offset);
      gain.gain.exponentialRampToValueAtTime(0.3, audio.currentTime + offset + 0.02);
      gain.gain.exponentialRampToValueAtTime(0.0001, audio.currentTime + offset + 0.18);
      oscillator.connect(gain).connect(audio.destination);
      oscillator.start(audio.currentTime + offset);
      oscillator.stop(audio.currentTime + offset + 0.2);
    }
  }
}
