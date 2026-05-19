# Angular Patterns Reference

## Adding a New Page Component

Follow these steps in order:

1. Create directory `src/app/<name>/` with `.component.ts`, `.component.html`, `.component.css`
2. Create the component (standalone, no base class):
```typescript
import { Component, inject } from '@angular/core';

@Component({
  selector: 'app-your-component',
  standalone: true,
  imports: [],
  templateUrl: './your-component.component.html',
  styleUrl: './your-component.component.css'
})
export class YourComponent {
}
```
3. Add route to `src/app/app.routes.ts` (lazy-loaded with `loadComponent`)
4. Add navigation methods to `src/app/shared/services/routing.service.ts`:
   - `getXxxUrl()` returning `UrlTree`
   - `navigateToXxx()`

---

## DialogService

Always use the most specific dialog method for the data type. Using `getTextFromInputDialog` for a number is wrong — use `getNumberFromInputDialog`.

```typescript
// Notification
this.dialogService.showNotificationDialog({ title: 'Error', text: 'Something failed' });

// Confirmation
const confirmed = await this.dialogService.getBooleanFromConfirmationDialog({
  title: 'Confirm', text: 'Are you sure?', confirmActionName: 'Yes', cancelActionName: 'No'
});

// Text input
const value = await this.dialogService.getTextFromInputDialog({
  title: 'Input', text: 'Enter value:', label: 'Value', defaultValue: '', confirmActionName: 'OK'
});

// Number input — use for any numeric value, never getTextFromInputDialog
const value = await this.dialogService.getNumberFromInputDialog({
  title: 'Set amount', text: 'Enter a number:', label: 'Amount',
  defaultValue: 0, minValue: 0, maxValue: 100, confirmActionName: 'Set'
});
// Returns number | null (null if cancelled)

// Selection (single)
const value = await this.dialogService.getValueFromSelectionDialog({ ... });

// Selection (multiple)
const values = await this.dialogService.getValuesFromMultipleSelectionDialog({ ... });

// Range
const range = await this.dialogService.getRangeFromRangeDialog({ ... });
```

### Dialog Design Rule

Never pass callbacks as inputs to dialog components. Pass the data the dialog needs (e.g. IDs) and inject required services directly inside the dialog. The dialog calls APIs itself.

```typescript
// Bad — callback as input
dialogService.open(MyDialog, { onConfirm: () => this.doSomething() });

// Good — pass IDs, dialog calls the API itself
dialogService.open(MyDialog, { sessionId: 123, imageId: 456 });
```

---

## Reorderable List Pattern

When creating a list of items, always use `app-reorderable-list`:

```html
<div class="flex mb-2">
  <span class="text-writing font-bold">List Title</span>
  @if (canEdit()) {
    <button class="icon-btn ml-4" (click)="openCreateDialog()">
      <ng-icon [svg]="bootstrapPlusCircle"></ng-icon>
    </button>
  }
</div>
<app-reorderable-list
  [items]="listItems()"
  emptyMessage="No items yet"
  [disabled]="!canEdit()"
  (reordered)="onReordered($event)"
></app-reorderable-list>
```

- Title and `+` button always on the same row, `+` immediately after the title (`ml-4`)
- Edit (`bootstrapPencilSquare`) and delete (`featherDelete`) icon buttons on each item
- For items with a `priority` field: use midpoint-priority algorithm in `onReordered` — find the dragged item by max index-distance, compute new priority as midpoint of its new neighbors' priorities, send one PATCH call
- For simple arrays (no backend IDs): map the new item order back to the data array directly

---

## Responsive Grid Patterns

The layout root sets `@container`, so all container-query variants (`@sm:`, `@md:`, `@lg:`) respond to the main content area width — not the viewport.

### Card / config grid (1 → 3 cols, dense flow)
Use for cards containing forms, settings, or structured content. Items fill gaps automatically.
```html
<div class="grid grid-cols-1 @lg:grid-cols-3 @lg:grid-flow-dense gap-4">
  <div class="card-layer-2">…</div>
</div>
```

### Image gallery grid (2 → 3 cols)
Use for square image tiles (images-tab, chapters list, session thumbnails).
```html
<div class="grid grid-cols-2 @lg:grid-cols-3 gap-4">
  …
</div>
```

### Entity gallery (1 → 2 → 3 → 4 cols)
Use `<app-gallery>` for entity cards that include an image + text below. Starts at 1 col on small screens.
```html
<app-gallery>
  @for (item of items; track item.id) {
    <div class="card-layer-2">…</div>
  }
</app-gallery>
```

### Item / clock grid (1 → 2 → 3 cols)
Use for medium-density items like clock cards, list rows with metadata.
```html
<div class="grid grid-cols-1 @md:grid-cols-2 @lg:grid-cols-3 gap-3">
  …
</div>
```

---

## Icons

**Always use `@ng-icons` — never write custom SVGs inline.**

Available sets: `@ng-icons/bootstrap-icons` (preferred), `feather-icons`, `heroicons`, `ionicons`.

Pattern — use `[svg]` binding with a protected class field (no `provideIcons` needed):

```typescript
import {bootstrapGearFill} from '@ng-icons/bootstrap-icons';
import {NgIcon} from '@ng-icons/core';

@Component({ imports: [NgIcon], ... })
export class MyComponent {
  protected readonly bootstrapGearFill = bootstrapGearFill;
}
```

```html
<ng-icon [svg]="bootstrapGearFill" class="text-base text-secondary-400" />
```

Size via Tailwind `text-*`: `text-sm` ≈ 14px, `text-base` ≈ 16px, `text-xl` ≈ 20px.
