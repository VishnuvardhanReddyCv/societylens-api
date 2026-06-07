# societylens-api

FastAPI backend for **SocietyLens** — a multi-tenant apartment maintenance management platform for Indian apartment communities.

## Quick Start

```bash
# 1. Create and activate virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env — set DATABASE_URL and SECRET_KEY

# 4. Run migrations
alembic upgrade head

# 5. Seed sample data
python seed.py

# 6. Start development server
uvicorn app.main:app --reload
```

API docs: http://localhost:8000/docs  
ReDoc: http://localhost:8000/redoc

## Seed Credentials

| Role   | Email                  | Password  | Unit  |
|--------|------------------------|-----------|-------|
| Admin  | admin@prestige.com     | admin123  | —     |
| Tenant | anjali@prestige.com    | tenant123 | B-204 |
| Tenant | suresh@prestige.com    | tenant123 | B-102 |
| Tenant | priya@prestige.com     | tenant123 | A-301 |

Invite code: **482910**

## Project Structure

```
app/
  main.py          — FastAPI app, CORS, router registration
  database.py      — async SQLAlchemy engine + session
  models/          — SQLAlchemy ORM models
  schemas/         — Pydantic v2 request/response schemas
  routers/         — one file per domain
  core/            — config, security, dependencies
  services/        — all business logic (routers call services)
alembic/           — database migrations
seed.py            — sample data
```

## API Overview

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | /api/auth/register | — | Create complex + admin |
| POST | /api/auth/join | — | Join via invite code |
| POST | /api/auth/login | — | Login |
| GET | /api/auth/me | Bearer | Current user |
| GET | /api/expenses | Bearer | List expenses |
| POST | /api/expenses | Admin | Create expense |
| POST | /api/expenses/{id}/vote | Bearer | Cast vote |
| GET | /api/issues | Bearer | List issues |
| POST | /api/issues | Bearer | Create issue |
| PATCH | /api/issues/{id} | Admin | Update status |
| GET | /api/announcements | Bearer | List announcements |
| POST | /api/announcements | Admin | Create announcement |
| GET | /api/admin/summary | Admin | Financial + issues summary |
| GET | /api/admin/tenants | Admin | List tenants |
| PATCH | /api/admin/invite | Admin | Regenerate invite code |
| PATCH | /api/admin/settings | Admin | Update complex details |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | PostgreSQL async URL (`postgresql+asyncpg://...`) |
| `SECRET_KEY` | JWT signing secret |
| `ALGORITHM` | JWT algorithm (default: HS256) |
| `ACCESS_TOKEN_EXPIRE_DAYS` | Token TTL (default: 7) |
| `FRONTEND_URL` | Allowed CORS origin |

## Deploy to Railway

1. Push to GitHub
2. Create new Railway project → Deploy from GitHub
3. Add PostgreSQL plugin
4. Set environment variables in Railway dashboard
5. Railway uses `Procfile` automatically: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

## Future Roadmap

### Phase 2 — Razorpay Payments
- `Expense.amount` is `NUMERIC(10,2)` — Razorpay-ready
- `ApartmentComplex.payment_status` placeholder column exists
- Extend `app/services/finance_service.py` for webhook handlers

### Phase 3 — Push Notifications
- `device_tokens` table already migrated
- All notification triggers go through `app/services/notification_service.py` stub
- Replace logger calls with FCM/APNs SDK calls

### Phase 4 — React Native Mobile App
- Fully stateless JWT API — no sessions
- All list endpoints paginated via `?skip=&limit=`
- Consistent `{ data, meta }` envelope on all list responses

### Phase 5 — Contractor Rating System
- `contractors` and `contractor_reviews` tables already migrated
- `expenses.contractor_id` FK exists
- Extend `app/routers/contractors.py`
