import sqlite3

conn = sqlite3.connect("app.db")
cursor = conn.cursor()

# List all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
print("Tables:", tables)

# Query 1: daily_briefs
print("\n--- daily_briefs (last 7) ---")
try:
    cursor.execute(
        "SELECT date, stories_analyzed, stories_filtered, stories_selected FROM daily_briefs ORDER BY date DESC LIMIT 7"
    )
    for row in cursor.fetchall():
        print(row)
except Exception as e:
    print(f"Error: {e}")

# Query 2: story_clusters
print("\n--- story_clusters (top 10 by importance) ---")
try:
    cursor.execute(
        "SELECT id, title, importance, action, created_at, updated_at FROM story_clusters ORDER BY importance DESC NULLS LAST LIMIT 10"
    )
    for row in cursor.fetchall():
        print(row)
except Exception as e:
    print(f"Error: {e}")

# Query 3: articles by source
print("\n--- articles by source ---")
try:
    cursor.execute(
        "SELECT source, COUNT(*), MAX(published_at) as newest, MIN(published_at) as oldest FROM articles GROUP BY source"
    )
    for row in cursor.fetchall():
        print(row)
except Exception as e:
    print(f"Error: {e}")

# Query 4: papers count
print("\n--- papers count ---")
try:
    cursor.execute("SELECT COUNT(*) FROM papers")
    print(cursor.fetchone())
except Exception as e:
    print(f"Error: {e}")

conn.close()
