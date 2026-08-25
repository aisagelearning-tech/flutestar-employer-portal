# Deployment Guide — https://employer.flute-star.com

This document is the deployment handoff for Phase 4. I have prepared the
project for deployment (Dockerfile, Procfile, env-based config, working
migrations) but I have not deployed anything, touched DNS, or pushed to
GitHub — I have no access to do any of that. Every claim below about what's
"done" refers to code/config that exists in this package and was validated
locally; nothing here should be read as "already live."

---

## A. Recommended production architecture

```
GitHub: aisagelearning-tech/flutestar-employer-portal
       |
       +---- frontend/  -> Static hosting (any provider serving plain HTML/CSS/JS)
       |            served at https://employer.flute-star.com
       |
       +---- backend/   -> FastAPI, containerized (Dockerfile provided) or
                            buildpack-based (Procfile provided) — either works,
                            pick based on your hosting provider
                    |
                    +---- PostgreSQL (managed instance recommended:
                          RDS, Supabase, Neon, Render Postgres, etc.)
```

This matches the brief: simplest maintainable V1 architecture, no unnecessary
infrastructure (no Kubernetes, no message queues, no separate cache layer —
none of that is justified at this stage). It also doesn't foreclose the
planned future integrations (Student Portal, AI SAGE, CV builder, etc.) —
those would be separate services/routes added later behind the same pattern:
FastAPI service(s) + PostgreSQL + static frontend(s), not a rearchitecture of
this backend.

**Hosting provider is not yet selected.** I have not chosen one for you, and
I have not configured one — see section F for the decision this still
requires from you.

---

## B. GitHub repository setup

Target repository: **aisagelearning-tech/flutestar-employer-portal**

I did not create this repository, verify it exists, or check its current
contents — I have no GitHub access. Before pushing:

