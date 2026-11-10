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

// Number separators (UAX #9 classes CS and ES) join digits only between them; at a token's edge they belong
// to the text around it. Currency and percent signs (ET) stay with the number they touch.
const SEPARATOR = /[.,:/+\-\u00A0]/;
const TERMINATOR = /[\p{Sc}%\u2030\u00B0#]/u;

// Reverses each left-to-right token on its own: in right-to-left text, numbers apart from each other (by a
// space or a dash) are separate runs, and a colon or comma at a number's edge goes with the Hebrew beside it.
function reverseTokens(order: number[], chars: string[]): Set<number> {
  const covered = new Set<number>();
  const joins = (c: string) => isLtrOrDigit(c) || SEPARATOR.test(c) || TERMINATOR.test(c);
  let i = 0;
  while (i < order.length) {
    if (!joins(chars[order[i]])) {
      i++;
      continue;
    }
    let end = i;
    while (end + 1 < order.length && joins(chars[order[end + 1]])) {
      end++;
    }
    const next = end + 1;
    let first = i;
    let last = end;
    while (first <= last && SEPARATOR.test(chars[order[first]])) {
      first++;
    }
    while (last >= first && SEPARATOR.test(chars[order[last]])) {
      last--;
    }
    if (first <= last && order.slice(first, last + 1).some(k => isLtrOrDigit(chars[k]))) {
      const run = order.slice(first, last + 1).reverse();
      order.splice(first, run.length, ...run);
      for (let k = first; k <= last; k++) {
        covered.add(k);
      }
    }
    i = next;
  }
  return covered;
}

function readingOrder(visualChars: string[], rtl: boolean, strategy: 'runs' | 'tokens'): {order: number[]; rtlPositions: (position: number) => boolean} {
  const order = visualChars.map((_, i) => i);
  if (rtl) {
    order.reverse();
    const ltrRuns = strategy === 'runs' ? reverseRuns(order, visualChars, isLtrOrDigit) : reverseTokens(order, visualChars);
    return {order, rtlPositions: position => !ltrRuns.has(position)};
  }
  const rtlRuns = reverseRuns(order, visualChars, isRtlChar);
  return {order, rtlPositions: position => rtlRuns.has(position)};
}

const BRACKET = /[()[\]{}<>]/g;

// Whether the bidi algorithm lays `logical` out as `visualChars` (brackets aside: which way they face depends
// on the font's convention, settled separately).
function displaysAs(logical: string, rtl: boolean, visualChars: string[]): boolean {
  const shown = logicalToVisual(logical, rtl).map(v => v.char).join('').replace(BRACKET, '|');
  return shown === visualChars.join('').replace(BRACKET, '|');
}

// PDFs store glyphs in display order. Turns display order (left to right) into reading order. With
// `mirror`, brackets inside right-to-left text are swapped (see EditableLine.labelsByShape).
//
// Reading order is guessed, then checked: the bidi algorithm must display the guess the way the line is
// drawn, or the edit box shows the line differently and an edit rewrites it differently. The first guess keeps
// a left-to-right run with its inner spaces together (a Latin phrase in Hebrew); the second takes numbers
// apart ("2,559.00 ₪1" is two runs in right-to-left text, and so is "04–6954611").
export function visualToLogical(visualChars: string[], rtl: boolean, mirror: boolean): LogicalChar[] {
  let chosen = readingOrder(visualChars, rtl, 'runs');
  if (rtl && !displaysAs(chosen.order.map(i => visualChars[i]).join(''), rtl, visualChars)) {
    const tokens = readingOrder(visualChars, rtl, 'tokens');
    if (displaysAs(tokens.order.map(i => visualChars[i]).join(''), rtl, visualChars)) {
      chosen = tokens;
    }
  }
  const {order, rtlPositions} = chosen;
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
