"""Import every ORM model module here so Base.metadata is fully populated.
Import this module (not app.db.base directly) wherever you need Base.metadata
to know about all tables: Alembic's env.py, test fixtures, etc.
"""

from app.db.base import Base  # noqa: F401
from app.models.article import Article  # noqa: F401
from app.models.cluster import StoryCluster  # noqa: F401
from app.models.daily_brief import DailyBrief  # noqa: F401
from app.models.topic import ArticleTopic, Topic  # noqa: F401
from app.models.trend import Trend  # noqa: F401
