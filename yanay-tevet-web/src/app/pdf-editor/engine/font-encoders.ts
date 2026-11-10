import type {Font, PDFDocument, PDFObject} from 'mupdf';
import {fontKey} from './font-names';
import {mupdf} from './mupdf-runtime';
import {FontChoice, FontFamily} from './pdf-engine.types';

export interface GlyphCode {
  hex: string;
  // Advance in thousandths of the font size, as in a PDF /Widths array.
  width: number;
  // Draw at this fraction of the text size: a substitute Hebrew letter sized to match the original font's.
  scale?: number;
}

// Something that can draw characters on a page: either a font the PDF already has, or a bundled one.
export interface CharEncoder {
  readonly key: string;
  readonly label: string;
  readonly substitute: boolean;
  encode(codePoint: number): GlyphCode | null;
  fontObject(): PDFObject;
}

function toHex(code: number, bytes: number): string {
  return code.toString(16).padStart(bytes * 2, '0');
}

function items(array: PDFObject): PDFObject[] {
  const result: PDFObject[] = [];
  if (array.isArray()) {
    array.forEach(value => result.push(value));
  }
  return result;
}

function utf16HexToString(hex: string): string {
  const units: number[] = [];
  for (let i = 0; i + 4 <= hex.length; i += 4) {
    units.push(parseInt(hex.slice(i, i + 4), 16));
  }
  if (hex.length === 2) {
    units.push(parseInt(hex, 16));
  }
  return String.fromCharCode(...units);
}

interface ParsedCMap {
  bytes: number;
  codeToUnicode: Map<number, string>;
}

function hexTokens(body: string): string[] {
  return [...body.matchAll(/<([0-9a-fA-F\s]*)>|\[|\]/g)].map(m => (m[0].startsWith('<') ? m[1].replace(/\s/g, '') : m[0]));
}

export function parseToUnicodeCMap(text: string, defaultBytes: number): ParsedCMap {
  const codespace = /begincodespacerange\s*<([0-9a-fA-F]+)>/.exec(text);
  const bytes = codespace ? codespace[1].length / 2 : defaultBytes;
  const codeToUnicode = new Map<number, string>();
  for (const section of text.matchAll(/beginbfchar([\s\S]*?)endbfchar/g)) {
    const tokens = hexTokens(section[1]);
    for (let i = 0; i + 1 < tokens.length; i += 2) {
      codeToUnicode.set(parseInt(tokens[i], 16), utf16HexToString(tokens[i + 1]));
    }
  }
  for (const section of text.matchAll(/beginbfrange([\s\S]*?)endbfrange/g)) {
    const tokens = hexTokens(section[1]);
    let i = 0;
    while (i + 2 < tokens.length) {
      const lo = parseInt(tokens[i], 16);
      const hi = Math.min(parseInt(tokens[i + 1], 16), lo + 0xffff);
      if (tokens[i + 2] === '[') {
        let j = i + 3;
        let code = lo;
        while (j < tokens.length && tokens[j] !== ']') {
          codeToUnicode.set(code, utf16HexToString(tokens[j]));
          code++;
          j++;
        }
        i = j + 1;
      } else {
        const start = utf16HexToString(tokens[i + 2]);
        const prefix = start.slice(0, -1);
        const last = start.charCodeAt(start.length - 1);
        for (let code = lo; code <= hi; code++) {
          codeToUnicode.set(code, prefix + String.fromCharCode(last + code - lo));
        }
        i += 3;
      }
    }
  }
  return {bytes, codeToUnicode};
}

