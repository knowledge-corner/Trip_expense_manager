# Trip Expense Manager

Django REST Framework backend with Django Template Language frontend (so the same
REST API can later power an Android app).

## Apps
- `trips` — Trip and TripParticipant models, trip CRUD, analytics endpoint, home/detail pages
- `expenses` — Expense and ExpenseSplit models, category choices, equal/custom split logic
- `reviews` — PlaceReview model for restaurant/hotel/attraction reviews with ratings and alternatives
- `core` — Excel backup/restore (full DB) and per-trip expense bulk import
- `accounts` — login/signup/logout

## Setup
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Key features
- Trip CRUD with budget, destination/state, start/end dates, traveller list, single-payer or split-by-default.
- Expense logging with categories (hotel, food, toll, fuel, shopping, entertainment, adventure,
  sightseeing, flight/train/bus/cab/boat/metro, parking, misc), per-expense split type
  (single / equal / custom), destination & location autocomplete from existing data.
- Home page filters: search, year, state, status (upcoming/ongoing/completed), ordering.
- Trip detail page: tabs for Expenses, Analytics (pie + bar charts via Chart.js), Reviews, Travellers.
- Budget exceeded is highlighted on the trip detail page.
- Place reviews: rating, amount spent, review text, "better alternative nearby" field.
- Admin-only Excel full-database backup/restore (`/backup/`) for safe SQLite → MySQL migration.
- Per-trip Excel expense bulk import (`/backup/expense-template/` + upload on trip page) for
  loading historical expenses.

## Migrating to MySQL later
1. Download a full backup from `/backup/` (admin only).
2. Point `DATABASES` in `config/settings.py` to MySQL and run `python manage.py migrate`.
3. Restore the backup file from `/backup/` with "clear existing data" checked once on the new DB.
