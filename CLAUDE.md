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

## MCP Server (Claude Connector)

The `mcp_server` app exposes the platform to Claude as a remote MCP connector (claude.ai, Desktop, mobile, Claude Code), secured by a self-hosted **OAuth 2.1** authorization server. Ported from the-dark-forge, with security fixes.

- **Auth server** (plain async Django views, `mcp_server/oauth/`): `/.well-known/oauth-authorization-server`, `/oauth/authorize|token|register|revoke`. Tokens/codes are stored **hashed**. **PKCE S256 is mandatory**, codes and refresh tokens are single-use (atomic claim), scope is always `MCP_SCOPE`. **Dynamic registration only accepts redirect URIs on `claude.ai`/`claude.com` (https) or loopback** (`config.is_allowed_redirect_uri`) — this blocks phishing via attacker-registered clients; extend the allowlist deliberately if another client must connect.
- **Consent happens in the web app**: `/oauth/authorize` redirects to the frontend `/connect-claude` page (login via `/login?redirect=`), which shows the client name + redirect host (`GET /api/mcp/oauth/client-info/`) and posts to `POST /api/mcp/oauth/approve/` (JWT-authed). Logic lives in `OAuthManager`.
- **Resource server** (FastMCP, `mcp_server/mcp/`): mounted in `asgi.py` (path dispatch for `/mcp` + `/.well-known/oauth-protected-resource/mcp`); session manager started lazily (Daphne dev server emits no ASGI lifespan). **`stateless_http=True`** so autoreloads/restarts don't strand clients on dead sessions.
- **Tools are typed, one per verb** (`mcp/tools/task_tools.py`, `mcp/tools/shopping_list_tools.py`; inputs in `mcp/schemas/`), not a generic `entity_type`+`data: dict` registry — the typed schema is what Claude reads. Keep the server `INSTRUCTIONS` in `mcp/server.py` in sync with the real tool names.
- **Every tool MUST apply the same checks as the web API**: the app-level checker the router applies (`TaskManagementPermissionChecker`, `ShoppingListsPermissionChecker` — MCP bypasses routers, so call it explicitly) plus the object checker (`ProjectMemberPermissionChecker`, `ShoppingListMemberPermissionChecker`). Writes go through the app's managers; outputs use the app's serializers. Annotate tools `READ_ONLY` / `WRITE` / `DESTRUCTIVE`. Batch tools validate every id/permission before the first write. Tools return pydantic schemas (not bare `dict`, which yields no structured output).
- Deliberately **not exposed**: deleting projects/lists and sharing/unsharing (irreversible or visible to other people) — do those in the app.
- **Config**: `mcp_server/config.py` → `get_public_base_url()` = the **backend's** public URL. `MCP_PUBLIC_BASE_URL` env in prod (`https://api.yanaytevet.com`); in dev it auto-discovers the ngrok tunnel (`ngrok http 8001`); cached per process, restart the backend after (re)starting ngrok.
- **Frontend**: Account Settings "Connect to Claude" card (`GET /api/mcp/connection-info/`) with the connector URL + "Add to Claude" deep link.
- Adding another app to MCP: new `mcp/tools/<app>_tools.py` with a `register(mcp)`, call it from `build_mcp_server()`, update `INSTRUCTIONS` and the consent-page copy.
- The `mcp` package is in `requirements.txt`; after changing it the backend **image must be rebuilt**.

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
- **The user runs the backend and frontend servers themselves.** Assume the backend (`localhost:8000`) and frontend dev server are already running — do not start, restart, or offer to start them. Verify changes with build/compile checks (`npm run build:prod`, `npm run check`) instead. When a step genuinely needs a running server (e.g. `npm run create-api` after endpoint changes), state that the user must run it rather than starting the server yourself.
