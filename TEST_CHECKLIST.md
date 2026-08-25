# Test Checklist — FLUTESTAR Employer Portal

All backend tests below were **actually executed** locally against
`http://localhost:8000` during this session (not hypothetical). Frontend
items marked "verified" were checked via static analysis, syntax checks, and
manual code tracing against the live backend responses — there is no browser
available in this environment, so a real click-through in Chrome/Safari/etc.
on your machine is still the last mile before calling this production-ready.

## 1. Health check

```
GET http://localhost:8000/api/health
```
Expected: `{"status":"ok"}`
**Result: PASS**

## 2. Employer registration

```
POST http://localhost:8000/api/employer/register
Content-Type: application/json

{"company":"Acme Robotics","contact":"Jane Doe","email":"jane@acme.com",
 "phone":"9999999999","website":"https://acme.com","location":"Pune",
 "organization_type":"Private Company","description":"Robotics firm"}
```
Expected: `{"success":true,"message":"...","employer_id":<int>,"storage":"sqlite"}`
**Result: PASS** — returned `employer_id: 1`

## 3. Employer retrieval

```
GET http://localhost:8000/api/employers
GET http://localhost:8000/api/employers/1
```
Expected: list containing the registered employer; single-employer lookup returns matching record.
**Result: PASS**

## 4. Requirement submission

```
POST http://localhost:8000/api/employer/requirement
Content-Type: application/json

{"employer_id":1,"requirement":"Full-Time Employee","role":"Embedded Engineer",
 "count":2,"location":"Pune","qualification":"BE Electronics","experience":"2-4 years",
 "priority":"High Priority","required_within":"Within 1 month",
 "skills":"C, RTOS, Verilog","details":"Need embedded firmware engineers."}
```
Expected: `{"success":true,"message":"...","requirement_id":<int>,"storage":"sqlite"}`
**Result: PASS** — returned `requirement_id: 1`

## 5. General requirement retrieval

```
GET http://localhost:8000/api/requirements
```
Expected: all requirements across all employers.
**Result: PASS** — returned both employer 1's and employer 2's requirements after step 6

## 6. Individual requirement retrieval

```
GET http://localhost:8000/api/requirements/1
```
Expected: single requirement record, 404 for a nonexistent id.
**Result: PASS**

## 7. Employer-specific requirement retrieval (the endpoint that was missing)

Registered a second employer ("Beta Corp", `employer_id=2`) and gave it its own requirement, then:

```
GET http://localhost:8000/api/employers/1/requirements
GET http://localhost:8000/api/employers/2/requirements
```
Expected: employer 1's endpoint returns only employer 1's requirement; employer 2's endpoint returns only employer 2's. No cross-contamination.
**Result: PASS** — confirmed each response contained exactly one requirement, matching only that employer's own submission, plus correct `success`, `employer_id`, `company`, `count`, `requirements` fields as specified.

## 8. Frontend registration (code-level verified)

`registerForm` submit handler calls `POST /api/employer/register`, stores `employer_id` in `localStorage`, shows a success message with the returned ID, and reveals the "My Requirements" panel.
**Result: PASS (code-verified against live API contract)** — not yet clicked through in a real browser.

## 9. Frontend requirement submission (code-level verified)

`reqForm` submit handler blocks submission with a clear message if no employer session exists, otherwise calls `POST /api/employer/requirement` with the session's `employer_id` and refreshes the requirement list on success.
**Result: PASS (code-verified)**

## 10. Frontend requirement listing (code-level verified)

`loadEmployerRequirements()` calls `GET /api/employers/{id}/requirements` and renders each item; shows a distinct empty-state message when `count === 0` and a distinct error message on fetch failure.
**Result: PASS (code-verified)**

## 11. Error cases

```
GET http://localhost:8000/api/employers/999
GET http://localhost:8000/api/employers/999/requirements
GET http://localhost:8000/api/requirements/999
```
Expected: HTTP 404 with a descriptive `detail` message for each.
**Result: PASS** — all three returned 404 with clear messages.

## 12. Invalid employer_id

```
POST http://localhost:8000/api/employer/requirement
{"employer_id": 999, ...}
```
Expected: HTTP 404, requirement NOT created.
**Result: PASS**

## 13. Empty requirement list

```
GET http://localhost:8000/api/employers/{new_employer_with_no_requirements}/requirements
```
Expected: `{"success":true,"employer_id":...,"company":...,"count":0,"requirements":[]}`
**Result: PASS** (verified via the initial empty `/api/employers` and `/api/requirements` calls before any data existed; the shape matches for a per-employer query too since it uses the same query pattern)

## 14. Production API connectivity

**Not yet performed** — requires the backend actually deployed to a reachable
HTTPS host. See `DEPLOYMENT.md`.

## 15. Production frontend connectivity

**Not yet performed** — requires DNS + hosting for `https://employer.flute-star.com`
to exist. See `DEPLOYMENT.md`.

## 16. Mobile browser testing

**Not yet performed** — requires a real device/emulator, which this
environment doesn't have. The CSS already includes a `@media(max-width:800px)`
responsive breakpoint from the original prototype; worth a manual pass once
deployed.

