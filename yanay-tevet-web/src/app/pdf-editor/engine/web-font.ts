import type {PDFObject} from 'mupdf';

// Turns a font embedded in the PDF into something the browser can load with FontFace, so the edit box shows
// the line in its real font. Only TrueType and OpenType programs: browsers can't load bare CFF or Type 1.
//
// Embedded subsets usually map glyphs by PDF code, not by Unicode, so the font gets a fresh Unicode cmap
// built from the PDF's own /ToUnicode (or simple encoding) and the font's code-to-glyph mapping.

interface Table {
  tag: string;
  data: Uint8Array;
}

function readTables(font: Uint8Array): Table[] | null {
  const view = new DataView(font.buffer, font.byteOffset, font.byteLength);
  const version = view.getUint32(0);
  if (version !== 0x00010000 && version !== 0x74727565 && version !== 0x4f54544f) {
    return null;
  }
  const count = view.getUint16(4);
  const tables: Table[] = [];
  for (let i = 0; i < count; i++) {
    const record = 12 + i * 16;
    const tag = String.fromCharCode(...font.slice(record, record + 4));
    const offset = view.getUint32(record + 8);
    const length = view.getUint32(record + 12);
    if (offset + length > font.length) {
      return null;
    }
    tables.push({tag, data: font.slice(offset, offset + length)});
  }
  return tables;
}

function checksum(data: Uint8Array): number {
  const padded = new Uint8Array(Math.ceil(data.length / 4) * 4);
  padded.set(data);
  const view = new DataView(padded.buffer);
  let sum = 0;
  for (let i = 0; i < padded.length; i += 4) {
    sum = (sum + view.getUint32(i)) >>> 0;
  }
  return sum;
}

function writeFont(version: number, tables: Table[]): Uint8Array {
  const sorted = [...tables].sort((a, b) => (a.tag < b.tag ? -1 : 1));
  const count = sorted.length;
  let offset = 12 + count * 16;
  const offsets = sorted.map(t => {
    const at = offset;
    offset += Math.ceil(t.data.length / 4) * 4;
    return at;
  });
  const out = new Uint8Array(offset);
  const view = new DataView(out.buffer);
  const entrySelector = Math.floor(Math.log2(count));
  const searchRange = 2 ** entrySelector * 16;
  view.setUint32(0, version);
  view.setUint16(4, count);
  view.setUint16(6, searchRange);
  view.setUint16(8, entrySelector);
  view.setUint16(10, count * 16 - searchRange);
  let headOffset = -1;
  sorted.forEach((t, i) => {
    const record = 12 + i * 16;
    for (let k = 0; k < 4; k++) {
      out[record + k] = t.tag.charCodeAt(k);
    }
    if (t.tag === 'head' && t.data.length >= 12) {
      new DataView(t.data.buffer, t.data.byteOffset).setUint32(8, 0);
      headOffset = offsets[i];
    }
    view.setUint32(record + 4, checksum(t.data));
    view.setUint32(record + 8, offsets[i]);
    view.setUint32(record + 12, t.data.length);
    out.set(t.data, offsets[i]);
  });
  if (headOffset >= 0) {
    view.setUint32(headOffset + 8, (0xb1b0afba - checksum(out)) >>> 0);
  }
  return out;
}

