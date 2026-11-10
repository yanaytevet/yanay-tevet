// One font, many names: Word writes "Times New Roman,Bold", the font itself says "TimesNewRomanPS-BoldMT",
// and a subset adds "ABCDEF+". Both reduce to "timesnewromanbold".
export function fontKey(name: string): string {
  return name
    .replace(/^[A-Z]{6}\+/, '')
    .replace(/PSMT$|MT$/, '')
    .replace(/PS(?=-|$)/, '')
    .replace(/[\s,_-]/g, '')
    .replace(/regular$/i, '')
    .toLowerCase();
}