// A small part of the Adobe Glyph List: enough for fonts that name their glyphs in a /Differences array.
const GLYPH_NAMES: Record<string, string> = {
  space: ' ', exclam: '!', quotedbl: '"', numbersign: '#', dollar: '$', percent: '%', ampersand: '&',
  quotesingle: "'", parenleft: '(', parenright: ')', asterisk: '*', plus: '+', comma: ',', hyphen: '-',
  period: '.', slash: '/', zero: '0', one: '1', two: '2', three: '3', four: '4', five: '5', six: '6',
  seven: '7', eight: '8', nine: '9', colon: ':', semicolon: ';', less: '<', equal: '=', greater: '>',
  question: '?', at: '@', bracketleft: '[', backslash: '\\', bracketright: ']', asciicircum: '^',
  underscore: '_', grave: '`', braceleft: '{', bar: '|', braceright: '}', asciitilde: '~',
  quoteleft: '‘', quoteright: '’', quotedblleft: '“', quotedblright: '”',
  endash: '–', emdash: '—', bullet: '•', ellipsis: '…', fi: 'ﬁ', fl: 'ﬂ',
  Euro: '€', copyright: '©', registered: '®', trademark: '™', degree: '°',
  nbspace: '\u00a0', sterling: '£', yen: '¥', section: '§', paragraph: '¶',
};

function glyphNameToUnicode(name: string): string | null {
  if (/^[A-Za-z]$/.test(name)) {
    return name;
  }
  const uni = /^uni([0-9A-Fa-f]{4})$/.exec(name) ?? /^u([0-9A-Fa-f]{4,6})$/.exec(name);
  if (uni) {
    return String.fromCodePoint(parseInt(uni[1], 16));
  }
  return GLYPH_NAMES[name] ?? null;
}

function baseEncodingTable(name: string): Map<number, string> {
  const table = new Map<number, string>();
  const decoderName = name === 'MacRomanEncoding' ? 'macintosh' : 'windows-1252';
  const decoder = new TextDecoder(decoderName);
  for (let code = 32; code < 256; code++) {
    if (code === 127 || (code > 127 && code < 160 && name !== 'WinAnsiEncoding' && name !== 'MacRomanEncoding')) {
      continue;
    }
    table.set(code, decoder.decode(new Uint8Array([code])));
  }
  if (name === 'StandardEncoding') {
    table.set(0x27, '’');
    table.set(0x60, '‘');
  }
  return table;
}

function simpleEncodingTable(fontDict: PDFObject, subtype: string): Map<number, string> | null {
  const encoding = fontDict.get('Encoding');
  const descriptor = fontDict.get('FontDescriptor');
  const symbolic = !descriptor.isNull() && (descriptor.get('Flags').asNumber() & 4) !== 0;
  let baseName = subtype === 'TrueType' ? 'WinAnsiEncoding' : 'StandardEncoding';
  let differences: PDFObject | null = null;
  if (encoding.isName()) {
    baseName = encoding.asName();
  } else if (encoding.isDictionary()) {
    const base = encoding.get('BaseEncoding');
    if (base.isName()) {
      baseName = base.asName();
    }
    differences = encoding.get('Differences');
  } else if (symbolic) {
    return null;
  }
  const table = baseEncodingTable(baseName);
  if (differences) {
    let code = 0;
    for (const item of items(differences)) {
      if (item.isNumber()) {
        code = item.asNumber();
      } else if (item.isName()) {
        const unicode = glyphNameToUnicode(item.asName());
        if (unicode) {
          table.set(code, unicode);
        } else {
          table.delete(code);
        }
        code++;
      }
    }
  }
  return table;
}

function cidWidths(descendant: PDFObject): {widths: Map<number, number>; defaultWidth: number} {
  const widths = new Map<number, number>();
  const dw = descendant.get('DW');
  const defaultWidth = dw.isNumber() ? dw.asNumber() : 1000;
  const list = items(descendant.get('W'));
  let i = 0;
  while (i < list.length) {
    const first = list[i].asNumber();
    if (i + 1 < list.length && list[i + 1].isArray()) {
      items(list[i + 1]).forEach((w, k) => widths.set(first + k, w.asNumber()));
      i += 2;
    } else if (i + 2 < list.length) {
      const last = list[i + 1].asNumber();
      const w = list[i + 2].asNumber();
      for (let cid = first; cid <= last && cid - first < 0xffff; cid++) {
        widths.set(cid, w);
      }
      i += 3;
    } else {
      break;
    }
  }
  return {widths, defaultWidth};
}

