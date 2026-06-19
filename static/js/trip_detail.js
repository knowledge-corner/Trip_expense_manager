let CATEGORIES = [];
let PARTICIPANTS = [];
let charts = {};

async function loadTripOverview() {
  const trip = await apiGet(`/api/trips/${TRIP_ID}/`);
  document.getElementById("trip-name").textContent = trip.name;
  document.getElementById("trip-meta").textContent =
    `${trip.destination}${trip.state ? ", " + trip.state : ""} | ${trip.start_date}${trip.end_date ? " → " + trip.end_date : ""}`;

  const overBudgetBadge = trip.is_over_budget
    ? '<span class="badge badge-over-budget ms-2">Over Budget!</span>'
    : "";
  document.getElementById("stat-cards").innerHTML = `
    <div class="col-md-3"><div class="card stat-card p-3"><div class="text-muted small">Status</div><div class="fs-5 text-capitalize">${trip.status}</div></div></div>
    <div class="col-md-3"><div class="card stat-card p-3"><div class="text-muted small">Total Spent</div><div class="fs-5">${formatMoney(trip.total_expense)}</div></div></div>
    <div class="col-md-3"><div class="card stat-card p-3"><div class="text-muted small">Budget</div><div class="fs-5">${trip.budget ? formatMoney(trip.budget) : "Not set"}${overBudgetBadge}</div></div></div>
    <div class="col-md-3"><div class="card stat-card p-3"><div class="text-muted small">Travellers</div><div class="fs-5">${trip.participants.length}</div></div></div>
  `;
  PARTICIPANTS = trip.participants;
  populateParticipantSelect();
  renderParticipantList();
}

function populateParticipantSelect() {
  const sel = document.getElementById("exp-paid-by");
  sel.innerHTML = '<option value="">--</option>' + PARTICIPANTS.map((p) => `<option value="${p.id}">${p.name}</option>`).join("");
}

async function loadCategories() {
  CATEGORIES = await apiGet("/api/expenses/categories/");
  const opts = CATEGORIES.map((c) => `<option value="${c.value}">${c.label}</option>`).join("");
  document.getElementById("exp-category").innerHTML = opts;
  document.getElementById("exp-filter-category").innerHTML = '<option value="">All Categories</option>' + opts;
}

async function loadExpenses() {
  const params = new URLSearchParams({ trip: TRIP_ID });
  const cat = document.getElementById("exp-filter-category").value;
  const search = document.getElementById("exp-filter-search").value;
  if (cat) params.set("category", cat);
  if (search) params.set("search", search);
  const data = await apiGet("/api/expenses/?" + params.toString());
  const rows = data.results || data;
  document.getElementById("expense-rows").innerHTML = rows
    .map(
      (e) => `
    <tr class="expense-row">
      <td>${e.date}</td>
      <td>${e.category_display}</td>
      <td>${e.description || ""}</td>
      <td>${e.location || ""}</td>
      <td>${e.paid_by_name || "-"}</td>
      <td class="text-capitalize">${e.split_type}</td>
      <td class="text-end">${formatMoney(e.amount)}</td>
      <td>
        <button class="btn btn-sm btn-outline-secondary" onclick='editExpense(${JSON.stringify(e)})'><i class="bi bi-pencil"></i></button>
        <button class="btn btn-sm btn-outline-danger" onclick="deleteExpense(${e.id})"><i class="bi bi-trash"></i></button>
      </td>
    </tr>`
    )
    .join("");
}

function renderCustomSplitArea() {
  const area = document.getElementById("custom-split-area");
  area.innerHTML = PARTICIPANTS.map(
    (p) => `
    <div class="input-group input-group-sm mb-1">
      <span class="input-group-text" style="width:120px;">${p.name}</span>
      <input type="number" step="0.01" class="form-control split-amount" data-participant="${p.id}">
    </div>`
  ).join("");
}

document.getElementById("exp-split-type").addEventListener("change", (e) => {
  const area = document.getElementById("custom-split-area");
  if (e.target.value === "custom") {
    renderCustomSplitArea();
    area.classList.remove("d-none");
  } else {
    area.classList.add("d-none");
  }
});

function openExpenseModal() {
  document.getElementById("expense-form").reset();
  document.getElementById("exp-id").value = "";
  document.getElementById("custom-split-area").classList.add("d-none");
  document.getElementById("exp-date").value = new Date().toISOString().slice(0, 10);
}

