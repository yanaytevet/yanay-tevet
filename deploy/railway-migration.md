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
4. **Cutover (~15 min of downtime):**
   1. On the VM: `docker compose stop yanay_tevet_backend` (freezes writes).
   2. On the VM (it's inside the DB firewall): `docker run --rm postgres:18 pg_dump -Fc "<DO yanay_db URL>"`
      piped into `pg_restore --clean --no-owner` against Railway's `DATABASE_PUBLIC_URL`.
   3. Spot-check row counts on both sides.
   4. Railway: add custom domain `api.yanaytevet.com`.
   5. Cloudflare DNS: replace the `api` A record (→ 164.92.130.67) with the CNAME + TXT Railway gives.
      Either grey-cloud it (simplest, Railway's cert) or keep orange and set SSL mode **Full, not
      Full (strict)** for that host via a Configuration Rule (strict breaks Railway's cert issuance).
   6. Delete the DO deploy workflow; push.
5. **Verify** in the live app: Google sign-in, passkey sign-in, a websocket screen, an image upload
   (Cloudinary), an invitation email (Brevo), and the Claude connector (MCP OAuth + one tool call).
6. Delete Postgres's public TCP proxy: `railway tcp-proxy delete <id> --service Postgres --yes`.

**Rollback:** point the DNS record back at the droplet IP and start the container. Anything written on
Railway after cutover is lost, so decide within a day or two.

## Phase 2 — the-dark-forge

Same as Phase 1 with `the_dark_forge_db`, `/etc/the-dark-forge/env/prod.env` (has `ANTHROPIC_API_KEY`)
and `api.thedarkforge.io`. `stage-api.thedarkforge.io` in `environment.stage.ts` has no DNS record — ignore.

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
