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
| `engine/font-files.ts`, `engine/font-names.ts` | Installed fonts: the face in a collection, the embedding licence, matching PDF names |
| `engine/decorations.ts` | Underlines and strike-throughs found under a line, carried along when it is edited or moved |
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
   own Hebrew is a sans design and doesn't blend); Japanese from Noto Sans JP or Noto Serif JP (Regular and
   Bold, cut from Google's variable fonts, 5.8 and 8.1 MB each). Then the Nimbus fonts built into MuPDF (and
   for mono text). Ahead of all of them comes the same font installed on the user's computer, when they
   allowed it (see *Fonts on this computer*). The UI marks such
   lines, except where the bundled font is the one made to match the original's family (Arimo for
   Arial/Helvetica, Tinos and Frank Ruhl Libre for Times); the user can pick a font for the whole line.
4. The old line is redacted (text only, a band through the middle of the line), and the new glyphs are
   appended as a `q … Q`-wrapped content stream with `TJ` adjustments for the measured spacing.

### Fonts on this computer

Chrome and Edge's Local Font Access API (`queryLocalFonts`) gives a page the font files installed on the
computer: Times New Roman, Arial and Hiragino are on every Mac, so the characters a PDF's subset lacks come out
exactly right. Before saving an edit, the page asks the engine which of the line's fonts lack some of the new
characters (`localFontsWanted`); if the permission hasn't been decided, the edit box asks first ("Use my fonts"
/ "Use a look-alike", because Chrome only prompts from a click; a decline lasts for the visit), then hands the
matching installed files over (`addLocalFont`). Names are matched by `fontKey()`: Word writes
"Times New Roman,Bold" where the font says "TimesNewRomanPS-BoldMT". `font-files.ts` picks the face out of a
`.ttc` collection and skips fonts whose licence forbids embedding (OS/2 `fsType` restricted or bitmap-only).
Saving subsets them like any other font (an installed Hiragino added 64 KB). Other browsers use the bundled
fonts. The built-in browser of the Claude desktop app denies the permission, so this path is tested in Chrome.

### Japanese

