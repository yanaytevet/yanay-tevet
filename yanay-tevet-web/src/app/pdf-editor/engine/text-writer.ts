import type {Font, PDFDocument, PDFObject, PDFPage} from 'mupdf';
import {logicalToVisual} from './bidi';
import {CharEncoder, ExistingFontEncoder, FallbackFontEncoder, FallbackFonts, GlyphCode} from './font-encoders';
import {mupdf} from './mupdf-runtime';
import {FontChoice, Point, Rect, TextStyle} from './pdf-engine.types';
import {CharStyle, fontChoiceOf} from './text-lines';

// A character to write. `style` is the original character's style (or the style it inherits); `source`
// is the original character it keeps, if any, so unchanged text keeps its original spacing.
export interface CharToWrite {
  char: string;
  style: CharStyle | null;
  source: {visualIndex: number; measuredAdvance: number | null} | null;
}

export interface WriteSpec {
  chars: CharToWrite[];
  rtl: boolean;
  // A point on the baseline: where the text starts, or where it ends when `anchorIsEnd`.
  anchor: Point;
  anchorIsEnd: boolean;
  dir: Point;
  // Replaces every character's style: the user picked a font.
  override: TextStyle | null;
  // See EditableLine.labelsByShape.
  existingFontsLabelByShape: boolean;
}

export interface WriteOutcome {
  substitutedFonts: string[];
  missingCharacters: string[];
}

function fmt(n: number): string {
  const s = n.toFixed(4).replace(/\.?0+$/, '');
  return s === '-0' ? '0' : s;
}

function colorOperator(color: number[]): string {
  const values = color.map(fmt).join(' ');
  if (color.length === 1) {
    return `${values} g`;
  }
  if (color.length === 4) {
    return `${values} k`;
  }
  return `${values} rg`;
}

// Fonts the document can draw with, per document; reset when the document changes underneath (undo).
export class FontRegistry {
  private existing = new Map<string, ExistingFontEncoder[]>();
  private fallback = new Map<string, FallbackFontEncoder>();

  constructor(private readonly doc: PDFDocument, readonly fallbackFonts: FallbackFonts) {}

  resetPageFonts(): void {
    this.existing.clear();
  }

  resetAll(): void {
    this.existing.clear();
    this.fallback.clear();
  }

  // The PDF fonts on a page whose /BaseFont is `name`.
  fontObjectsNamed(page: PDFPage, name: string): PDFObject[] {
    return this.fontObjectsOf(page).filter(ref => {
      const baseFont = ref.resolve().get('BaseFont');
      return baseFont.isName() && baseFont.asName() === name;
    });
  }

  private fontObjectsOf(page: PDFPage): PDFObject[] {
    const result: PDFObject[] = [];
    const seen = new Set<number>();
    const visit = (resources: PDFObject, depth: number): void => {
      if (resources.isNull() || depth > 3) {
        return;
      }
      const fonts = resources.get('Font');
      if (fonts.isDictionary()) {
        fonts.forEach(value => {
          if (value.isIndirect() && !seen.has(value.asIndirect())) {
            seen.add(value.asIndirect());
            result.push(value);
          }
        });
      }
      const xobjects = resources.get('XObject');
      if (xobjects.isDictionary()) {
        xobjects.forEach(value => {
          const xobject = value.resolve();
          if (xobject.get('Subtype').isName() && xobject.get('Subtype').asName() === 'Form') {
            visit(xobject.get('Resources'), depth + 1);
          }
        });
      }
    };
    visit(page.getObject().getInheritable('Resources'), 0);
    return result;
  }

  // The PDF font behind a font the text extraction reported, picked by name and, among same-named
  // subsets, by how many of the given characters it can draw.
  existingFor(pageIndex: number, page: PDFPage, font: Font, codePoints: number[]): ExistingFontEncoder | null {
    const name = font.getName();
    const cacheKey = `${pageIndex}|${name}`;
    let candidates = this.existing.get(cacheKey);
    if (!candidates) {
      candidates = [];
      for (const ref of this.fontObjectsOf(page)) {
        const baseFont = ref.resolve().get('BaseFont');
        if (baseFont.isName() && baseFont.asName() === name) {
          const encoder = ExistingFontEncoder.fromFontObject(ref);
          if (encoder) {
            candidates.push(encoder);
          }
        }
      }
      this.existing.set(cacheKey, candidates);
    }
    let best: ExistingFontEncoder | null = null;
    let bestCount = -1;
    for (const candidate of candidates) {
      const count = candidate.covers(codePoints);
      if (count > bestCount) {
        best = candidate;
        bestCount = count;
      }
    }
    return best;
  }