function editExpense(e) {
  document.getElementById("exp-id").value = e.id;
  document.getElementById("exp-category").value = e.category;
  document.getElementById("exp-amount").value = e.amount;
  document.getElementById("exp-date").value = e.date;
  document.getElementById("exp-description").value = e.description || "";
  document.getElementById("exp-location").value = e.location || "";
  document.getElementById("exp-paid-by").value = e.paid_by || "";
  document.getElementById("exp-split-type").value = e.split_type;
  if (e.split_type === "custom") {
    renderCustomSplitArea();
    document.getElementById("custom-split-area").classList.remove("d-none");
    e.splits.forEach((s) => {
      const input = document.querySelector(`.split-amount[data-participant="${s.participant}"]`);
      if (input) input.value = s.amount;
    });
  } else {
    document.getElementById("custom-split-area").classList.add("d-none");
  }
  new bootstrap.Modal(document.getElementById("expenseModal")).show();
}

async function deleteExpense(id) {
  if (!confirm("Delete this expense?")) return;
  await apiDelete(`/api/expenses/${id}/`);
  showToast("Expense deleted");
  refreshAll();
}

document.getElementById("expense-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const id = document.getElementById("exp-id").value;
  const splitType = document.getElementById("exp-split-type").value;
  const payload = {
    trip: TRIP_ID,
    category: document.getElementById("exp-category").value,
    amount: document.getElementById("exp-amount").value,
    date: document.getElementById("exp-date").value,
    description: document.getElementById("exp-description").value,
    location: document.getElementById("exp-location").value,
    paid_by: document.getElementById("exp-paid-by").value || null,
    split_type: splitType,
  };
  if (splitType === "custom") {
    payload.splits = Array.from(document.querySelectorAll(".split-amount"))
      .filter((i) => i.value)
      .map((i) => ({ participant: Number(i.dataset.participant), amount: i.value }));
  }
  try {
    if (id) {
      await apiPatch(`/api/expenses/${id}/`, payload);
    } else {
      await apiPost("/api/expenses/", payload);
    }
    bootstrap.Modal.getInstance(document.getElementById("expenseModal")).hide();
    showToast("Expense saved");
    refreshAll();
  } catch (err) {
    showToast("Error: " + JSON.stringify(err.data || {}), "danger");
  }
});

async function setupExpenseLocationAutocomplete() {
  const input = document.getElementById("exp-location");
  const list = document.getElementById("exp-autocomplete-list");
  input.addEventListener("input", async () => {
    const val = input.value.trim();
    list.innerHTML = "";
    if (!val) return;
    const data = await apiGet(`/api/expenses/?trip=${TRIP_ID}&search=${encodeURIComponent(val)}`);
    const rows = data.results || data;
    const locations = [...new Set(rows.map((r) => r.location).filter(Boolean))];
    locations.slice(0, 6).forEach((loc) => {
      const item = document.createElement("div");
      item.className = "item";
      item.textContent = loc;
      item.onclick = () => {
        input.value = loc;
        list.innerHTML = "";
      };
      list.appendChild(item);
    });
  });
}

async function loadAnalytics() {
  const data = await apiGet(`/api/trips/${TRIP_ID}/analytics/`);
  Object.values(charts).forEach((c) => c && c.destroy());

  charts.category = new Chart(document.getElementById("chart-category"), {
    type: "pie",
    data: {
      labels: data.by_category.map((c) => c.category_display),
      datasets: [{ data: data.by_category.map((c) => c.total), backgroundColor: palette(data.by_category.length) }],
    },
    options: { plugins: { title: { display: true, text: "Spend by Category" } } },
  });

  charts.daily = new Chart(document.getElementById("chart-daily"), {
    type: "bar",
    data: {
      labels: data.by_date.map((d) => d.date),
      datasets: [{ label: "Daily Spend", data: data.by_date.map((d) => d.total), backgroundColor: "#6366f1" }],
    },
    options: { plugins: { title: { display: true, text: "Daily Spend" } } },
  });

  charts.participant = new Chart(document.getElementById("chart-participant"), {
    type: "bar",
    data: {
      labels: data.by_participant.map((p) => p.paid_by__name),
      datasets: [{ label: "Paid by", data: data.by_participant.map((p) => p.total), backgroundColor: "#ec4899" }],
    },
    options: { indexAxis: "y", plugins: { title: { display: true, text: "Who Paid How Much" } } },
  });
}

