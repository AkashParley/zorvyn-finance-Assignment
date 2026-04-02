// Always hit the FastAPI backend (port 8000), not the CRA dev server (3000/3001).
// Relative URLs like `/api/v1/...` would resolve to the wrong host and cause "Failed to fetch".
const API_ORIGIN = process.env.REACT_APP_API_URL || "http://127.0.0.1:8000";
const BASE = "/api/v1";
const BASE_URL = `${API_ORIGIN.replace(/\/+$/, "")}${BASE}`;

function getToken() {
  return localStorage.getItem("token");
}

function clearTokenAndRedirect() {
  localStorage.removeItem("token");
  window.location.href = "/login";
}

async function request(method, path, body = null, params = null) {
  const url = new URL(BASE_URL + path);
  if (params) {
    Object.entries(params).forEach(([k, v]) => {
      if (v !== null && v !== undefined && v !== "") url.searchParams.set(k, v);
    });
  }

  const headers = { "Content-Type": "application/json" };
  const token = (getToken() || "").trim();
  if (token) headers.Authorization = `Bearer ${token}`;

  let res;
  try {
    res = await fetch(url.toString(), {
      method,
      headers,
      body: body ? JSON.stringify(body) : null,
    });
  } catch (err) {
    const hint = `Cannot reach API at ${API_ORIGIN}. Is the backend running (uvicorn on port 8000)?`;
    throw new Error(err?.message === "Failed to fetch" ? `${hint} (${err.message})` : err.message || String(err));
  }

  if (res.status === 204) return null;

  if (res.status === 401) {
    clearTokenAndRedirect();
    throw new Error("Session expired. Please sign in again.");
  }

  const ct = res.headers.get("content-type") || "";
  const data = ct.includes("application/json")
    ? await res.json()
    : { detail: await res.text().catch(() => res.statusText) };

  if (!res.ok) {
    const msg = data?.detail || "An error occurred.";
    throw new Error(typeof msg === "string" ? msg : JSON.stringify(msg));
  }
  return data;
}

// ── Auth ─────────────────────────────────────────────────────────────────────
export const authApi = {
  login: (username, password) =>
    request("POST", "/auth/login", { username, password }),
  register: (data) => request("POST", "/auth/register", data),
  me: () => request("GET", "/auth/me"),
};

// ── Transactions ─────────────────────────────────────────────────────────────
export const txApi = {
  list: (params) => request("GET", "/transactions", null, params),
  get: (id) => request("GET", `/transactions/${id}`),
  create: (data) => request("POST", "/transactions", data),
  update: (id, data) => request("PATCH", `/transactions/${id}`, data),
  remove: (id) => request("DELETE", `/transactions/${id}`),
};

// ── Dashboard ─────────────────────────────────────────────────────────────────
export const dashApi = {
  summary: () => request("GET", "/dashboard/summary"),
};

// ── Users ─────────────────────────────────────────────────────────────────────
export const usersApi = {
  list: (page = 1, page_size = 20) =>
    request("GET", "/users", null, { page, page_size }),
  get: (id) => request("GET", `/users/${id}`),
  update: (id, data) => request("PATCH", `/users/${id}`, data),
  deactivate: (id) => request("DELETE", `/users/${id}`),
};
