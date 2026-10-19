# Yanay Tevet — Design System

The authoritative spec for how every screen in `yanay-tevet-web` looks. Read it before writing UI. The tokens
live in `yanay-tevet-web/src/styles.css` (light in `@theme`, dark under `.dark`, app accents under
`[data-app]`); the shared classes in `src/assets/styles/{buttons,forms,surfaces}.css`; the shared components
in `src/app/common/components/page/`. `design/` holds the audit and the roadmap of what is not done yet.

## 1. Principles

- **A calm base, one accent per app.** Warm neutral surfaces, thin hairlines, soft shadows. Each sub-app has
  one accent colour that marks where you are and what you can act on. The hub itself (home, login, settings,
  admin, legal pages) is blue.
- **Colour comes only from tokens.** No hex, no `rgba()`, no stock Tailwind colour (`text-red-500`,
  `bg-emerald-50`) in a template or component: those have no dark value. The only exceptions are things
  that are deliberately theme-independent — image overlays, the always-dark login, the genre-trainer canvas,
  confetti.
- **Both themes, both sizes, every change.** Each change is checked in light and dark and at phone (375px)
  and desktop width. Neither is the "real" one.
- **Shared pieces over copies.** A page header, an empty state, a loading line, a dialog — each has one
  implementation. A page that needs a variant extends the shared piece; it doesn't fork a copy.
- **Quiet until it counts.** Secondary actions are neutral; one primary (accent) action per view; destructive
  actions turn red only on hover, focus and in the confirmation that commits them.

## 2. Colour

### Surfaces, text, lines

| Token (Tailwind class) | Light | Dark | Use |
|---|---|---|---|
| `bg-layer-1` | `#f6f5f4` | `#1a1917` | Page background |
| `bg-layer-2` | `#ffffff` | `#31302e` | Cards, panels, dialogs, inputs |
| `bg-layer-3` | `#eeece9` | `#3d3c3a` | Inner surfaces: neutral chips, wells, the drawer's theme button |
| `bg-layer-4` | `#e0ddd8` | `#4a4845` | Stronger fills: progress tracks, empty slots |
| `bg-layer-overlay` | black 5% | white 8% | Hover / pressed wash on any surface |
| `text-writing` | black 95% | white 95% | Primary text, titles |
| `text-writing-minor` | `#615d59` | `#a39e98` | Secondary text, subtitles, labels, idle icons |
| `text-writing-least` | `#a39e98` | `#77736d` | Placeholders, disabled text, decorative separators |
| `border-line` / `divide-line` | black 10% | white 10% | The hairline: cards, dividers, header bars |
| `border-line-subtle` / `divide-line-subtle` | black 6% | white 6% | Row dividers inside a card, form footers |

There is one text ladder (`writing`, `writing-minor`, `writing-least`); the old aliases `primary-500`,
`secondary-400`, `muted-300` are gone. Hairlines are always 1px `line` or `line-subtle` — never
`border-black/10`, never `border-[rgba(…)]`, and never a bare `border` without a colour (in Tailwind v4 it
takes the text colour).

### The accent

| Token | Use |
|---|---|
| `bg-accent`, `text-accent`, `border-accent` | Primary buttons, links, selected state, checkbox fill, active tab, focus ring |
| `bg-accent-hover` | Hover on an accent fill |
| `bg-accent-soft` | Tinted backgrounds: the app chip, selected rows/pills, accent chips |
| `text-on-accent` | Text and icons on an accent fill — white in light, near-black in dark |