Japanese PDFs from macOS embed Hiragino as CID fonts with no `/ToUnicode`, so their characters can't be looked
up the usual way. MuPDF still reads them (through the font's Adobe-Japan1 character collection), so
`FontRegistry.learned` runs the first pages through a text device and records which code drew each character:
with Identity-H the glyph MuPDF reports is the code in the content stream. Characters already in the subset are
then redrawn in the original font; new ones come from the installed font or Noto JP. Vertical text is not
supported.

### Lines and moving

MuPDF starts a new line wherever the producer started a new text object, so one sentence can arrive in
pieces on one baseline. `joinLinePieces` joins pieces on the same baseline that are less than about a word
gap apart (adding a space where the gap has none) and leaves wider gaps alone (table columns). Without it,
a lengthened piece runs over its neighbour, and editing the neighbour then cuts into it.

The opposite happens too: MuPDF can put text that only shares a baseline into one line (a browser print
header's date at the margin and its title in the middle). `splitAtGaps` cuts a line wherever the ink stops for
more than 1.5 × the font size, before the pieces are joined.

The Move tool (`PdfEngine.moveLines`) takes every selected line off before writing any back, in one journal
operation. A moved line is written glyph for glyph in its display order with every original gap
(`WriteSpec.visualOrder`), not re-run through the bidi algorithm, which can order mixed Hebrew/Latin text
differently from its producer. While dragging, the page shows snapshots cut from the
rendered page; they stay until the page has re-rendered, so nothing jumps back. Arrow-key nudges collect
into one move after 700 ms of quiet.

Fill & select (the cursor tool) shares that line layer, under its form fields and annotations: click text to
select it, drag to move it, double-click to edit it in place without leaving the tool (a click elsewhere
saves the edit).

### Things that bit

- **Reading order must redraw the line.** Text comes out of a PDF in display order; the guessed reading
  order is checked by running the bidi algorithm on it. Keeping a Latin run with its spaces together is tried
  first, then splitting numbers apart: "2,559.00 ₪1" is two runs in RTL text, and read back as one it showed
  in the edit box in a different order than on the page.
- **Brackets in RTL text.** MuPDF already mirrors brackets when it extracts right-to-left text, which is right
  for fonts whose `/ToUnicode` labels bracket glyphs by shape (Chrome's PDFs). `EditableLine.labelsByShape`
  records which convention a line's fonts follow (by which reading balances the brackets), and writing follows
  it.
- **`bidi-js`'s `getMirroredCharactersMap` takes `levels.levels`**, not the result object.
- **Hebrew in form fields.** MuPDF lays out a single-line field with non-Latin text one line too low; the
  engine shifts it back (`fixSingleLineAppearance`) and drops `/NeedAppearances` so viewers don't rebuild it.
  The Hebrew font reaches MuPDF's layout through `installLoadFontFunction`, so it must be loaded first.
- **Subsets often have no space glyph** (and MuPDF reports synthetic spaces for gaps), so spaces come from a
  bundled font; they still keep the original gap, or a rewritten line comes out narrower. An original space
  keeps its gap whatever follows it, a typed space takes the line's median gap, and a moved line keeps every
  original advance.
- **The edit box must open exactly over the line.** The page has an outline, not a border: a border took 2px
  from the box the page image fills, so the image came out smaller than the overlays and they drifted apart
  towards the bottom (2.5pt by the page's foot). The box is placed by the line's `baseline` (font ascent from
  canvas `measureText`), and the PDF's own spacing difference (`textWidth` against the browser's width) is
  spread over its spaces as `word-spacing`, or its characters as `letter-spacing`. Measured on a
  Chrome-printed Hebrew page: both ends within 0.15pt, baseline within half a pixel.
- **Underlines and strike-throughs are separate drawings** (Word draws them as thin filled rectangles).
  `decorations.ts` finds the thin horizontal bars under or through a line's text and, on an edit or a move,
  removes them (a line-art redaction that leaves text alone) and draws them again for the text's new extent:
  the ends keep their distance from the text's ends.
- **Never garbage-collect the open document.** `saveToBuffer('garbage=compact')` renumbers its objects in
  place, and after an edit that lost an image's soft mask: a signature vanished from the download and from
  the open page. `save()` writes the open document plain and compacts only the copy it subsets.
- **Text is never dropped.** If any character of a rewritten line has no font to draw it (Japanese in a
  Hiragino CID font with no `/ToUnicode`, so even its own characters can't be encoded), `writeText` throws and
  the journal operation is abandoned: the edit or move is refused with a message and the page is unchanged.
- **A gap without a space character** (a colon set 3pt from the number after it) moves past characters typed
  into it instead of closing. MuPDF then reads the gap as a space, since the glyphs now follow each other in
  the content stream.
- **A saved edit's box stays until the page re-renders** (`editSavedAt`, read-only and borderless), or the old
  line shows for the moment the worker takes, then jumps to the new one. Deleting a line works the same way.
- **A redaction rewrites the page's content**; image and vector removal is on only for the Erase tool.

Zoom: the toolbar buttons, Ctrl/⌘ + scroll or a trackpad pinch (browsers send it as a Ctrl wheel), zooming
around the pointer, and Ctrl/⌘ +, − and 0 (fit width).

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

Scanned PDFs (no OCR), Chinese and Korean beyond what installed fonts can draw (no bundled font; lines whose
characters no font can draw are refused, not damaged), vertical Japanese, paragraph reflow (a line is edited in place; a longer line can run past the margin),
vertical text, Type 3 fonts and CID fonts with a non-Identity encoding (their text falls back to bundled fonts),
scripts other than Latin, Greek, Cyrillic, Hebrew and Japanese, and certified digital signatures ("Sign" places an image).

## Testing the engine

**The dev server does not rebuild the worker on an engine change**: its incremental rebuild updates the page
code and keeps serving the old `worker-*.js`. After changing anything under `engine/`, `docker restart
yanay_tevet_web`, then reload the page and reopen the file.

The engine runs in Node too: bundle a script that calls `setMupdf(await import('mupdf'))` and drives
`PdfEngine` with `npx esbuild <script> --bundle --platform=node --format=esm --external:mupdf`, run it from
`yanay-tevet-web/` so `mupdf` resolves, and render pages to PNG with `page.toPixmap(...).asPNG()` to look at the
result. Headless Chrome's `--print-to-pdf` makes realistic test files (subset fonts, Hebrew).

## License

MuPDF is AGPL-3.0: once the app is public, its source has to be available to its users. The repo is private
for now; opening it is the plan (add an AGPL `LICENSE` then). Tinos, Arimo and Frank Ruhl Libre are OFL (`public/pdf-editor/fonts/*-OFL.txt`).

The bundled fonts go into the document whole (300–580 KB each); Download and Save pages subset fonts on a
copy of the saved file (`subsetCopy`), so the open document keeps full fonts and its undo history.
