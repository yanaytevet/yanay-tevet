// Shared between the PDF worker and the page. Every coordinate is in page space: points, origin at the
// top-left of the page as displayed (the page's /Rotate already applied), y growing downwards.

export type Point = [number, number];
export type Rect = [number, number, number, number];
export type RgbColor = [number, number, number];

export type FontFamily = 'sans' | 'serif' | 'mono';

export interface FontChoice {
  family: FontFamily;
  bold: boolean;
  italic: boolean;
}

export interface TextStyle {
  font: FontChoice;
  size: number;
  color: RgbColor;
}

export interface PageSize {
  width: number;
  height: number;
}

export interface OpenResult {
  needsPassword: boolean;
}

export interface DocState {
  pageCount: number;
  pageSizes: PageSize[];
  canUndo: boolean;
  canRedo: boolean;
}

export interface RenderedPage {
  width: number;
  height: number;
  pixels: ArrayBuffer;
}

export interface TextLineInfo {
  index: number;
  bbox: Rect;
  text: string;
  rtl: boolean;
  horizontal: boolean;
  size: number;
  font: FontChoice;
  fontName: string;
  // The font's name as the PDF has it (with its subset tag); identifies it for webFont().
  pdfFontName: string;
  color: RgbColor;
}

export interface TextWriteResult {
  state: DocState;
  // Bundled fonts used for characters the original font could not draw.
  substitutedFonts: string[];
  // Characters no available font can draw; they were left out.
  missingCharacters: string[];
}

export type MarkupType = 'Highlight' | 'Underline' | 'StrikeOut';

export interface AnnotationInfo {
  index: number;
  type: string;
  rect: Rect;
  contents: string;
  movable: boolean;
}

export type WidgetKind = 'text' | 'checkbox' | 'radio' | 'choice' | 'button' | 'signature';

export interface WidgetInfo {
  index: number;
  kind: WidgetKind;
  name: string;
  rect: Rect;
  value: string;
  checked: boolean;
  options: string[];
  multiline: boolean;
  readOnly: boolean;
}

export type AddTextStyle = {kind: 'custom'; style: TextStyle} | {kind: 'match'; lineIndex: number};

export interface PdfEngineApi {
  open(data: ArrayBuffer): Promise<OpenResult>;
  authenticate(password: string): Promise<boolean>;
  state(): Promise<DocState>;
  render(page: number, scale: number): Promise<RenderedPage>;
  textLines(page: number): Promise<TextLineInfo[]>;
  // The embedded font a line uses, as a font file the browser can load, or null when it can't be.
  webFont(page: number, fontName: string): Promise<ArrayBuffer | null>;
  editLine(page: number, lineIndex: number, expectedText: string, newText: string, fontOverride: FontChoice | null): Promise<TextWriteResult>;
  addText(page: number, anchor: Point, rtl: boolean, text: string, style: AddTextStyle): Promise<TextWriteResult>;
  eraseArea(page: number, rect: Rect): Promise<DocState>;
  annotations(page: number): Promise<AnnotationInfo[]>;
  addMarkup(page: number, type: MarkupType, from: Point, to: Point, color: RgbColor): Promise<DocState | null>;
  addNote(page: number, at: Point, text: string): Promise<DocState>;
  addInk(page: number, strokes: Point[][], color: RgbColor, width: number): Promise<DocState>;
  addImage(page: number, rect: Rect, png: ArrayBuffer): Promise<DocState>;
  moveAnnotation(page: number, index: number, rect: Rect): Promise<DocState>;
  deleteAnnotation(page: number, index: number): Promise<DocState>;
  widgets(page: number): Promise<WidgetInfo[]>;
  setWidgetValue(page: number, index: number, value: string | boolean): Promise<DocState>;
  rotatePage(page: number, degrees: number): Promise<DocState>;
  deletePage(page: number): Promise<DocState>;
  movePage(from: number, to: number): Promise<DocState>;
  insertBlankPage(at: number): Promise<DocState>;
  insertPdf(at: number, data: ArrayBuffer): Promise<DocState>;
  extractPages(pages: number[]): Promise<ArrayBuffer>;
  undo(): Promise<DocState>;
  redo(): Promise<DocState>;
  save(): Promise<ArrayBuffer>;
}

export interface WorkerRequest {
  id: number;
  method: keyof PdfEngineApi;
  args: unknown[];
}

export type WorkerResponse = {id: number; result: unknown} | {id: number; error: string};