The accent is a variable, not a colour: `AppAccentService` writes the current app's key to
`<html data-app="…">` on every navigation, and `styles.css` maps each key to its pair of colours. Dialogs and
menus render in the CDK overlay under `<body>`, so they inherit it too. Any element can borrow another app's
accent with `data-app` — the home tiles and the nav drawer do, so each app's icon shows in its own colour —
and shared chrome inside an app (the top bar's Sign in) sets `data-app="hub"` to stay blue.

Native checkboxes and radios take the accent through `accent-color`; nothing else needs per-app code.

### App accents

Every pair passes WCAG AA: white text on the light fill, near-black text on the dark fill, and the accent as
text on the page and card backgrounds. The registry is `src/app/shared/apps/hub-apps.ts`.

| App (`data-app`) | Icon | Light | Dark |
|---|---|---|---|
| Hub (no key, or `hub`): home, login, settings, admin, legal | — | `#0068c4` | `#62aef0` |
| Task management (`tasks`) | `bootstrapCheck2Square` | `#0068c4` | `#62aef0` |
| Shopping lists (`shopping`) | `bootstrapCart3` | `#2b7a2b` | `#6fcf63` |
| Special dates (`dates`) | `bootstrapCake2` | `#c2255c` | `#f783ac` |
| Dream diary (`dreams`) | `bootstrapMoonStars` | `#7048c8` | `#b39cf5` |
| Workout plan (`workout`) | `bootstrapHeartPulse` | `#c2410c` | `#ff8f5a` |
| Itinerary lists (`itinerary`) | `bootstrapLuggage` | `#0e7c86` | `#4cc9d3` |
| Home Sweet Home, apartment hunt, villa, renters CRM (`home`) | `bootstrapHouseHeart` | `#8a5a2b` | `#d9a46c` |
| Japanese (`japanese`) | `bootstrapTranslate` | `#3b4fb8` | `#98a6ff` |
| Genre trainer (`genre`) | `bootstrapHeadphones` | `#a3238f` | `#ee82dc` |
| My dashboard (`dashboard`) | `bootstrapSpeedometer2` | `#4d5a6a` | `#aab6c4` |

A new app gets a key, an icon and a pair in the same style (light fill ≥ 4.5:1 against white, dark fill
≥ 4.5:1 against `#141413`), and an entry in `hub-apps.ts`.

### Status

| Token | Light | Dark | Use |
|---|---|---|---|
| `danger`, `danger-soft`, `on-danger` | `#c9281e` | `#ff7a7a` | Errors, destructive confirmation, overdue |
| `warning`, `warning-soft` | `#a35600` | `#f0b04a` | Attention, needs-buying, due soon |
| `success`, `success-soft` | `#1a7f37` | `#56c271` | Done, correct answer, healthy status |
| `info`, `info-soft` | `#0068c4` | `#62aef0` | Neutral information that must not change colour per app |

`*-soft` is the colour at 14% over whatever is behind it, for banners and chips: `bg-danger-soft text-danger`.
Status colours never stand in for the accent, and the accent never signals status.

## 3. Typography

The system UI stack (Tailwind's default `--font-sans`: SF Pro on Apple devices, Segoe UI on Windows, Roboto
on Android) — no webfont to load, and it is what each phone reads best. Lining numerals; `tabular-nums` for
anything that updates in place (times, counts, prices). Text sizes are **roles**, defined in `@theme` with their own line height and
tracking — use the role, never `text-[13px]`:

| Class | Size / line height / tracking | Use |
|---|---|---|
| `text-hero` | 40 / 1.1 / −1px | Marketing and legal page titles only |
| `text-display` | 28 / 1.15 / −0.6px | Big numbers, the logged-in home greeting |
| `text-title` | 22 / 1.25 / −0.4px | Page titles (via `<app-page-header>`) |
| `text-heading` | 20 / 1.3 / −0.25px | Long-form section headings (legal pages) |
| `text-section` | 18 / 1.35 / −0.2px | Dialog titles, section titles inside a page |
| `text-lead` | 16 / 1.5 | Intro paragraphs, card titles on wide cards, inputs |
| `text-ui` | 15 / 1.45 | Nav items, list item titles, card titles |
| `text-body` | 14 / 1.5 | Body copy, buttons, form values |
| `text-meta` | 13 / 1.45 | Subtitles, descriptions, secondary lines |
| `text-caption` | 12 / 1.4 | Chips, timestamps, helper text |
| `text-label` | 11 / 1.35 | Eyebrow labels (with `.eyebrow`), counters |

- **Weights:** 400 reading, 500 interactive and labels, 600 emphasis and buttons, 700 titles. Nothing lighter.
- **`.eyebrow`** is the small uppercase label above a group: `text-label`, 600, `uppercase`, 0.08em,
  `text-writing-minor`. One class, not five spellings of it.
- Tailwind's numeric sizes (`text-sm`, `text-xl`, `text-4xl`) remain only for **icon and glyph sizing**
  (`<ng-icon class="text-xl">`, a 72px kanji) — never for text.

## 4. Space, shape, depth

- **Spacing** follows Tailwind's 4px scale; between stacked cards `gap-3`, between page sections `mb-6`. Card
  padding has three tiers: `p-4` for content cards (list items, tiles, panels, the rows of a list);
  `p-5 sm:p-6` for cards that hold a form or a settings section, and for the focal content block of a detail page;
  `p-6 sm:p-8` for a single card centred on an otherwise empty page (join a calendar, connect Claude, contact).
  A card that only frames a list of rows has no padding and lets the rows pad themselves.
- **Page width** — two containers, both with `px-4 py-6 sm:px-6`:
  - `.page-narrow` (`max-w-3xl`): lists, details, forms, settings, dialogs-as-pages.
  - `.page-wide` (`max-w-5xl`): tables and grids (apartment hunt, renters CRM, Japanese, dashboard).
  A sub-nav bar uses the same container class as the content under it, so their edges line up.
- **Radius:** `rounded` (4px) inputs; `rounded-md` (6px) buttons, icon buttons, small chips-as-buttons;
  `rounded-xl` (12px) cards and dialogs; `rounded-full` pills, avatars, dots. No `rounded-[Npx]`.
- **Depth:** `shadow-1` cards, `shadow-2` raised/hovered cards and dropdowns, `shadow-3` dialogs. Dark mode
  redefines all three. Cards always pair the shadow with a `line` border.

## 5. Components

### Page header — `<app-page-header>`
Every app page starts with it: the app chip (the current app's icon on `bg-accent-soft`, in `text-accent`),
the title (`text-title` 700), an optional one-line subtitle (`text-meta text-writing-minor`), and the page's
actions projected on the right. Below `sm` the actions wrap under the title. `[icon]` overrides the app icon
for a sub-page; `dir="auto"` on title and subtitle handles Hebrew names.

```html
<app-page-header title="Projects" subtitle="4 projects · 12 open tasks">
  <button class="btn btn-primary" (click)="create()"><ng-icon [svg]="featherPlus"/> New project</button>
</app-page-header>
```

### Empty, loading and error states
- `<app-empty-state title="…" text="…">` — a card with the app chip, a title and one line of text, and an
  optional projected call to action. An empty state invites ("Add your first item"), it doesn't apologise.
- `<app-loading-state label="Loading projects"/>` — one muted line with a spinner, centred, never a card.
- `<app-error-state text="…" [backUrl]="…" backLabel="…"/>` — when a page's resource fails to load.

### Buttons — `buttons.css`
| Class | Look | Use |
|---|---|---|
| `btn` + `btn-primary` | Accent fill, `on-accent` text | The one main action of a view |
| `btn` + `btn-secondary` (or bare `btn`) | Neutral wash | Everything else, Cancel |
| `btn` + `btn-ghost` | Transparent, wash on hover | Toolbar text actions in a header card |
| `btn` + `btn-danger` | Danger fill, `on-danger` text | Only the confirm button of a destructive dialog |
| `btn-sm` | Smaller padding, `text-meta` | Inline row actions |
| `icon-btn` | 32px hit area, `writing-minor` → `writing` on hover, wash | Icon-only actions; always with `aria-label` |
| `icon-btn icon-btn-danger` | As above, turns `danger` on hover/focus | Trash icons |

All buttons share the focus ring: 2px `accent` outline, 2px offset, on `:focus-visible`. Disabled is 40%
opacity and no pointer — prefer leaving a button enabled and explaining on click.

### Chips — `surfaces.css`
`chip` is the neutral pill (`bg-layer-3`, `text-writing-minor`, `text-caption` 500, `px-2 py-0.5`,
`rounded-full`). Tinted variants: `chip-accent`, `chip-success`, `chip-warning`, `chip-danger`, `chip-info`
(the `*-soft` background with the matching text). A chip that is a filter toggle is a `<button class="chip">`
with `chip-selected` when on.

### Inputs — `forms.css`
`main-input` (a `bg-layer-2` field, `line` border, 16px text so iOS doesn't zoom, accent border + soft ring on
focus), `input-label` above it (`text-meta` 500 `writing-minor`), helper or error text below in `text-caption`
(`text-danger` for errors). No `<label>`, no unstyled native inputs.

### Cards — `surfaces.css`
`card` (`bg-layer-2`, `line` border, `rounded-xl`, `shadow-1`). A whole-card link or button adds
`card-interactive` (hover `shadow-2`, focus ring, pointer) and must be an `<a>` or `<button>`, not a
`<div (click)>`. Rows inside a card are separated with `divide-y divide-line-subtle`.

### Tabs
`<app-tabs-group>` with `<app-tab name label>` children for in-page tabs: real buttons with `role="tab"`, the
current tab in a query param (so it survives a reload and can be linked), and `(tabChange)` for a page that
loads a tab's data on first view. Its scroll arrows work in both directions. `<app-sub-nav>` is for an app's
section links (Japanese, Home Sweet Home). Both mark the active item with a 2px `accent` underline and
`text-writing`; idle items are `text-writing-minor`.

### Checkboxes
`<app-checkbox-mark [checked] [size]>` is the one checkbox look — a 20px box (16px with `size="sm"`) that fills
with the accent and shows a tick. It is only the visual: wrap it in a `<button type="button">` that carries
`aria-pressed` (or `role="checkbox"` + `aria-checked`), a hit area of at least 32px, and `group/check` so the
box outline turns accent on hover. Native checkboxes take the accent through `accent-color` and are fine in
dense forms.

### Icons
`@ng-icons` only, and one glyph per action everywhere: edit `featherEdit`, delete `featherTrash2`, add
`featherPlus`, more `featherMoreHorizontal`, close and clear `featherX`, disclosure and paging
`featherChevronRight` / `Down` / `Left` / `Up`. App icons come from `hub-apps.ts`.

### Dialogs
Every dialog's root is `.dialog-container` (`bg-layer-2`, `line` border, `rounded-xl`, `shadow-3`, `p-5
sm:p-6`), its title `text-section` 700, its actions a right-aligned row (`.dialog-buttons-container`) with
Cancel (`btn-secondary`) before the main action. The confirmation dialog takes `danger: true` for destructive
actions — its confirm button becomes `btn-danger` — and `dir` for Hebrew text.

### Navigation drawer
Each app row carries its icon in a small chip in the app's own accent (`data-app` on the row); sub-items
are indented under a `line` rule. The active row gets `bg-layer-overlay` and `text-writing` 600.

## 6. States

- **Hover:** a wash (`bg-layer-overlay`) on neutral things; `bg-accent-hover` on accent fills; cards lift
  to `shadow-2`. Never scale on hover.
- **Pressed:** `scale(0.97)` on buttons only.
- **Focus:** `:focus-visible` gets the 2px accent ring everywhere (global rule in `styles.css`); inputs use
  their own border + soft ring instead.
- **Selected:** `bg-accent-soft` + `text-accent` (rows, pills), or the accent fill for a segmented control.
- **Touch:** anything tappable is at least 32px, ideally 44px on phone rows. Actions never depend on hover
  being available.

## 7. Destructive actions

A trash icon or Delete button is neutral at rest (`icon-btn icon-btn-danger`, or `btn-secondary`) and turns
`danger` on hover and focus. It always opens the confirmation dialog with `danger: true`, whose confirm
button is the only solid red in the app. No red text buttons at rest, no rows full of red icons.

## 8. Right-to-left

Hebrew pages set `dir="rtl"` on their root and use logical utilities (`ps-`, `pe-`, `ms-`, `me-`, `start-`,
`end-`, `text-start`). User-entered names get `dir="auto"`. Shared components (page header, empty state,
confirmation dialog) take or inherit `dir`, so a Hebrew page never shows an LTR dialog.

## 9. Do and don't

| Do | Don't |
|---|---|
| `bg-accent text-on-accent` | `bg-notion-blue text-white`, `bg-[#0075de]` |
| `text-danger`, `bg-danger-soft` | `text-red-500`, `bg-red-50 text-red-700` |
| `border-line`, `divide-line-subtle` | `border-black/10`, `border-[rgba(0,0,0,0.06)]` |
| `text-meta`, `text-title` | `text-[13px]`, `text-[22px]` |
| `.eyebrow` | `text-[11px] font-semibold uppercase tracking-wide` |
| `<app-page-header>`, `<app-empty-state>` | A hand-built title row or emoji empty card |
| `icon-btn icon-btn-danger` + confirm with `danger: true` | A red trash icon at rest, a blue "Delete" confirm |
| `<a class="card card-interactive">` | `<div class="card cursor-pointer" (click)>` |
| An app's icon from `hub-apps.ts` | Emoji as app icons |
