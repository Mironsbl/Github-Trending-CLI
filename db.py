"""SQLite database manager for storing historical trending repositories."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from datetime import datetime, timezone
from typing import Any

CACHE_DIR = Path.home() / ".cache" / "github-trending-cli"
DB_PATH = CACHE_DIR / "trends_history.db"


def init_db() -> None:
    """Initialize the SQLite database schema."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS repos_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            name TEXT NOT NULL,
            html_url TEXT NOT NULL,
            description TEXT,
            language TEXT,
            stars INTEGER,
            forks INTEGER,
            stars_today INTEGER,
            hype_score REAL,
            scraped_at TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_repos_history_full_name ON repos_history (full_name)
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_repos_history_scraped_at ON repos_history (scraped_at)
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_watchlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            repo_name TEXT NOT NULL,
            repo_data TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_user_watchlist_user ON user_watchlist (user_id)
    """)
    conn.commit()
    conn.close()


def add_to_watchlist(user_id: str, repo: dict[str, Any]) -> None:
    """Add a repository to a user's persistent watchlist."""
    import json
    init_db()
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    repo_name = repo.get("full_name") or repo.get("name") or "unknown"
    created_at = datetime.now(tz=timezone.utc).isoformat()
    repo_data_json = json.dumps(repo, ensure_ascii=False)
    
    # Check if already saved
    cursor.execute(
        "SELECT 1 FROM user_watchlist WHERE user_id = ? AND repo_name = ?",
        (user_id, repo_name)
    )
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO user_watchlist (user_id, repo_name, repo_data, created_at)
            VALUES (?, ?, ?, ?)
        """, (user_id, repo_name, repo_data_json, created_at))
        conn.commit()
    conn.close()


def remove_from_watchlist(user_id: str, repo_name: str) -> None:
    """Remove a repository from a user's persistent watchlist."""
    init_db()
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM user_watchlist WHERE user_id = ? AND repo_name = ?",
        (user_id, repo_name)
    )
    conn.commit()
    conn.close()


def get_user_watchlist(user_id: str) -> list[dict[str, Any]]:
    """Retrieve a user's persistent watchlist."""
    import json
    init_db()
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute(
        "SELECT repo_data FROM user_watchlist WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    
    watchlist = []
    for r in rows:
        try:
            watchlist.append(json.loads(r[0]))
        except Exception:
            continue
    return watchlist



def save_repos(repos: list[dict[str, Any]]) -> None:
    """Save trending repositories snapshot to history."""
    init_db()
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    scraped_at = datetime.now(tz=timezone.utc).isoformat()

    for r in repos:
        # Calculate hotness/hype_score if missing
        hype = r.get("hype_score") or r.get("hotness") or 0.0
        
        # Extract fields safely
        full_name = r.get("full_name") or r.get("name") or "unknown"
        name = r.get("name") or (full_name.split("/")[-1] if "/" in full_name else full_name)
        html_url = r.get("html_url") or f"https://github.com/{full_name}"
        desc = r.get("description")
        lang = r.get("language")
        stars = r.get("stargazers_count") or r.get("stars") or 0
        forks = r.get("forks_count") or r.get("forks") or 0
        stars_today = r.get("stars_today") or 0

        # Don't save duplicates in the exact same hour to save space
        cursor.execute(
            "SELECT 1 FROM repos_history WHERE full_name = ? AND substr(scraped_at, 1, 13) = ?",
            (full_name, scraped_at[:13])
        )
        if cursor.fetchone():
            continue

        cursor.execute("""
            INSERT INTO repos_history (
                full_name, name, html_url, description, language, stars, forks, stars_today, hype_score, scraped_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            full_name, name, html_url, desc, lang, stars, forks, stars_today, hype, scraped_at
        ))

    conn.commit()
    conn.close()


def get_history(limit: int = 100, search_query: str | None = None) -> list[dict[str, Any]]:
    """Retrieve historical repository snapshots."""
    init_db()
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    if search_query:
        cursor.execute("""
            SELECT * FROM repos_history 
            WHERE full_name LIKE ? OR description LIKE ? OR language LIKE ?
            ORDER BY scraped_at DESC LIMIT ?
        """, (f"%{search_query}%", f"%{search_query}%", f"%{search_query}%", limit))
    else:
        cursor.execute("""
            SELECT * FROM repos_history 
            ORDER BY scraped_at DESC LIMIT ?
        """, (limit,))
        
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(row) for row in rows]


def get_top_historical_languages() -> list[dict[str, Any]]:
    """Return top languages aggregate from history."""
    init_db()
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("""
        SELECT language, COUNT(DISTINCT full_name) as count 
        FROM repos_history 
        WHERE language IS NOT NULL AND language != ''
        GROUP BY language 
        ORDER BY count DESC 
        LIMIT 10
    """)
    rows = cursor.fetchall()
    conn.close()
    return [{"language": r[0], "count": r[1]} for r in rows]


def get_trends_over_time(full_name: str) -> list[dict[str, Any]]:
    """Get stars and hype score growth over time for a specific repository."""
    init_db()
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("""
        SELECT scraped_at, stars, hype_score 
        FROM repos_history 
        WHERE full_name = ? 
        ORDER BY scraped_at ASC
    """, (full_name,))
    rows = cursor.fetchall()
    conn.close()
    return [{"scraped_at": r[0], "stars": r[1], "hype_score": r[2]} for r in rows]
