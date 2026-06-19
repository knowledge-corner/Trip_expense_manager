async function loadFiltersMeta() {
  const meta = await apiGet("/api/trips/filters_meta/");
  const yearSel = document.getElementById("f-year");
  meta.years.forEach((y) => {
    const opt = document.createElement("option");
    opt.value = y;
    opt.textContent = y;
    yearSel.appendChild(opt);
  });
  const stateSel = document.getElementById("f-state");
  meta.states.forEach((s) => {
    const opt = document.createElement("option");
    opt.value = s;
    opt.textContent = s;
    stateSel.appendChild(opt);
  });
}

function statusBadge(status) {
  return `<span class="badge badge-status-${status} text-capitalize">${status}</span>`;
}

async function loadTrips() {
  const params = new URLSearchParams();
  const search = document.getElementById("f-search").value;
  const year = document.getElementById("f-year").value;
  const state = document.getElementById("f-state").value;
  const status = document.getElementById("f-status").value;
  const ordering = document.getElementById("f-ordering").value;
  if (search) params.set("search", search);
  if (year) params.set("year", year);
  if (state) params.set("state", state);
  if (status) params.set("status", status);
  if (ordering) params.set("ordering", ordering);

  const data = await apiGet("/api/trips/?" + params.toString());
  const container = document.getElementById("trip-list");
  const trips = data.results || data;
  if (!trips.length) {
    container.innerHTML = '<p class="text-muted">No trips found. Create your first trip!</p>';
    return;
  }
  container.innerHTML = trips
    .map((t) => {
      const overBudget = t.is_over_budget
        ? '<span class="badge badge-over-budget">Over budget!</span>'
        : "";
      return `
      <div class="col-md-4">
        <div class="card trip-card">
          <div class="card-img-top-placeholder"></div>
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-start">
              <h5 class="card-title mb-1">${t.name}</h5>
              ${statusBadge(t.status)}
            </div>
            <p class="text-muted small mb-1"><i class="bi bi-geo-alt"></i> ${t.destination}${t.state ? ", " + t.state : ""}</p>
            <p class="small mb-2">${t.start_date} ${t.end_date ? "→ " + t.end_date : ""}</p>
            <p class="mb-1">Spent: <strong>${formatMoney(t.total_expense)}</strong>${t.budget ? " / " + formatMoney(t.budget) : ""} ${overBudget}</p>
            <a href="/trips/${t.id}/" class="btn btn-sm btn-primary mt-2">View Trip</a>
          </div>
        </div>
      </div>`;
    })
    .join("");
}

document.addEventListener("DOMContentLoaded", () => {
  loadFiltersMeta();
  loadTrips();
});