1. Confirm the repository exists at
   `https://github.com/aisagelearning-tech/flutestar-employer-portal`
   (create it via GitHub's web UI if it doesn't, as an empty repo — no
   README/license/gitignore auto-generated, to avoid merge conflicts with
   this package's own files).
2. See `GIT_COMMANDS.md` for the exact commands to push this package to it.

---

## C. Backend deployment

Two deployment paths are supported by this package — use whichever matches
your hosting choice:

**Option 1 — Container-based hosting** (Render "Docker" service, Fly.io,
AWS ECS/Fargate, a VM running Docker, etc.):
```bash
cd backend
docker build -t flutestar-employer-backend .
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql+psycopg2://<user>:<pass>@<host>:5432/<db>" \
  -e ALLOWED_ORIGINS="https://employer.flute-star.com" \
  flutestar-employer-backend
```
Your hosting provider's own docs will tell you how to hand it this
Dockerfile and set the two environment variables above through its UI/CLI
rather than the `docker run -e` flags shown.

**Option 2 — Buildpack-based PaaS** (Render "Native Environment",
Heroku-style platforms): the included `backend/Procfile` declares the start
command (`uvicorn app.main:app --host 0.0.0.0 --port $PORT`). Point the
platform at the `backend/` directory, set the same two environment
variables through its dashboard, and it should detect and run this
automatically via `requirements.txt` + `Procfile`.

Either way, the backend needs outbound network access to your PostgreSQL
instance and needs `DATABASE_URL` / `ALLOWED_ORIGINS` set as real
environment variables on the host — never baked into the image or committed
to git.

---

## D. PostgreSQL production database setup

1. Provision a PostgreSQL instance (managed service strongly recommended
   over self-hosting for V1).
2. Note its connection string in the form:
   `postgresql+psycopg2://<user>:<password>@<host>:<port>/<database>`
   (the `+psycopg2` driver suffix matters — it's what `requirements.txt`
   now installs via `psycopg2-binary`).
3. Set that string as `DATABASE_URL` on the backend host (section C).
4. Run migrations against it (section I) — do this once, not automatically
   on every container start.

I have not provisioned a database and have no real connection string —
the example above is illustrative, not a real credential.

---

## E. Frontend static hosting

The frontend is plain HTML/CSS/JS with no build step, so it works on any
static host (Netlify, Vercel, Cloudflare Pages, S3+CloudFront, Nginx on a
VM, GitHub Pages, etc.).

1. Deploy the contents of `frontend/` as-is.
2. Edit `frontend/config.js`'s `API_BASE_URL` to the backend's real public
   HTTPS URL from step C (e.g. `https://api.employer.flute-star.com`, or
   `https://employer.flute-star.com/api` if you reverse-proxy both behind
   one domain). Commit this change and redeploy — `config.js` is the only
   file that needs to change between environments.

---

## F. DNS configuration for employer.flute-star.com

**Not yet configured — this requires access to your DNS provider, which I
don't have.** Once you've picked a static host (section E):

1. Add whatever DNS record that host requires (typically a `CNAME` for a
   subdomain like `employer`, or an `A`/`ALIAS` record if `employer` is
   being treated as an apex-style entry under `flute-star.com`).
2. Point it at the frontend host, **not** the backend.
3. Do **not** create or leave active a `www.employer.flute-star.com` record
   pointed at this app — the canonical URL is explicitly
   `https://employer.flute-star.com` per this project's requirements. If
   your registrar or host auto-creates a `www` variant, either delete it or
   set it to redirect to the non-www URL.

---

## G. HTTPS/TLS

Nearly all static hosts and PaaS backends provision TLS automatically
(typically via Let's Encrypt) once DNS is pointed at them correctly — no
manual certificate handling is normally needed for this architecture. If
your provider requires manual TLS setup, follow its documentation; this
project doesn't do anything unusual (like custom certificate pinning) that
would complicate that.

---

## H. Production environment variables

Set these on the **backend** host (never commit real values — see
`backend/.env.example` for the template):

| Variable | Production value | Notes |
|---|---|---|
| `DATABASE_URL` | `postgresql+psycopg2://<user>:<pass>@<host>:5432/<db>` | Real credentials, set via host's secret/env-var mechanism |
| `ALLOWED_ORIGINS` | `https://employer.flute-star.com` | Exactly this origin, no trailing slash, no `www.` variant, no wildcard |

Set this in the **frontend** (`frontend/config.js`, committed to git — it
holds no secret):

| Variable | Production value |
|---|---|
| `API_BASE_URL` | The backend's real public HTTPS URL |

---

## I. Database migration command

Run once against the production database, after the backend is deployed but
as a separate one-off step (not automatically on every container start, to
avoid race conditions if you ever run multiple backend instances):

```bash
# From the backend/ directory, with DATABASE_URL set to the production value:
python -m alembic upgrade head
```

If deploying via Docker, run this inside a one-off container with the same
image and the same `DATABASE_URL`:
```bash
docker run --rm -e DATABASE_URL="postgresql+psycopg2://..." flutestar-employer-backend \
  python -m alembic upgrade head
```

**This was fixed during this phase:** `alembic/env.py` previously ignored
`DATABASE_URL` entirely and always read the SQLite URL hardcoded in
`alembic.ini`. Running migrations in production would have silently migrated
a local SQLite file instead of your real PostgreSQL database. This is now
fixed — `env.py` uses `DATABASE_URL` when it's set, falling back to
`alembic.ini`'s SQLite default only for local development. See
`TEST_CHECKLIST.md` for how this was verified.

---

## J. Backend health check

```
GET https://<your-backend-host>/api/health
```
Expected: `{"status":"ok"}`, HTTP 200. Point your hosting provider's health
check / load balancer probe at this path. A Docker `HEALTHCHECK` hitting the
same endpoint is already defined in `backend/Dockerfile`.

---

## K. Production smoke test

Once deployed, run these against the real production URLs (replace
placeholders):

```
GET  https://<backend-host>/api/health                         -> {"status":"ok"}
POST https://<backend-host>/api/employer/register               -> employer_id returned
GET  https://<backend-host>/api/employers/<employer_id>         -> matches what you registered
POST https://<backend-host>/api/employer/requirement             -> requirement_id returned
GET  https://<backend-host>/api/employers/<employer_id>/requirements -> contains only that employer's requirement
GET  https://employer.flute-star.com                             -> frontend loads, no console errors
```
Then, in an actual browser at `https://employer.flute-star.com`: register a
test employer, submit a requirement, confirm it appears under "My
Requirements," and confirm a browser network-tab check shows requests going
to your real backend host over HTTPS with no CORS errors.

---

## L. Rollback procedure

Specific rollback steps depend on the hosting provider you choose (most
container/PaaS platforms support redeploying a previous build or image tag
with one command/click). General principles that apply regardless of
provider:

1. Keep the previous known-good container image tag or git commit
   identifiable before deploying a new one.
2. Database migrations here are additive so far (one initial migration
   creating both tables) — there's currently nothing to roll back at the
   schema level. If a future migration needs to be reversible, write it with
   a working `downgrade()` and test `alembic downgrade -1` locally before
   applying it in production.
3. If a bad deploy reaches production, redeploy the previous
   image/build/commit through your host's mechanism, then verify with
   section K's smoke test.

---

## M. Production end-to-end test sequence

1. Confirm DNS resolves: `https://employer.flute-star.com` loads over HTTPS
   with a valid certificate (no browser warning).
2. Confirm `https://<backend-host>/api/health` returns 200.
3. Register a real test employer through the live frontend.
4. Submit a requirement as that employer.
5. Confirm "My Requirements" shows only that employer's own requirement.
6. Register a second test employer and confirm it does **not** see the
   first employer's requirement (isolation check, same as the local test).
7. Try `https://www.employer.flute-star.com` and confirm it either doesn't
   resolve or redirects to the non-www canonical URL — it must not serve a
   separate/duplicate copy of the app.
8. Check the browser console and network tab for CORS errors — there
   should be none, since `ALLOWED_ORIGINS` should exactly match the
   frontend's real origin.

## N. Local development vs. production — summary

| | Local development | Production |
|---|---|---|
| Database | SQLite file (`backend/flutestar.db`), created automatically by Alembic | PostgreSQL, `DATABASE_URL` set on the host |
| CORS | `ALLOWED_ORIGINS` unset defaults to `*` (open), or set to `http://localhost:8080` | `ALLOWED_ORIGINS=https://employer.flute-star.com` exactly |
| Frontend API target | `frontend/config.js` → `http://localhost:8000` | `frontend/config.js` → real backend HTTPS URL |
| Secrets | `.env` (git-ignored, never committed) | Host's own env-var/secret manager |
| Run backend | `uvicorn app.main:app --reload` | Dockerfile or Procfile, per section C |

---

## Still required from you before this can go live (see final chat message for the full list)

- Choice of backend hosting provider
- Choice of frontend static hosting provider
- A provisioned PostgreSQL instance and its real connection string
- DNS access to point `employer.flute-star.com` at the chosen frontend host
- Pushing this package to `aisagelearning-tech/flutestar-employer-portal` (see `GIT_COMMANDS.md`)

Nothing in this project is deployed or live as of this writing.