const BASE14_NAMES = new Set([
  'Helvetica', 'Helvetica-Bold', 'Helvetica-Oblique', 'Helvetica-BoldOblique', 'Times-Roman', 'Times-Bold',
  'Times-Italic', 'Times-BoldItalic', 'Courier', 'Courier-Bold', 'Courier-Oblique', 'Courier-BoldOblique',
  'Symbol', 'ZapfDingbats',
]);

// A font already in the PDF. New text drawn with it uses the codes its /ToUnicode (or encoding) maps
// back to each character, so it looks exactly like the text around it.
export class ExistingFontEncoder implements CharEncoder {
  readonly substitute = false;

  private constructor(
    readonly key: string,
    readonly label: string,
    private readonly ref: PDFObject,
    private readonly bytes: number,
    private readonly unicodeToCode: Map<number, number>,
    private readonly widthOf: (code: number, codePoint: number) => number,
  ) {}

  // `learned`: for a CID font with no /ToUnicode (Japanese from macOS, say), which character each code drew
  // on the document's pages, as MuPDF read it through the font's character collection.
  static fromFontObject(ref: PDFObject, learned: () => Map<number, number> | null = () => null): ExistingFontEncoder | null {
    const dict = ref.resolve();
    const subtype = dict.get('Subtype').isName() ? dict.get('Subtype').asName() : '';
    const baseFont = dict.get('BaseFont').isName() ? dict.get('BaseFont').asName() : '';
    const key = `existing:${ref.isIndirect() ? ref.asIndirect() : baseFont}`;
    const toUnicode = dict.get('ToUnicode');

    if (subtype === 'Type0') {
      const encoding = dict.get('Encoding');
      if (!encoding.isName() || !['Identity-H', 'Identity-V'].includes(encoding.asName())) {
        return null;
      }
      let unicodeToCode: Map<number, number> | null;
      if (toUnicode.isStream()) {
        unicodeToCode = ExistingFontEncoder.invert(parseToUnicodeCMap(toUnicode.readStream().asString(), 2).codeToUnicode);
      } else {
        unicodeToCode = learned();
      }
      if (!unicodeToCode || unicodeToCode.size === 0) {
        return null;
      }
      const descendant = dict.get('DescendantFonts').get(0).resolve();
      const {widths, defaultWidth} = cidWidths(descendant);
      return new ExistingFontEncoder(key, baseFont, ref, 2, unicodeToCode, code => widths.get(code) ?? defaultWidth);
    }

    if (subtype !== 'TrueType' && subtype !== 'Type1' && subtype !== 'MMType1') {
      return null;
    }
    const codeToUnicode = toUnicode.isStream()
      ? parseToUnicodeCMap(toUnicode.readStream().asString(), 1).codeToUnicode
      : simpleEncodingTable(dict, subtype);
    if (!codeToUnicode) {
      return null;
    }
    const firstChar = dict.get('FirstChar').isNumber() ? dict.get('FirstChar').asNumber() : 0;
    const widthList = items(dict.get('Widths')).map(w => w.asNumber());
    const descriptor = dict.get('FontDescriptor');
    const missingWidth = !descriptor.isNull() && descriptor.get('MissingWidth').isNumber()
      ? descriptor.get('MissingWidth').asNumber() : 0;
    const strippedName = baseFont.replace(/^[A-Z]{6}\+/, '');
    let metricsFont: Font | null = null;
    if (widthList.length === 0 && BASE14_NAMES.has(strippedName)) {
      metricsFont = new (mupdf().Font)(strippedName);
    }
    const widthOf = (code: number, codePoint: number): number => {
      if (metricsFont) {
        return metricsFont.advanceGlyph(metricsFont.encodeCharacter(codePoint), 0) * 1000;
      }
      const index = code - firstChar;
      return index >= 0 && index < widthList.length ? widthList[index] : missingWidth;
    };
    return new ExistingFontEncoder(key, baseFont, ref, 1, ExistingFontEncoder.invert(codeToUnicode), widthOf);
  }

