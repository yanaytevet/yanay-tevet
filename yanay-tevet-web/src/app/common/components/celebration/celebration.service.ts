import {Injectable, signal} from '@angular/core';

export interface ConfettiPiece {
  left: number;
  color: string;
  delayMs: number;
  durationMs: number;
  drift: number;
  rotate: number;
  size: number;
  round: boolean;
}

export interface CelebrationBurst {
  id: number;
  creature: string;
  flyRightToLeft: boolean;
  confetti: ConfettiPiece[];
}

const BURST_LIFETIME_MS = 2600;

@Injectable({providedIn: 'root'})
export class CelebrationService {
  readonly bursts = signal<CelebrationBurst[]>([]);
  private nextId = 0;

  private readonly creatures = ['🦄', '🌈', '🎉', '🎊', '⭐', '🚀', '🏆', '✨', '🥳'];
  private readonly colors = ['#ff4d6d', '#ff9e00', '#ffd000', '#38b000', '#00bbf9', '#9b5de5', '#f15bb5'];

  celebrate(): void {
    const id = this.nextId++;
    const confetti: ConfettiPiece[] = Array.from({length: 46}, () => ({
      left: Math.random() * 100,
      color: this.colors[Math.floor(Math.random() * this.colors.length)],
      delayMs: Math.random() * 250,
      durationMs: 1400 + Math.random() * 1100,
      drift: (Math.random() - 0.5) * 240,
      rotate: Math.random() * 720 - 360,
      size: 7 + Math.random() * 7,
      round: Math.random() < 0.4,
    }));
    const burst: CelebrationBurst = {
      id,
      creature: this.creatures[Math.floor(Math.random() * this.creatures.length)],
      flyRightToLeft: Math.random() < 0.5,
      confetti,
    };
    this.bursts.update(b => [...b, burst]);
    setTimeout(() => this.bursts.update(b => b.filter(x => x.id !== id)), BURST_LIFETIME_MS);
  }
}
