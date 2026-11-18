// Flags physical-direction styling that breaks the right-to-left layout (docs/frontend.md, Language → Direction):
// Tailwind classes like ml-2 / text-left in templates and margin-left / left: in component CSS. A line that is
// physically fixed on purpose (PDF geometry, chart axes) opts out with an `rtl-ok` comment on the same line.
// Usage: node scripts/check-rtl.mjs [paths...]   (default: src/app). Exits 1 when something is found.
import {readdirSync, readFileSync, statSync} from 'node:fs';
import {join} from 'node:path';

const CLASS_PATTERN = /(?<![\w-])-?(?:m[lr]|p[lr]|border-[lr]|rounded-(?:[lr]|[tb][lr])|(?:left|right)|text-(?:left|right)|scroll-[mp][lr])(?:-[\w./[\]%]+)?(?![\w-])/g;
const CSS_PATTERN = /\b(?:margin|padding|border)-(?:left|right)\b|(?<![\w-])(?:left|right)\s*:|text-align\s*:\s*(?:left|right)|float\s*:\s*(?:left|right)/;
const CLASS_ATTR = /\b(?:class|\[class\.[^\]]+\]|ngClass)="([^"]*)"/g;

function* files(path) {
  if (statSync(path).isDirectory()) {
    for (const entry of readdirSync(path)) {
      // Strings folders hold words like 'left' ("Align left"), not classes.
      if (entry !== 'node_modules' && entry !== 'generated-files' && entry !== 'i18n') {
        yield* files(join(path, entry));
      }
    }
  } else if (/\.(html|css|ts)$/.test(path)) {
    yield path;
  }
}

const roots = process.argv.slice(2).length > 0 ? process.argv.slice(2) : ['src/app'];
let found = 0;
for (const root of roots) {
  for (const file of files(root)) {
    const lines = readFileSync(file, 'utf8').split('\n');
    lines.forEach((line, index) => {
      if (line.includes('rtl-ok')) {
        return;
      }
      const hits = [];
      if (file.endsWith('.css')) {
        if (CSS_PATTERN.test(line)) {
          hits.push(line.trim());
        }
      } else {
        // Templates, and class strings built in TS (template: `...`, class lists in arrays).
        // In TS, only strings that look like class lists (several space-separated tokens).
        const sources = file.endsWith('.html')
          ? [...line.matchAll(CLASS_ATTR)].map(match => match[1])
          : [...line.matchAll(/'([^']*)'/g)].map(match => match[1]).filter(text => /^[\w:./[\]%-]+( [\w:./[\]%-]+)+$/.test(text));
        for (const source of sources) {
          hits.push(...(source.match(CLASS_PATTERN) ?? []));
        }
      }
      if (hits.length > 0) {
        found += hits.length;
        console.log(`${file}:${index + 1}: ${hits.join(' ')}`);
      }
    });
  }
}
if (found > 0) {
  console.log(`\n${found} physical-direction style(s). Use ms-/me-/ps-/pe-/start-/end-/text-start or margin-inline-*, or mark the line rtl-ok.`);
  process.exit(1);
}
