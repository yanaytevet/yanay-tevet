# CLAUDE.md

**This file is an index, not a knowledge base.** It carries what applies to *every* task; everything
else lives in `docs/` and is read only when the task reaches it. Keep it that way. Something learned
about one app or area belongs in that area's file under `docs/` — a line is added *here* only when it
would change how an unrelated task is done, and then only as a line. Every paragraph in this file is
paid for on every task, including the ones that never touch the area it describes.

---

## Project Overview

Full-stack monorepo: **Angular 21** frontend + **Django 5** backend, real-time via Django Channels/WebSockets.

```
yanay-tevet/
├── yanay-tevet-web/          # Angular 21 frontend
├── yanay_tevet_backend/      # Django backend
├── deploy/                   # Local dev stack: Docker Compose files + dev_scripts
└── package.json              # Root monorepo scripts
```

**Pushing to `main` deploys the backend to production** (Railway) whenever `yanay_tevet_backend/` changed —
migrations included. See `docs/deployment.md`.

**Ports are deliberately non-default** so this app runs alongside the other projects on this machine: backend `8001`, frontend `4201`, postgres `5433`, redis `6380`. The Docker Compose project is `yanay_tevet` and the network is `yanay_tevet-network` (the compose files declare it as `common-network` and override its name). Inside the network, services still talk on default ports; only host mappings are offset.

Underneath the apps lives the framework: auth, the `simple_api` view/serializer layer, routing, websockets, email, the design system, and a `blocks` app that is a worked example of the view types. Build features on top of these — don't reinvent them.

---

## Where the details live

Each file below is the authoritative account of its area. Read the one that covers the task **before**
starting it.

| Working on | Read first |
|---|---|
| Angular — components, templates, styling, dialogs, icons, navigation | `docs/frontend.md` |
| Django — app layout, views, permissions, serializers, models, background work | `docs/backend.md` |
| Any UI at all | `DESIGN.md` (see **Design System** below) |
| The Claude connector — OAuth server, MCP tools, ngrok in dev | `docs/mcp-server.md` |
| The new-version banner and the reload after a missing lazy chunk | `docs/frontend.md`, *New-version refresh* |
| Production — Railway hosting, deploys, env vars, prod shell, DNS | `docs/deployment.md` |

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
npm run start              # Dev server on :4201 (stop yanay_tevet_web first — see below)
npm run build:prod         # Production build
npm run lint               # eslint
npm run create-api         # Regenerate API clients from backend OpenAPI spec
```

### Backend
```bash
# Scripts must be run from deploy/dev_scripts/ (they use relative paths)
cd deploy/dev_scripts
bash start_dev.sh          # postgres + redis (detached)
bash create_backend.sh     # Rebuild the backend image — after a requirements.txt change
bash run_manage.sh migrate
bash run_manage.sh makemigrations
bash run_backend_worker.sh # Celery worker by hand; the stack runs none (docs/backend.md, Background work)
```

### The running app

`docker-compose -f ../dockers/docker-compose-dev-backend.yml up -d` (from `deploy/dev_scripts/`) is the normal
way to run the app: the backend (`yanay_tevet_backend`, :8001) and the Angular dev server (`yanay_tevet_web`,
:4201) run in the background, owned by no terminal or session. Every session starts with a status line from
`deploy/dev_scripts/dev_status.sh` (a SessionStart hook); run it again before checking a change in the running
app, and start or repair the stack with the command it prints rather than asking. Read output with
`docker logs <container>` — build errors from `ng serve` land in `docker logs yanay_tevet_web`.

- The web container keeps its own Linux `node_modules` in a Docker volume and reinstalls when it starts with a
  changed `package-lock.json` — after a dependency change, `docker restart yanay_tevet_web`. The host's
  `node_modules` is still the one `lint`, `build` and `create-api` use.
- `npm run start` needs `yanay_tevet_web` stopped first (`docker stop yanay_tevet_web`) — they share :4201.
- The backend reloads on code changes, but not on a `requirements.txt` change: rebuild with `create_backend.sh`,
  then run the `up -d` command again.
- The infra and app compose files share the project name `yanay_tevet`, so each warns about the other's
  containers as "orphans". **Never pass `--remove-orphans`** — it would remove the database container.
- Don't stop the stack when a task is done; leave it running.

**A UI change is not done until you have looked at it.** Open the page at http://localhost:4201 in the
built-in browser (its sign-in persists between sessions), check what changed in both themes (the dark-mode
switch is in the left drawer) and the console for errors. A clean build says nothing about layout, dark mode
or what a page actually shows.

---

## API Client Generation Workflow

After changing backend models or endpoints:

1. Run migrations: `bash run_manage.sh makemigrations && bash run_manage.sh migrate`
2. Make sure the backend is up (`dev_status.sh`)
3. Regenerate frontend clients: `cd yanay-tevet-web && npm run create-api`

`create-api` reads the router list out of `yanay_tevet_backend/yanay_tevet_backend/urls.py` (the `path(r'…')` entries, `admin/` excluded) and fetches live OpenAPI specs from `http://localhost:8001`. It deletes the generated directories *before* checking that the backend answers, so with the backend down it fails having deleted them. A new router in `urls.py` automatically becomes a new generated client and is wired into `ApiConfigService`.

**NEVER write frontend API call functions by hand.** All API functions in `src/generated-files/` are auto-generated. Import them directly.

---

## Design System

**Always read `DESIGN.md` before writing any UI code.** It is the authoritative reference. Its palette is implemented as theme tokens in `yanay-tevet-web/src/styles.css` (light, and `.dark` overrides) plus the shared classes in `src/assets/styles/{buttons,forms,surfaces}.css`.

---

## Hard Rules (Always Active)

- **No custom SVG icons** — always use `@ng-icons` with the `[svg]="iconVar"` pattern (see `docs/frontend.md`, *Layout and icons*).
- **No getters or value-computing methods called from templates** — use `readonly` properties or `computed()` signals. For parameterised lookups, use a computed record: `computed(() => Object.fromEntries(items().map(i => [i.id, i.id === active()])))` then index in the template.
- **No `getattr`/`setattr` in Python** — use explicit `if`/`elif` or `match`/`case`.
- **Always import at the top of Python files** — no string type annotations, no lazy imports inside methods.
- **Always run migrations after model changes** — the backend won't start with unapplied migrations.
- **No `@property` in Django models** — use regular methods instead.
- **Permission checks belong in checker classes, not inline in views.** Use existing `PermissionsChecker` subclasses (e.g. `AdminPermissionsChecker`, `LoginPermissionChecker`) via `await Checker().async_raise_exception_if_not_valid(user)`. If no checker fits, add one under `<app>/permissions_checkers/`. Never write inline `if not user.is_admin(): raise ...` in a view.
- **Business logic belongs in managers, not in views.** Views are thin: parse input → call permission checker → call a manager → return the output schema. Network calls, DB writes, multi-step computation, third-party API calls — all go in `<app>/managers/<name>_manager.py`. See `dream_diary/managers/dream_diary_entry_manager.py` for the pattern.
- **When adding a new app, link to it from the home page** (`src/app/home/home.component.html`) and from the left nav drawer (`src/app/layout/app-navigation-left-drawer/app-navigation-left-drawer.component.html`). Both the logged-in and logged-out home variants need a card if the app is public. The home page is the front door — apps without a tile there are invisible to users.
- **Never name a Schema field after a type it uses** (e.g. `date: Optional[date] = None`). Python 3.14 evaluates annotations lazily, so the annotation resolves to the field's own default and the OpenAPI type becomes `null`. Use `import datetime` + `datetime.date`.
