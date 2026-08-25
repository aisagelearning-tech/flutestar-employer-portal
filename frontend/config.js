/**
 * FLUTESTAR Employer Portal - environment configuration
 *
 * This file is intentionally the ONLY place that knows the backend API
 * base URL. Swap the value per environment at deploy time - do not hard-code
 * API URLs anywhere else in the app.
 *
 * Local development (backend running on your machine):
 *   window.FLUTESTAR_CONFIG = { API_BASE_URL: "http://localhost:8000" };
 *
 * Production (employer.flute-star.com):
 *   window.FLUTESTAR_CONFIG = { API_BASE_URL: "https://api.employer.flute-star.com" };
 *   (or whatever hostname/path the production backend is actually deployed to)
 *
 * This file holds NO secrets - it is safe to commit to GitHub.
 */
window.FLUTESTAR_CONFIG = {
  API_BASE_URL: "http://localhost:8000",
};
