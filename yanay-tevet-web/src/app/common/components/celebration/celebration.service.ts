import {Injectable, signal} from '@angular/core';
import {AnimationOptions} from 'ngx-lottie';

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
  creatureOptions: AnimationOptions;
  confettiOptions: AnimationOptions;
  flyRightToLeft: boolean;
  confetti: ConfettiPiece[];
}

const BURST_LIFETIME_MS = 2800;

// Drop any open-source Lottie .json into public/celebrations and add its path here
// to extend the random pool of flying creatures (e.g. a unicorn, party-popper).
const CREATURE_ANIMATIONS = [
  '/celebrations/rocket.json',
  '/celebrations/trophy.json',
  '/celebrations/stars.json',
];
const CONFETTI_ANIMATIONS = [
  '/celebrations/confetti.json',
  '/celebrations/ribbons.json',
];

function pick<T>(items: T[]): T {
  return items[Math.floor(Math.random() * items.length)];
}

@Injectable({providedIn: 'root'})
export class CelebrationService {
  readonly bursts = signal<CelebrationBurst[]>([]);
  private nextId = 0;

  private readonly colors = ['#ff4d6d', '#ff9e00', '#ffd000', '#38b000', '#00bbf9', '#9b5de5', '#f15bb5'];

  celebrate(): void {
    const id = this.nextId++;
    const confetti: ConfettiPiece[] = Array.from({length: 60}, () => ({
      left: Math.random() * 100,
      color: this.colors[Math.floor(Math.random() * this.colors.length)],
      delayMs: Math.random() * 300,
      durationMs: 1400 + Math.random() * 1200,
      drift: (Math.random() - 0.5) * 280,
      rotate: Math.random() * 900 - 450,
      size: 7 + Math.random() * 8,
      round: Math.random() < 0.4,
    }));
    const burst: CelebrationBurst = {
      id,
      creatureOptions: {path: pick(CREATURE_ANIMATIONS), loop: true, autoplay: true},
      confettiOptions: {
        path: pick(CONFETTI_ANIMATIONS),
        loop: false,
        autoplay: true,
        rendererSettings: {preserveAspectRatio: 'xMidYMid slice'},
      },
      flyRightToLeft: Math.random() < 0.5,
      confetti,
    };
    this.bursts.update(b => [...b, burst]);
    setTimeout(() => this.bursts.update(b => b.filter(x => x.id !== id)), BURST_LIFETIME_MS);
  }
}