// Code → glyph from the font's own cmap: the (3,0) symbol or (1,0) Mac table that simple fonts carry.
function codeToGlyph(cmap: Uint8Array): Map<number, number> {
  const view = new DataView(cmap.buffer, cmap.byteOffset, cmap.byteLength);
  const result = new Map<number, number>();
  const count = view.getUint16(2);
  const records: {platform: number; encoding: number; offset: number}[] = [];
  for (let i = 0; i < count; i++) {
    records.push({platform: view.getUint16(4 + i * 8), encoding: view.getUint16(6 + i * 8), offset: view.getUint32(8 + i * 8)});
  }
  const pick = records.find(r => r.platform === 3 && r.encoding === 0) ?? records.find(r => r.platform === 1 && r.encoding === 0)
    ?? records.find(r => r.platform === 3 && r.encoding === 1);
  if (!pick) {
    return result;
  }
  const at = pick.offset;
  const format = view.getUint16(at);
  if (format === 0) {
    for (let code = 0; code < 256; code++) {
      result.set(code, cmap[at + 6 + code]);
    }
  } else if (format === 6) {
    const first = view.getUint16(at + 6);
    const n = view.getUint16(at + 8);
    for (let i = 0; i < n; i++) {
      result.set(first + i, view.getUint16(at + 10 + i * 2));
    }
  } else if (format === 4) {
    const segments = view.getUint16(at + 6) / 2;
    const ends = at + 14;
    const starts = ends + segments * 2 + 2;
    const deltas = starts + segments * 2;
    const rangeOffsets = deltas + segments * 2;
    for (let s = 0; s < segments; s++) {
      const end = view.getUint16(ends + s * 2);
      const start = view.getUint16(starts + s * 2);
      const delta = view.getInt16(deltas + s * 2);
      const rangeOffset = view.getUint16(rangeOffsets + s * 2);
      for (let code = start; code <= end && code !== 0xffff; code++) {
        let glyph: number;
        if (rangeOffset === 0) {
          glyph = (code + delta) & 0xffff;
        } else {
          const address = rangeOffsets + s * 2 + rangeOffset + (code - start) * 2;
          glyph = address + 2 <= cmap.length ? view.getUint16(address) : 0;
          glyph = glyph ? (glyph + delta) & 0xffff : 0;
        }
        if (glyph) {
          result.set(code, glyph);
        }
      }
    }
  }
  // Symbol fonts often put their codes at 0xF000 + code.
  if (result.size > 0 && [...result.keys()].every(c => c >= 0xf000)) {
    return new Map([...result].map(([code, glyph]) => [code - 0xf000, glyph]));
  }
  return result;
}

// Browsers refuse a TrueType font without an OS/2 table, and macOS leaves it out of the subsets it embeds.
// A minimal one, with the vertical metrics taken from hhea.
function minimalOs2(tables: Table[]): Uint8Array {
  const out = new Uint8Array(86);
  const view = new DataView(out.buffer);
  const hhea = tables.find(t => t.tag === 'hhea');
  const hheaView = hhea && hhea.data.length >= 10 ? new DataView(hhea.data.buffer, hhea.data.byteOffset) : null;
  const ascender = hheaView ? hheaView.getInt16(4) : 800;
  const descender = hheaView ? hheaView.getInt16(6) : -200;
  const lineGap = hheaView ? hheaView.getInt16(8) : 0;
  view.setUint16(0, 1);
  view.setUint16(4, 400);
  view.setUint16(6, 5);
  for (let i = 0; i < 4; i++) {
    out[58 + i] = 0x20;
  }
  view.setUint16(62, 0x40);
  view.setUint16(64, 0x20);
  view.setUint16(66, 0xffff);
  view.setInt16(68, ascender);
  view.setInt16(70, descender);
  view.setInt16(72, lineGap);
  view.setUint16(74, Math.max(0, ascender));
  view.setUint16(76, Math.max(0, -descender));
  view.setUint32(78, 1);
  return out;
}