## CORS verification (extra, done because Phase 6 calls for it)

```
OPTIONS http://localhost:8000/api/employers   Origin: http://localhost:8080
OPTIONS http://localhost:8000/api/employers   Origin: http://evil.example.com
```
With `ALLOWED_ORIGINS=http://localhost:8080,http://127.0.0.1:8080` set:
- First request: response included `access-control-allow-origin: http://localhost:8080`
- Second request: response did **not** include an `access-control-allow-origin` header
**Result: PASS** — CORS restriction genuinely blocks non-allowed origins, not just documented.

---

## Phase 4 — deployment-prep validation

All items below were actually run in this environment (no external hosting
available, so items involving real production infrastructure are marked
accordingly rather than claimed).

### API version consistency (defect found + fixed)

Before the fix: `GET /` returned `"version": "0.1.0"` while the `FastAPI(...)`
constructor was set to `"0.1.1"` — a real inconsistency.
Fix: both now read from `app.version` (single source of truth, currently `0.2.0`).
```
GET http://localhost:8000/          -> {"service":"...","version":"0.2.0","status":"running"}
GET http://localhost:8000/api/health -> {"status":"ok"}
```
**Result: PASS** — confirmed both report `0.2.0` after the fix.

### Alembic DATABASE_URL override (deployment-blocking defect found + fixed)

Before the fix: `alembic/env.py` always used the SQLite URL hardcoded in
`alembic.ini`, ignoring `DATABASE_URL` entirely.
Test performed: set `DATABASE_URL` to a fake PostgreSQL-style URL
(`postgresql+psycopg2://fakeuser:fakepass@fake-host:5432/fakedb`, not a real
credential) and confirmed via the same config-loading logic `env.py` uses
that the resolved `sqlalchemy.url` matched the environment variable instead
of the `alembic.ini` default.
**Result: PASS** — override logic works. (Not tested against a real
PostgreSQL server — none is available here — so the *connection* itself is
unverified; only the *URL resolution logic* is confirmed correct.)

### Local development regression check (confirm the fix didn't break SQLite)

With `DATABASE_URL` unset:
```
python -m alembic upgrade head    -> ran cleanly against local flutestar.db
GET /api/health                   -> {"status":"ok"}
POST /api/employer/register (x2)  -> employer_id 1, 2
POST /api/employer/requirement    -> requirement_id 1, for employer 1
GET /api/employers/1/requirements -> 1 requirement (employer 1's own)
GET /api/employers/2/requirements -> 0 requirements (correctly isolated, empty-state shape)
GET /api/employers/999/requirements -> 404
GET /api/employer/lookup?email=jane@acme.com -> matched employer 1
```
**Result: PASS** — full functional + isolation + 404 + empty-state behavior
unchanged after the Phase 4 fixes.

### psycopg2-binary installability

```
pip install psycopg2-binary
python -c "import psycopg2"
```
**Result: PASS** — installs and imports cleanly in this environment.

### Production CORS value, end to end

Set `ALLOWED_ORIGINS=https://employer.flute-star.com` (the real intended
production value) and re-ran the CORS preflight check from above:
```
OPTIONS http://localhost:8000/api/employers   Origin: https://employer.flute-star.com
  -> access-control-allow-origin: https://employer.flute-star.com  (allowed)
OPTIONS http://localhost:8000/api/employers   Origin: https://www.employer.flute-star.com
  -> (no access-control-allow-origin header — correctly rejected)
```
**Result: PASS** — confirms the `www.` variant is correctly excluded when
`ALLOWED_ORIGINS` is set to the exact canonical production origin, matching
the requirement that `https://www.employer.flute-star.com` must not be
treated as the app's origin.

### Dockerfile

Reviewed manually for correctness (base image, dependency install order,
`EXPOSE`, `HEALTHCHECK` against the real `/api/health` path, non-root-friendly
structure). **Not build-tested** — no Docker daemon is available in this
environment (`docker: command not found`). Recommend running
`docker build -t flutestar-employer-backend .` yourself before relying on it,
though the Dockerfile follows a standard, low-risk pattern.

### Procfile

Reviewed manually; syntax matches the standard `web: <command>` format
expected by buildpack-based platforms. Not tested against an actual PaaS
(none available here).

### Frontend (unchanged from prior phase, re-confirmed)

```
node --check frontend/app.js     -> syntax OK
node --check frontend/config.js  -> syntax OK
```
No frontend application logic changed in this phase — only backend/deployment
config did. `frontend/config.js` remains the single API-base configuration
point as required.

### Secrets scan

```
grep -r "password\|secret\|api_key\|token" backend/ frontend/ --include=*.py --include=*.js -i
```
No hardcoded credentials found outside of `.env.example` placeholders
(`REPLACE_ME`) and comments. `backend/.env` was deleted before packaging;
only `backend/.env.example` (placeholder values) is included.

### Not performed (requires infrastructure this environment doesn't have)

- Real PostgreSQL connection test
- Real Docker image build/run
- Real GitHub push
- Real hosting deployment
- Real DNS/TLS check for `employer.flute-star.com`
- Real browser click-through

