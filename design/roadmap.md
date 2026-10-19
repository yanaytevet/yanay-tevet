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

## Round 2 — roll the shared pieces out to every app

- Genre trainer and dashboard: drop the nested `min-h-screen` shell (double scroll) and the inline letter-spacing.
- Replace the remaining hand-built page headers, empty states, loading lines and error blocks with the
  shared components, app by app (shopping lists, itinerary lists, workout plan, dream diary, special dates,
  Home Sweet Home and its sub-apps, Japanese, genre trainer, dashboard, settings).
- Move every page to `page-narrow` / `page-wide`; align sub-nav bars with their content.
- Switch every trash icon to `icon-btn icon-btn-danger` with an `aria-label` (confirmations already pass `danger: true`).
- Replace the 22 `border-layer-4` hairlines with `border-line`.
- Special dates: in-page tabs onto `app-tabs-group`; calendar palette with dark values.

## Round 3 — consistency details

- One icon per action (edit, delete, add, more) across the apps.
- Clickable `<div>` cards become `<a>`/`<button class="card card-interactive">`.
- One checkbox (`accent-color` native, or one shared component); remove the feather-square and 18px copies.
- Delete the unused shared components and classes listed in the audit.
- Radius and chip-size cleanup: no `rounded-[Npx]`; every chip is `chip` + variant.
