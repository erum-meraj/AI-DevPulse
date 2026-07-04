# AI DevPulse — Technical Architecture & Development Specification
**Version:** 2.0
**Status:** Implementation-ready
**Audience:** Coding agents (Claude Code, etc.) and human maintainers

---

## 0. How to Use This Document

This spec is written so a coding agent can implement AI DevPulse **phase by phase, file by file**, without needing to guess. Each phase lists:
- Exact files to create
- Exact interfaces/signatures
- Exact acceptance criteria ("Definition of Done")
- Explicit dependencies on prior phases

**Rule for the coding agent:** Do not start Phase N+1 until every "Definition of Done" item in Phase N is checked off and tests pass. If something in this spec is ambiguous, stop and ask rather than guessing — but this version has been written specifically to remove those ambiguities.

---

## 1. Product Vision (unchanged, clarified)

AI DevPulse is a personal AI research analyst. It ingests AI/software-engineering news from multiple sources, deduplicates and clusters related stories, uses an LLM to explain what happened and why it matters, ranks stories by importance, and delivers a daily digest via web dashboard and Discord.

**Non-goals (explicitly out of scope for v1):**
- No multi-user auth / multi-tenant support in Phase 1–8 (single-user, personal use). Add a `users` table later if needed.
- No mobile app.
- No support for arbitrary user-added RSS feeds in v1 (hardcode the 4 sources; make it extensible in code, but don't build a UI for it yet).
- No payment/billing.

---

## 2. Tech Stack (pinned versions)

Pin versions explicitly so the coding agent doesn't pull incompatible latest releases.

| Layer | Choice | Version constraint |
|---|---|---|
| Backend language | Python | 3.11+ |
| Web framework | FastAPI | ^0.115 |
| Validation | Pydantic | ^2.9 |
| ORM | SQLAlchemy | ^2.0 (async engine, `asyncpg` driver) |
| Migrations | Alembic | ^1.13 |
| DB | PostgreSQL | 15+ with `pgvector` extension |
| Queue/broker | Redis | 7+ |
| Task runner | Celery | ^5.4 (with `redis` as broker + result backend) |
| Scheduler | APScheduler (Phase 1–8), migrate to Celery beat or Temporal later | ^3.10 |
| AI SDKs | `openai`, `anthropic` | latest stable, pinned in lockfile |
| LLM abstraction | `litellm` (optional — see §13.1 decision) | ^1.48 |
| Structured output | `instructor` | ^1.5 |
| Embeddings | OpenAI `text-embedding-3-small` (1536 dims) | — |
| Frontend | Next.js 14 (App Router), TypeScript, Tailwind, shadcn/ui | — |
| Config | `pydantic-settings` | ^2.5 |
| Logging | `structlog` | ^24.4 |
| Testing | `pytest`, `pytest-asyncio`, `factory-boy`, `faker` | latest |
| Lint/format/type | `ruff`, `black`, `mypy` | latest, enforced via pre-commit |
| Package manager | `uv` (recommended) or `poetry` — pick one, don't mix | — |

**Deployment:** Frontend → Vercel. Backend → Railway. DB → Supabase (Postgres + pgvector enabled) or Railway Postgres. Redis → Upstash. All secrets via environment variables, never committed.

### 13.1 Decision: LiteLLM vs direct SDKs
Use **direct `openai` and `anthropic` SDKs** wrapped behind your own `AIProvider` interface (see §13.2), not LiteLLM, for Phase 1. Reason: fewer abstraction layers to debug while the core pipeline is being built. Revisit LiteLLM only if you need >2 providers with automatic failover in production. This removes a real ambiguity from v1 of this doc (it listed both without saying which to actually call).

---

## 3. Repository Structure (complete, with file-level detail)

```
aidevpulse/
├── frontend/                          # Next.js app (Phase 6)
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── package.json
│
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI app factory + startup/shutdown events
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── router.py          # aggregates all v1 routers
│   │   │   │   ├── stories.py
│   │   │   │   ├── clusters.py
│   │   │   │   ├── trends.py
│   │   │   │   ├── daily_brief.py
│   │   │   │   └── dashboard.py
│   │   │   └── deps.py                # shared FastAPI dependencies (DB session, pagination)
│   │   ├── core/
│   │   │   ├── config.py              # Settings(BaseSettings)
│   │   │   ├── logging.py             # structlog setup
│   │   │   ├── exceptions.py          # custom exception classes + handlers
│   │   │   └── constants.py           # thresholds, weights (see §14)
│   │   ├── db/
│   │   │   ├── session.py             # async engine + sessionmaker
│   │   │   └── base.py                # Base declarative class, import hub for Alembic
│   │   ├── models/                    # SQLAlchemy ORM models (1 file per table group)
│   │   │   ├── article.py
│   │   │   ├── cluster.py
│   │   │   ├── topic.py
│   │   │   ├── daily_brief.py
│   │   │   └── trend.py
│   │   ├── schemas/                   # Pydantic request/response schemas
│   │   │   ├── article.py
│   │   │   ├── cluster.py
│   │   │   ├── trend.py
│   │   │   └── daily_brief.py
│   │   ├── repositories/              # DB access only, no business logic
│   │   │   ├── article_repo.py
│   │   │   ├── cluster_repo.py
│   │   │   ├── trend_repo.py
│   │   │   └── daily_brief_repo.py
│   │   ├── services/                  # business logic, orchestrates repos
│   │   │   ├── ingestion_service.py
│   │   │   ├── normalization_service.py
│   │   │   ├── dedup_service.py
│   │   │   ├── embedding_service.py
│   │   │   ├── clustering_service.py
│   │   │   ├── analysis_service.py
│   │   │   ├── ranking_service.py
│   │   │   ├── trend_service.py
│   │   │   ├── daily_brief_service.py
│   │   │   └── ai_provider.py          # thin wrapper around openai/anthropic SDKs
│   │   ├── connectors/                 # one file per external data source
│   │   │   ├── base.py                 # Connector ABC
│   │   │   ├── hackernews.py
│   │   │   ├── openai_rss.py
│   │   │   ├── anthropic_rss.py
│   │   │   └── huggingface_rss.py
│   │   ├── tasks/                      # Celery task definitions (thin, call services)
│   │   │   ├── celery_app.py
│   │   │   ├── ingestion_tasks.py
│   │   │   ├── embedding_tasks.py
│   │   │   ├── clustering_tasks.py
│   │   │   ├── trend_tasks.py
│   │   │   └── brief_tasks.py
│   │   ├── prompts/                    # raw prompt templates, no logic
│   │   │   ├── summarize.md
│   │   │   ├── why_it_matters.md
│   │   │   ├── importance.md
│   │   │   ├── trend.md
│   │   │   └── daily_brief.md
│   │   ├── discord_bot/                # Phase 8
│   │   │   ├── bot.py
│   │   │   └── commands.py
│   │   └── utils/
│   │       ├── datetime_utils.py
│   │       └── text_utils.py
│   ├── alembic/
│   │   ├── versions/
│   │   └── env.py
│   ├── tests/
│   │   ├── conftest.py
│   │   ├── unit/
│   │   └── integration/
│   ├── pyproject.toml
│   └── .env.example
├── infrastructure/
│   ├── docker-compose.yml              # local Postgres+pgvector, Redis
│   └── railway.json
└── docs/
    └── (this file, ADRs, runbooks)
```

**Hard rule:** API routes never import repositories directly, and repositories never import services. Direction is strictly: `api → services → repositories → db`. If the coding agent finds itself importing a repository into an API route file, that's a bug — stop and fix the layering.

---

## 4. Database Schema (exact DDL-level detail)

Run `CREATE EXTENSION IF NOT EXISTS vector;` and `CREATE EXTENSION IF NOT EXISTS "uuid-ossp";` in an early Alembic migration before any tables.

### 4.1 `articles`
| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK, default `gen_random_uuid()` |
| title | TEXT | NOT NULL |
| content | TEXT | NOT NULL |
| summary | TEXT | nullable (filled by AI analysis step) |
| url | TEXT | NOT NULL, UNIQUE |
| source | VARCHAR(50) | NOT NULL, one of `hackernews`, `openai`, `anthropic`, `huggingface` — enforce via Python `Enum`, not DB CHECK, for easy extension |
| external_id | TEXT | nullable — source's native ID (e.g. HN item id), used for idempotent upserts |
| author | TEXT | nullable |
| score | INTEGER | nullable (HN points) |
| comment_count | INTEGER | nullable |
| published_at | TIMESTAMPTZ | NOT NULL |
| created_at | TIMESTAMPTZ | NOT NULL, default `now()` |
| embedding | VECTOR(1536) | nullable until embedding step runs |
| cluster_id | UUID | nullable FK → `story_clusters.id`, `ON DELETE SET NULL` |
| importance | FLOAT | nullable, range 0–100 |
| confidence | VARCHAR(20) | nullable, one of `low`, `medium`, `high`, `very_high` |
| status | VARCHAR(20) | NOT NULL, default `pending` — one of `pending`, `normalized`, `embedded`, `clustered`, `analyzed`, `ranked` |

Indexes: `UNIQUE(url)`, `INDEX(source, external_id)`, `INDEX(cluster_id)`, `INDEX(published_at)`, IVFFlat or HNSW index on `embedding` (create via raw SQL migration: `CREATE INDEX ON articles USING hnsw (embedding vector_cosine_ops);`).

### 4.2 `story_clusters`
| Column | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| title | TEXT | NOT NULL |
| cluster_summary | TEXT | nullable |
| why_it_matters | TEXT | nullable |
| importance | FLOAT | nullable |
| confidence | VARCHAR(20) | nullable |
| sentiment | VARCHAR(20) | nullable, one of `positive`, `neutral`, `negative`, `mixed` |
| discussion_count | INTEGER | default 0 |
| action | VARCHAR(20) | nullable, one of `read_now`, `weekend`, `ignore` (see §14.4) |
| centroid_embedding | VECTOR(1536) | nullable — running centroid of member articles, recomputed on each new member |
| created_at | TIMESTAMPTZ | default `now()` |
| updated_at | TIMESTAMPTZ | default `now()`, updated on change |

### 4.3 `topics` and `article_topics`
Standard many-to-many. `topics(id, name UNIQUE, description)`. `article_topics(article_id FK, topic_id FK, PRIMARY KEY(article_id, topic_id))`.

### 4.4 `daily_briefs`
| Column | Type |
|---|---|
| id | UUID PK |
| date | DATE, UNIQUE NOT NULL |
| summary | TEXT |
| estimated_read_time_minutes | INTEGER |
| stories_analyzed | INTEGER |
| stories_filtered | INTEGER |
| stories_selected | INTEGER |
| top_cluster_ids | UUID[] — ordered array of `story_clusters.id` |
| created_at | TIMESTAMPTZ default now() |

### 4.5 `trends`
| Column | Type |
|---|---|
| id | UUID PK |
| name | TEXT UNIQUE |
| mentions_today | INTEGER |
| mentions_7d_avg | FLOAT |
| growth_rate | FLOAT — `(mentions_today - mentions_7d_avg) / max(mentions_7d_avg, 1)` |
| status | VARCHAR(20) — one of `exploding`, `rising`, `stable`, `declining` (thresholds in §15) |
| updated_at | TIMESTAMPTZ |

**Definition of Done for Phase 1 (DB + models + repos):**
- [ ] All 5 tables created via Alembic migrations, migrations run cleanly on a fresh DB (`alembic upgrade head`)
- [ ] `vector` extension enabled, HNSW index created
- [ ] SQLAlchemy models match schema exactly, all with type hints
- [ ] One repository per table with methods: `create`, `get_by_id`, `update`, `delete`, `list` (paginated), plus table-specific methods (e.g. `ArticleRepository.get_by_url`, `.get_unembedded`, `.get_unclustered`)
- [ ] Repositories are 100% async, use `AsyncSession`, no raw SQL except the vector similarity query
- [ ] Unit tests for every repository method using a test DB (via `pytest-asyncio` + transactional rollback fixture)

---

## 5. Connector Interface (removes ambiguity in "Ingestion Pipeline")

```python
# app/connectors/base.py
from abc import ABC, abstractmethod
from app.schemas.article import RawArticle

class Connector(ABC):
    source_name: str

    @abstractmethod
    async def fetch(self) -> list[RawArticle]:
        """Fetch raw items since last run. Must be idempotent — safe to call repeatedly."""
        ...
```

`RawArticle` is a Pydantic model with fields: `external_id: str`, `title: str`, `content: str`, `url: str`, `author: str | None`, `score: int | None`, `comment_count: int | None`, `published_at: datetime`.

**Per-connector rules:**
- `HackerNewsConnector`: pull top/new story IDs from `https://hacker-news.firebaseio.com/v0/topstories.json`, fetch item details individually, filter to items whose `url` domain matches an AI-relevance allowlist OR whose title matches AI keyword regex (list keywords in `constants.py`) — HN's firehose is not filtered by source, so DevPulse must filter by content.
- `OpenAIRSSConnector` / `AnthropicRSSConnector` / `HuggingFaceRSSConnector`: use `feedparser`, map RSS fields to `RawArticle`. `content` = full entry body if available, else `summary`.
- All connectors must set a realistic `User-Agent` header and respect a 10s timeout with 2 retries (exponential backoff) via `tenacity`.
- Rate limit: no more than 1 request/second to any single host.

**Ingestion service** (`ingestion_service.py`) responsibilities:
1. Loop over all registered connectors.
2. For each fetched `RawArticle`, check `ArticleRepository.get_by_url()` — if exists, skip (idempotent).
3. Otherwise construct an `Article` ORM row with `status='pending'` and persist.
4. Return counts: `{source: count_new}` for logging.

**Definition of Done for Phase 2:**
- [ ] All 4 connectors implemented and unit-tested with mocked HTTP responses (use `respx` or `pytest-httpx`)
- [ ] Ingestion service correctly dedupes by URL on repeated runs (test this explicitly)
- [ ] Celery task `collect_articles` calls ingestion service and logs structured output
- [ ] APScheduler (or Celery beat) triggers `collect_articles` every 30 minutes

---

## 6. Embedding & Clustering (concrete algorithm, no pseudocode gaps)

### 6.1 Embedding
- `EmbeddingService.embed_article(article: Article) -> list[float]`: concatenate `f"{title}\n\n{content[:2000]}"` (cap content to 2000 chars to control cost), call OpenAI embeddings API, store result on `article.embedding`, set `status='embedded'`.
- Batch articles in groups of 50 per API call using the embeddings endpoint's native batch support (list input), not 50 separate calls.
- Celery task `generate_embeddings` runs every 10 minutes, pulls all `status='normalized'` (or `'pending'` once normalization is trivial — see note) articles.

**Note on normalization step:** Since all connectors already emit the shared `RawArticle`→`Article` schema, "normalization" in this pipeline reduces to: HTML-stripping content (`BeautifulSoup` or `trafilatura`), truncating, and language-detection (drop non-English articles for v1 — use `langdetect`, threshold 0.9 confidence). Implement this in `normalization_service.py` and run it immediately after ingestion, before setting status to `normalized`.

### 6.2 Clustering
Use incremental nearest-neighbor clustering, not batch k-means (batch reclustering would constantly reshuffle cluster IDs, breaking the `cluster_id` FK and the daily brief history).

Algorithm for `ClusteringService.assign_cluster(article: Article)`:
1. Query `story_clusters` for the cluster whose `centroid_embedding` has the highest cosine similarity to `article.embedding`, using pgvector's `<=>` operator (cosine distance), restricted to clusters `updated_at` within the last 7 days (older clusters shouldn't absorb new unrelated articles).
2. If `similarity >= 0.82` (threshold from original spec, kept): assign `article.cluster_id` to that cluster; recompute `centroid_embedding` as the running mean of all member embeddings; increment `discussion_count`; set cluster `updated_at = now()`.
3. Else: create a new `story_clusters` row with `centroid_embedding = article.embedding`, `title = article.title`, `discussion_count = 1`.
4. Set `article.status = 'clustered'`.

