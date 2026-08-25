# Git / GitHub Commands — Windows PC + GitHub Web

Target repository: **aisagelearning-tech/flutestar-employer-portal**

I have not created this repository, pushed to it, or verified its current
state — I have no GitHub access. Everything below is for you to run. Two
kinds of actions are mixed together in any GitHub workflow — I've labelled
each step so it's clear which is which:

- 🖥️ **PC (PowerShell)** — run in a terminal on your Windows machine
- 🌐 **GitHub web** — done by clicking around at github.com

---

## Step 0 — 🌐 GitHub web: confirm/create the repository

1. Go to `https://github.com/aisagelearning-tech/flutestar-employer-portal`.
2. If it **doesn't exist yet**: go to `https://github.com/organizations/aisagelearning-tech/repositories/new`,
   name it exactly `flutestar-employer-portal`, and create it **empty**
   (do not check "Add a README", "Add .gitignore", or "Choose a license" —
   those would conflict with the files already in this package).
3. If it **already exists**: check whether it already has commits. If it's
   non-empty, do not run `git push -u origin main` blindly later — see
   Step 4's "if the remote already has history" note instead.

---

## Step 1 — 🖥️ PC: unzip and open a terminal in the project root

Unzip the final package (see chat message for filename) somewhere on your
machine, then open PowerShell in that folder — the one containing
`backend/`, `frontend/`, `.gitignore`, `README.md`, etc.

```powershell
cd C:\path\to\flutestar-employer-portal
```

---

## Step 2 — 🖥️ PC: initialize git and check status

```powershell
git init
git status
```

`git status` should show all the project files as untracked. Confirm you do
**not** see `backend/.env`, `backend/flutestar.db`, `backend/venv/`, or any
`__pycache__/` folder listed — this package doesn't include them, and
`.gitignore` will keep them out even if they get created locally later
(e.g. when you run the app).

---

## Step 3 — 🖥️ PC: stage and commit

```powershell
git add .
git status
```

Re-run `git status` after `git add .` and look through the "Changes to be
committed" list one more time before committing — same check as Step 2, now
against what's actually staged.

```powershell
git commit -m "Phase 4: deployment-ready backend/frontend, Docker/Procfile, fixed Alembic env-var handling, version consistency fix"
git branch -M main
```

---

## Step 4 — 🖥️ PC: connect to GitHub and push

```powershell
git remote add origin https://github.com/aisagelearning-tech/flutestar-employer-portal.git
git push -u origin main
```

**If the remote already has commits** (i.e. Step 0 found an existing
non-empty repo), `git push` will be rejected. Do not force-push over
existing history without deliberately deciding to. Instead, either:

```powershell
# Option A: bring your local main up to date with the remote first, then push
git pull origin main --allow-unrelated-histories
# resolve any merge conflicts if prompted, then:
git push -u origin main
```
```powershell
# Option B: push this as a feature branch and open a Pull Request instead
git checkout -b phase-4-deployment-prep
git push -u origin phase-4-deployment-prep
# then open a PR on GitHub web
```

I'm not choosing between these for you — it depends on what's already in
that repository, which I can't see.

---

## Step 5 — 🌐 GitHub web: verify

1. Refresh `https://github.com/aisagelearning-tech/flutestar-employer-portal`.
2. Confirm `backend/`, `frontend/`, `README.md`, `DEPLOYMENT.md`, etc. are
   all present.
3. Open a couple of files (e.g. `backend/.env.example`) and confirm no real
   secrets are visible anywhere in the repo — only the placeholder/example
   values from this package.
4. Check the repo's file list does **not** contain `.env`, `*.db`,
   `__pycache__/`, or `venv/` — if any of those appear, stop and remove them
   (`git rm --cached <path>`, commit, push) before treating the repo as
   clean.

---

## Step 6 — 🖥️ PC: ongoing workflow (for future changes)

```powershell
git status
git add .
git commit -m "Describe what changed"
git push origin main          # or your feature branch name
```

---

## A note on secrets, for when you actually deploy

Your real `DATABASE_URL` and `ALLOWED_ORIGINS` values go into your hosting
provider's environment-variable settings (🌐 done on that provider's
dashboard, not GitHub, not a committed file). If you ever need a local
`.env` file to test against a real database, create it from
`backend/.env.example` — it's already git-ignored, so `git status` should
never show it as trackable. If it ever does show up as trackable, that means
`.gitignore` isn't being respected (e.g. the file was already committed
before `.gitignore` existed) — resolve that before pushing.