  private static invert(codeToUnicode: Map<number, string>): Map<number, number> {
    const result = new Map<number, number>();
    for (const [code, unicode] of codeToUnicode) {
      const codePoints = Array.from(unicode);
      if (codePoints.length !== 1) {
        continue;
      }
      const cp = codePoints[0].codePointAt(0)!;
      if (!result.has(cp)) {
        result.set(cp, code);
      }
    }
    return result;
  }

  encode(codePoint: number): GlyphCode | null {
    const code = this.unicodeToCode.get(codePoint);
    if (code === undefined) {
      return null;
    }
    return {hex: toHex(code, this.bytes), width: this.widthOf(code, codePoint)};
  }

  // Unicode → the code this font draws it with.
  unicodeMap(): Map<number, number> {
    return this.unicodeToCode;
  }

  covers(codePoints: number[]): number {
    return codePoints.filter(cp => this.unicodeToCode.has(cp)).length;
  }

  fontObject(): PDFObject {
    return this.ref;
  }
}

// One of the bundled fonts, embedded into the document the first time it is used.
export class FallbackFontEncoder implements CharEncoder {
  readonly substitute = true;
  private ref: PDFObject | null = null;

  constructor(readonly key: string, readonly label: string, private readonly font: Font, private readonly doc: PDFDocument,
              private readonly hebrewScale = 1) {}

  // Whether text extraction reported `name` for text drawn with this font. The built-in fonts go in under
  // their standard names and come back under their real ones (Times-Roman → NimbusRoman-Regular).
  drew(name: string): boolean {
    // Exact names only: a subset like ABCDEF+Helvetica-Bold is the producer's own font, not this one.
    const own = this.font.getName();
    return name === own || name === BUILT_IN_REAL_NAMES[own];
  }

  // Whether this is the bundled font picked to match the original family (Arimo for Arial and Helvetica,
  // Tinos and Frank Ruhl Libre for Times), so characters it fills in blend in and need no warning.
  standsInFor(originalName: string): boolean {
    if (this.key.startsWith('local:')) {
      return this.key === `local:${fontKey(originalName)}`;
    }
    if (this.key.startsWith('fallback:Arimo')) {
      return /Arial|Helvetica|Arimo|Liberation ?Sans/i.test(originalName);
    }
    if (this.key.startsWith('fallback:Tinos') || this.key.startsWith('fallback:FrankRuhlLibre')) {
      return /Times|Tinos|Liberation ?Serif/i.test(originalName);
    }
    return false;
  }

  encode(codePoint: number): GlyphCode | null {
    const gid = this.font.encodeCharacter(codePoint);
    if (gid <= 0) {
      return null;
    }
    const scale = this.hebrewScale !== 1 && isHebrewCodePoint(codePoint) ? this.hebrewScale : undefined;
    return {hex: toHex(gid, 2), width: this.font.advanceGlyph(gid, 0) * 1000, scale};
  }

  fontObject(): PDFObject {
    if (!this.ref) {
      this.ref = this.doc.addFont(this.font);
    }
    return this.ref;
  }
}

const BASE14_BY_FAMILY: Record<FontFamily, [string, string, string, string]> = {
  sans: ['Helvetica', 'Helvetica-Bold', 'Helvetica-Oblique', 'Helvetica-BoldOblique'],
  serif: ['Times-Roman', 'Times-Bold', 'Times-Italic', 'Times-BoldItalic'],
  mono: ['Courier', 'Courier-Bold', 'Courier-Oblique', 'Courier-BoldOblique'],
};

const BUILT_IN_REAL_NAMES: Record<string, string> = {
  'Helvetica': 'NimbusSans-Regular', 'Helvetica-Bold': 'NimbusSans-Bold',
  'Helvetica-Oblique': 'NimbusSans-Italic', 'Helvetica-BoldOblique': 'NimbusSans-BoldItalic',
  'Times-Roman': 'NimbusRoman-Regular', 'Times-Bold': 'NimbusRoman-Bold',
  'Times-Italic': 'NimbusRoman-Italic', 'Times-BoldItalic': 'NimbusRoman-BoldItalic',
  'Courier': 'NimbusMonoPS-Regular', 'Courier-Bold': 'NimbusMonoPS-Bold',
  'Courier-Oblique': 'NimbusMonoPS-Italic', 'Courier-BoldOblique': 'NimbusMonoPS-BoldItalic',
};