**Definition of Done for Phase 3:**
- [ ] Embedding batches correctly, handles API errors with retry, never crashes on a single bad article (isolate failures per-item)
- [ ] Clustering threshold is a named constant in `core/constants.py` (`CLUSTER_SIMILARITY_THRESHOLD = 0.82`), not a magic number in code
- [ ] Test: two near-duplicate articles (cosine similarity > 0.82) land in the same cluster; two unrelated articles do not
- [ ] Centroid recomputation verified correct via unit test (mean of N vectors)

---

## 7. AI Analysis Engine (exact prompt contracts)

Use `instructor` to force structured output — never parse free-text LLM responses with regex.

```python
# app/schemas/analysis.py
from pydantic import BaseModel, Field
from typing import Literal

class ClusterAnalysis(BaseModel):
    summary: str = Field(..., description="2-3 sentences: what happened")
    why_it_matters: str = Field(..., description="2-3 sentences: why engineers should care")
    signals: list[str] = Field(..., description="short bullet reasons this was surfaced, e.g. 'OpenAI release', 'HN trending'")
    developer_impact: dict[Literal["ai_engineers", "backend", "researchers"], Literal["low", "medium", "high"]]
    confidence: Literal["low", "medium", "high", "very_high"]
    sentiment: Literal["positive", "neutral", "negative", "mixed"]
```

