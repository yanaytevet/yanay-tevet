# DigitalOcean → Railway migration

Runbook for moving yanay-tevet, the-dark-forge off DigitalOcean.
Delete this file once the move is done.

## Today (DigitalOcean, fra1) — ~$45/mo at a full month

| Resource | What runs there | $/mo |
|---|---|---|
| `the-dark-forge-db` managed PG 17, 1 GB + 10 GiB | **shared**: `yanay_db` and `the_dark_forge_db` | 15.15 |
| `the-dark-forge-vm` 2 GB | dark-forge backend + redis + nginx (Cloudflare origin cert) | 12 |
| `yanay-tevet-vm` 1 GB | yanay-tevet backend + redis + nginx | 6 |
| `foundry-vtt` 2 GB | Foundry VTT (created 2026-09-19) | 12 |

Deploys: GitHub Action SSHes into the VM and runs `~/reload.sh` (git pull, build, compose up).
Secrets live on each VM in `/etc/<app>/env/prod.env`. DB firewall only trusts the two app droplets.
No Celery worker or beat runs in prod. Media is on Cloudinary, so nothing on disk needs moving.

## Target (Railway, workspace "yanaytevet's Projects", same as landx)

One Railway project per app, each with three services:

- `backend` — built from the repo's Dockerfile, root dir `<app>_backend/`, auto-deploy on push to `main`,
  watch path `<app>_backend/**` so frontend-only commits don't rebuild it.
- `Postgres` — Railway template, PG 17 (match the source), volume-backed.
- `Redis` — Railway template.

nginx and the Cloudflare origin cert go away: Railway terminates TLS, whitenoise (already in
`MIDDLEWARE`) serves `/static/`, websockets are supported and exempt from Railway's idle limits.

**Estimated cost:** ~$6/mo per app always-on (backend ~0.3 GB, Postgres ~0.15 GB, Redis tiny), so
~$12/mo for both, on top of the Hobby fee you already pay for landx. Serverless sleep on the
backends could cut it further — see *Sleep* below. Check the real number on Railway's usage page after a week.

## Phase 0 — Code changes (both repos, same diff)

1. ✅ **Redis password.** Railway Redis requires auth. `REDIS_PASSWORD` now feeds `CHANNEL_LAYERS`
   (host entry is a dict) and `CACHEOPS_REDIS`. Unset in dev, so dev is unchanged.
2. ✅ **Log directory.** `LOGGING` has a `RotatingFileHandler` in `/var/log/<app>/`, which today exists only
   because of a compose volume. Add `RUN mkdir -p /var/log/<app>` to the Dockerfile, or startup crashes.
   Railway keeps stdout for 7 days (Hobby); the file log and log viewer reset on every deploy.
3. ✅ **Port.** uvicorn binds `${PORT:-8000}`. Proxy headers stay untrusted, as behind nginx today
   (nothing calls `build_absolute_uri`; MCP uses `MCP_PUBLIC_BASE_URL`).
4. **Deploy workflow.** Delete `.github/workflows/deploy-backend.yml` *at cutover*, not before
   (pushing to main still deploys to DO until then).
5. Optional: `railway.json` per repo to pin build/watch paths and a healthcheck in code instead of the dashboard.

## Phase 1 — yanay-tevet (pilot)

1. ✅ Project `yanay-tevet` (region `ams`) with Postgres **18**, Redis and `backend`. Deployed with
   `railway up` from the local tree for now; switch to GitHub autodeploy at cutover with
   `railway service source connect --repo yanaytevet/yanay-tevet --branch main --service backend`
   (+ root dir `yanay_tevet_backend`, watch path `yanay_tevet_backend/**`).
   Test URL: https://backend-production-e6ff.up.railway.app
