import type {PDFDocument, PDFObject} from 'mupdf';
import {parseToUnicodeCMap} from './font-encoders';
import {unicodeCmapOf} from './web-font';

// Some producers write a /ToUnicode that doesn't describe the font (macOS re-saving a Word PDF labelled
// David's "2" glyph as "1" and its space as "ב", and left most glyphs out). Everything here reads and writes
// text through /ToUnicode, so such a font reads as garbage and typing "1" draws a "2". For an Identity CID
// TrueType font the code is the glyph, and the embedded program's own Unicode cmap says what each glyph is:
// when the /ToUnicode contradicts it, or is empty, it is rebuilt from that cmap.

// Reading the same bracket glyph as its mirror is a convention (right-to-left text), not a broken map.
const MIRRORS = new Map([['(', ')'], [')', '('], ['[', ']'], [']', '['], ['{', '}'], ['}', '{'], ['<', '>'], ['>', '<']]);

function isUsableCodePoint(cp: number): boolean {
  return cp >= 0x20 && !(cp >= 0x7f && cp <= 0x9f) && !(cp >= 0xe000 && cp <= 0xf8ff) && cp < 0xf0000;
}

function utf16Hex(text: string): string {
  let hex = '';
  for (let i = 0; i < text.length; i++) {
    hex += text.charCodeAt(i).toString(16).padStart(4, '0');
  }
  return hex;
}

function fontProgram(descendant: PDFObject): Uint8Array | null {
  const descriptor = descendant.get('FontDescriptor');
  if (descriptor.isNull()) {
    return null;
  }
  const fontFile2 = descriptor.get('FontFile2');
  const fontFile3 = descriptor.get('FontFile3');
  if (fontFile2.isStream()) {
    return fontFile2.readStream().asUint8Array().slice();
  }
  if (fontFile3.isStream() && fontFile3.get('Subtype').isName() && fontFile3.get('Subtype').asName() === 'OpenType') {
    return fontFile3.readStream().asUint8Array().slice();
  }
  return null;
}

// Glyph → CID: identity, or the inverse of a /CIDToGIDMap stream.
function glyphToCid(descendant: PDFObject): ((glyph: number) => number | undefined) | null {
  const map = descendant.get('CIDToGIDMap');
  if (map.isNull() || (map.isName() && map.asName() === 'Identity')) {
    return glyph => glyph;
  }
  if (!map.isStream()) {
    return null;
  }
  const bytes = map.readStream().asUint8Array();
  const inverse = new Map<number, number>();
  for (let cid = 0; cid * 2 + 1 < bytes.length; cid++) {
    const glyph = (bytes[cid * 2] << 8) | bytes[cid * 2 + 1];
    if (glyph && !inverse.has(glyph)) {
      inverse.set(glyph, cid);
    }
  }
  return glyph => inverse.get(glyph);
}

// CID → the character its glyph is, from the font program's Unicode cmap. A glyph several characters map to
// takes the lowest ordinary one (David maps both U+05E0 and a private-use code to its nun).
function cmapCharacters(descendant: PDFObject): Map<number, number> | null {
  const program = fontProgram(descendant);
  const cmap = program ? unicodeCmapOf(program) : null;
  const toCid = glyphToCid(descendant);
  if (!cmap || !toCid) {
    return null;
  }
  const result = new Map<number, number>();
  for (const [cp, glyph] of [...cmap].sort((a, b) => a[0] - b[0])) {
    const cid = toCid(glyph);
    if (glyph === 0 || cid === undefined || !isUsableCodePoint(cp) || result.has(cid)) {
      continue;
    }
    result.set(cid, cp);
  }
  return result;
}

// Whether the /ToUnicode is wrong about the glyphs it names: it is empty, every entry the cmap can check
// disagrees with it, or at least a fifth do (and more than two).
function isBroken(toUnicode: Map<number, string>, fromCmap: Map<number, number>): boolean {
  if (toUnicode.size === 0) {
    return true;
  }
  let checked = 0;
  let wrong = 0;
  for (const [code, text] of toUnicode) {
    const expected = fromCmap.get(code);
    const chars = Array.from(text);
    if (expected === undefined || chars.length !== 1) {
      continue;
    }
    checked++;
    // Presentation forms (U+FB4F for אל, Arabic U+FExx) are the same text as the letters they decompose to.
    const actual = String.fromCodePoint(expected).normalize('NFKC');
    const said = chars[0].normalize('NFKC');
    if (said !== actual && MIRRORS.get(said) !== actual) {
      wrong++;
    }
  }
  return (wrong > 0 && wrong === checked) || (wrong > 2 && wrong * 5 >= checked);
}

function writeCMap(characters: Map<number, string>): string {
  const entries = [...characters].sort((a, b) => a[0] - b[0]);
  const sections: string[] = [];
  for (let i = 0; i < entries.length; i += 100) {
    const chunk = entries.slice(i, i + 100);
    sections.push(`${chunk.length} beginbfchar\n${chunk.map(([cid, text]) => `<${cid.toString(16).padStart(4, '0')}> <${utf16Hex(text)}>`).join('\n')}\nendbfchar`);
  }
  return [
    '/CIDInit /ProcSet findresource begin',
    '12 dict begin',
    'begincmap',
    '/CIDSystemInfo << /Registry (Adobe) /Ordering (UCS) /Supplement 0 >> def',
    '/CMapName /Adobe-Identity-UCS def',
    '/CMapType 2 def',
    '1 begincodespacerange',
    '<0000> <FFFF>',
    'endcodespacerange',
    ...sections,
    'endcmap',
    'CMapName currentdict /CMap defineresource pop',
    'end',
    'end',
  ].join('\n');
}

// Rebuilds every broken /ToUnicode of an Identity CID font in the document. Runs once the file is open
// (and decrypted), before any page is read and before the journal starts, so it isn't an undoable edit.
// Returns how many fonts were repaired.
export function repairToUnicodeMaps(doc: PDFDocument): number {
  let repaired = 0;
  const count = doc.countObjects();
  for (let num = 1; num < count; num++) {
    try {
      const font = doc.newIndirect(num).resolve();
      if (!font.isDictionary() || !font.get('Type').isName() || font.get('Type').asName() !== 'Font') {
        continue;
      }
      if (!font.get('Subtype').isName() || font.get('Subtype').asName() !== 'Type0') {
        continue;
      }
      const encoding = font.get('Encoding');
      const toUnicode = font.get('ToUnicode');
      if (!encoding.isName() || !['Identity-H', 'Identity-V'].includes(encoding.asName()) || !toUnicode.isStream()) {
        continue;
      }
      const descendant = font.get('DescendantFonts').get(0).resolve();
      const fromCmap = cmapCharacters(descendant);
      if (!fromCmap || fromCmap.size === 0) {
        continue;
      }
      const current = parseToUnicodeCMap(toUnicode.readStream().asString(), 2).codeToUnicode;
      if (!isBroken(current, fromCmap)) {
        continue;
      }
      // Entries for glyphs the cmap doesn't reach (ligatures, alternates) are kept.
      const merged = new Map<number, string>([...current].filter(([code]) => !fromCmap.has(code)));
      for (const [cid, cp] of fromCmap) {
        merged.set(cid, String.fromCodePoint(cp));
      }
      const cmapText = writeCMap(merged);
      font.put('ToUnicode', doc.addStream(new TextEncoder().encode(cmapText), doc.newDictionary()));
      repaired++;
    } catch {
      // A damaged object: leave it as it is.
    }
  }
  return repaired;
}
