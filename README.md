# Stage 1 — Sample App: React + Django + Redis + MongoDB Atlas

This is a minimal but fully working **Task Board** app that demonstrates the
Stage 1 stack end-to-end:

- **Frontend:** React (Vite)
- **Backend:** Django + Django REST Framework
- **Primary database:** MongoDB Atlas (accessed via PyMongo)
- **Middleware / cache:** Redis (caches the task list for a few seconds,
  invalidated on every write)

This is intentionally scoped to Stage 1 only — no Docker, Jenkins,
Kubernetes, or Terraform yet. Those come in later stages and will build on
top of this same `frontend/` and `backend/` folder structure, so keep the
layout as-is.

```
stage1-app/
├── backend/          # Django + DRF API
│   ├── backend/       # Django project (settings, urls)
│   ├── tasks/          # Django app: Mongo + Redis logic, CRUD API
│   ├── manage.py
│   ├── requirements.txt
│   └── .env.example
└── frontend/          # React (Vite) app
    ├── src/
    ├── package.json
    └── .env.example
```

## How the pieces fit together

- Django does **not** use its ORM for application data. MongoDB Atlas is
  talked to directly through PyMongo (`backend/tasks/mongo.py`). Django's
  ORM is SQL-oriented, so mixing it with Mongo tends to cause more problems
  than it solves — a thin PyMongo data-access layer is simpler and more
  reliable.
- Django still keeps a small local SQLite file purely so its built-in apps
  (admin, auth, sessions) have somewhere to store their own internal
  tables. It is **not** used for your task data.
- Redis sits in front of the `GET /api/tasks/` endpoint as a cache. Reads
  hit Redis first; on a cache miss it reads MongoDB Atlas and repopulates
  the cache. Any create/update/delete invalidates the cache.

## Prerequisites

- Python 3.11+
- Node.js 18+
- A MongoDB Atlas cluster (free tier is fine) — https://www.mongodb.com/cloud/atlas/register
  - Create a database user, and allow your IP (or `0.0.0.0/0` for local dev)
    under Network Access.
  - Copy the connection string from **Connect → Drivers → Python**.
- Redis running locally. Easiest option if you have Docker:
  ```bash
  docker run -d --name redis-stage1 -p 6379:6379 redis:7-alpine
  ```
  Or install Redis natively (`brew install redis`, `sudo apt install redis-server`, etc.)
  and run `redis-server`.

## 1. Backend setup (Django)

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# now edit .env and fill in:
#   MONGO_URI=<your Atlas connection string>
#   (defaults are fine for REDIS_HOST/PORT if using the docker command above)

python manage.py migrate        # sets up Django's internal SQLite tables
python manage.py runserver 0.0.0.0:8000
```

Verify it's working:

```bash
curl http://localhost:8000/api/health/
# {"api": "ok", "mongodb": "ok", "redis": "ok"}
```

If `mongodb` shows an error, double check `MONGO_URI` in `.env` and that
your current IP is allow-listed in Atlas Network Access. If `redis` shows
an error, make sure the Redis container/service is running on port 6379.

## 2. Frontend setup (React)

In a **new terminal**:

```bash
cd frontend
npm install

cp .env.example .env
# defaults already point to http://localhost:8000/api, only change this
# if your backend runs somewhere else

npm run dev
```

Vite will print a local URL, normally **http://localhost:5173**. Open it in
a browser — you should see the Task Board UI. Add a task, refresh, and
you'll see the "list served from: cache" badge for a few seconds (per
`REDIS_CACHE_TTL_SECONDS` in `backend/.env`) before it goes back to hitting
the database.

## API reference

| Method | Endpoint            | Description                          |
|--------|----------------------|---------------------------------------|
| GET    | `/api/health/`        | Checks API, Mongo, and Redis status  |
| GET    | `/api/tasks/`         | List all tasks (cached in Redis)     |
| POST   | `/api/tasks/`         | Create a task, body: `{"title": "..."}` |
| PUT    | `/api/tasks/<id>/`    | Update a task, body: `{"title": "...", "completed": true}` |
| DELETE | `/api/tasks/<id>/`    | Delete a task                        |

## Troubleshooting

- **CORS errors in the browser console:** confirm `CORS_ALLOWED_ORIGIN` in
  `backend/.env` matches the URL Vite is actually running on.
- **`MONGO_URI is not set` error:** you likely forgot to copy `.env.example`
  to `.env` in `backend/`, or forgot to restart `runserver` after editing it.
- **Redis connection refused:** confirm `docker ps` shows the `redis-stage1`
  container running, or that `redis-server` is active locally.

## What's next (later stages, not part of this deliverable)

- **Stage 2:** Dockerize `frontend/` and `backend/` into separate images,
  push to Docker Hub, automate the build/push with Jenkins, and deploy on
  Kubernetes for load balancing and scaling.
- **Stage 3:** Provision AWS infrastructure with Terraform — a VPC with
  public/private subnets, S3 for static assets, and Lambda-based API
  endpoints.