2. ✅ Copied `/etc/yanay-tevet/env/prod.env` (SSH as `deployer`, key `~/.ssh/yanay-tevet-deployer`) into
   the backend's variables, minus the DB/Redis keys. Wire infra with
   reference variables instead of literals: `DATABASE_HOST=${{Postgres.PGHOST}}`,
   `DATABASE_PASSWORD=${{Postgres.PGPASSWORD}}`, `REDIS_HOST=${{Redis.REDISHOST}}`,
   `REDIS_PASSWORD=${{Redis.REDISPASSWORD}}`, etc. Keep `MCP_PUBLIC_BASE_URL=https://api.yanaytevet.com`.
3. ✅ Booted and smoke-tested (admin, static, OpenAPI, OAuth metadata, websocket, channel layer, cacheops).
   ✅ Trial copy from the VM: 48 tables / 1,669 rows matched, 344 KB dump, 12 s.
   Postgres has a temporary public TCP proxy (`autorack.proxy.rlwy.net:57408`) for the copy.
4. ✅ **Cutover done 2026-10-10** (~20 min of 502s, all of it waiting on DNS):
   stopped `yanay_tevet_backend` on the VM → final copy (48 tables / 1,669 rows matched) →
   custom domain `api.yanaytevet.com` → Cloudflare: `api` CNAME `9d6jcjvh.up.railway.app` (DNS only)
   + TXT `_railway-verify.api` → cert valid → pushed `0e17316` (drops the DO deploy workflow) →
   service connected to GitHub (root `/yanay_tevet_backend`, watch `/yanay_tevet_backend/**`,
   healthcheck `/admin/login/`). First GitHub deploy built from the Dockerfile and went live.
5. ✅ Verified on the live domain: admin, static, OpenAPI, CORS from yanaytevet.com, websocket,
   Claude connector (existing OAuth token, real data). ⏳ You: Google sign-in and passkey sign-in.
6. ✅ Postgres TCP proxy deleted.

The old VM still runs nginx + redis with the backend container stopped — that's the rollback.

**Rollback:** point the DNS record back at the droplet IP and start the container. Anything written on
Railway after cutover is lost, so decide within a day or two.

## Phase 2 — the-dark-forge ✅ (2026-10-10)

Same steps; ~3 min of downtime. Railway project `the-dark-forge` (ams), test URL
https://backend-production-d129.up.railway.app. Final copy: 55 tables / 1,070 rows matched.
`api` CNAME `4xyh1u6y.up.railway.app` (DNS only) + TXT `_railway-verify.api`. Pushed `9c6e714`
(drops the DO deploy workflow); the repo moved to `yanaytevet/the-dark-forge` and the local remote
now points there. GitHub deploy live; Dark Forge connector verified with real data.
Prod env has no OpenAI/Anthropic keys — Railway matches.

## Now: both app droplets are powered off (still billed), the shared DB is idle

## Out of scope (for now): Foundry VTT

`foundry-vtt` stays on DO. If it moves later: `felddy/foundryvtt` image with a volume on `/data`;
Hobby volumes cap at **5 GB**.

## Phase 3 — Decommission DO (after a week of quiet)

1. Snapshot the two app droplets (cheap insurance), then destroy them — **powered-off droplets still
   bill**. Leave `foundry-vtt` alone.
2. Destroy the managed DB cluster **last**: it is shared, so only after both apps are moved.
3. Delete the `VM_HOST` / `VM_USER` / `VM_SSH_KEY` repo secrets and the Cloudflare origin certs.

## Sleep (serverless) — test, don't assume

Railway sleeps a service after ~5–10 min with **no outbound packets**; the first request after that
takes a cold start and may get a 502. Any open DB/Redis connection keeps it awake. Enable it on a
backend only after cutover, watch whether it actually sleeps, and try a cold sign-in. Keep Postgres
and Redis awake. The ~$6/mo-per-app estimate assumes no sleep.

## Who does what

- **Me (CLI):** code changes, Railway projects/services/variables (`railway` is logged in), dump/restore,
  verification, DO teardown via `doctl`.
- **You:** approve SSH into the VMs and each destructive DO step; the Cloudflare DNS edits (two records
  per app in the dashboard — or create a DNS-edit API token scoped to the two zones and I'll do it).
