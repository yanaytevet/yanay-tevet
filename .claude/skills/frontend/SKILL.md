---
name: frontend
description: This skill should be used when working on the Angular 20 frontend, creating components, implementing UI features, styling with Tailwind, adding dialogs, or writing Angular TypeScript. Load before any frontend development task in yanay-tevet-web/.
---

# Frontend Development — Angular 20

## Design System

**Read `DESIGN.md` before writing any UI code.** It is the authoritative reference for all colors, typography, spacing, borders, and shadows.

- Colors: warm neutrals only — `#f6f5f4`, `#31302e`, `#615d59`, `#a39e98`. Primary CTA: `#0075de`. Never blue-gray.
- Borders: always `1px solid rgba(0,0,0,0.1)`.
- Radius: 4px buttons/inputs, 12px cards, 9999px pills.
- Shadows: 4–5 layer stacks, individual opacity ≤ 0.05.

**Design handoff:** `design_handoff_tdf/README.md` lists confirmed screens. Only implement confirmed screens. The HTML files are pixel-accurate visual references — recreate in Angular + Tailwind, do not copy HTML.

---

## Critical Rules

### No Getters or Value-Computing Methods in Templates — Strictly Forbidden

Never use `get` accessors, and never call methods that compute values from the template. Both are called on every change detection cycle and cause performance problems.

```typescript
// Bad — never do this
get canDoThing(): boolean { return this.data.x && this.data.y; }
get currentItem() { return this.mySignal()?.value ?? null; }
isItemActive(id: number): boolean { return this.activeId() === id; }  // called in template

// Good — static value
readonly canDoThing = this.data.x && this.data.y;

// Good — derived from signals
readonly currentItem = computed(() => this.mySignal()?.value ?? null);

// Good — parameterised lookup via a computed record/map
readonly itemActive = computed(() => {
  const active = this.activeId();
  return Object.fromEntries(this.items().map(i => [i.id, i.id === active]));
});
// template: [active]="itemActive()[item.id]"
```

---

## Angular 19+ Syntax

- **Signals**: `input<T>()`, `input.required<T>()`, `output<T>()` — no `@Input`/`@Output` decorators
- **DI**: `readonly x = inject(X)` as a class field — never constructor injection, not even for `ElementRef`
- **Control flow**: `@if`/`@else`, `@for ... track`, `@empty` — no `*ngIf`/`*ngFor`
- **Templates**: always `templateUrl`, never inline `template`

---

## Template Rules

- No `<form (ngSubmit)>` — use `<button type="button" (click)="onSubmit()">`
- No `<label>` — use `<span>`
- No browser dialogs (`alert`, `confirm`, `prompt`) — use `DialogService`
- No success notifications for backend operations (only errors or required follow-up)
- No shorthand `if`/`for` without curly braces
- No semantic HTML (`section`, `article`, etc.); no excessive div nesting

---

## Styling

- Tailwind utility classes only — avoid per-component CSS files
- Theme classes only — no direct hex colors, no standard Tailwind color classes:
  - Backgrounds: `bg-layer-1`, `bg-layer-2`
  - Shadows: `shadow-1`, `shadow-2`
  - Text: `text-primary-500`, `text-secondary-400`
- Reusable classes: `btn`, `btn-primary`, `btn-secondary`, `main-input`, `card`

---

## API Calls — Never Hand-Roll

Never write frontend API call functions by hand. All API functions live in `src/generated-files/api/` and are auto-generated. Import generated functions directly in components — no wrapper files, no hand-rolled fetch calls.

After changing any backend endpoint, regenerate (requires backend running):
```bash
cd yanay-tevet-web && npm run create-api
```

---

## Code Comments

- No unnecessary comments — code is self-documenting
- No `TODO` comments — create tickets
- Comments only for complex algorithms or non-obvious workarounds

---

## References

For detailed patterns and examples, consult:
- **[`references/angular-patterns.md`](references/angular-patterns.md)** — Creating new page components, full DialogService API, dialog design rule, reorderable list pattern, icons
