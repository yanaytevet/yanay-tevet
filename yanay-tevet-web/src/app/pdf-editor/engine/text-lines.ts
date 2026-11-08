import type {Font, PDFPage} from 'mupdf';
import {bracketMismatches, hasBrackets, isMostlyRtl, visualToLogical} from './bidi';
import {FontChoice, FontFamily, Point, Rect, RgbColor, TextLineInfo} from './pdf-engine.types';

export interface CharStyle {
  font: Font;
  size: number;
  color: number[];
}

export interface LineChar {
  char: string;
  origin: Point;
  quad: number[];
  style: CharStyle;
  // Position in display order within the original line.
  visualIndex: number;
  // How far the next character along the line actually starts, which keeps the original spacing
  // (kerning, justification) for characters an edit leaves alone. Null for the last one.
  measuredAdvance: number | null;
}

export interface EditableLine {
  bbox: Rect;
  dir: Point;
  rtl: boolean;
  // Whether the line's fonts label bracket glyphs by their shape (the usual case). MuPDF mirrors brackets
  // in right-to-left text when it extracts it, which is right for those fonts; for fonts that label a
  // mirrored glyph by the character it stands for, extraction has to undo that, and writing has to use
  // the character rather than its mirror.
  labelsByShape: boolean;
  // In display order, left to right along the baseline.
  visual: LineChar[];
  // In reading order.
  logical: LineChar[];
  text: string;
}

const SERIF_NAME = /Times|Georgia|Serif|Garamond|Roman|Cambria|Book|Minion|Palatino|David|Frank|Narkis|Miriam Fixed/i;
const MONO_NAME = /Courier|Mono|Consol|Menlo|Monaco|Fixed/i;
const SANS_NAME = /Arial|Helvetica|Sans|Verdana|Tahoma|Calibri|Segoe|Roboto|Inter|Open|Lato|Gisha|Rubik|Heebo|Assistant|Futura|Avenir|Gill|Trebuchet|Lucida/i;

export function fontChoiceOf(font: Font): FontChoice {
  const name = font.getName();
  // Names first: embedded subsets often carry wrong or missing serif/mono flags.
  let family: FontFamily;
  if (MONO_NAME.test(name)) {
    family = 'mono';
  } else if (SERIF_NAME.test(name)) {
    family = 'serif';
  } else if (SANS_NAME.test(name)) {
    family = 'sans';
  } else if (font.isMono()) {
    family = 'mono';
  } else {
    family = font.isSerif() ? 'serif' : 'sans';
  }
  return {
    family,
    bold: font.isBold() || /Bold|Black|Heavy|Semibold|Demi/i.test(name),
    italic: font.isItalic() || /Italic|Oblique/i.test(name),
  };
}

export function toRgb(color: number[]): RgbColor {
  if (color.length === 1) {
    return [color[0], color[0], color[0]];
  }
  if (color.length === 4) {
    const [c, m, y, k] = color;
    return [(1 - c) * (1 - k), (1 - m) * (1 - k), (1 - y) * (1 - k)];
  }
  if (color.length === 3) {
    return [color[0], color[1], color[2]];
  }
  return [0, 0, 0];
}

function along(p: Point, dir: Point): number {
  return p[0] * dir[0] + p[1] * dir[1];
}

function buildLine(bbox: Rect, dir: Point, chars: RawChar[]): EditableLine | null {
  if (chars.every(c => c.char.trim() === '')) {
    return null;
  }
  const visualChars = [...chars].sort((a, b) => along(a.origin, dir) - along(b.origin, dir));
  const visual: LineChar[] = visualChars.map((c, i) => {
    const next = visualChars[i + 1];
    let measuredAdvance: number | null = null;
    if (next) {
      const gap = along(next.origin, dir) - along(c.origin, dir);
      // A big jump means a gap the line's text doesn't account for (a tab stop, a column); don't keep it.
      if (gap >= 0 && gap < c.style.size * 1.5) {
        measuredAdvance = gap;
      }
    }
    return {...c, visualIndex: i, measuredAdvance};
  });
  const rtl = isMostlyRtl(visual.map(c => c.char));
  const visualText = visual.map(c => c.char);
  let labelsByShape = true;
  let order = visualToLogical(visualText, rtl, false);
  if (hasBrackets(visualText)) {
    const mirrored = visualToLogical(visualText, rtl, true);
    if (bracketMismatches(mirrored.map(l => l.char)) < bracketMismatches(order.map(l => l.char))) {
      order = mirrored;
      labelsByShape = false;
    }
  }
  const logical = order.map(l => ({...visual[l.visualIndex], char: l.char}));
  // Trailing spaces a producer padded the line with are not text anyone wants to edit.
  while (logical.length > 0 && logical[logical.length - 1].char === ' ') {
    logical.pop();
  }
  while (logical.length > 0 && logical[0].char === ' ') {
    logical.shift();
  }
  return {bbox, dir, rtl, labelsByShape, visual, logical, text: logical.map(c => c.char).join('')};
}

type RawChar = Omit<LineChar, 'measuredAdvance' | 'visualIndex'>;

interface RawLine {
  bbox: Rect;
  dir: Point;
  chars: RawChar[];
  order: number;
}

function isHorizontal(dir: Point): boolean {
  return Math.abs(dir[1]) < 0.01 && dir[0] > 0;
}

