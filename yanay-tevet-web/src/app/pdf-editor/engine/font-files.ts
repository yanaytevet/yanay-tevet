// Just enough of the OpenType file format to use a font installed on the user's computer: find the face with
// a given PostScript name in a collection (.ttc, as Hiragino ships), and honour its embedding licence.

interface Face {
  index: number;
  postscriptName: string;
  fsType: number;
}

function tableOffset(view: DataView, faceOffset: number, tag: string): number | null {
  const count = view.getUint16(faceOffset + 4);
  for (let i = 0; i < count; i++) {
    const record = faceOffset + 12 + i * 16;
    const name = String.fromCharCode(view.getUint8(record), view.getUint8(record + 1), view.getUint8(record + 2), view.getUint8(record + 3));
    if (name === tag) {
      return view.getUint32(record + 8);
    }
  }
  return null;
}

function postscriptNameAt(view: DataView, nameTable: number): string {
  const count = view.getUint16(nameTable + 2);
  const strings = nameTable + view.getUint16(nameTable + 4);
  let mac = '';
  for (let i = 0; i < count; i++) {
    const record = nameTable + 6 + i * 12;
    const platform = view.getUint16(record);
    const nameId = view.getUint16(record + 6);
    if (nameId !== 6) {
      continue;
    }
    const length = view.getUint16(record + 8);
    const offset = strings + view.getUint16(record + 10);
    if (platform === 3 || platform === 0) {
      let value = '';
      for (let k = 0; k + 1 < length; k += 2) {
        value += String.fromCharCode(view.getUint16(offset + k));
      }
      return value;
    }
    if (platform === 1 && !mac) {
      for (let k = 0; k < length; k++) {
        mac += String.fromCharCode(view.getUint8(offset + k));
      }
    }
  }
  return mac;
}

function faces(bytes: Uint8Array): Face[] {
  const view = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
  const offsets = view.getUint32(0) === 0x74746366
    ? Array.from({length: view.getUint32(8)}, (_, i) => view.getUint32(12 + i * 4))
    : [0];
  return offsets.map((faceOffset, index) => {
    const name = tableOffset(view, faceOffset, 'name');
    const os2 = tableOffset(view, faceOffset, 'OS/2');
    return {
      index,
      postscriptName: name === null ? '' : postscriptNameAt(view, name),
      fsType: os2 === null ? 0 : view.getUint16(os2 + 8),
    };
  });
}

// The face to load, or null when the file doesn't hold it or its licence forbids embedding it in a document
// (fsType bit 1, "restricted"; bit 9, bitmap embedding only).
export function fontFace(bytes: Uint8Array, postscriptName: string): number | null {
  try {
    const face = faces(bytes).find(f => f.postscriptName === postscriptName);
    if (!face || (face.fsType & 0x0002) !== 0 || (face.fsType & 0x0200) !== 0) {
      return null;
    }
    return face.index;
  } catch {
    return null;
  }
}
