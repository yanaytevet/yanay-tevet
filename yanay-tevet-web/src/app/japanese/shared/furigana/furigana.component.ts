import {Component, computed, input} from '@angular/core';

interface FuriganaSegment {
  base: string;
  reading: string | null;
}

const FURIGANA_PATTERN = /([一-龯㐀-䶿]+)\(([぀-ゟー]+)\)/g;

function parseFurigana(text: string): FuriganaSegment[] {
  const segments: FuriganaSegment[] = [];
  let lastIndex = 0;
  let match: RegExpExecArray | null;
  FURIGANA_PATTERN.lastIndex = 0;
  while ((match = FURIGANA_PATTERN.exec(text)) !== null) {
    if (match.index > lastIndex) {
      segments.push({base: text.slice(lastIndex, match.index), reading: null});
    }
    segments.push({base: match[1], reading: match[2]});
    lastIndex = match.index + match[0].length;
  }
  if (lastIndex < text.length) {
    segments.push({base: text.slice(lastIndex), reading: null});
  }
  return segments;
}

@Component({
  selector: 'app-furigana',
  standalone: true,
  templateUrl: './furigana.component.html',
})
export class FuriganaComponent {
  text = input.required<string>();
  hideReadings = input<boolean>(false);

  readonly segments = computed<FuriganaSegment[]>(() => parseFurigana(this.text()));
}