function baselineOf(line: RawLine): number {
  const ys = line.chars.map(c => c.origin[1]).sort((a, b) => a - b);
  return ys[Math.floor(ys.length / 2)];
}

function sizeOf(line: RawLine): number {
  return Math.max(...line.chars.map(c => c.style.size), 1);
}

// MuPDF splits a line wherever the producer started a new text object, so one sentence can arrive as
// pieces sitting side by side on one baseline. Editing a piece alone lets a longer edit run over its
// neighbour; joining them makes the sentence one line. Pieces further apart than about a word gap stay
// separate (table columns).
export function joinLinePieces(raw: RawLine[]): RawLine[] {
  const horizontal = raw.filter(l => isHorizontal(l.dir) && l.chars.length > 0);
  const others = raw.filter(l => !isHorizontal(l.dir) || l.chars.length === 0);
  const sorted = [...horizontal].sort((a, b) => baselineOf(a) - baselineOf(b) || a.bbox[0] - b.bbox[0]);
  const rows: RawLine[][] = [];
  for (const line of sorted) {
    const row = rows[rows.length - 1];
    if (row && Math.abs(baselineOf(row[0]) - baselineOf(line)) < 0.2 * Math.min(sizeOf(row[0]), sizeOf(line))) {
      row.push(line);
    } else {
      rows.push([line]);
    }
  }
  const joined: RawLine[] = [];
  for (const row of rows) {
    row.sort((a, b) => a.bbox[0] - b.bbox[0]);
    let current: RawLine = {...row[0], chars: [...row[0].chars]};
    for (const next of row.slice(1)) {
      const size = Math.max(sizeOf(current), sizeOf(next));
      const gap = next.bbox[0] - current.bbox[2];
      if (gap > 0.8 * size || gap < -0.5 * size) {
        joined.push(current);
        current = {...next, chars: [...next.chars]};
        continue;
      }
      const left = [...current.chars].sort((a, b) => a.origin[0] - b.origin[0]).pop()!;
      const right = [...next.chars].sort((a, b) => a.origin[0] - b.origin[0])[0];
      const chars = [...current.chars];
      // The pieces' word gap has no space character of its own; give it one so the words stay apart.
      if (gap > 0.15 * size && left.char !== ' ' && right.char !== ' ') {
        const x = current.bbox[2];
        chars.push({char: ' ', origin: [x, left.origin[1]], quad: [x, left.quad[1], next.bbox[0], left.quad[3], x, left.quad[5], next.bbox[0], left.quad[7]], style: left.style});
      }
      chars.push(...next.chars);
      current = {
        bbox: [current.bbox[0], Math.min(current.bbox[1], next.bbox[1]), Math.max(current.bbox[2], next.bbox[2]), Math.max(current.bbox[3], next.bbox[3])],
        dir: current.dir,
        chars,
        order: Math.min(current.order, next.order),
      };
    }
    joined.push(current);
  }
  return [...joined, ...others].sort((a, b) => a.order - b.order);
}

export function extractLines(page: PDFPage): EditableLine[] {
  const stext = page.toStructuredText('');
  // One object per distinct style, so styles compare by identity.
  const styles = new Map<string, CharStyle>();
  const styleOf = (font: Font, size: number, color: number[]): CharStyle => {
    const key = `${font.getName()}|${size.toFixed(2)}|${color.join(',')}`;
    let style = styles.get(key);
    if (!style) {
      style = {font, size, color: [...color]};
      styles.set(key, style);
    }
    return style;
  };
  const raw: RawLine[] = [];
  let current: RawLine | null = null;
  stext.walk({
    beginLine(bbox, _wmode, dir) {
      current = {bbox: [...bbox] as Rect, dir: [dir[0], dir[1]], chars: [], order: raw.length};
    },
    onChar(c, origin, font, size, quad, color) {
      current?.chars.push({char: c, origin: [origin[0], origin[1]], quad: [...quad], style: styleOf(font, size, color)});
    },
    endLine() {
      if (current) {
        raw.push(current);
      }
      current = null;
    },
  });
  const lines: EditableLine[] = [];
  for (const piece of joinLinePieces(raw)) {
    const line = buildLine(piece.bbox, piece.dir, piece.chars);
    if (line) {
      lines.push(line);
    }
  }
  return lines;
}

export function dominantStyle(line: EditableLine): CharStyle {
  const counts = new Map<CharStyle, number>();
  for (const c of line.logical) {
    if (c.char.trim() !== '') {
      counts.set(c.style, (counts.get(c.style) ?? 0) + 1);
    }
  }
  let best = line.logical[0].style;
  let bestCount = -1;
  for (const [style, count] of counts) {
    if (count > bestCount) {
      best = style;
      bestCount = count;
    }
  }
  return best;
}

export function lineInfo(line: EditableLine, index: number): TextLineInfo {
  const style = dominantStyle(line);
  return {
    index,
    bbox: line.bbox,
    text: line.text,
    rtl: line.rtl,
    horizontal: Math.abs(line.dir[1]) < 0.01 && line.dir[0] > 0,
    size: Math.round(style.size * 10) / 10,
    font: fontChoiceOf(style.font),
    fontName: style.font.getName().replace(/^[A-Z]{6}\+/, ''),
    pdfFontName: style.font.getName(),
    color: toRgb(style.color),
  };
}