  // Looks the fonts up while the page still uses them: a redaction drops fonts nothing draws with any more.
  warm(pageIndex: number, page: PDFPage, chars: {char: string; style: CharStyle}[]): void {
    const byFont = new Map<Font, number[]>();
    for (const c of chars) {
      const list = byFont.get(c.style.font) ?? [];
      list.push(c.char.codePointAt(0)!);
      byFont.set(c.style.font, list);
    }
    for (const [font, codePoints] of byFont) {
      this.existingFor(pageIndex, page, font, codePoints);
    }
  }

  fallbackEncoders(codePoint: number, choice: FontChoice): FallbackFontEncoder[] {
    return this.fallbackFonts.candidates(codePoint, choice).map(({key, label, font}) => {
      let encoder = this.fallback.get(key);
      if (!encoder) {
        encoder = new FallbackFontEncoder(key, label, font, this.doc);
        this.fallback.set(key, encoder);
      }
      return encoder;
    });
  }
}

export function pageResources(doc: PDFDocument, page: PDFPage): PDFObject {
  const pageObject = page.getObject();
  if (pageObject.get('Resources').isNull()) {
    const inherited = pageObject.getInheritable('Resources');
    const copy = doc.newDictionary();
    if (!inherited.isNull()) {
      inherited.forEach((value, key) => copy.put(key, value));
    }
    pageObject.put('Resources', copy);
  }
  return pageObject.get('Resources');
}

function resourceName(doc: PDFDocument, page: PDFPage, kind: 'Font' | 'XObject', object: PDFObject, prefix: string): string {
  const resources = pageResources(doc, page);
  if (resources.get(kind).isNull()) {
    resources.put(kind, doc.newDictionary());
  }
  const dict = resources.get(kind);
  let found: string | null = null;
  dict.forEach((value, key) => {
    if (found === null && value.isIndirect() && object.isIndirect() && value.asIndirect() === object.asIndirect()) {
      found = String(key);
    }
  });
  if (found !== null) {
    return found;
  }
  let n = 1;
  while (!dict.get(`${prefix}${n}`).isNull()) {
    n++;
  }
  dict.put(`${prefix}${n}`, object);
  return `${prefix}${n}`;
}

// Draws `content` over the page. The existing content is wrapped in q/Q so whatever graphics state it
// leaves behind does not leak into ours.
export function appendContent(doc: PDFDocument, page: PDFPage, content: string): void {
  const pageObject = page.getObject();
  const contents = pageObject.get('Contents');
  const array = doc.newArray();
  array.push(doc.addStream('q\n', {}));
  if (contents.isArray()) {
    contents.forEach(value => array.push(value));
  } else if (!contents.isNull()) {
    array.push(contents);
  }
  array.push(doc.addStream(`Q\n${content}`, {}));
  pageObject.put('Contents', array);
}

export function redact(page: PDFPage, rect: Rect, images: boolean): void {
  const annotation = page.createAnnotation('Redact');
  annotation.setRect(rect);
  const m = mupdf().PDFPage;
  page.applyRedactions(
    false,
    images ? m.REDACT_IMAGE_REMOVE : m.REDACT_IMAGE_NONE,
    images ? m.REDACT_LINE_ART_REMOVE_IF_COVERED : m.REDACT_LINE_ART_NONE,
    m.REDACT_TEXT_REMOVE,
  );
}

interface PlacedGlyph {
  encoder: CharEncoder;
  glyph: GlyphCode;
  size: number;
  color: number[];
  advance: number;
}

