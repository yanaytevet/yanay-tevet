import {Component, computed, input, signal} from '@angular/core';
import {NgIcon} from '@ng-icons/core';
import {bootstrapVolumeUpFill} from '@ng-icons/bootstrap-icons';

// Furigana annotations look like 漢字(かんじ); for speech we keep just the reading
// so the synthesizer pronounces ambiguous kanji exactly as intended.
const FURIGANA_PATTERN = /([一-龯㐀-䶿]+)\(([぀-ゟー]+)\)/g;

function toSpeechText(text: string): string {
  return text.replace(FURIGANA_PATTERN, '$2');
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

  speak(event: MouseEvent): void {
    // The button can live inside a card-wide link; don't trigger navigation.
    event.preventDefault();
    event.stopPropagation();
    if (!this.isSupported) {
      return;
    }
    const synth = window.speechSynthesis;
    synth.cancel();

    const utterance = new SpeechSynthesisUtterance(this.speechText());
    utterance.lang = 'ja-JP';
    const jaVoice = synth.getVoices().find(v => v.lang.startsWith('ja'));
    if (jaVoice) {
      utterance.voice = jaVoice;
    }
    utterance.onend = () => this.isSpeaking.set(false);
    utterance.onerror = () => this.isSpeaking.set(false);

    this.isSpeaking.set(true);
    synth.speak(utterance);
  }
}