`AnalysisService.analyze_cluster(cluster: StoryCluster, member_articles: list[Article]) -> ClusterAnalysis`:
1. Build prompt from `prompts/summarize.md` + `prompts/why_it_matters.md` templates, injecting article titles/content (cap total input to ~6000 tokens — if cluster has >10 articles, sample the 10 highest-score ones).
2. Call `instructor`-patched Anthropic client (`claude-sonnet-4-6` — confirm current model string via the product-self-knowledge check at implementation time, do not hardcode blindly) requesting `response_model=ClusterAnalysis`.
3. Persist fields onto the `story_clusters` row.
4. Set `article.status='analyzed'` for all members.

Store the actual prompt template text in the `.md` files under `prompts/`; the service loads and `.format()`s them. Never inline prompt strings in Python.

**Definition of Done for Phase 4 (part 1):**
- [ ] `instructor` validates every LLM response against `ClusterAnalysis`, retries on validation failure (max 2 retries)
- [ ] Prompts are loaded from files, not hardcoded
- [ ] Test with a mocked LLM client (don't hit real API in unit tests — use a fixture returning a canned `ClusterAnalysis`)
- [ ] Integration test (marked `@pytest.mark.integration`, skipped by default) hits real API once to confirm the contract works end-to-end

---

## 8. Ranking Engine (fully specified formula)

```
score = (
    source_score_normalized * 0.3 +
    popularity_score_normalized * 0.3 +
    trend_score_normalized * 0.2 +
    freshness_score * 0.2
) * 100   # final score in 0-100
```

- `source_score_normalized`: lookup table in `constants.py`: `{openai: 1.0, anthropic: 0.95, huggingface: 0.90, hackernews: 0.80}`. For a cluster, use the max across member articles' sources.
- `popularity_score_normalized`: `min(sum(article.score or 0 for article in members) / 500, 1.0)` — 500 HN points ≈ max normalized popularity; tune this constant after observing real data, but it must exist as a named constant (`POPULARITY_NORMALIZATION_CAP`), not a hardcoded literal in the formula.
- `trend_score_normalized`: from `TrendService`, 0–1 scale based on `growth_rate` (see §9), clipped.
- `freshness_score`: `exp(-hours_since_published / 24)`, where `hours_since_published` = hours since the **most recent** member article's `published_at`.

`RankingService.rank_cluster(cluster) -> float` computes this and writes to `cluster.importance`. Then confidence is derived separately (from the AI analysis step, §7) — importance (numeric ranking) and confidence (LLM's self-assessed certainty) are **two different fields, do not conflate them**. This was ambiguous in v1 of the doc; v2 makes it explicit.

---

## 9. Trend Detection (concrete thresholds)

`TrendService.update_trends()` runs daily:
1. Extract topic/keyword mentions per day (use extracted topics from `topics` table, populated during analysis — add topic extraction to the `ClusterAnalysis` schema as an additional field `topics: list[str]` if not already covered by signals).
2. For each topic: `mentions_today` = count of clustered articles today tagged with that topic. `mentions_7d_avg` = average daily count over trailing 7 days (excluding today).
3. `growth_rate = (mentions_today - mentions_7d_avg) / max(mentions_7d_avg, 1)`.
4. Status thresholds (named constants):
   - `growth_rate > 2.0` → `exploding`
   - `0.5 < growth_rate <= 2.0` → `rising`
   - `-0.3 <= growth_rate <= 0.5` → `stable`
   - `growth_rate < -0.3` → `declining`

---

## 10. Action Recommendation (fixed thresholds, named constants)

```python
IMPORTANCE_READ_NOW_THRESHOLD = 90
IMPORTANCE_WEEKEND_THRESHOLD = 70

def recommend_action(importance: float) -> Literal["read_now", "weekend", "ignore"]:
    if importance > IMPORTANCE_READ_NOW_THRESHOLD:
        return "read_now"
    elif importance > IMPORTANCE_WEEKEND_THRESHOLD:
        return "weekend"
    return "ignore"
```
Written to `cluster.action` immediately after ranking.

---

## 11. Daily Brief Generation

`DailyBriefService.generate_for_date(date: date)`:
1. Query all clusters whose member articles were `published_at` within the target date (or, better, whose `updated_at` fell on that date — pick **published date of newest member article**, documented here to remove ambiguity).
2. Sort by `importance` descending. Take top 8 as `top_cluster_ids` (configurable via `DAILY_BRIEF_TOP_N = 8`).
3. Call LLM once with `prompts/daily_brief.md`, feeding in the top clusters' summaries, to produce an overall narrative `summary` (2-3 paragraphs covering major themes) — this is a separate, cheaper LLM call from per-cluster analysis, not a re-analysis.
4. Compute `stories_analyzed` = total articles ingested that day, `stories_filtered` = those NOT in the top 8's clusters, `stories_selected` = 8 (or fewer if <8 clusters exist).
5. `estimated_read_time_minutes` = `max(1, round(stories_selected * 1.0))` — 1 minute per story, tunable constant.
6. Upsert into `daily_briefs` keyed by `date` (idempotent — re-running for the same day overwrites, doesn't duplicate).

Celery task `generate_daily_brief` scheduled once daily at a fixed hour (default 07:00 in the user's local timezone — timezone is a required setting, not hardcoded).

---

## 12. API Design (exact routes, request/response shapes)

All routes under `/api/v1`. All list endpoints support `?page=1&page_size=20` (default 20, max 100).

| Method | Path | Returns |
|---|---|---|
| GET | `/dashboard` | Summary: today's brief stats, top 3 clusters, trend highlights |
| GET | `/stories` | Paginated list of `story_clusters`, sortable by `importance` (default), `created_at` |
| GET | `/stories/{cluster_id}` | Full cluster detail incl. member articles |
| GET | `/clusters` | Alias of `/stories` for now (kept separate per original spec naming; document as same underlying query) |
| GET | `/trends` | List of trends, sorted by `growth_rate` desc |
| GET | `/daily-brief?date=YYYY-MM-DD` | Defaults to today if no date given |
| GET | `/weekly-report` | Aggregates last 7 `daily_briefs` |

Every response uses a Pydantic response model — never return raw ORM objects or dicts. Errors use a consistent envelope: `{"error": {"code": str, "message": str}}` with proper HTTP status codes, via a global exception handler in `core/exceptions.py`.

**Definition of Done for Phase 5:**
- [ ] Every route has a Pydantic response_model
- [ ] OpenAPI docs auto-generated and reviewed at `/docs`
- [ ] Pagination consistent across all list endpoints
- [ ] Integration tests hit each endpoint against a seeded test DB

---

## 13.2 AI Provider Wrapper

```python
# app/services/ai_provider.py
class AIProvider:
    async def embed(self, texts: list[str]) -> list[list[float]]: ...
    async def complete_structured(self, prompt: str, response_model: type[T], model: str) -> T: ...
```
All AI calls in the codebase go through this class — never call `openai.*` or `anthropic.*` directly from a service. This makes swapping providers or adding retries/caching a one-file change.

---

## 14. Configuration (`core/config.py`)

```python
class Settings(BaseSettings):
    OPENAI_API_KEY: str
    ANTHROPIC_API_KEY: str
    DATABASE_URL: str
    REDIS_URL: str
    DISCORD_BOT_TOKEN: str | None = None
    TIMEZONE: str = "UTC"
    DAILY_BRIEF_HOUR: int = 7
    ENVIRONMENT: Literal["local", "staging", "production"] = "local"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
```
Ship `.env.example` with every key listed but blank/placeholder values. Never commit `.env`.

---

## 15. Discord Bot (Phase 8, concrete commands)

Use `discord.py` with slash commands.
- `/brief` — posts today's daily brief (embed with top 8 clusters, action labels)
- `/trends` — posts current exploding/rising trends
- `/weekly` — posts the weekly report
- `/bookmark <cluster_id>` — saves to a simple `bookmarks` table (add this table: `id, cluster_id FK, created_at`) — this is new vs v1, needed since `/bookmark` was listed as a command but had no backing storage.

Scheduled daily post: bot posts the brief automatically at `DAILY_BRIEF_HOUR` in `TIMEZONE`, formatted per the original example ("Good morning. You missed N stories...").

---

## 16. Testing Strategy (concrete, not just tool names)

- **Unit tests**: one test file per service/repository, mock all external calls (LLM APIs, HTTP fetches). Target: every public method has ≥1 happy-path test and ≥1 edge-case test (empty input, API failure, duplicate).
- **Integration tests**: marked `@pytest.mark.integration`, use a real (local/dockerized) Postgres with pgvector, run in CI on a schedule (not every commit, to control cost if they hit real LLM APIs — but by default they should use mocked LLM responses too; only a small handful of explicitly-marked `@pytest.mark.live` tests hit real APIs).
- **Coverage target**: 90%+ on `services/` and `repositories/`; lower bar (60%+) acceptable on `connectors/` and `discord_bot/` since those are I/O-heavy and harder to meaningfully unit test.
- **Fixtures**: `conftest.py` provides `async_session` (rollback-per-test), `sample_article_factory`, `sample_cluster_factory` via `factory-boy`.

---

## 17. Development Order (Phases, restated with explicit exit criteria)

| Phase | Deliverable | Exit criteria |
|---|---|---|
| 1 | DB, models, repos | §4 Definition of Done met |
| 2 | 4 connectors + ingestion service + Celery task | §5 Definition of Done met |
| 3 | Normalization, embeddings, clustering | §6 Definition of Done met |
| 4 | AI analysis + ranking + trend + action engines | §7 DoD + ranking/trend/action formulas implemented with named constants, unit-tested |
| 5 | FastAPI routes | §12 Definition of Done met |
| 6 | Next.js dashboard consuming the API | Dashboard renders daily brief, story list, trends against a real running backend |
| 7 | Daily brief generation scheduled | Brief auto-generates daily, idempotent re-runs verified |
| 8 | Discord bot | All 4 commands + scheduled post working against a test Discord server |

**Do not parallelize phases with a coding agent** — each phase's services depend on the prior phase's schema and repos being stable. If you want to parallelize, split by *file* within a phase (e.g. all 4 connectors in Phase 2 can be built concurrently by separate agent runs since they don't depend on each other).

---

## 18. Code Quality Gates (enforced, not aspirational)

- Pre-commit hooks run `ruff check --fix`, `black`, `mypy --strict` on `app/`. CI fails the build if any fail.
- No `Any` types except at genuine external-boundary points (raw API JSON parsing), and even then, parse into a Pydantic model immediately.
- Every service method has a docstring describing inputs/outputs/side effects (does it write to DB? call an external API?).
- No prompt strings inline in `.py` files — this is enforced by convention, add a simple grep-based pre-commit check if desired: fail if any `.py` file under `services/` contains a multi-line string longer than N characters that looks like a prompt.

---

## 19. Open Decisions to Confirm Before Coding (do these first)

Before Phase 1 begins, resolve these — each was ambiguous or unspecified in the original doc:
1. **LLM model strings** — confirm current Anthropic/OpenAI model identifiers at build time rather than trusting this doc's memory of them.
2. **Package manager** — `uv` vs `poetry`, pick one for the whole backend.
3. **Timezone** — what timezone should `DAILY_BRIEF_HOUR` default to? (Set in `.env`, not hardcoded.)
4. **Hosting for Postgres** — Supabase vs Railway Postgres — either works, pick based on whichever also hosts pgvector cleanly (both support pgvector as of last check, verify).
5. **English-only filter** — confirmed for v1 (see §6.1); revisit if you want multilingual coverage later.

---

*End of specification. This document should be treated as the single source of truth — if the coding agent's implementation diverges from it, either the code or this doc is wrong; reconcile explicitly rather than letting them drift.*
