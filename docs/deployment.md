# Production (Railway)

The backend runs on **Railway**: project `yanay-tevet` in the workspace "yanaytevet's Projects", region `ams`
(Amsterdam), with services `backend`, `Postgres` (PG 18) and `Redis`. The frontend is hosted on Cloudflare and
isn't covered here. Moved from DigitalOcean on 2026-10-10.

- **Deploys**: every push to `main` that touches `yanay_tevet_backend/` rebuilds the backend from
  `yanay_tevet_backend/Dockerfile` (service root dir `/yanay_tevet_backend`, watch path
  `/yanay_tevet_backend/**`; other pushes are skipped). A new deployment takes traffic only once `/admin/login/`
  answers (healthcheck), so a crash on boot leaves the previous one serving. Railway's pre-deploy command
  (`/venv/bin/python manage.py migrate`, service setting `deploy.preDeployCommand`) runs on the new image
  before it takes traffic, and a failure stops the deploy, so **migrations reach prod on push** and must be safe
  against live data. Static files are collected into the image at build time; the container's `CMD` starts
  uvicorn and nothing else.
- **CI**: `.github/workflows/ci.yml` runs on every push to `main` and every pull request. Job `web` lints and
  builds the frontend for production; job `backend` fails on a missing migration, runs `manage.py check` and
  the tests against Postgres 17 and Redis 8. Railway's "Wait for CI" (backend service settings, Deploy) holds
  a deploy until the checks pass. The Cloudflare frontend doesn't wait: it builds on every push.
- **Serving**: uvicorn on `$PORT` (pinned to `8000` by a service variable); Railway terminates TLS. Static files
  are served by whitenoise and media lives on Cloudinary, so the container keeps nothing on disk. The
  `/var/log/yanay_tevet/` file log (and the admin log viewer) reset on every deploy;
  `railway logs --service backend` keeps stdout for 7 days.
- **Config**: service variables on `backend`. DB and Redis are reference variables
  (`DATABASE_HOST=${{Postgres.PGHOST}}`, `REDIS_PASSWORD=${{Redis.REDISPASSWORD}}`, …). A new env var read in
  `settings.py` needs its Railway variable before the push that uses it. Set secrets without echoing them:
  `printf %s "$VALUE" | railway variable set KEY --stdin --service backend`.
- **Environment and hosts**: `ENVIRONMENT=prod` is what makes it production; `DEBUG` follows from it (a
  missing `ENVIRONMENT` also means production). `ALLOWED_HOSTS` comes from Railway's own variables:
  `RAILWAY_PUBLIC_DOMAIN` (`api.yanaytevet.com`) plus `healthcheck.railway.app`, the health checker's Host.
  Without that one every healthcheck answers 400 and no deploy goes live. `ALLOWED_ORIGINS` lists the frontend
  origins; CORS and the websocket Origin check both read it, so a new frontend domain goes there.
- **Prod shell**: from the repo root (already linked to the project):
  `railway ssh --service backend -- /venv/bin/python manage.py <command>`.
- **Database**: private only. For a one-off external connection, `railway tcp-proxy create --port 5432
  --service Postgres`, then delete it (`railway tcp-proxy delete <id> --service Postgres --yes`).
- **No Celery** worker or beat runs in prod (`docs/backend.md`, *Background work*). Adding one means another
  Railway service from the same repo with its own start command.
- **DNS**: `api.yanaytevet.com` is a **DNS-only** (grey cloud) CNAME in Cloudflare to Railway's target, plus a
  `_railway-verify.api` TXT record. Railway issues the certificate; proxying it through Cloudflare with SSL
  *Full (strict)* breaks issuance.
- **Backup from the move**: the final DigitalOcean `pg_dump` (data as of the 2026-10-10 cutover) is in
  `~/dev/do-final-backups-2026-10-10/` on the owner's Mac. The droplet and its snapshot are deleted.
