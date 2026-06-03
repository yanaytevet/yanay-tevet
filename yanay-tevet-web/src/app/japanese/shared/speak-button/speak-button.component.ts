import {Component, computed, input, signal} from '@angular/core';
import {NgIcon} from '@ng-icons/core';
import {bootstrapVolumeUpFill} from '@ng-icons/bootstrap-icons';

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

@Component({
  selector: 'app-speak-button',
  standalone: true,
  imports: [NgIcon],
  templateUrl: './speak-button.component.html',
})
export class SpeakButtonComponent {
  text = input.required<string>();

  protected readonly bootstrapVolumeUpFill = bootstrapVolumeUpFill;
  protected readonly isSpeaking = signal<boolean>(false);

  private readonly speechText = computed(() => toSpeechText(this.text()));
  protected readonly isSupported =
    typeof window !== 'undefined' && 'speechSynthesis' in window;

  constructor() {
    if (this.isSupported) {
      // Voices load asynchronously; warm the list so the first click already has them.
      window.speechSynthesis.getVoices();
    }
  }

  speak(event: MouseEvent): void {
    // The button can live inside a card-wide link; don't trigger navigation.
    event.preventDefault();
    event.stopPropagation();
    if (!this.isSupported) {
      return;
    }
    const synth = window.speechSynthesis;

    const voices = synth.getVoices();
    if (voices.length === 0) {
      // Voices not ready yet — wait for them, then speak once.
      synth.addEventListener('voiceschanged', () => this.utter(synth.getVoices()), {once: true});
      return;
    }
    this.utter(voices);
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
    // Slightly slower and lower pitch reads more naturally than the snappy default.
    utterance.rate = 0.95;
    utterance.pitch = 1;
    utterance.onend = () => this.isSpeaking.set(false);
    utterance.onerror = () => this.isSpeaking.set(false);

    this.isSpeaking.set(true);
    synth.speak(utterance);
  }
}
