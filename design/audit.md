# Design audit — October 2026

A sweep of `yanay-tevet-web/src/app` against the design system, before the round-1 rewrite. Counts are from
that sweep. **Status** is updated as rounds land: ✅ fixed, ◐ partly, ○ open. Statuses as of the end of round 1.

At the time, `DESIGN.md` was a verbatim copy of Notion's marketing-site spec ("Get Notion free", trust bars)
inherited from the-dark-forge, so nothing in the repo described this app's own system.

## 1. Colour outside the tokens

| Finding | Count / where | Status |
|---|---|---|
| Hairlines that vanish in dark: `border-[rgba(0,0,0,0.06/0.1)]`, `divide-[rgba]`, `border-black/10` | 48 — every form footer, apartment/renters tables, footer, faq, home, genre trainer | ✅ |
| Three hairline sources at once: `outline-border-1`, `border-layer-4`, arbitrary values | 27 / 23 / 48 — `border-layer-4` (22) still left | ◐ |
| Error text as stock `text-red-500` / `border-red-500` | 19 — common dialogs, special dates, user settings | ✅ |
| Error banners `text-red-700 bg-red-50`: a pastel slab in dark | 5 — japanese ×3, genre trainer, openai credits | ✅ |
| Right/wrong feedback in `emerald-50/300/700`, `rose-50…` | genre-trainer guess and reveal | ✅ |
| Primary blue in three forms: `#0075de` in `.btn-primary`, `bg-[#0075de]` ×7, `bg-notion-blue text-white` ×18 (2.4:1 in dark) | buttons.css, genre trainer, layout, drawer, admin, dream diary | ✅ |
| Japanese status chips in `emerald/amber/sky-100`, duplicated in two files | `node-summary-card.ts`, `japanese-node-detail.ts` | ✅ |
| Special-dates calendar palette `.calendar-color-0..5` has no dark values | `styles.css` | ○ |
| Light-only washes: `hover:bg-black/5`, `from-white`, `text-gray-700` drawer moon, stock `checkbox-input`, `dark:text-blue-400` table filter | genre player, openai card, dream diary, drawer, column filter | ✅ |
| `.card`, `.tooltip-box`, `.dialog-container` copy the light shadow string instead of `var(--shadow-*)` | surfaces.css, dialogs-style.css | ✅ |
| Duplicate text tokens: `primary-500` = `writing`, `secondary-400` = `writing-minor`, `muted-300` ≈ `writing-least` | 198 / 107 / 8 uses | ✅ |
| Missing semantic tokens: danger, success, warning, info, on-accent, hairline | — | ✅ |

## 2. Buttons

| Finding | Status |
|---|---|
| 22 button classes; 15 never used (`indigo/emerald/violet/red/yellow/orange/pink/purple/teal/blue-btn`, `small-btn`, `transparent-btn`, `selected-pill`, `soft-green/red-btn`) | ✅ |
| Duplicates: `btn-primary` = `indigo-btn` = `blue-btn` = `accept-btn`; `btn-secondary` = `cancel-btn` = `.btn` | ✅ |
| No `:focus-visible` on any button | ✅ |
| `icon-btn` has no padding: ~16px tap targets (65 of 66 uses) | ✅ |
| No danger style: trash icons are grey `cancel-btn` or grey `icon-btn`; the confirm dialog's "Delete" is blue — every delete confirmation is now red; `icon-btn-danger` only in task management so far | ◐ |

## 3. Typography

| Finding | Status |
|---|---|
| 546 arbitrary sizes: `text-[13px]` 173, `[14px]` 104, `[11px]` 100, `[12px]` 89, `[15px]` 80, … | ✅ |
| Four page-title styles: 22px (25 pages), 28px (Japanese), `text-4xl` + inline letter-spacing (genre trainer, dashboard), none (dream diary, settings) — sizes are roles now; only task management uses `<app-page-header>` | ◐ |
| Eyebrow labels spelled two ways: `tracking-wide` ×50, `tracking-[0.08em]` ×27 | ✅ |
| Dialog titles: `text-[18px] font-bold` ×12 vs `.dialog-container h2` `text-xl` ×11 | ✅ |

## 4. Page structure

| Finding | Status |
|---|---|
| No shared page header; the same title + subtitle + primary-button block copied into 9 list pages, 4 detail-header variants — `<app-page-header>` exists, used by task management | ◐ |
| Empty state `card p-10 text-center` + emoji copied 13×; Japanese uses a different one — `<app-empty-state>` exists, used by task management | ◐ |
| Loading line copied 19× with 4 variants; error-with-back-button copied 13× — `<app-loading-state>`/`<app-error-state>` exist, used by task management | ◐ |
| Unused shared components (`app-entity-card`, `app-gallery`, `app-main-image-card`, `app-collapsible-section`, `app-reorderable-list`) and classes (`.page`, `.card-layer-2/3`, `.mask-edges`) | ○ |
| Two dialog shells: `.dialog-container` vs `card bg-layer-2 p-5 sm:p-6` (12 dialogs) | ✅ |
| Four tab implementations: `tabs-group`, identical `japanese-nav` and `home-sweet-home-nav`, hand-rolled special-dates tabs — the two navs share `<app-sub-nav>`; special dates still hand-rolled | ◐ |
| Four checkbox implementations: native unstyled, hand-rolled 18px (7×), feather squares, unused `checkbox-input` — native ones take the accent via `accent-color` | ◐ |
| Genre trainer and dashboard nest a `min-h-screen bg-layer-1` shell inside the `h-screen` layout (double scroll) | ○ |
| Dream diary has no header and full-contrast icon buttons | ○ |

## 5. Space, shape, depth

| Finding | Status |
|---|---|
| Page widths: `2xl`, `3xl`, `4xl`, `5xl`, `xl` across apps; sub-nav `5xl` over `4xl` content — `page-narrow`/`page-wide` exist, used by task management and the sub-nav | ◐ |
| Radius: `rounded-full` 94, `rounded-lg` 31, `rounded` 17, `rounded-xl` 14, plus `[5px]` 7, `[8px]` 5, `[10px]` 3, `[4px]` 1; `rounded-pill` (undefined, renders square) 4 — no arbitrary radius left | ◐ |
| Card padding `p-3/4/5/6/8/10`; chip sizes in 5 variants — `chip` classes exist, used by task management | ◐ |
| Clickable-card hover is `shadow-2 → shadow-3` in some apps, `→ shadow-2` in others — `card-interactive` on home and task management | ◐ |

## 6. Other

| Finding | Status |
|---|---|
| Icon sets: feather in 12 apps, bootstrap in layout/genre/japanese/dashboard, heroicons in tabs; edit is `featherEdit` ×17 vs `featherEdit2` ×4, delete `featherTrash2` ×20 vs `featherDelete` ×1 | ○ |
| 8 clickable cards are `<div (click)>` with no role or tabindex — task projects are links now | ◐ |
| `focus:shadow-outline` (no-op in Tailwind v4) and `focus:ring-primary` (colour doesn't exist) — the first removed | ◐ |
| Bare `border` (takes the text colour in v4) on `selectable-box` and the selection-dialog inputs — `selectable-box` fixed | ◐ |
| The confirmation dialog has no `dir`, so Hebrew delete confirmations are LTR | ✅ |
| No per-app identity: emoji on home tiles, text-only drawer | ✅ |
