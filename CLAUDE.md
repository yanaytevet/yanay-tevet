# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Keep this file up to date.** When you discover new patterns, conventions, or rules, add them here.

---

## Project Overview

Full-stack monorepo: **Angular 21** frontend + **Django 5** backend, real-time via Django Channels/WebSockets.

```
yanay-tevet/
├── yanay-tevet-web/          # Angular 21 frontend
├── yanay_tevet_backend/      # Django backend
├── deploy/                   # Docker, nginx, scripts
└── package.json              # Root monorepo scripts
```

---

## Skills

Before starting any significant task, load the relevant skill:
- `/frontend` — Angular conventions, syntax rules, styling, dialogs, patterns
- `/backend` — Django conventions, simple_api framework, models, serializers, patterns

---

## Common Commands

### Root
```bash
npm run build:web          # Build frontend (dev)
npm run build:web:prod     # Build frontend (prod)
npm run check:backend      # Compile-check Python code
npm run check              # Full check: prod build + backend compile
```

### Frontend
```bash
cd yanay-tevet-web
npm run start              # Dev server
npm run build:prod         # Production build
npm run create-api         # Regenerate API clients from backend OpenAPI spec
```

### Backend
```bash
# Scripts must be run from deploy/dev_scripts/ (they use relative paths)
cd deploy/dev_scripts
bash run_backend.sh
bash run_manage.sh migrate
bash run_manage.sh makemigrations
```

---

## API Client Generation Workflow

After changing backend models or endpoints:

1. Run migrations: `bash run_manage.sh makemigrations && bash run_manage.sh migrate`
2. Start the backend server
3. Regenerate frontend clients: `cd yanay-tevet-web && npm run create-api`

`create-api` fetches live OpenAPI specs from `http://localhost:8000` — if the backend is not running it will fail and delete existing generated files.

**NEVER write frontend API call functions by hand.** All API functions in `src/generated-files/` are auto-generated. Import them directly.

---

## Design System

**Always read `DESIGN.md` before writing any UI code.** It is the authoritative reference.

---

## Hard Rules (Always Active)

- **No custom SVG icons** — always use `@ng-icons` with the `[svg]="iconVar"` pattern (see frontend skill for details).
- **No getters or value-computing methods called from templates** — use `readonly` properties or `computed()` signals. For parameterised lookups, use a computed record: `computed(() => Object.fromEntries(items().map(i => [i.id, i.id === active()])))` then index in the template.
- **No `getattr`/`setattr` in Python** — use explicit `if`/`elif` or `match`/`case`.
- **Always import at the top of Python files** — no string type annotations, no lazy imports inside methods.
- **Always run migrations after model changes** — the backend won't start with unapplied migrations.
- **No `@property` in Django models** — use regular methods instead.
- **Permission checks belong in checker classes, not inline in views.** Use existing `PermissionsChecker` subclasses (e.g. `AdminPermissionsChecker`, `LoginPermissionChecker`) via `await Checker().async_raise_exception_if_not_valid(user)`. If no checker fits, add one under `<app>/permissions_checkers/`. Never write inline `if not user.is_admin(): raise ...` in a view.
- **Business logic belongs in managers, not in views.** Views are thin: parse input → call permission checker → call a manager → return the output schema. Network calls, DB writes, multi-step computation, third-party API calls — all go in `<app>/managers/<name>_manager.py`. See `dream_diary/managers/dream_diary_entry_manager.py` for the pattern.
- **When adding a new app, link to it from the home page** (`src/app/home/home.component.html`) and from the left nav drawer (`src/app/layout/app-navigation-left-drawer/app-navigation-left-drawer.component.html`). Both the logged-in and logged-out home variants need a card if the app is public. The home page is the front door — apps without a tile there are invisible to users.
