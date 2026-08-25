# FLUTESTAR Employer Portal — Backend container image
#
# Build:
#   docker build -t flutestar-employer-backend .
#
# Run locally (SQLite, for a quick sanity check only):
#   docker run -p 8000:8000 flutestar-employer-backend
#
# Run in production (PostgreSQL, real config via env vars):
#   docker run -p 8000:8000 \
#     -e DATABASE_URL="postgresql+psycopg2://user:pass@host:5432/dbname" \
#     -e ALLOWED_ORIGINS="https://employer.flute-star.com" \
#     flutestar-employer-backend
#
# Migrations are NOT run automatically by this image on every start (running
# migrations as a side effect of container boot is a common source of race
# conditions with multiple replicas). Run them as a separate one-off step —
# see DEPLOYMENT.md, section "Database migration command".

FROM python:3.12-slim

WORKDIR /app

# System deps needed to build psycopg2-binary wheels on some platforms;
# safe no-op on platforms where prebuilt wheels are used.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY alembic ./alembic
COPY alembic.ini .

EXPOSE 8000

# Health check hits the existing /api/health endpoint (Step 2, item 9).
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/api/health').status==200 else 1)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
