import type {Font, PDFDocument, PDFObject} from 'mupdf';
import {mupdf} from './mupdf-runtime';
import {FontChoice, FontFamily} from './pdf-engine.types';

export interface GlyphCode {
  hex: string;
  // Advance in thousandths of the font size, as in a PDF /Widths array.
  width: number;
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

  static fromFontObject(ref: PDFObject): ExistingFontEncoder | null {
    const dict = ref.resolve();
    const subtype = dict.get('Subtype').isName() ? dict.get('Subtype').asName() : '';
    const baseFont = dict.get('BaseFont').isName() ? dict.get('BaseFont').asName() : '';
    const key = `existing:${ref.isIndirect() ? ref.asIndirect() : baseFont}`;
    const toUnicode = dict.get('ToUnicode');

    if (subtype === 'Type0') {
      const encoding = dict.get('Encoding');
      if (!encoding.isName() || !['Identity-H', 'Identity-V'].includes(encoding.asName()) || !toUnicode.isStream()) {
        return null;
      }
      const cmap = parseToUnicodeCMap(toUnicode.readStream().asString(), 2);
      const descendant = dict.get('DescendantFonts').get(0).resolve();
      const {widths, defaultWidth} = cidWidths(descendant);
      return new ExistingFontEncoder(key, baseFont, ref, 2, ExistingFontEncoder.invert(cmap.codeToUnicode),
        code => widths.get(code) ?? defaultWidth);
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

  constructor(readonly key: string, readonly label: string, private readonly font: Font, private readonly doc: PDFDocument) {}

  // Whether text extraction reported `name` for text drawn with this font. The built-in fonts go in under
  // their standard names and come back under their real ones (Times-Roman → NimbusRoman-Regular).
  drew(name: string): boolean {
    // Exact names only: a subset like ABCDEF+Helvetica-Bold is the producer's own font, not this one.
    const own = this.font.getName();
    return name === own || name === BUILT_IN_REAL_NAMES[own];
  }

  encode(codePoint: number): GlyphCode | null {
    const gid = this.font.encodeCharacter(codePoint);
    if (gid <= 0) {
      return null;
    }
    return {hex: toHex(gid, 2), width: this.font.advanceGlyph(gid, 0) * 1000};
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
// glyph (same widths), Hebrew included. Mono text has no look-alike of its own and borrows Arimo's Hebrew.
function fileFor(choice: FontChoice): string {
  const family = choice.family === 'serif' ? 'Tinos' : 'Arimo';
  const style = choice.bold && choice.italic ? 'BoldItalic' : choice.bold ? 'Bold' : choice.italic ? 'Italic' : 'Regular';
  return `${family}-${style}.ttf`;
}

const FILE_LABELS: Record<string, string> = {Tinos: 'Tinos (Times New Roman look-alike)', Arimo: 'Arimo (Arial look-alike)'};

export function isHebrewCodePoint(cp: number): boolean {
  return (cp >= 0x0590 && cp <= 0x05ff) || (cp >= 0xfb1d && cp <= 0xfb4f);
}

// The bundled fonts: Tinos and Arimo (fetched when an edit needs them), then MuPDF's built-in Nimbus fonts.
export class FallbackFonts {
  private readonly fonts = new Map<string, Font>();

  constructor(private readonly loadFontFile: (name: string) => Promise<ArrayBuffer>) {}

  async prepare(choices: FontChoice[]): Promise<void> {
    for (const choice of choices) {
      const file = fileFor(choice);
      if (!this.fonts.has(file)) {
        const data = await this.loadFontFile(file);
        this.fonts.set(file, new (mupdf().Font)(file.replace('.ttf', ''), new Uint8Array(data)));
      }
    }
  }

  // The bundled fonts to try for a character, best match first.
  candidates(codePoint: number, choice: FontChoice): {key: string; label: string; font: Font}[] {
    const result: {key: string; label: string; font: Font}[] = [];
    const file = fileFor(choice);
    const lookAlike = this.fonts.get(file);
    const lookAlikeEntry = lookAlike ? {key: `fallback:${file}`, label: FILE_LABELS[file.split('-')[0]], font: lookAlike} : null;
    if (lookAlikeEntry && (choice.family !== 'mono' || isHebrewCodePoint(codePoint))) {
      result.push(lookAlikeEntry);
    }
    const variant = (choice.bold ? 1 : 0) + (choice.italic ? 2 : 0);
    const name = BASE14_BY_FAMILY[choice.family][variant];
    let font = this.fonts.get(name);
    if (!font) {
      font = new (mupdf().Font)(name);
      this.fonts.set(name, font);
    }
    const style = [choice.bold ? 'Bold' : '', choice.italic ? 'Italic' : ''].filter(Boolean).join(' ');
    result.push({key: `fallback:${name}`, label: `${BASE14_LABELS[choice.family]}${style ? ' ' + style : ''}`, font});
    return result;
  }

  // For MuPDF's own text layout (form field appearances), which asks for fonts by script. Only fonts
  // already loaded can be handed over: the hook is synchronous.
  fontForScript(script: string, bold: boolean): Font | null {
    if (script === 'Hebrew') {
      return this.fonts.get(fileFor({family: 'sans', bold, italic: false}))
        ?? this.fonts.get(fileFor({family: 'sans', bold: false, italic: false})) ?? null;
    }
    return null;
  }
}
