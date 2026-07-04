"""All tunable thresholds and magic numbers live here, per spec §18.
Never inline these values in services — import from this module instead.
"""

# --- Clustering (spec §6.2) ---
CLUSTER_SIMILARITY_THRESHOLD = 0.82
CLUSTER_CANDIDATE_LOOKBACK_DAYS = 7

# --- Ranking (spec §8) ---
SOURCE_SCORE = {
    "openai": 1.0,
    "anthropic": 0.95,
    "huggingface": 0.90,
    "hackernews": 0.80,
}
POPULARITY_NORMALIZATION_CAP = 500  # HN points considered "max" popularity
RANKING_WEIGHTS = {
    "source": 0.3,
    "popularity": 0.3,
    "trend": 0.2,
    "freshness": 0.2,
}
FRESHNESS_DECAY_HOURS = 24

# --- Trend detection (spec §9) ---
TREND_EXPLODING_THRESHOLD = 2.0
TREND_RISING_THRESHOLD = 0.5
TREND_STABLE_LOWER_BOUND = -0.3

# --- Action recommendation (spec §10) ---
IMPORTANCE_READ_NOW_THRESHOLD = 90
IMPORTANCE_WEEKEND_THRESHOLD = 70

# --- Daily brief (spec §11) ---
DAILY_BRIEF_TOP_N = 8
DAILY_BRIEF_MINUTES_PER_STORY = 1.0

# --- Normalization (spec §6.1) ---
MAX_CONTENT_CHARS_FOR_EMBEDDING = 2000
LANGUAGE_DETECTION_CONFIDENCE_THRESHOLD = 0.9

# --- Embedding ---
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSIONS = 1536
EMBEDDING_BATCH_SIZE = 50

# --- AI analysis (spec §7) ---
ANALYSIS_MODEL = "claude-sonnet-4-6"
ANALYSIS_MAX_ARTICLES = 10
ANALYSIS_MAX_INPUT_CHARS = 24_000  # Approximately 6,000 tokens.
ANALYSIS_MAX_RETRIES = 2
ANALYSIS_MAX_OUTPUT_TOKENS = 2_048

# --- API presentation (spec §12.1) ---
TREND_HIGHLIGHT_LIMIT = 5
DASHBOARD_TOP_CLUSTER_LIMIT = 3

# --- Source enum values (kept as plain strings, not a DB CHECK, per spec §4.1) ---
SOURCE_HACKERNEWS = "hackernews"
SOURCE_OPENAI = "openai"
SOURCE_ANTHROPIC = "anthropic"
SOURCE_HUGGINGFACE = "huggingface"
VALID_SOURCES = {SOURCE_HACKERNEWS, SOURCE_OPENAI, SOURCE_ANTHROPIC, SOURCE_HUGGINGFACE}
# --- Connector / HTTP behavior (spec §5) ---
HTTP_USER_AGENT = "AI-DevPulse/0.1 (+https://github.com/ai-devpulse/backend)"
HTTP_TIMEOUT_SECONDS = 10
HTTP_RETRY_ATTEMPTS = 3
HTTP_RETRY_BACKOFF_MIN_SECONDS = 1
HTTP_RETRY_BACKOFF_MAX_SECONDS = 4
HTTP_MIN_REQUEST_INTERVAL_SECONDS = 1.0

HACKERNEWS_TOP_STORIES_URL = "https://hacker-news.firebaseio.com/v0/topstories.json"
HACKERNEWS_NEW_STORIES_URL = "https://hacker-news.firebaseio.com/v0/newstories.json"
HACKERNEWS_ITEM_URL_TEMPLATE = "https://hacker-news.firebaseio.com/v0/item/{item_id}.json"

OPENAI_RSS_FEED_URL = "https://openai.com/news/rss.xml"
ANTHROPIC_RSS_FEED_URL = "https://www.anthropic.com/news/rss.xml"
HUGGINGFACE_RSS_FEED_URL = "https://huggingface.co/blog/feed.xml"

AI_RELEVANT_KEYWORDS = [
    "ai",
    "artificial intelligence",
    "llm",
    "gpt",
    "openai",
    "anthropic",
    "claude",
    "hugging face",
    "transformer",
    "agent",
    "agents",
    "prompt",
    "rag",
    "embedding",
    "multimodal",
    "inference",
    "fine-tuning",
    "model",
    "benchmark",
    "copilot",
    "cursor",
]