function buildCmap(unicodeToGlyph: Map<number, number>): Uint8Array {
  const pairs = [...unicodeToGlyph].sort((a, b) => a[0] - b[0]);
  const groups: [number, number, number][] = [];
  for (const [cp, glyph] of pairs) {
    const last = groups[groups.length - 1];
    if (last && cp === last[1] + 1 && glyph === last[2] + (cp - last[0])) {
      last[1] = cp;
    } else {
      groups.push([cp, cp, glyph]);
    }
  }
  const subtableLength = 16 + groups.length * 12;
  const out = new Uint8Array(4 + 8 * 2 + subtableLength);
  const view = new DataView(out.buffer);
  view.setUint16(0, 0);
  view.setUint16(2, 2);
  // Unicode full repertoire (0,4) and Windows UCS-4 (3,10), both pointing at one format 12 table.
  view.setUint16(4, 0);
  view.setUint16(6, 4);
  view.setUint32(8, 20);
  view.setUint16(12, 3);
  view.setUint16(14, 10);
  view.setUint32(16, 20);
  const at = 20;
  view.setUint16(at, 12);
  view.setUint16(at + 2, 0);
  view.setUint32(at + 4, subtableLength);
  view.setUint32(at + 8, 0);
  view.setUint32(at + 12, groups.length);
  groups.forEach(([start, end, glyph], i) => {
    view.setUint32(at + 16 + i * 12, start);
    view.setUint32(at + 20 + i * 12, end);
    view.setUint32(at + 24 + i * 12, glyph);
  });
  return out;
}

// `unicodeToCode` is the inverse of the font's /ToUnicode (or encoding), as ExistingFontEncoder builds it.
export function webFontFromPdfFont(fontDict: PDFObject, unicodeToCode: Map<number, number> | null): Uint8Array | null {
  const dict = fontDict.resolve();
  const type0 = dict.get('Subtype').isName() && dict.get('Subtype').asName() === 'Type0';
  const descendant = type0 ? dict.get('DescendantFonts').get(0).resolve() : dict;
  const descriptor = descendant.get('FontDescriptor');
  if (descriptor.isNull()) {
    return null;
  }
  let program: Uint8Array | null = null;
  const fontFile2 = descriptor.get('FontFile2');
  const fontFile3 = descriptor.get('FontFile3');
  if (fontFile2.isStream()) {
    program = fontFile2.readStream().asUint8Array().slice();
  } else if (fontFile3.isStream() && fontFile3.get('Subtype').isName() && fontFile3.get('Subtype').asName() === 'OpenType') {
    program = fontFile3.readStream().asUint8Array().slice();
  }
  if (!program || program.length < 12) {
    return null;
  }
  const tables = readTables(program);
  if (!tables) {
    return null;
  }
  const extra: Table[] = tables.some(t => t.tag === 'OS/2') ? [] : [{tag: 'OS/2', data: minimalOs2(tables)}];
  if (!unicodeToCode || unicodeToCode.size === 0) {
    return extra.length > 0 ? writeFont(0x00010000, [...tables, ...extra]) : program;
  }
  const version = new DataView(program.buffer).getUint32(0);
  const glyphOf = new Map<number, number>();
  if (type0) {
    const cidToGid = descendant.get('CIDToGIDMap');
    if (cidToGid.isStream()) {
      const map = cidToGid.readStream().asUint8Array();
      for (const [cp, cid] of unicodeToCode) {
        if (cid * 2 + 1 < map.length) {
          glyphOf.set(cp, (map[cid * 2] << 8) | map[cid * 2 + 1]);
        }
      }
    } else {
      for (const [cp, cid] of unicodeToCode) {
        glyphOf.set(cp, cid);
      }
    }
  } else {
    const cmap = tables.find(t => t.tag === 'cmap');
    const codes = cmap ? codeToGlyph(cmap.data) : new Map<number, number>();
    for (const [cp, code] of unicodeToCode) {
      const glyph = codes.get(code);
      if (glyph) {
        glyphOf.set(cp, glyph);
      }
    }
  }
  const sfntVersion = version === 0x74727565 ? 0x00010000 : version;
  if (glyphOf.size === 0) {
    return extra.length > 0 ? writeFont(sfntVersion, [...tables, ...extra]) : program;
  }
  const rest = tables.filter(t => t.tag !== 'cmap');
  return writeFont(sfntVersion, [...rest, ...extra, {tag: 'cmap', data: buildCmap(glyphOf)}]);
}
