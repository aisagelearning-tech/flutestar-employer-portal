# FLUTESTAR Employer Portal — Frontend

Static HTML/CSS/JS frontend, now connected to the real backend API (no more
"captured locally" placeholder messages).

Target production domain: **https://employer.flute-star.com**
(not `www.employer.flute-star.com` — see project deployment docs)

## Files

- `index.html` — page structure and forms
- `styles.css` — styling
- `app.js` — application logic: calls the backend API, manages the employer
  session in the browser, renders loading/empty/error states
- `config.js` — **the only file that knows the backend API base URL.** Edit
  this per environment; it holds no secrets so it is safe to commit.

## Running locally

This is a static site — any static file server works:

```bash
cd frontend
python3 -m http.server 8080
```

Then open http://localhost:8080. Make sure the backend is also running (see
`backend/README.md`) and that `config.js` points at it
(`http://localhost:8000` by default).

## What works end-to-end now

1. **Register** — creates an employer via `POST /api/employer/register`,
   stores the returned `employer_id` in the browser (localStorage) as the
   session, and reveals the "My Requirements" panel.
2. **Post a requirement** — submits via `POST /api/employer/requirement`
   using the logged-in employer's `employer_id`. You cannot submit a
   requirement without first registering or logging in.
3. **My Requirements** — fetches `GET /api/employers/{employer_id}/requirements`
   and renders only that employer's requirements, with loading, empty, and
   error states handled.
4. **Login (existing employer)** — looks the employer up by business email via
   `GET /api/employer/lookup`. See the known-limitation note below.
5. **Logout** — clears the local session.

## Known limitation: login has no password check yet

The V1 prototype's own copy said "authentication will be connected in the
backend stage." This stage adds a working *account lookup*, not full
authentication. `GET /api/employer/lookup` matches on business email only.
Before production launch this should be replaced with real authentication
(password hashing + session/JWT), which is tracked as a Phase 6 follow-up.

## Deploying to production

1. Build/host the backend somewhere reachable over HTTPS (see
   `08_DEPLOYMENT` docs in the project package).
2. Edit `config.js` so `API_BASE_URL` points at that HTTPS backend URL.
3. Host these static files at `https://employer.flute-star.com`.
4. On the backend, set `ALLOWED_ORIGINS=https://employer.flute-star.com` so
   CORS only allows this exact origin.
