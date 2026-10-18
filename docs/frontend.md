# Frontend conventions

How the Angular code in `yanay-tevet-web/src/app/` is written. Anything visual — palette, type, spacing,
radii, shadows — is `DESIGN.md`. CLAUDE.md's Hard Rules — `@ng-icons` only, no getters or
value-computing methods in templates, generated API clients only, a new app linked from home and the nav
drawer — hold throughout and are not repeated here.

## Components

- Standalone, with `templateUrl` — no inline `template`.
- Dependencies are fields: `readonly dialogService = inject(DialogService)`. No constructor injection in
  a component, directive or service; a component's constructor, when it has one, takes no arguments and
  only sets up effects or subscriptions. Plain classes made with `new` (`PaginatedTableHandler`, the
  debouncers in `common/data/`) take constructor arguments as usual.
- Signal inputs and outputs — `input<T>()`, `input.required<T>()`, `output<T>()` — never `@Input` or
  `@Output`.
- Built-in control flow — `@if`/`@else`, `@for (…; track …)`, `@empty` — never `*ngIf`/`*ngFor`, and
  every `if` and `for` in TypeScript takes braces.
- Comments explain why, not what, and there are no `TODO` comments.

## Styling

Tailwind utilities, plus the shared classes in `src/assets/styles/` — `btn`, `btn-primary`,
`btn-secondary`, `icon-btn` (`buttons.css`), `main-input`, `input-label` (`forms.css`), `card`
(`surfaces.css`). A component `.css` file is only for what utilities cannot express.

`DESIGN.md`'s palette is implemented as theme tokens in `src/styles.css` (`@theme`), and the same file
redefines them under `.dark`. Colour and shadow come from those tokens — `bg-layer-1`/`bg-layer-2`,
`text-writing`, `text-writing-minor`, `text-primary-500`, `text-secondary-400`, `shadow-1`/`shadow-2` —
never from a hex value or a stock Tailwind colour, because only the tokens follow the theme.
`DarkModeService` toggles `.dark` on `<html>` from the switch in the left drawer and remembers it in
`localStorage`.

## Templates

- No `<form (ngSubmit)>`: submit from `<button type="button" (click)="onSubmit()">`.
- No `<label>`: a field's caption is `<span class="input-label">`.
- No semantic elements (`section`, `article`, …), and no more `div` nesting than the layout needs.
- No browser dialogs (`alert`, `confirm`, `prompt`) — `DialogService`.
- No success notification after a backend call. Show errors, or a follow-up the user has to act on.

## Pages and navigation

A page is a lazy route in `app.routes.ts` (`loadComponent`) plus two methods in
`shared/services/routing.service.ts`: `getXxxUrl(): UrlTree` and `navigateToXxx(): Promise<boolean>`.
A template binds `[routerLink]` to a `UrlTree` held in a field or signal, not to a call of the URL
builder — `home.component.html` still calls them directly and is not the model to copy.

API calls are the generated functions, imported from `src/generated-files/<router path>`
(`generated-files/api/task-management`); `create-api` is CLAUDE.md's *API Client Generation Workflow*.

## Dialogs

`DialogService` (`common/dialogs/dialogs.service.ts`) has a method per kind of answer; use the most
specific one — a number comes from `getNumberFromInputDialog`, not from parsing text.

| To get | Method | Resolves to |
|---|---|---|
| nothing — tell the user something | `showNotificationDialog` | `void` |
| yes or no | `getBooleanFromConfirmationDialog` | `boolean` |
| yes, by typing a given phrase | `getBooleanFromTextConfirmationDialog` | `boolean` |
| a number | `getNumberFromInputDialog` | `number \| null` |
| text | `getTextFromInputDialog` | `string \| null` |
| one / several options | `getValueFromSelectionDialog` / `getValuesFromMultipleSelectionDialog` | the value(s), or `null` |
| a range | `getRangeFromRangeDialog` | `RangeDialogOutput \| null` |

`null` means the user cancelled. Each method also takes an optional width in percent (50 by default;
95% on narrow screens).

A dialog of your own extends `BaseDialogComponent<TInput, TOutput>` — its input arrives as `data`, and
`emitClose(result)` answers — and opens with `dialogService.open(Component, data)`. Pass it the ids it
needs, not callbacks: the dialog injects the services it uses and calls the API itself. The one exception
is `ShareDialogComponent` (`common/dialogs/share-dialog/`), the sharing dialog every shared resource
reuses, which takes `listMembers` / `share` / `unshare` from its caller because it serves many APIs;
use it rather than writing another.

## Layout and icons

The main content area is a size container (`@container` in `layout/layout.component.html`), so the
container variants — `@md:`, `@lg:` — follow the content's width rather than the window's and are not
thrown off by the drawer. Prefer them to the viewport ones (`md:`).

Icons come from `@ng-icons` (bootstrap, feather, heroicons, ionicons): import the icon from its set,
expose it as a field, and render it with `[svg]` — no `provideIcons` needed:

```typescript
import {bootstrapGearFill} from '@ng-icons/bootstrap-icons';
import {NgIcon} from '@ng-icons/core';

@Component({imports: [NgIcon], ...})
export class MyComponent {
  protected readonly bootstrapGearFill = bootstrapGearFill;
}
```

```html
<ng-icon [svg]="bootstrapGearFill" class="text-base text-secondary-400" />
```

Size comes from the text size: `text-sm` ≈ 14px, `text-base` ≈ 16px, `text-xl` ≈ 20px.

## New-version refresh

`VersionCheckService` spots a new deploy by comparing the hashed `main-*.js` / `styles-*.css` names this
tab booted from with those in a freshly fetched `/index.html`. It checks on navigation, when the tab
becomes visible again, when the page comes back from the back-forward cache (`pageshow` with `persisted`,
which iPhone Safari fires without a `visibilitychange`), when the device comes back `online`, and every 5
minutes while the tab is visible; a hidden tab doesn't poll. Checks are at least 30 s apart. It is off under
`ng serve` because those names have no hash, so test it on a production build served locally.
`VersionUpdateBannerComponent` offers a refresh and never forces one; below `sm` it is a full-width bar with
44 px touch targets. `ChunkLoadErrorHandler` reloads automatically when a lazy chunk 404s, at most once a
minute. No build step or `version.json` is involved.

## Live updates (websocket)

`UserWebsocketsService` keeps one socket per tab to `/ws/socket/` and hands pages
`websocketGroupSubscribe(eventType, additionalInfo, callback)`. A dropped socket reconnects with backoff from
1 s to 30 s, at once when the device comes back `online` or the tab becomes visible, and replays every active
subscription; only `disconnect()` keeps it down. A 30 s client ping keeps idle proxies from closing it. A
subscribe frame carries the access token, so the service asks `AuthenticationService.freshAccessToken()` for
one, which renews it first when it is within a minute of expiring. The server ignores a refused subscription
without answering, so a page waiting on one sees nothing rather than an error.
