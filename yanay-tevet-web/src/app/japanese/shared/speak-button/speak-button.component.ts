import {Component, computed, input, signal} from '@angular/core';
import {NgIcon} from '@ng-icons/core';
import {bootstrapVolumeUpFill, bootstrapStopFill, bootstrapArrowRepeat} from '@ng-icons/bootstrap-icons';

// Furigana annotations look like 漢字(かんじ); for speech we keep just the reading
// so the synthesizer pronounces ambiguous kanji exactly as intended.
const FURIGANA_PATTERN = /([一-龯㐀-䶿]+)\(([぀-ゟー]+)\)/g;

function toSpeechText(text: string): string {
  return text.replace(FURIGANA_PATTERN, '$2');
}

// Higher-quality Japanese voices, best first. Network voices (Google, Microsoft
// "Natural") sound dramatically more human than the default local fallbacks, so
// we prefer them; the named locals are the best on-device options per-OS.
const PREFERRED_VOICE_NAMES = [
  'Google 日本語',
  'Microsoft Nanami Online (Natural) - Japanese (Japan)',
  'Microsoft Keita Online (Natural) - Japanese (Japan)',
  'Microsoft Nanami',
  'O-ren', // macOS enhanced
  'Kyoko', // macOS
];

function pickVoice(voices: SpeechSynthesisVoice[]): SpeechSynthesisVoice | null {
  const ja = voices.filter(v => v.lang.toLowerCase().startsWith('ja'));
  if (ja.length === 0) {
    return null;
  }
  for (const name of PREFERRED_VOICE_NAMES) {
    const match = ja.find(v => v.name === name || v.name.includes(name));
    if (match) {
      return match;
    }
  }
  // Otherwise prefer any network voice over a local one — they're far more natural.
  return ja.find(v => !v.localService) ?? ja[0];
}

const BASE_RATE = 0.95;
const BASE_PITCH = 1;

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}

@Component({
  selector: 'app-speak-button',
  standalone: true,
  imports: [NgIcon],
  templateUrl: './speak-button.component.html',
})
export class SpeakButtonComponent {
  text = input.required<string>();

  protected readonly bootstrapVolumeUpFill = bootstrapVolumeUpFill;
  protected readonly bootstrapStopFill = bootstrapStopFill;
  protected readonly bootstrapArrowRepeat = bootstrapArrowRepeat;

  protected readonly isSpeaking = signal<boolean>(false);
  protected readonly loopEnabled = signal<boolean>(false);

  private readonly speechText = computed(() => toSpeechText(this.text()));
  protected readonly isSupported =
    typeof window !== 'undefined' && 'speechSynthesis' in window;

  private iteration = 0;

  constructor() {
    if (this.isSupported) {
      // Voices load asynchronously; warm the list so the first click already has them.
      window.speechSynthesis.getVoices();
    }
  }

  toggleSpeak(event: MouseEvent): void {
    // The button can live inside a card-wide link; don't trigger navigation.
    event.preventDefault();
    event.stopPropagation();
    if (!this.isSupported) {
      return;
    }
    if (this.isSpeaking()) {
      this.stop();
      return;
    }
    this.start();
  }

  toggleLoop(event: MouseEvent): void {
    event.preventDefault();
    event.stopPropagation();
    this.loopEnabled.update(v => !v);
  }

  private start(): void {
    const synth = window.speechSynthesis;
    this.iteration = 0;
    this.isSpeaking.set(true);

    const voices = synth.getVoices();
    if (voices.length === 0) {
      // Voices not ready yet — wait for them, then speak once.
      synth.addEventListener('voiceschanged', () => this.utter(synth.getVoices()), {once: true});
      return;
    }
    this.utter(voices);
  }

  private stop(): void {
    // Clearing isSpeaking first tells the onend handler (cancel fires it) not to loop.
    this.isSpeaking.set(false);
    window.speechSynthesis.cancel();
  }

  private utter(voices: SpeechSynthesisVoice[]): void {
    const synth = window.speechSynthesis;
    synth.cancel();

    const utterance = new SpeechSynthesisUtterance(this.speechText());
    utterance.lang = 'ja-JP';
    const voice = pickVoice(voices);
    if (voice) {
      utterance.voice = voice;
    }
    // The first pass uses the natural baseline; each looped repeat nudges rate and
    // pitch by a small random amount so successive readings don't sound robotically
    // identical, without drifting far enough to distort the pronunciation.
    if (this.iteration === 0) {
      utterance.rate = BASE_RATE;
      utterance.pitch = BASE_PITCH;
    } else {
      utterance.rate = clamp(BASE_RATE + (Math.random() * 2 - 1) * 0.06, 0.85, 1.1);
      utterance.pitch = clamp(BASE_PITCH + (Math.random() * 2 - 1) * 0.08, 0.85, 1.15);
    }

    utterance.onend = () => {
      if (this.loopEnabled() && this.isSpeaking()) {
        this.iteration++;
        this.utter(voices);
        return;
      }
      this.isSpeaking.set(false);
    };
    utterance.onerror = () => this.isSpeaking.set(false);

    synth.speak(utterance);
  }
}
