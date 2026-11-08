# PDF editor

`yanay-tevet-web/src/app/pdf-editor/`, route `/pdf-editor`, gated by the `pdf_editor` permission. Everything runs
in the browser: the file is read, edited and saved in a web worker, and nothing is uploaded. The backend only
holds the permission.

## Engine

MuPDF (`mupdf` on npm, AGPL-3.0) compiled to WebAssembly, run in `engine/pdf-editor.worker.ts`. It is **not
bundled**: `angular.json` copies `mupdf.js`, `mupdf-wasm.js` and the 10 MB `mupdf-wasm.wasm` to
`/pdf-editor/mupdf/`, and the worker imports it from there at runtime, because MuPDF finds its `.wasm` next to
its own URL. Engine code takes the module from `engine/mupdf-runtime.ts` instead of importing it; types come
from `import type … from 'mupdf'`.

| File | What it does |
|---|---|
| `engine/pdf-engine.types.ts` | The worker's API (`PdfEngineApi`) and every shape crossing the worker boundary |
| `engine/pdf-engine.ts` | `PdfEngine`: one open document, every operation wrapped in a MuPDF journal operation (undo/redo) |
| `engine/text-lines.ts` | Lines from MuPDF's structured text, in display and reading order, with per-character style |
| `engine/text-writer.ts` | Writes text into the page's content stream; redaction; the font registry |
| `engine/font-encoders.ts` | Drawing with a font the PDF already has (via its `/ToUnicode` or encoding) or a bundled one |
| `engine/bidi.ts` | Display order ↔ reading order for Hebrew/mixed lines (`bidi-js` for UAX #9) |
| `engine/web-font.ts` | The PDF's embedded font as a browser font for the edit boxes (fresh Unicode cmap, OS/2 if missing) |
| `engine/pdf-engine-client.ts` | The page's side: typed `call(method, …args)` over `postMessage` |
| `pdf-editor.store.ts` | Component-level state shared by the editor's pieces; every edit goes through it |

Coordinates everywhere are page space: points, origin top-left of the page as displayed (rotation applied).

### How a line edit works

1. The line comes from structured text; characters are sorted along the baseline (display order), then
   turned into reading order. Each keeps its font, size, colour and its measured advance to the next one.
2. The new text is diffed against the old (longest common subsequence): unchanged characters keep their
   style and original spacing, inserted ones take the style of the character before them.
3. **Fonts are looked up before the redaction**: redacting a line drops fonts nothing draws with any more from
   the page's resources. A font is matched by `BaseFont` == MuPDF's font name, and new characters are encoded
   through the inverse of its `/ToUnicode` (or simple encoding). Subset fonts lack most characters, so any
   character the original can't draw falls back to a bundled font picked by serif/mono/bold/italic, fetched
   from `public/pdf-editor/fonts/` when an edit needs it: Latin from Tinos (serif) or Arimo (sans), which match
   Times New Roman and Arial glyph for glyph; Hebrew from Frank Ruhl Libre (serif) or Arimo (sans), whose
   Hebrew is closest to Times New Roman's and Arial's, drawn at `HEBREW_SCALE` so the widths match (Tinos's
   own Hebrew is a sans design and doesn't blend). Then the Nimbus fonts built into MuPDF (and for mono
   text). The UI marks such
   lines; the user can pick a font for the whole line.
4. The old line is redacted (text only, a band through the middle of the line), and the new glyphs are
   appended as a `q … Q`-wrapped content stream with `TJ` adjustments for the measured spacing.

### Lines and moving

MuPDF starts a new line wherever the producer started a new text object, so one sentence can arrive in
pieces on one baseline. `joinLinePieces` joins pieces on the same baseline that are less than about a word
gap apart (adding a space where the gap has none) and leaves wider gaps alone (table columns). Without it,
a lengthened piece runs over its neighbour, and editing the neighbour then cuts into it.

The Move tool (`PdfEngine.moveLines`) takes every selected line off before writing any back, at the same
anchor plus the offset, in one journal operation. While dragging, the page shows snapshots cut from the
rendered page; they stay until the page has re-rendered, so nothing jumps back. Arrow-key nudges collect
into one move after 700 ms of quiet.

### Things that bit

- **Brackets in RTL text.** MuPDF already mirrors brackets when it extracts right-to-left text, which is right
  for fonts whose `/ToUnicode` labels bracket glyphs by shape (Chrome's PDFs). `EditableLine.labelsByShape`
  records which convention a line's fonts follow (by which reading balances the brackets), and writing follows
  it.
- **`bidi-js`'s `getMirroredCharactersMap` takes `levels.levels`**, not the result object.
- **Hebrew in form fields.** MuPDF lays out a single-line field with non-Latin text one line too low; the
  engine shifts it back (`fixSingleLineAppearance`) and drops `/NeedAppearances` so viewers don't rebuild it.
  The Hebrew font reaches MuPDF's layout through `installLoadFontFunction`, so it must be loaded first.
- **Subsets often have no space glyph** (and MuPDF reports synthetic spaces for gaps), so spaces come from a
  bundled font; they still keep the original gap, or a rewritten line comes out narrower. A moved line keeps
  every original advance.
- **A redaction rewrites the page's content**; image and vector removal is on only for the Erase tool.

## Usage log (development only)

`debug/pdf-editor-log.ts` records what happens in the editor (tool and zoom changes, line clicks, every edit
with the page's lines before and after, undo/redo, page operations, errors, a text box closed because the page
changed) in `localStorage`, capped at 600 events. The toolbar's **Flag** button adds a `flag` event with a
note. The console exposes it as `window.__pdfEditorLog` (`events()`, `last(n)`, `flags()`, `clear()`), so an
agent driving the built-in browser reads it with a JavaScript call. `isDevMode()` gates all of it: production
builds log nothing and show no Flag button.

### The edit box shows the PDF's own font

`PdfEngine.webFont` hands the embedded TrueType/OpenType program to the page, which loads it with `FontFace`
(`PdfEditorStore.webFontFamily`). Embedded subsets map glyphs by PDF code, so `web-font.ts` replaces the cmap
with a Unicode one built from `/ToUnicode` (code = glyph for Identity CID fonts; via the font's own (3,0)/(1,0)
cmap for simple fonts), and adds a minimal `OS/2` table when the subset has none (macOS leaves it out; browsers
refuse a font without one). Bare CFF and Type 1 programs can't load in a browser; those lines fall back to a
generic family. Characters the subset lacks fall back the same way, as they do on the page.

## Not supported

Scanned PDFs (no OCR), paragraph reflow (a line is edited in place; a longer line can run past the margin),
vertical text, Type 3 fonts and CID fonts with a non-Identity encoding (their text falls back to bundled fonts),
scripts other than Latin, Greek, Cyrillic and Hebrew, and certified digital signatures ("Sign" places an image).

## Testing the engine

The engine runs in Node too: bundle a script that calls `setMupdf(await import('mupdf'))` and drives
`PdfEngine` with `npx esbuild <script> --bundle --platform=node --format=esm --external:mupdf`, run it from
`yanay-tevet-web/` so `mupdf` resolves, and render pages to PNG with `page.toPixmap(...).asPNG()` to look at the
result. Headless Chrome's `--print-to-pdf` makes realistic test files (subset fonts, Hebrew).

## License

MuPDF is AGPL-3.0: once the app is public, its source has to be available to its users. The repo is private
for now; opening it is the plan (add an AGPL `LICENSE` then). Tinos, Arimo and Frank Ruhl Libre are OFL (`public/pdf-editor/fonts/*-OFL.txt`).

The bundled fonts go into the document whole (300–580 KB each); Download and Save pages subset fonts on a
copy of the saved file (`subsetCopy`), so the open document keeps full fonts and its undo history.
