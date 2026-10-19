# Design roadmap

Decisions behind the rounds, from the October 2026 planning session:

- A calm base (warm neutrals, hairlines, soft shadows) with **one accent per app**, which also colours that
  app's primary buttons, checkboxes and selection. Login, settings, admin and legal pages stay blue.
- Semantic token names (`accent`, `danger`, `success`, `warning`, `info`, `line`); the `notion-*` names
  and duplicate text aliases are removed, not kept as aliases.
- One shared page header (app chip, title, subtitle, actions on the right); accent-tinted `@ng-icons` app
  icons instead of emoji.
- Named text roles; every arbitrary `text-[Npx]` migrated in one pass.
- Two page widths: `page-narrow` (`max-w-3xl`) and `page-wide` (`max-w-5xl`).
- Destructive actions are quiet until hover; the confirmation is the only solid red.
- Phone and desktop get equal weight at every step.

## Round 1 — foundation + task management

| Step | Status |
|---|---|
| `DESIGN.md` rewritten as this app's own spec; `design/` audit and roadmap | ✅ |
| Tokens: surfaces, text ladder, hairlines, accent + per-app accents, status colours, text roles | ✅ |
| `AppAccentService` + `hub-apps.ts` registry; home tiles and drawer use app icons in their accent | ✅ |
| `buttons.css` pruned to `btn`/`btn-primary`/`btn-secondary`/`btn-ghost`/`btn-danger`/`btn-sm`/`icon-btn`; focus ring; tap targets | ✅ |
| Mechanical migration: `notion-*`, text aliases, arbitrary sizes, hairlines, stock colours | ✅ |
| Shared `app-page-header`, `app-empty-state`, `app-loading-state`, `app-error-state`, `app-sub-nav` | ✅ |
| Confirmation dialog: `danger` and `dir`; one dialog shell | ✅ |
| Task management polish pass (flagship) | ✅ |

## Round 2 — the shared pieces in every app

| Step | Status |
|---|---|
| Every app page on `<app-page-header>` and `page-narrow` / `page-wide`; sub-navs aligned with their content | ✅ |
| Shared empty, loading and error states everywhere; emoji empty states gone | ✅ |
| Detail pages: common actions in the header, rare and destructive ones in a "more" menu | ✅ |
| Trash icons `icon-btn icon-btn-danger` with `aria-label`; hairline `border-layer-4` → `border-line` | ✅ |
| Genre trainer and dashboard: nested full-height shell and inline letter-spacing removed | ✅ |
| Special dates: page structure, calendar palette with dark values | ✅ |
| Special dates in-page tabs onto `app-tabs-group` | ○ — blocked by `tabs-group` (see round 3) |

## Round 3 — consistency details

- `tabs-group`: tabs as real buttons (keyboard), a change output, RTL-aware scroll arrows, no inner padding — then
  move special dates onto it.

- One icon per action (edit, delete, add, more) across the apps.
- Clickable `<div>` cards become `<a>`/`<button class="card card-interactive">`.
- One checkbox (`accent-color` native, or one shared component); remove the feather-square and 18px copies.
- Delete the unused shared components and classes listed in the audit.
- Radius and chip-size cleanup: no `rounded-[Npx]`; every chip is `chip` + variant.
