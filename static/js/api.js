function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
  return null;
}

const CSRF_TOKEN = getCookie("csrftoken");

async function apiRequest(url, options = {}) {
  const headers = options.headers || {};
  headers["X-CSRFToken"] = CSRF_TOKEN;
  if (!(options.body instanceof FormData)) {
    headers["Content-Type"] = "application/json";
  }
  const resp = await fetch(url, { ...options, headers, credentials: "same-origin" });
  let data = null;
  try {
    data = await resp.json();
  } catch (e) {
    data = null;
  }
  if (!resp.ok) {
    const err = new Error("Request failed");
    err.data = data;
    err.status = resp.status;
    throw err;
  }
  return data;
}

function apiGet(url) {
  return apiRequest(url, { method: "GET" });
}
function apiPost(url, body) {
  return apiRequest(url, { method: "POST", body: JSON.stringify(body) });
}
function apiPatch(url, body) {
  return apiRequest(url, { method: "PATCH", body: JSON.stringify(body) });
}
function apiDelete(url) {
  return apiRequest(url, { method: "DELETE" });
}

function showToast(message, type = "success") {
  const area = document.getElementById("toast-area");
  if (!area) return alert(message);
  const div = document.createElement("div");
  div.className = `alert alert-${type} alert-dismissible fade show`;
  div.role = "alert";
  div.innerHTML = `${message}<button type="button" class="btn-close" data-bs-dismiss="alert"></button>`;
  area.appendChild(div);
  setTimeout(() => div.remove(), 5000);
}

function formatMoney(n) {
  const num = Number(n || 0);
  return "₹" + num.toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}
