import type {Path, PDFDocument, PDFPage, StrokeState} from 'mupdf';
import {mupdf} from './mupdf-runtime';
import {Rect} from './pdf-engine.types';
import {appendContent, colorOperator} from './text-writer';

// Underlines and strike-throughs. Word and most producers draw them as thin filled rectangles of their own,
// not as part of the text, so a line that is edited or moved has to take them along: stretched to the new
// text, or carried with it.

export interface Decoration {
  // Page space.
  rect: Rect;
  color: number[];
}

// Where a line's text sits, along a horizontal baseline.
export interface TextExtent {
  left: number;
  right: number;
  baseline: number;
  size: number;
}

type Matrix = [number, number, number, number, number, number];

function pathBounds(path: Path, ctm: Matrix): {rect: Rect; points: number} | null {
  const xs: number[] = [];
  const ys: number[] = [];
  let curved = false;
  const add = (x: number, y: number) => {
    xs.push(ctm[0] * x + ctm[2] * y + ctm[4]);
    ys.push(ctm[1] * x + ctm[3] * y + ctm[5]);
  };
  path.walk({
    moveTo: add,
    lineTo: add,
    curveTo: () => {
      curved = true;
    },
    closePath: () => undefined,
  });
  if (curved || xs.length < 2) {
    return null;
  }
  return {rect: [Math.min(...xs), Math.min(...ys), Math.max(...xs), Math.max(...ys)], points: xs.length};
}

// Every thin horizontal bar on the page: a filled rectangle or a stroked straight line.
export function pageBars(page: PDFPage): Decoration[] {
  const bars: Decoration[] = [];
  const keep = (rect: Rect, color: number[]) => {
    const height = rect[3] - rect[1];
    const width = rect[2] - rect[0];
    if (height > 0 && height <= 3 && width >= 3 * height) {
      bars.push({rect, color: [...color]});
    }
  };
  const device = new (mupdf().Device)({
    fillPath(path: Path, _evenOdd: boolean, ctm: Matrix, _colorspace: unknown, color: number[]) {
      const bounds = pathBounds(path, ctm);
      if (bounds && bounds.points <= 5) {
        keep(bounds.rect, color);
      }
    },
    strokePath(path: Path, stroke: StrokeState, ctm: Matrix, _colorspace: unknown, color: number[]) {
      const bounds = pathBounds(path, ctm);
      if (!bounds || bounds.points !== 2 || bounds.rect[3] - bounds.rect[1] > 0.01) {
        return;
      }
      const half = (stroke.getLineWidth() * Math.sqrt(Math.abs(ctm[0] * ctm[3] - ctm[1] * ctm[2]))) / 2;
      keep([bounds.rect[0], bounds.rect[1] - half, bounds.rect[2], bounds.rect[3] + half], color);
    },
  } as never);
  page.run(device, mupdf().Matrix.identity);
  device.close();
  return bars;
}

// The bars that belong to a line: under it (an underline) or through it (a strike-through), and mostly
// within its text.
export function decorationsOf(extent: TextExtent, bars: Decoration[]): Decoration[] {
  return bars.filter(bar => {
    const middle = (bar.rect[1] + bar.rect[3]) / 2;
    const thinEnough = bar.rect[3] - bar.rect[1] <= Math.max(1, 0.15 * extent.size);
    const inBand = middle >= extent.baseline - 0.5 * extent.size && middle <= extent.baseline + 0.3 * extent.size;
    const width = bar.rect[2] - bar.rect[0];
    const overlap = Math.min(bar.rect[2], extent.right) - Math.max(bar.rect[0], extent.left);
    const fits = bar.rect[0] >= extent.left - extent.size && bar.rect[2] <= extent.right + extent.size;
    return thinEnough && inBand && overlap >= 0.6 * width && fits;
  });
}

// Takes a line's bars off the page; nothing else is touched.
export function removeDecorations(page: PDFPage, decorations: Decoration[]): void {
  if (decorations.length === 0) {
    return;
  }
  const m = mupdf().PDFPage;
  for (const d of decorations) {
    const annotation = page.createAnnotation('Redact');
    annotation.setRect([d.rect[0] - 0.25, d.rect[1] - 0.25, d.rect[2] + 0.25, d.rect[3] + 0.25]);
  }
  page.applyRedactions(false, m.REDACT_IMAGE_NONE, m.REDACT_LINE_ART_REMOVE_IF_COVERED, m.REDACT_TEXT_NONE);
}

// Draws a line's bars again for its text's new place: the ends keep their distance from the text's ends, so
// an underline grows and shrinks with the text and moves with it.
export function redrawDecorations(doc: PDFDocument, page: PDFPage, decorations: Decoration[], before: TextExtent, after: TextExtent): void {
  const toUser = mupdf().Matrix.invert(page.getTransform());
  const parts: string[] = [];
  const dy = after.baseline - before.baseline;
  for (const d of decorations) {
    const left = after.left + (d.rect[0] - before.left);
    const right = after.right + (d.rect[2] - before.right);
    if (right - left < d.rect[3] - d.rect[1]) {
      continue;
    }
    const corners = [[left, d.rect[1] + dy], [right, d.rect[3] + dy]].map(([x, y]) => [
      toUser[0] * x + toUser[2] * y + toUser[4],
      toUser[1] * x + toUser[3] * y + toUser[5],
    ]);
    const x = Math.min(corners[0][0], corners[1][0]);
    const y = Math.min(corners[0][1], corners[1][1]);
    const w = Math.abs(corners[1][0] - corners[0][0]);
    const h = Math.abs(corners[1][1] - corners[0][1]);
    parts.push(`${colorOperator(d.color)} ${x.toFixed(3)} ${y.toFixed(3)} ${w.toFixed(3)} ${h.toFixed(3)} re f`);
  }
  if (parts.length > 0) {
    appendContent(doc, page, `q\n${parts.join('\n')}\nQ\n`);
  }
}
