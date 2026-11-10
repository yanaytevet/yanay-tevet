import type {Font, PDFDocument, PDFObject, PDFPage, Text} from 'mupdf';
import {logicalToVisual} from './bidi';
import {CharEncoder, ExistingFontEncoder, FallbackFontEncoder, FallbackFonts, GlyphCode} from './font-encoders';
import {mupdf} from './mupdf-runtime';
import {FontChoice, Point, Rect, TextStyle} from './pdf-engine.types';
import {CharStyle, fontChoiceOf} from './text-lines';

// A character to write. `style` is the original character's style (or the style it inherits); `source`
// is the original character it keeps, if any, so unchanged text keeps its original spacing.
export interface CharToWrite {
  char: string;
  // With WriteSpec.visualOrder: the character as it is drawn (its mirrored form in right-to-left text).
  visualChar?: string;
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
  // Keep every original character's spacing, whatever font draws it (moving a line unchanged).
  keepSpacing?: boolean;
  // `chars` are already in display order and stay in it: a line moved as it is keeps its layout even where
  // re-running the bidi algorithm over its text would order it differently from how its producer did.
  visualOrder?: boolean;
}

export interface WriteOutcome {
  substitutedFonts: string[];
  missingCharacters: string[];
  // Where the written text starts and ends along the line (x, for horizontal text), or null if nothing was.
  extent: [number, number] | null;
}

function fmt(n: number): string {
  const s = n.toFixed(4).replace(/\.?0+$/, '');
  return s === '-0' ? '0' : s;
}

