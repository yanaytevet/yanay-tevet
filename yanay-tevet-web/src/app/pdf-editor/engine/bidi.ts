import bidiFactory from 'bidi-js';

const bidi = bidiFactory();

const RTL_CHAR = /[\u0590-\u08FF\uFB1D-\uFDFF\uFE70-\uFEFF]/;
const LTR_CHAR = /[\p{L}\p{Nd}]/u;

export function isRtlChar(c: string): boolean {
  return RTL_CHAR.test(c);
}

function isLtrOrDigit(c: string): boolean {
  return !RTL_CHAR.test(c) && LTR_CHAR.test(c);
}

export function hasRtl(text: string): boolean {
  return RTL_CHAR.test(text);
}

// The paragraph direction of a line, by the majority of its strong characters.
export function isMostlyRtl(chars: string[]): boolean {
  let rtl = 0;
  let ltr = 0;
  for (const c of chars) {
    if (RTL_CHAR.test(c)) {
      rtl++;
    } else if (/\p{L}/u.test(c)) {
      ltr++;
    }
  }
  return rtl > ltr;
}

// The first strong character decides, as in a text editor.
export function startsRtl(text: string): boolean {
  for (const c of text) {
    if (RTL_CHAR.test(c)) {
      return true;
    }
    if (/\p{L}/u.test(c)) {
      return false;
    }
  }
  return false;
}

// Reverses each run of `inRun` characters in place and returns the positions the runs cover.
function reverseRuns(order: number[], chars: string[], inRun: (c: string) => boolean): Set<number> {
  const covered = new Set<number>();
  let i = 0;
  while (i < order.length) {
    if (!inRun(chars[order[i]])) {
      i++;
      continue;
    }
    // A run spans from a run character to the last run character before the next opposite-direction one;
    // neutrals (spaces, punctuation) inside it stay with it.
    let end = i;
    let j = i + 1;
    while (j < order.length) {
      const c = chars[order[j]];
      if (inRun(c)) {
        end = j;
      } else if (isRtlChar(c) !== isRtlChar(chars[order[i]]) && /[\p{L}\p{Nd}]/u.test(c)) {
        break;
      }
      j++;
    }
    const run = order.slice(i, end + 1).reverse();
    order.splice(i, run.length, ...run);
    for (let k = i; k <= end; k++) {
      covered.add(k);
    }
    i = end + 1;
  }
  return covered;
}

const MIRRORED: Record<string, string> = {'(': ')', ')': '(', '[': ']', ']': '[', '{': '}', '}': '{', '<': '>', '>': '<'};

export interface LogicalChar {
  visualIndex: number;
  char: string;
}

// PDFs store glyphs in display order. Turns display order (left to right) into reading order. With
// `mirror`, brackets inside right-to-left text are swapped (see EditableLine.labelsByShape).
export function visualToLogical(visualChars: string[], rtl: boolean, mirror: boolean): LogicalChar[] {
  const order = visualChars.map((_, i) => i);
  let rtlPositions: (position: number) => boolean;
  if (rtl) {
    order.reverse();
    const ltrRuns = reverseRuns(order, visualChars, isLtrOrDigit);
    rtlPositions = position => !ltrRuns.has(position);
  } else {
    const rtlRuns = reverseRuns(order, visualChars, isRtlChar);
    rtlPositions = position => rtlRuns.has(position);
  }
  return order.map((visualIndex, position) => {
    const c = visualChars[visualIndex];
    return {visualIndex, char: mirror && rtlPositions(position) ? (MIRRORED[c] ?? c) : c};
  });
}

const OPENING = new Set(['(', '[', '{']);
const CLOSING = new Set([')', ']', '}']);

export function hasBrackets(chars: string[]): boolean {
  return chars.some(c => OPENING.has(c) || CLOSING.has(c));
}

// How often a closing bracket comes before its opening one; lower is more plausible.
export function bracketMismatches(chars: string[]): number {
  let depth = 0;
  let mismatches = 0;
  for (const c of chars) {
    if (OPENING.has(c)) {
      depth++;
    } else if (CLOSING.has(c)) {
      depth--;
      if (depth < 0) {
        mismatches++;
        depth = 0;
      }
    }
  }
  return mismatches + depth;
}

export interface VisualChar {
  logicalIndex: number;
  char: string;
}

// Reading order to display order, with mirrored brackets in right-to-left runs (UAX #9).
export function logicalToVisual(text: string, rtl: boolean): VisualChar[] {
  const chars = Array.from(text);
  // bidi-js works on UTF-16 indices; map them back to code points.
  const unitToChar: number[] = [];
  chars.forEach((c, i) => unitToChar.push(...Array<number>(c.length).fill(i)));
  const levels = bidi.getEmbeddingLevels(text, rtl ? 'rtl' : 'ltr');
  const indices = bidi.getReorderedIndices(text, levels);
  const mirrored = bidi.getMirroredCharactersMap(text, levels.levels);
  const result: VisualChar[] = [];
  let lastChar = -1;
  for (const unit of indices) {
    const charIndex = unitToChar[unit];
    if (charIndex === lastChar) {
      continue;
    }
    lastChar = charIndex;
    const char = mirrored.get(unit) ?? chars[charIndex];
    result.push({logicalIndex: charIndex, char});
  }
  return result;
}