const BASE14_LABELS: Record<FontFamily, string> = {sans: 'Sans', serif: 'Serif', mono: 'Mono'};

// Bundled look-alikes, fetched on first use: Tinos matches Times New Roman and Arimo matches Arial glyph for
// glyph in Latin (same widths). Their Hebrew doesn't match: Hebrew serif comes from Frank Ruhl Libre, closest
// to Times New Roman's Hebrew, and Hebrew sans from Arimo, drawn smaller (HEBREW_SCALE) to match the widths of
// the Times New Roman and Arial Hebrew letters they stand in for.
function fileFor(choice: FontChoice): string {
  const family = choice.family === 'serif' ? 'Tinos' : 'Arimo';
  const style = choice.bold && choice.italic ? 'BoldItalic' : choice.bold ? 'Bold' : choice.italic ? 'Italic' : 'Regular';
  return `${family}-${style}.ttf`;
}

export function stripSubsetTag(name: string): string {
  return name.replace(/^[A-Z]{6}\+/, '');
}

export type Script = 'latin' | 'hebrew' | 'japanese';

export function isJapaneseCodePoint(cp: number): boolean {
  return (cp >= 0x3000 && cp <= 0x30ff) || (cp >= 0x31f0 && cp <= 0x31ff) || (cp >= 0x3400 && cp <= 0x4dbf)
    || (cp >= 0x4e00 && cp <= 0x9fff) || (cp >= 0xf900 && cp <= 0xfaff) || (cp >= 0xff00 && cp <= 0xffef);
}

export function scriptOf(cp: number): Script {
  if (isHebrewCodePoint(cp)) {
    return 'hebrew';
  }
  return isJapaneseCodePoint(cp) ? 'japanese' : 'latin';
}

// Noto Sans JP and Noto Serif JP, cut to Regular and Bold from Google's variable fonts.
function japaneseFileFor(choice: FontChoice): string {
  return `Noto${choice.family === 'serif' ? 'Serif' : 'Sans'}JP-${choice.bold ? 'Bold' : 'Regular'}.ttf`;
}

function fileForScript(script: Script, choice: FontChoice): string {
  if (script === 'hebrew') {
    return hebrewFileFor(choice);
  }
  return script === 'japanese' ? japaneseFileFor(choice) : fileFor(choice);
}

function hebrewFileFor(choice: FontChoice): string {
  if (choice.family === 'serif') {
    return `FrankRuhlLibre-${choice.bold ? 'Bold' : 'Regular'}.ttf`;
  }
  return `Arimo-${choice.bold ? 'Bold' : 'Regular'}.ttf`;
}

// Width of Times New Roman's / Arial's Hebrew alphabet over the substitute's, measured.
const HEBREW_SCALE: Record<string, number> = {
  'FrankRuhlLibre-Regular.ttf': 0.945, 'FrankRuhlLibre-Bold.ttf': 0.976,
  'Arimo-Regular.ttf': 0.918, 'Arimo-Bold.ttf': 0.897,
};

const FILE_LABELS: Record<string, string> = {
  Tinos: 'Tinos (Times New Roman look-alike)',
  Arimo: 'Arimo (Arial look-alike)',
  FrankRuhlLibre: 'Frank Ruhl Libre (Hebrew serif)',
  NotoSansJP: 'Noto Sans JP',
  NotoSerifJP: 'Noto Serif JP',
};

export interface FallbackNeed {
  choice: FontChoice;
  script: Script;
}

export interface FallbackCandidate {
  key: string;
  label: string;
  font: Font;
  hebrewScale: number;
}

