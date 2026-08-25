# FLUTESTAR Employer Portal — Implementation Package

This package contains the **working, updated** backend and frontend for the
FLUTESTAR Employer Portal, built directly on top of the baseline you provided
(`FLUTESTAR_EMPLOYER_PORTAL_CLAUDE_V1.2.zip`). It is not a rewrite — the
existing API contracts, data model, and frontend structure were preserved and
completed.

Production target domain: **https://employer.flute-star.com**
(explicitly not `www.employer.flute-star.com`)

## What's in here

```
backend/     FastAPI + SQLAlchemy + Alembic API (was already present, now completed)
frontend/    Static HTML/CSS/JS portal (was a disconnected prototype, now wired to the API)
.gitignore   Keeps secrets, DBs, venvs, caches out of git
TEST_CHECKLIST.md   Every endpoint + flow, with exact URLs and results from local testing
GIT_COMMANDS.md     Exact commands to get this into GitHub
DEPLOYMENT.md        Production deployment notes and open decisions
```

The original package's `00_MASTER_INSTRUCTIONS` through `09_PROJECT_DOCUMENTATION`
folders are documentation scaffolding, not code — they aren't duplicated here.
Everything in this package is the actual, runnable implementation.

## Quick start (local)

Terminal 1 — backend:
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m alembic upgrade head
python -m uvicorn app.main:app --reload
```

Terminal 2 — frontend:
```bash
cd frontend
python3 -m http.server 8080
```

Open http://localhost:8080 — register an employer, submit a requirement, and
watch it appear in "My Requirements" (fetched live from the backend, scoped
to that employer only).

## What changed vs. the baseline, and why

| Area | Baseline | Now |
|---|---|---|
| `GET /api/employers/{id}/requirements` | Missing | Added, employer-scoped, 404s correctly, verified with two separate employers |
| `requirements.txt` | Missing `sqlalchemy`/`alembic` despite being imported | Fixed — backend now installs and runs cleanly |
| CORS | Hardcoded `allow_origins=["*"]` | Configurable via `ALLOWED_ORIGINS` env var; verified it actually blocks unlisted origins |
| Database URL | Hardcoded SQLite path | Configurable via `DATABASE_URL` env var (drop-in PostgreSQL support for production) |
| Frontend forms | Logged to console, showed a canned "captured locally" message, no network calls at all | Real `fetch()` calls to every relevant endpoint, with loading/error/empty states |
| Employer session | None | Employer ID stored client-side (`localStorage`) after register/login, used to scope requirement submission and retrieval |
| Login | Fake, no backend | `GET /api/employer/lookup?email=` — an honest MVP account lookup, **not** password authentication (flagged in the UI and in both READMEs) |
| Secrets hygiene | No `.gitignore`, no `.env.example` | Both added |

## Known gaps (called out on purpose, not hidden)

1. **No real authentication.** Login matches on business email only. This
   matches what the original prototype's own text promised ("authentication
   will be connected in the backend stage") but production launch needs real
   password hashing + sessions/JWT before this handles real employer data.
   This is intentionally deferred to the next security-focused phase, not
   forgotten.
2. **No production hosting/DNS/TLS has been configured** — I don't have
   access to your GitHub remote, hosting provider, or DNS for
   `employer.flute-star.com`. `DEPLOYMENT.md` gives the exact steps and
   decisions needed on your end.
3. **Testing here is API-level (curl) and frontend-code-level (static
   analysis + syntax checks), not a real browser click-through**, since this
   environment has no browser. See `TEST_CHECKLIST.md` for exactly what was
   and wasn't verified.

## Phase 4 update — deployment preparation

Building directly on the implementation above (no redesign), this pass:

- Fixed a real version-inconsistency bug: `app.main:root()` reported
  `version: "0.1.0"` while the FastAPI app object reported `"0.1.1"`. Both
  now derive from a single source (`app.version`, currently `0.2.0`).
- Fixed a real deployment-blocking defect: `backend/alembic/env.py` ignored
  the `DATABASE_URL` environment variable and always migrated the SQLite URL
  hardcoded in `alembic.ini`. Running `alembic upgrade head` in production
  would have silently migrated the wrong database. Now `DATABASE_URL` (when
  set) takes precedence; local development is unaffected.
- Added `psycopg2-binary` to `requirements.txt` so `DATABASE_URL` can
  actually point at PostgreSQL, not just document that it theoretically could.
- Added `backend/Dockerfile`, `backend/.dockerignore`, and `backend/Procfile`
  — minimum deployment configuration for either a container-based host or a
  buildpack-based PaaS, without prescribing a specific provider.
- Rewrote `DEPLOYMENT.md` and `GIT_COMMANDS.md` in full, targeting the real
  repository `aisagelearning-tech/flutestar-employer-portal`.

Target repository: **aisagelearning-tech/flutestar-employer-portal**
(not pushed by me — see `GIT_COMMANDS.md`)
