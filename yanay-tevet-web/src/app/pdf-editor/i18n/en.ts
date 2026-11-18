import type {EngineErrorCode, MarkupType} from '../engine/pdf-engine.types';
import type {PdfTool} from '../pdf-editor.store';
import type {PluralForms} from '../../shared/i18n/strings';

interface ToolStrings {
  label: string;
  hint: string;
}

// The PDF editor's strings. This file is the contract: every other language's file is typed against it.
// Font names (and the generic Sans/Serif/Mono families) are not translated.
export const en = {
  title: 'PDF Editor',
  subtitle: 'Edit text, fill forms, sign and rearrange pages. Your files never leave this browser.',
  opening: 'Opening the PDF',
  openPdf: 'Open a PDF',
  dropHint: 'Drop it here, or choose a file. It\'s read and edited right here, not uploaded.',
  choosePdf: 'Choose a PDF',
  features: {
    textTitle: 'Real text editing',
    text: 'Change a line in its own font, remove text for good, add text that matches what\'s around it. Hebrew included.',
    formsTitle: 'Forms and signatures',
    forms: 'Fill in form fields, then sign with a drawn or uploaded signature.',
    markupTitle: 'Highlights, notes, drawing',
    markup: 'Mark up the document the way you would on paper.',
    pagesTitle: 'Pages',
    pages: 'Reorder, rotate, delete, add blank pages, merge in another PDF, or save some pages as their own file.',
  },

  toolbar: {
    showPages: 'Show pages',
    pages: 'Pages',
    tools: 'Tools',
    pageOf: 'Page {page} of {count}',
    working: 'Working',
    undo: 'Undo',
    undoTitle: 'Undo (Ctrl+Z)',
    redo: 'Redo',
    redoTitle: 'Redo (Ctrl+Shift+Z)',
    zoomOut: 'Zoom out',
    zoomOutTitle: 'Zoom out (Ctrl/⌘ −, or Ctrl/⌘ + scroll)',
    fitWidthTitle: 'Fit to width (Ctrl/⌘ 0)',
    zoomIn: 'Zoom in',
    zoomInTitle: 'Zoom in (Ctrl/⌘ +, or Ctrl/⌘ + scroll)',
    download: 'Download',
    closeFile: 'Close file',
  },
  tools: {
    select: {
      label: 'Fill & select',
      hint: 'Fill in form fields. Click a note, drawing or signature to move or delete it. Drag text to move it, double-click it to edit it.',
    },
    editText: {
      label: 'Edit text',
      hint: 'Click a line to change or delete it. It keeps its font; characters that font lacks are marked with a warning.',
    },
    move: {
      label: 'Move text',
      hint: 'Drag a line to move it. Drag a box or Shift+click to pick several. Arrow keys nudge (Shift: 10pt).',
    },
    addText: {label: 'Add text', hint: 'Click where the text should start.'},
    erase: {label: 'Erase', hint: 'Drag over text or images to remove them from the file.'},
    markup: {label: 'Highlight', hint: 'Drag across text to mark it.'},
    note: {label: 'Note', hint: 'Click to leave a note.'},
    draw: {label: 'Draw', hint: 'Draw freehand on the page.'},
    sign: {label: 'Sign', hint: 'Drag a box, or click, to place your signature.'},
  } satisfies Record<PdfTool, ToolStrings>,
  options: {
    font: 'Font',
    matchNearby: 'Match nearby text',
    bold: 'Bold',
    italic: 'Italic',
    fontSize: 'Font size',
    textColour: 'Text colour',
    colour: 'Colour',
    colourValue: 'Colour {value}',
    lineWidth: 'Line width',
    widthValue: 'Width {value}',
    yourSignature: 'Your signature',
    changeSignature: 'Change signature',
  },
  markupTypes: {
    Highlight: 'Highlight',
    Underline: 'Underline',
    StrikeOut: 'Strike out',
  } satisfies Record<MarkupType, string>,
  closeDialog: {
    title: 'Close without downloading?',
    text: 'Your changes live only in this tab. Download the PDF first to keep them.',
    confirm: 'Close',
  },

  thumbnails: {
    pages: 'Pages',
    insertPdf: 'Insert another PDF after this page',
    savePages: 'Save pages as a new PDF',
    goToPage: 'Go to page {page}',
    rotateLeft: 'Rotate left',
    rotateRight: 'Rotate right',
    insertBlank: 'Insert a blank page after',
    deletePage: 'Delete page',
    extractText: 'Pick the pages to save. This file stays as it is.',
    pageOption: 'Page {page}',
    savePdf: 'Save PDF',
  },

  signature: {
    title: 'Your signature',
    intro: 'Then drag a box on the page, or click, to place it. It stays on this device only.',
    saved: 'Saved',
    useThis: 'Use this signature',
    forget: 'Forget this signature',
    draw: 'Draw',
    upload: 'Upload an image',
    signHere: 'Sign here',
    clear: 'Clear',
    imageLabel: 'Signature image',
    uploadedAlt: 'Uploaded signature',
    pngTip: 'A PNG with a transparent background looks best.',
    remember: 'Remember it on this device',
    cancel: 'Cancel',
    use: 'Use signature',
  },

  page: {
    editLine: 'Edit line: {text}',
    moveText: 'Move text',
    page: 'Page',
    substitutedMarker: 'Some characters are drawn in {fonts}: the original font doesn\'t have them. Click to pick a font for the line.',
    lineText: 'Line text',
    original: 'Original ({font})',
    deleteLine: 'Delete line',
    cancel: 'Cancel',
    cancelTitle: 'Cancel (Esc)',
    save: 'Save',
    localFontOffer: 'Some of these characters aren\'t in this PDF\'s copy of {fonts}. Use the copy installed on this computer, so they match exactly? Your browser will ask once.',
    substitutionNote: 'The original font lacks some of these characters, so they\'re drawn in {fonts}. To draw the whole line in one font, pick it here.',
    useLookAlike: 'Use a look-alike',
    useMyFonts: 'Use my fonts',
    deleteAnnotation: 'Delete annotation',
    annotationWithText: '{name}: {text}',
    newText: 'New text',
    fontAndSize: '{font} · {size}pt',
    matching: 'Matching {font} · {size}pt',
    draftHelp: 'Enter to place, Shift+Enter for a new line',
    // PDF annotation subtypes; anything else shows its PDF name.
    annotationNames: {
      Stamp: 'Signature',
      Ink: 'Drawing',
      Text: 'Note',
      FreeText: 'Text box',
      Highlight: 'Highlight',
      Underline: 'Underline',
      StrikeOut: 'Strike-out',
      Square: 'Box',
      Circle: 'Circle',
      Line: 'Line',
    },
  },

  dialogs: {
    failedTitle: 'That didn\'t work',
    passwordTitle: 'Password',
    passwordText: 'This PDF is protected. Enter its password to open it.',
    passwordWrong: 'That password is wrong. Try again.',
    passwordLabel: 'Password',
    open: 'Open',
    missingTitle: 'Some characters were left out',
    missingText: 'No available font can draw: {chars}',
    noteTitle: 'Add a note',
    noteText: 'The note shows as a comment icon on the page.',
    noteLabel: 'Note',
    addNote: 'Add note',
    deletePageTitle: 'Delete page {page}?',
    deletePageText: 'You can undo this until you close the file.',
    deletePage: 'Delete page',
  },

  // Names of downloaded files. {name} is the opened file's name without ".pdf".
  files: {
    edited: '{name} (edited).pdf',
    onePage: '{name} (page {page}).pdf',
    pages: {one: '{name} ({count} page).pdf', other: '{name} ({count} pages).pdf'} as PluralForms,
  },

  engineErrors: {
    notAPdf: 'This file is not a PDF.',
    insertedNotAPdf: 'That file is not a PDF.',
    insertedNeedsPassword: 'That PDF is password-protected.',
    lastPage: 'A PDF needs at least one page.',
    pageChanged: 'The page changed; pick the line again.',
    missingGlyphs: 'No font here can draw {chars}, so the text was left as it was. Chinese, Korean and scripts besides Latin, Greek, Cyrillic, Hebrew and Japanese can only be edited with fonts installed on this computer, in Chrome or Edge.',
    fontLoadFailed: 'Could not load the font {name}.',
    engineFailed: 'The PDF editor failed to start. Reload the page and try again.',
  } satisfies Record<EngineErrorCode, string>,
};

export type PdfEditorStrings = typeof en;