export function isHebrewCodePoint(cp: number): boolean {
  return (cp >= 0x0590 && cp <= 0x05ff) || (cp >= 0xfb1d && cp <= 0xfb4f);
}

// The bundled fonts: the look-alikes (fetched when an edit needs them), then MuPDF's built-in Nimbus fonts.
export class FallbackFonts {
  private readonly fonts = new Map<string, Font>();
  // Fonts installed on the user's computer, handed over by the page, by fontKey().
  private readonly local = new Map<string, Font>();

  constructor(private readonly loadFontFile: (name: string) => Promise<ArrayBuffer>) {}

  addLocal(pdfFontName: string, font: Font): void {
    this.local.set(fontKey(pdfFontName), font);
  }

  hasLocal(pdfFontName: string): boolean {
    return this.local.has(fontKey(pdfFontName));
  }

  async prepare(needs: FallbackNeed[]): Promise<void> {
    for (const need of needs) {
      const file = fileForScript(need.script, need.choice);
      if (!this.fonts.has(file)) {
        const data = await this.loadFontFile(file);
        this.fonts.set(file, new (mupdf().Font)(file.replace('.ttf', ''), new Uint8Array(data)));
      }
    }
  }

  private entry(file: string, scaled: boolean): FallbackCandidate | null {
    const font = this.fonts.get(file);
    if (!font) {
      return null;
    }
    return {key: `fallback:${file}`, label: FILE_LABELS[file.split('-')[0]], font, hebrewScale: scaled ? (HEBREW_SCALE[file] ?? 1) : 1};
  }

  // The fonts to try for a character the original can't draw, best match first: the same font installed on
  // this computer, then the bundled look-alike for its script, then MuPDF's built-in fonts.
  candidates(codePoint: number, choice: FontChoice, originalName: string | null): FallbackCandidate[] {
    const result: FallbackCandidate[] = [];
    const installed = originalName ? this.local.get(fontKey(originalName)) : undefined;
    if (installed && originalName) {
      result.push({key: `local:${fontKey(originalName)}`, label: `${stripSubsetTag(originalName)} (this computer)`, font: installed, hebrewScale: 1});
    }
    const script = scriptOf(codePoint);
    if (script === 'hebrew') {
      const hebrew = this.entry(hebrewFileFor(choice), true);
      if (hebrew) {
        result.push(hebrew);
      }
    } else if (script === 'japanese') {
      const japanese = this.entry(japaneseFileFor(choice), false);
      if (japanese) {
        result.push(japanese);
      }
    } else if (choice.family !== 'mono') {
      const latin = this.entry(fileFor(choice), false);
      if (latin) {
        result.push(latin);
      }
    }
    const variant = (choice.bold ? 1 : 0) + (choice.italic ? 2 : 0);
    const name = BASE14_BY_FAMILY[choice.family][variant];
    let font = this.fonts.get(name);
    if (!font) {
      font = new (mupdf().Font)(name);
      this.fonts.set(name, font);
    }
    const style = [choice.bold ? 'Bold' : '', choice.italic ? 'Italic' : ''].filter(Boolean).join(' ');
    result.push({key: `fallback:${name}`, label: `${BASE14_LABELS[choice.family]}${style ? ' ' + style : ''}`, font, hebrewScale: 1});
    return result;
  }

  // For MuPDF's own text layout (form field appearances), which asks for fonts by script. Only fonts
  // already loaded can be handed over: the hook is synchronous.
  fontForScript(script: string, bold: boolean): Font | null {
    if (script === 'Hebrew') {
      return this.fonts.get(hebrewFileFor({family: 'sans', bold, italic: false}))
        ?? this.fonts.get(hebrewFileFor({family: 'sans', bold: false, italic: false})) ?? null;
    }
    if (script === 'Han' || script === 'Hiragana' || script === 'Katakana') {
      return this.fonts.get(japaneseFileFor({family: 'sans', bold, italic: false}))
        ?? this.fonts.get(japaneseFileFor({family: 'sans', bold: false, italic: false})) ?? null;
    }
    return null;
  }
}
