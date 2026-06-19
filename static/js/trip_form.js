async function setupDestinationAutocomplete() {
  const input = document.getElementById("destination");
  const list = document.getElementById("autocomplete-list");
  let known = [];
  try {
    const meta = await apiGet("/api/trips/filters_meta/");
    known = meta.destinations || [];
  } catch (e) {}
  input.addEventListener("input", () => {
    const val = input.value.toLowerCase();
    list.innerHTML = "";
    if (!val) return;
    known
      .filter((d) => d.toLowerCase().includes(val))
      .slice(0, 8)
      .forEach((d) => {
        const item = document.createElement("div");
        item.className = "item";
        item.textContent = d;
        item.onclick = () => {
          input.value = d;
          list.innerHTML = "";
        };
        list.appendChild(item);
      });
  });
  document.addEventListener("click", (e) => {
    if (e.target !== input) list.innerHTML = "";
  });
}

async function renderCategoryBudgetGrid() {
  const categories = await apiGet("/api/expenses/categories/");
  const grid = document.getElementById("category-budget-grid");
  grid.innerHTML = categories
    .map(
      (c) => `
    <div class="col-md-4">
      <label class="form-label small mb-0">${c.label}</label>
      <input type="number" step="0.01" min="0" class="form-control form-control-sm cat-budget-input" data-category="${c.value}" placeholder="0">
    </div>`
    )
    .join("");
}

async function loadTripForEdit() {
  if (!TRIP_ID) return;
  const trip = await apiGet(`/api/trips/${TRIP_ID}/`);
  document.getElementById("name").value = trip.name;
  document.getElementById("description").value = trip.description;
  document.getElementById("destination").value = trip.destination;
  document.getElementById("state").value = trip.state;
  document.getElementById("start_date").value = trip.start_date;
  document.getElementById("end_date").value = trip.end_date || "";
  document.getElementById("budget").value = trip.budget || "";
  document.getElementById("default_split_type").value = trip.default_split_type;
  document.getElementById("participants-field").style.display = "none";
  document.getElementById("category-budget-field").style.display = "none";
}

document.getElementById("trip-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const payload = {
    name: document.getElementById("name").value,
    description: document.getElementById("description").value,
    destination: document.getElementById("destination").value,
    state: document.getElementById("state").value,
    start_date: document.getElementById("start_date").value,
    end_date: document.getElementById("end_date").value || null,
    budget: document.getElementById("budget").value || null,
    default_split_type: document.getElementById("default_split_type").value,
  };
  try {
    let trip;
    if (TRIP_ID) {
      trip = await apiPatch(`/api/trips/${TRIP_ID}/`, payload);
    } else {
      const names = document
        .getElementById("participant_names")
        .value.split(",")
        .map((n) => n.trim())
        .filter((n) => n);
      payload.participant_names = names;
      const categoryBudgets = {};
      document.querySelectorAll(".cat-budget-input").forEach((input) => {
        if (input.value) categoryBudgets[input.dataset.category] = input.value;
      });
      if (Object.keys(categoryBudgets).length) payload.category_budgets = categoryBudgets;
      trip = await apiPost("/api/trips/", payload);
    }
    window.location.href = `/trips/${trip.id}/`;
  } catch (err) {
    showToast("Could not save trip: " + JSON.stringify(err.data || {}), "danger");
  }
});

document.addEventListener("DOMContentLoaded", () => {
  setupDestinationAutocomplete();
  renderCategoryBudgetGrid();
  loadTripForEdit();
});