function palette(n) {
  const colors = ["#6366f1", "#ec4899", "#f59e0b", "#10b981", "#3b82f6", "#ef4444", "#8b5cf6", "#14b8a6", "#f97316", "#84cc16"];
  return Array.from({ length: n }, (_, i) => colors[i % colors.length]);
}

function openReviewModal() {
  document.getElementById("review-form").reset();
}

document.getElementById("review-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const payload = {
    trip: TRIP_ID,
    place_name: document.getElementById("rev-place-name").value,
    place_type: document.getElementById("rev-place-type").value,
    location: document.getElementById("rev-location").value,
    rating: document.getElementById("rev-rating").value,
    amount_spent: document.getElementById("rev-amount").value || null,
    review_text: document.getElementById("rev-text").value,
    would_revisit: document.getElementById("rev-would-revisit").checked,
    alternative_suggestion: document.getElementById("rev-alternative").value,
  };
  try {
    await apiPost("/api/reviews/", payload);
    bootstrap.Modal.getInstance(document.getElementById("reviewModal")).hide();
    showToast("Review added");
    loadReviews();
  } catch (err) {
    showToast("Error: " + JSON.stringify(err.data || {}), "danger");
  }
});

async function loadReviews() {
  const data = await apiGet(`/api/reviews/?trip=${TRIP_ID}`);
  const rows = data.results || data;
  document.getElementById("review-cards").innerHTML = rows
    .map(
      (r) => `
    <div class="col-md-4">
      <div class="card trip-card p-3">
        <div class="d-flex justify-content-between">
          <h6 class="fw-bold">${r.place_name}</h6>
          <button class="btn btn-sm btn-outline-danger" onclick="deleteReview(${r.id})"><i class="bi bi-trash"></i></button>
        </div>
        <div class="small text-muted text-capitalize">${r.place_type} · ${r.location || ""}</div>
        <div>${"★".repeat(r.rating)}${"☆".repeat(5 - r.rating)}</div>
        ${r.amount_spent ? `<div class="small">Spent: ${formatMoney(r.amount_spent)}</div>` : ""}
        <p class="small mt-1">${r.review_text || ""}</p>
        ${r.alternative_suggestion ? `<div class="small text-warning">Try instead: ${r.alternative_suggestion}</div>` : ""}
      </div>
    </div>`
    )
    .join("");
}

async function deleteReview(id) {
  if (!confirm("Delete this review?")) return;
  await apiDelete(`/api/reviews/${id}/`);
  loadReviews();
}

function renderParticipantList() {
  document.getElementById("participant-list").innerHTML = PARTICIPANTS.map(
    (p) => `<li class="list-group-item d-flex justify-content-between align-items-center">${p.name}
      <button class="btn btn-sm btn-outline-danger" onclick="deleteParticipant(${p.id})"><i class="bi bi-x"></i></button></li>`
  ).join("");
}

async function addParticipantPrompt() {
  const name = prompt("Traveller name:");
  if (!name) return;
  await apiPost("/api/participants/", { trip: TRIP_ID, name });
  loadTripOverview();
}

async function deleteParticipant(id) {
  if (!confirm("Remove this traveller?")) return;
  await apiDelete(`/api/participants/${id}/`);
  loadTripOverview();
}

async function deleteTrip() {
  if (!confirm("Delete this trip and all its expenses/reviews? This cannot be undone.")) return;
  await apiDelete(`/api/trips/${TRIP_ID}/`);
  window.location.href = "/";
}

function refreshAll() {
  loadTripOverview();
  loadExpenses();
  loadAnalytics();
}

document.getElementById("import-form").addEventListener("submit", () => {
  // Standard form POST (multipart), browser will navigate back to this page.
});

document.addEventListener("DOMContentLoaded", async () => {
  await loadCategories();
  await loadTripOverview();
  setupExpenseLocationAutocomplete();
  loadExpenses();
  loadReviews();
  document.getElementById("tripTabs").addEventListener("shown.bs.tab", (e) => {
    if (e.target.dataset.bsTarget === "#tab-analytics") loadAnalytics();
  });
});
