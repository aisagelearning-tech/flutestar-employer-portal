// FLUTESTAR Employer Portal - frontend application logic
// Connects the UI to the FastAPI backend defined in config.js.

const API_BASE_URL = (window.FLUTESTAR_CONFIG && window.FLUTESTAR_CONFIG.API_BASE_URL) || "";
const SESSION_KEY = "flutestar_employer_session";

// ---------- Tabs ----------
const tabs = document.querySelectorAll(".tabs button");
const panels = document.querySelectorAll(".panel");
tabs.forEach((t) =>
  t.onclick = () => {
    tabs.forEach((x) => x.classList.remove("active"));
    panels.forEach((x) => x.classList.remove("active"));
    t.classList.add("active");
    document.getElementById(t.dataset.tab).classList.add("active");
  }
);

// ---------- Helpers ----------
async function apiRequest(path, options = {}) {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  let body = null;
  try {
    body = await res.json();
  } catch (_) {
    // no JSON body
  }
  if (!res.ok) {
    const detail = (body && body.detail) || `Request failed (HTTP ${res.status})`;
    throw new Error(detail);
  }
  return body;
}

function setMessage(el, text, kind) {
  // kind: "success" | "error" | "info" | "loading"
  el.textContent = text;
  el.className = `form-msg ${kind || ""}`.trim();
}

function getSession() {
  try {
    return JSON.parse(localStorage.getItem(SESSION_KEY) || "null");
  } catch (_) {
    return null;
  }
}

function setSession(session) {
  localStorage.setItem(SESSION_KEY, JSON.stringify(session));
}

function clearSession() {
  localStorage.removeItem(SESSION_KEY);
}

// ---------- Login (MVP: email lookup, no password backend yet) ----------
const loginForm = document.getElementById("loginForm");
const loginMsg = document.getElementById("loginMsg");
loginForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const email = new FormData(e.target).get("email");
  setMessage(loginMsg, "Checking employer account...", "loading");
  try {
    const data = await apiRequest(`/api/employer/lookup?email=${encodeURIComponent(email)}`);
    setSession({ employer_id: data.employer.id, company: data.employer.company, email: data.employer.email });
    setMessage(loginMsg, `Welcome back, ${data.employer.company}. Loading your requirements...`, "success");
    showRequirementsPanelFor(data.employer.id, data.employer.company);
  } catch (err) {
    setMessage(
      loginMsg,
      `Login failed: ${err.message}. Note: this V1 login checks the business email only; full password authentication is a planned production upgrade.`,
      "error"
    );
  }
});

// ---------- Registration ----------
const registerForm = document.getElementById("registerForm");
const registerMsg = document.getElementById("registerMsg");
registerForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const fd = new FormData(e.target);
  const payload = {
    company: fd.get("company"),
    contact: fd.get("contact"),
    email: fd.get("email"),
    phone: fd.get("phone"),
    website: fd.get("website") || null,
    location: fd.get("location"),
    organization_type: fd.get("type"),
    description: fd.get("description") || null,
  };
  setMessage(registerMsg, "Submitting registration...", "loading");
  try {
    const data = await apiRequest("/api/employer/register", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    setSession({ employer_id: data.employer_id, company: payload.company, email: payload.email });
    setMessage(
      registerMsg,
      `Registration successful. Your Employer ID is ${data.employer_id}. You can now post requirements.`,
      "success"
    );
    e.target.reset();
    populateEmployerIdHints(data.employer_id);
  } catch (err) {
    setMessage(registerMsg, `Registration failed: ${err.message}`, "error");
  }
});

// ---------- Requirement submission ----------
const reqForm = document.getElementById("reqForm");
const reqMsg = document.getElementById("reqMsg");
reqForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const session = getSession();
  if (!session || !session.employer_id) {
    setMessage(
      reqMsg,
      "Please register or log in first so we know which employer account this requirement belongs to.",
      "error"
    );
    return;
  }
  const fd = new FormData(e.target);
  const payload = {
    employer_id: session.employer_id,
    requirement: fd.get("requirement"),
    role: fd.get("role"),
    count: Number(fd.get("count")),
    location: fd.get("location"),
    qualification: fd.get("qualification"),
    experience: fd.get("experience"),
    priority: fd.get("priority"),
    required_within: fd.get("requiredWithin"),
    start_date: fd.get("startDate") || null,
    duration: fd.get("duration") || null,
    target_date: fd.get("targetDate") || null,
    budget: fd.get("budget") || null,
    skills: fd.get("skills"),
    details: fd.get("details"),
  };
  setMessage(reqMsg, "Submitting requirement...", "loading");
  try {
    const data = await apiRequest("/api/employer/requirement", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    setMessage(reqMsg, `Requirement submitted successfully (Requirement ID ${data.requirement_id}).`, "success");
    e.target.reset();
    if (session.employer_id) {
      loadEmployerRequirements(session.employer_id);
    }
  } catch (err) {
    setMessage(reqMsg, `Submission failed: ${err.message}`, "error");
  }
});

// ---------- Employer-specific requirement listing ----------
function populateEmployerIdHints(employerId) {
  document.querySelectorAll("[data-employer-id-hint]").forEach((el) => {
    el.textContent = `Your Employer ID: ${employerId}`;
  });
}

function showRequirementsPanelFor(employerId, company) {
  const panel = document.getElementById("myRequirements");
  if (panel) panel.hidden = false;
  populateEmployerIdHints(employerId);
  loadEmployerRequirements(employerId, company);
}

async function loadEmployerRequirements(employerId, company) {
  const list = document.getElementById("myRequirementsList");
  const status = document.getElementById("myRequirementsStatus");
  if (!list || !status) return;

  list.innerHTML = "";
  status.textContent = "Loading your requirements...";
  status.className = "form-msg loading";

  try {
    const data = await apiRequest(`/api/employers/${employerId}/requirements`);
    if (data.count === 0) {
      status.textContent = "No requirements posted yet. Use the form above to submit your first requirement.";
      status.className = "form-msg info";
      return;
    }
    status.textContent = `Showing ${data.count} requirement(s) for ${data.company || company || "your account"}.`;
    status.className = "form-msg success";
    data.requirements.forEach((r) => {
      const item = document.createElement("li");
      item.className = "req-item";
      item.innerHTML = `
        <strong>${escapeHtml(r.role)}</strong> — ${escapeHtml(r.requirement)} (x${r.count})<br>
        <span>Location: ${escapeHtml(r.location)} | Priority: ${escapeHtml(r.priority)} | Required within: ${escapeHtml(r.required_within)}</span><br>
        <span>Skills: ${escapeHtml(r.skills)}</span>
      `;
      list.appendChild(item);
    });
  } catch (err) {
    status.textContent = `Could not load requirements: ${err.message}`;
    status.className = "form-msg error";
  }
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str == null ? "" : String(str);
  return div.innerHTML;
}

// ---------- Restore session on page load ----------
window.addEventListener("DOMContentLoaded", () => {
  const session = getSession();
  if (session && session.employer_id) {
    showRequirementsPanelFor(session.employer_id, session.company);
  }

  const logoutBtn = document.getElementById("logoutBtn");
  if (logoutBtn) {
    logoutBtn.addEventListener("click", () => {
      clearSession();
      document.getElementById("myRequirements").hidden = true;
      location.reload();
    });
  }
});
