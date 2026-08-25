# FLUTESTAR Employer Portal — Backend API

FastAPI + SQLAlchemy backend. Data is persisted (SQLite locally, PostgreSQL-ready
for production via `DATABASE_URL`). This supersedes older README text that
described an earlier "validate but don't store" prototype — that stage is done.

## Stack

- FastAPI (API framework)
- SQLAlchemy 2.x (ORM)
- Alembic (schema migrations)
- SQLite for local dev, any SQLAlchemy-supported DB (e.g. PostgreSQL) for production

## Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/api/health` | Liveness check |
| GET | `/api/employers` | List all employers |
| GET | `/api/employers/{employer_id}` | Get one employer, 404 if missing |
| GET | `/api/employers/{employer_id}/requirements` | Requirements belonging to one employer only, 404 if employer missing |
| GET | `/api/requirements` | List all requirements (all employers) |
| GET | `/api/requirements/{requirement_id}` | Get one requirement, 404 if missing |
| POST | `/api/employer/register` | Register a new employer |
| POST | `/api/employer/requirement` | Submit a requirement for an existing employer |
| GET | `/api/employer/lookup?email=...` | MVP employer lookup by business email (used by the frontend login screen) |

Interactive API docs are auto-generated at `/docs` when the server is running.

## Setup (local development)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env             # edit if needed; defaults work for local dev
python -m alembic upgrade head   # creates tables in flutestar.db
python -m uvicorn app.main:app --reload
```

Then visit http://127.0.0.1:8000/docs.

## Configuration (environment variables)

See `.env.example`. Two variables matter:

- `DATABASE_URL` — SQLAlchemy connection string. Defaults to the local SQLite
  file if unset. Set this to your production PostgreSQL URL when deploying.
- `ALLOWED_ORIGINS` — comma-separated list of frontend origins allowed to call
  this API via CORS. Defaults to `*` (open) only when unset, which is fine for
  local development but **must** be set explicitly in production, e.g.
  `ALLOWED_ORIGINS=https://employer.flute-star.com`.

## Database migrations

Schema changes go through Alembic, not manual table edits:

```bash
python -m alembic revision --autogenerate -m "describe your change"
python -m alembic upgrade head
```

`alembic/env.py` uses `DATABASE_URL` from the environment when it's set
(production), falling back to the SQLite URL in `alembic.ini` otherwise
(local development) — so the same `alembic upgrade head` command is correct
in both environments as long as `DATABASE_URL` is set appropriately.

## Running in a container

`Dockerfile` and `.dockerignore` are provided for container-based hosting.
`Procfile` is provided as an alternative for buildpack-based PaaS hosting.
See the repository root's `DEPLOYMENT.md` for how to use either.

## Known limitations (by design, for this stage)

- `/api/employer/lookup` (used for "Existing Employer — Login") checks the
  business email only — there is no password check yet. This matches the
  original V1 prototype's own stated plan ("authentication will be connected
  in the backend stage"). Before production launch, replace this with real
  authentication (hashed passwords + session/JWT tokens).
- No rate limiting / brute-force protection yet on any endpoint.
- No employer-side ability to edit or delete a submitted requirement yet.