export function colorOperator(color: number[]): string {
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
  // Font name → character → code, read off the document's pages (see ExistingFontEncoder.fromFontObject).
  private learnedGlyphs: Map<string, Map<number, number>> | null = null;

  constructor(private readonly doc: PDFDocument, readonly fallbackFonts: FallbackFonts) {}

  resetPageFonts(): void {
    this.existing.clear();
  }

  resetAll(): void {
    this.existing.clear();
    this.fallback.clear();
    this.learnedGlyphs = null;
  }

  // Which code drew which character, for fonts without a /ToUnicode: MuPDF reads their text through the
  // font's character collection (Adobe-Japan1 for Japanese), and with Identity-H the glyph it reports is the
  // code in the content stream. Read once from the first pages, where the document's text is.
  private learned(name: string): Map<number, number> | null {
    if (!this.learnedGlyphs) {
      const learned = new Map<string, Map<number, number>>();
      const record = (text: Text) => text.walk({
        showGlyph(font: Font, _trm: unknown, glyph: number, unicode: number) {
          if (unicode > 0 && glyph >= 0) {
            const map = learned.get(font.getName()) ?? new Map<number, number>();
            if (!map.has(unicode)) {
              map.set(unicode, glyph);
            }
            learned.set(font.getName(), map);
          }
        },
      } as never);
      const m = mupdf();
      const device = new m.Device({
        fillText: (text: Text) => record(text),
        strokeText: (text: Text) => record(text),
        clipText: (text: Text) => record(text),
        clipStrokeText: (text: Text) => record(text),
        ignoreText: (text: Text) => record(text),
      } as never);
      const pages = Math.min(this.doc.countPages(), 60);
      for (let i = 0; i < pages; i++) {
        this.doc.loadPage(i).run(device, m.Matrix.identity);
      }
      device.close();
      this.learnedGlyphs = learned;
    }
    return this.learnedGlyphs.get(name) ?? null;
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
          const encoder = ExistingFontEncoder.fromFontObject(ref, () => this.learned(name));
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

  fallbackEncoders(codePoint: number, choice: FontChoice, originalName: string | null): FallbackFontEncoder[] {
    return this.fallbackFonts.candidates(codePoint, choice, originalName).map(({key, label, font, hebrewScale}) => {
      let encoder = this.fallback.get(key);
      if (!encoder) {
        encoder = new FallbackFontEncoder(key, label, font, this.doc, hebrewScale);
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
  char: string;
}

export function writeText(doc: PDFDocument, pageIndex: number, page: PDFPage, registry: FontRegistry, spec: WriteSpec): WriteOutcome {
  const substituted = new Set<string>();
  const missing = new Set<string>();
  const text = spec.chars.map(c => c.char).join('');
  const visual = spec.visualOrder
    ? spec.chars.map((c, logicalIndex) => ({char: c.visualChar ?? c.char, logicalIndex}))
    : logicalToVisual(text, spec.rtl);

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
      for (const fallback of registry.fallbackEncoders(codePoint, choice, spec.override ? null : (c.style?.font.getName() ?? null))) {
        glyph = fallback.encode(codePoint);
        if (glyph) {
          encoder = fallback;
          break;
        }
      }
      // Text an earlier edit already drew in this bundled font is not a substitution, and neither is the
      // bundled font made to match the original's family.
      const blends = encoder instanceof FallbackFontEncoder && c.style !== null
        && (encoder.drew(c.style.font.getName()) || encoder.standsInFor(c.style.font.getName()));
      if (glyph && encoder && c.style && !spec.override && v.char.trim() !== '' && !blends) {
        substituted.add(encoder.label);
      }
    }
    if (!glyph || !encoder) {
      if (v.char.trim() !== '') {
        missing.add(v.char);
      }
      continue;
    }
    const glyphSize = size * (glyph.scale ?? 1);
    glyphs.push({encoder, glyph, size: glyphSize, color, advance: (glyph.width / 1000) * glyphSize, source: c.source, char: v.char});
  }

  // Text is never dropped: a line whose characters no font here can draw stays as it was (the caller's journal
  // operation is abandoned, so the redaction that took it off comes back too).
  if (missing.size > 0) {
    const listed = [...missing].slice(0, 8).map(c => `“${c}”`).join(' ') + (missing.size > 8 ? ' …' : '');
    throw new Error(`No font here can draw ${listed}, so the text was left as it was. `
      + 'Chinese, Korean and scripts besides Latin, Greek, Cyrillic, Hebrew and Japanese can only be edited with fonts installed on this computer, in Chrome or Edge.');
  }

  // Keep a character's original advance when its original neighbour still follows it, unless a substitute
  // font now draws a visibly different glyph there. Spaces always keep it: many subsets have no space glyph,
  // and a substitute's narrower space would pull the words together.
  const faithful = (g: PlacedGlyph): boolean => spec.keepSpacing || !g.encoder.substitute || g.char.trim() === '';
  // A word gap is the space as the line was set (justified, or a subset's missing space drawn as a gap), so an
  // original space keeps it whatever now follows, and a typed space takes the line's usual one.
  const spaceGaps = glyphs.filter(g => g.char === ' ' && g.source?.measuredAdvance != null).map(g => g.source!.measuredAdvance!).sort((a, b) => a - b);
  const usualSpace = spaceGaps.length > 0 ? spaceGaps[Math.floor(spaceGaps.length / 2)] : null;
  for (let i = 0; i < glyphs.length - 1; i++) {
    const here = glyphs[i].source;
    const next = glyphs[i + 1].source;
    if (glyphs[i].char === ' ') {
      const gap = here?.measuredAdvance ?? usualSpace;
      if (gap !== null) {
        glyphs[i].advance = gap;
      }
    } else if (here && next && here.measuredAdvance !== null && next.visualIndex === here.visualIndex + 1
      && faithful(glyphs[i]) && faithful(glyphs[i + 1])) {
      glyphs[i].advance = here.measuredAdvance;
    }
  }
  // Producers often set a gap without a space character ("תשלום:365665109" has 3pt between the colon and the
  // number). Characters typed into that gap push it along: it goes after them, before the character that
  // followed it, instead of disappearing.
  for (let i = 0; i < glyphs.length - 1; i++) {
    const here = glyphs[i].source;
    if (!here || here.measuredAdvance === null || glyphs[i].char === ' ' || glyphs[i + 1].source || !faithful(glyphs[i])) {
      continue;
    }
    let j = i + 1;
    while (j + 1 < glyphs.length && !glyphs[j + 1].source) {
      j++;
    }
    const after = glyphs[j + 1]?.source;
    const extra = here.measuredAdvance - glyphs[i].advance;
    if (after && after.visualIndex === here.visualIndex + 1 && Math.abs(extra) > 0.01 && glyphs[j].char !== ' ') {
      glyphs[j].advance += extra;
    }
  }

  const total = glyphs.reduce((sum, g) => sum + g.advance, 0);
  const [dx, dy] = spec.dir;
  let x = spec.anchorIsEnd ? spec.anchor[0] - total * dx : spec.anchor[0];
  let y = spec.anchorIsEnd ? spec.anchor[1] - total * dy : spec.anchor[1];

  const toUser = mupdf().Matrix.invert(page.getTransform());
  const parts: string[] = [];
  const startX = x;
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
  return {substitutedFonts: [...substituted], missingCharacters: [...missing], extent: glyphs.length > 0 ? [startX, x] : null};
}