export function writeText(doc: PDFDocument, pageIndex: number, page: PDFPage, registry: FontRegistry, spec: WriteSpec): WriteOutcome {
  const substituted = new Set<string>();
  const missing = new Set<string>();
  const text = spec.chars.map(c => c.char).join('');
  const visual = logicalToVisual(text, spec.rtl);

  // Characters per original font, to pick the right subset among same-named fonts.
  const codePointsByFont = new Map<Font, number[]>();
  for (const c of spec.chars) {
    if (c.style && !spec.override) {
      const list = codePointsByFont.get(c.style.font) ?? [];
      list.push(c.char.codePointAt(0)!);
      codePointsByFont.set(c.style.font, list);
    }
  }

  const glyphs: (PlacedGlyph & {source: CharToWrite['source']})[] = [];
  for (const v of visual) {
    const c = spec.chars[v.logicalIndex];
    const codePoint = v.char.codePointAt(0)!;
    const choice = spec.override ? spec.override.font : c.style ? fontChoiceOf(c.style.font) : {family: 'sans' as const, bold: false, italic: false};
    const size = spec.override ? spec.override.size : (c.style?.size ?? 12);
    const color = spec.override ? [...spec.override.color] : (c.style?.color ?? [0, 0, 0]);
    let encoder: CharEncoder | null = null;
    let glyph: GlyphCode | null = null;
    if (c.style && !spec.override) {
      const existing = registry.existingFor(pageIndex, page, c.style.font, codePointsByFont.get(c.style.font) ?? []);
      const existingCodePoint = spec.existingFontsLabelByShape ? codePoint : c.char.codePointAt(0)!;
      glyph = existing?.encode(existingCodePoint) ?? null;
      encoder = glyph ? existing : null;
    }
    if (!glyph) {
      for (const fallback of registry.fallbackEncoders(codePoint, choice)) {
        glyph = fallback.encode(codePoint);
        if (glyph) {
          encoder = fallback;
          break;
        }
      }
      // Text an earlier edit already drew in this bundled font is not a substitution.
      const sameFont = encoder instanceof FallbackFontEncoder && c.style !== null && encoder.drew(c.style.font.getName());
      if (glyph && encoder && c.style && !spec.override && v.char.trim() !== '' && !sameFont) {
        substituted.add(encoder.label);
      }
    }
    if (!glyph || !encoder) {
      if (v.char.trim() !== '') {
        missing.add(v.char);
      }
      continue;
    }
    glyphs.push({encoder, glyph, size, color, advance: (glyph.width / 1000) * size, source: c.source});
  }

  // Keep a character's original advance only when its original neighbour still follows it.
  for (let i = 0; i < glyphs.length - 1; i++) {
    const here = glyphs[i].source;
    const next = glyphs[i + 1].source;
    if (here && next && here.measuredAdvance !== null && next.visualIndex === here.visualIndex + 1
      && !glyphs[i].encoder.substitute && !glyphs[i + 1].encoder.substitute) {
      glyphs[i].advance = here.measuredAdvance;
    }
  }

  const total = glyphs.reduce((sum, g) => sum + g.advance, 0);
  const [dx, dy] = spec.dir;
  let x = spec.anchorIsEnd ? spec.anchor[0] - total * dx : spec.anchor[0];
  let y = spec.anchorIsEnd ? spec.anchor[1] - total * dy : spec.anchor[1];

  const toUser = mupdf().Matrix.invert(page.getTransform());
  const parts: string[] = [];
  let i = 0;
  while (i < glyphs.length) {
    const run: typeof glyphs = [glyphs[i]];
    let j = i + 1;
    while (j < glyphs.length && glyphs[j].encoder === glyphs[i].encoder && glyphs[j].size === glyphs[i].size
      && glyphs[j].color.join() === glyphs[i].color.join()) {
      run.push(glyphs[j]);
      j++;
    }
    const s = run[0].size;
    const fontName = resourceName(doc, page, 'Font', run[0].encoder.fontObject(), 'PEF');
    const trm: [number, number, number, number, number, number] = [s * dx, s * dy, s * dy, -s * dx, x, y];
    const tm = mupdf().Matrix.concat(trm, toUser);
    const array = run.map(g => {
      const adjust = g.glyph.width - (g.advance * 1000) / s;
      return Math.abs(adjust) > 0.01 ? `<${g.glyph.hex}> ${fmt(adjust)}` : `<${g.glyph.hex}>`;
    }).join(' ');
    parts.push(`BT /${fontName} 1 Tf ${colorOperator(run[0].color)} ${tm.map(fmt).join(' ')} Tm [${array}] TJ ET`);
    for (const g of run) {
      x += g.advance * dx;
      y += g.advance * dy;
    }
    i = j;
  }
  if (parts.length > 0) {
    appendContent(doc, page, `q\n${parts.join('\n')}\nQ\n`);
  }
  return {substitutedFonts: [...substituted], missingCharacters: [...missing]};
}
