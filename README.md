# AI-DevPulse

tasks left:

- emerging trends is dummy 
- reading time is dummy 
- trust metrics and intelligence brief say 0 stories 
- find if the trust metrics values rae updated in the db 
- the pages made on nav bar are dummy, the papers fetch is done but the page is not created yet 
- connect papers to hugging face paper of the day (https://huggingface.co/papers)
- papers table is empty in the db
- action items -> dummhy values
- change theme of the site
- the top stories are not changed even if i read the article, new articles are fetched the next day but the top stories still shows stories from 2-3 days back


# Running AI DevPulse Locally

This section covers everything needed to get the full stack running on a fresh machine boot: database, cache, backend API, background worker, scheduler, and frontend.

## Prerequisites (one-time setup)

- Docker Desktop installed and the daemon running (check the whale icon in your system tray)
- Python 3.12 with the project's `.venv` created and dependencies installed
- Node.js for the frontend
- A `.env` file in `backend/` with real values (copy from `.env.example`):
  - `AICREDITS_API_KEY`
  - `DATABASE_URL`, `REDIS_URL` (defaults match docker-compose, usually don't need to change)
  - `EMAIL_ADDRESS`, `EMAIL_APP_PASSWORD` (Gmail App Password, requires 2-Step Verification enabled), `EMAIL_TO`
  - `TIMEZONE`, `DAILY_BRIEF_HOUR`

## Every time you want to run the app

Open **four separate terminals**. Do not reuse a terminal that's running a long-lived process for anything else — it will kill that process.

### 1. Infrastructure (Postgres + Redis)

```powershell
cd D:\code\AI-DevPulse\infrastructure
docker-compose up
```

Confirm it's actually up before moving on:
```powershell
docker ps
```
You should see postgres and redis containers with their ports mapped. If `docker-compose up` fails with a daemon connection error, Docker Desktop itself isn't running — launch it from the Start menu and wait ~30-60s before retrying.

### 2. Celery worker (background tasks)

```powershell
cd D:\code\AI-DevPulse\backend
celery -A app.tasks.celery_app worker --loglevel=info --pool=solo
```

`--pool=solo` is required on Windows. On startup, check the `[tasks]` section of the banner — it should list all task modules (ingestion, embedding, clustering, analysis, trend, brief, paper, ranking). If it's empty, tasks won't run even though the worker looks alive.

This single worker also runs the scheduler (APScheduler triggers Celery tasks via `.delay()` on a timer) — no separate scheduler process needed. Once running, ingestion/embedding/clustering/analysis/ranking/trends/daily brief/papers all fire automatically on their configured schedules with no further action needed.

**Caution:** Manually triggering `re_rank_recent_clusters` or `generate_daily_brief` sends a real email every time. Safe to manually trigger for testing: `collect_articles`, `generate_embeddings`, `cluster_articles`, `analyze_and_rank_clusters`, `update_trends`, `collect_papers`.

### 3. Backend API server

```powershell
cd D:\code\AI-DevPulse\backend
uvicorn app.main:app --reload
```

Starting this also starts the scheduler a second time via `main.py`'s `on_startup` hook — this is expected, both the worker and the API process run their own scheduler instance, but only one set of Celery tasks actually executes per firing since they're deduplicated by Celery/Redis, not by the scheduler.

Confirm it's healthy: `http://localhost:8000/health` should return `{"status": "ok"}`.

### 4. Frontend

```powershell
cd D:\code\AI-DevPulse\frontend
npm run dev
```

Open `http://localhost:3000`.

## One-time / occasional commands

**Run DB migrations** (after pulling new model changes):
```powershell
cd D:\code\AI-DevPulse\backend
alembic upgrade head
```

**Seed paper relevance weights** (safe to re-run, upserts):
```powershell
cd D:\code\AI-DevPulse\backend
python -m scripts.seed_paper_weights
```

**Manually trigger a task** for testing (replace the import/task name as needed):
```powershell
python -c "
from app.tasks.trend_tasks import update_trends
r = update_trends.delay()
print('Task ID:', r.id)
"
```
Don't rely on `.get()` to confirm success — check the worker's terminal/log output for the actual `..._completed` line and `succeeded` status instead, since `.get()` can time out on a busy queue even when the task eventually succeeds.

## Shutting down

Ctrl+C in each of the four terminals (worker may take a second press). `docker-compose down` if you also want to stop Postgres/Redis, or leave `docker-compose up` running between sessions if convenient.