"""Utility functions for date calculations, caching, table formatting, and export."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from rich.bar import Bar
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

CACHE_DIR = Path.home() / ".cache" / "github-trending-cli"
NOTIFY_FILE = CACHE_DIR / "last_seen.json"
DEFAULT_TTL_SECONDS = 600  # 10 minutes


# ---------------------------------------------------------------------------
# Date helpers
# ---------------------------------------------------------------------------

def get_since_date(duration: str) -> str:
    """Return a YYYY-MM-DD date string *duration* ago from today (UTC)."""
    today = datetime.now(tz=timezone.utc)
    deltas: dict[str, timedelta] = {
        "day": timedelta(days=1),
        "week": timedelta(weeks=1),
        "month": timedelta(days=30),
        "year": timedelta(days=365),
    }
    delta = deltas.get(duration, timedelta(weeks=1))
    return (today - delta).strftime("%Y-%m-%d")


# ---------------------------------------------------------------------------
# Caching helpers
# ---------------------------------------------------------------------------

def _cache_key(source: str, duration: str, limit: int, language: str | None) -> str:
    """Compute a deterministic cache filename from query parameters."""
    raw = f"{source}:{duration}:{limit}:{language or ''}"
    digest = hashlib.sha256(raw.encode()).hexdigest()[:16]
    return f"trending_{digest}.json"


def read_cache(
    source: str,
    duration: str,
    limit: int,
    language: str | None,
    ttl: int = DEFAULT_TTL_SECONDS,
) -> list[dict[str, Any]] | None:
    """Return cached results if they exist and are fresh, else None."""
    path = CACHE_DIR / _cache_key(source, duration, limit, language)
    if not path.exists():
        return None
    age = time.time() - path.stat().st_mtime
    if age > ttl:
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return data
    except (json.JSONDecodeError, OSError):
        pass
    return None


def write_cache(
    repos: list[dict[str, Any]],
    source: str,
    duration: str,
    limit: int,
    language: str | None,
) -> None:
    """Persist repos to the on-disk cache and save to SQLite history."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CACHE_DIR / _cache_key(source, duration, limit, language)
    path.write_text(json.dumps(repos, ensure_ascii=False), encoding="utf-8")
    
    # Save to historical SQLite database
    try:
        import db
        db.save_repos(repos)
    except Exception as e:
        # Don't break caching if db operations fail
        import logging
        logging.getLogger("github_trending_cli").warning("Failed to save history: %s", e)


# ---------------------------------------------------------------------------
# Star bar chart helper
# ---------------------------------------------------------------------------

def _star_bar(count: int, max_count: int, width: int = 15) -> str:
    """Return a Unicode bar proportional to count/max_count."""
    if max_count == 0:
        return ""
    filled = max(1, round(count / max_count * width))
    return "█" * filled + "░" * (width - filled)


def _format_stars(count: int) -> str:
    """Format a star count with comma separators."""
    return f"{count:,}"


# ---------------------------------------------------------------------------
# Rich table formatting
# ---------------------------------------------------------------------------

def build_rich_table(repos: list[dict[str, Any]], *, title: str = "") -> Table:
    """Build a rich.table.Table from a list of GitHub repo dicts."""
    table = Table(
        title=title,
        title_style="bold bright_white",
        show_lines=False,
        expand=False,
        border_style="dim",
        header_style="bold",
        pad_edge=True,
        padding=(0, 1),
    )

    table.add_column("#", style="dim", justify="right", width=3)
    table.add_column("Repository", style="bold cyan", no_wrap=True, max_width=38)
    table.add_column("⭐ Stars", style="bold gold1", justify="right", width=9)
    table.add_column("📊", style="gold1", no_wrap=True, width=15)
    table.add_column("🍴 Forks", style="bold blue", justify="right", width=8)
    table.add_column("Language", style="bold green", width=12, no_wrap=True)
    table.add_column("Description", style="white", max_width=50, no_wrap=True)

    max_stars = max((r.get("stargazers_count", 0) for r in repos), default=1)

    for idx, repo in enumerate(repos, start=1):
        name = repo.get("full_name", "N/A")
        stars_count = repo.get("stargazers_count", 0)
        stars = _format_stars(stars_count)
        bar = _star_bar(stars_count, max_stars)
        forks = _format_stars(repo.get("forks_count", 0))
        language = repo.get("language") or "—"
        description = repo.get("description") or "No description"
        if len(description) > 50:
            description = description[:47] + "..."

        table.add_row(str(idx), name, stars, bar, forks, language, description)

    return table


def build_header_panel(
    duration: str,
    limit: int,
    language: str | None,
    topic: str | None = None,
    sort: str = "stars",
    min_stars: int | None = None,
    source: str | None = None,
    query: str | None = None,
) -> Panel:
    """Return a styled Panel summarizing the current query."""
    parts = [
        f"Duration: [bold]{duration}[/bold]",
        f"Limit: [bold]{limit}[/bold]",
    ]
    if source:
        parts.append(f"Source: [bright_cyan]{source}[/bright_cyan]")
    if language:
        parts.append(f"Language: [green]{language}[/green]")
    if topic:
        parts.append(f"Topic: [magenta]{topic}[/magenta]")
    if query:
        parts.append(f"Query: [bright_yellow]{query}[/bright_yellow]")
    if sort != "stars":
        parts.append(f"Sort: [yellow]{sort}[/yellow]")
    if min_stars:
        parts.append(f"Min stars: [gold1]{min_stars}[/gold1]")

    subtitle = f"[dim]{'  │  '.join(parts)}[/dim]"
    return Panel(
        subtitle,
        title="[bold bright_white]🔥 GitHub Trending CLI[/bold bright_white]",
        border_style="bright_magenta",
        expand=False,
        padding=(0, 2),
    )


# ---------------------------------------------------------------------------
# Export helpers
# ---------------------------------------------------------------------------

_EXPORT_FIELDS = [
    "full_name",
    "html_url",
    "stargazers_count",
    "forks_count",
    "language",
    "description",
    "created_at",
]


def _slim_repo(repo: dict[str, Any]) -> dict[str, Any]:
    """Return a dict with only the fields we want to export."""
    return {k: repo.get(k) for k in _EXPORT_FIELDS}


def export_json(repos: list[dict[str, Any]], path: str) -> None:
    data = [_slim_repo(r) for r in repos]
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)


def export_csv(repos: list[dict[str, Any]], path: str) -> None:
    data = [_slim_repo(r) for r in repos]
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=_EXPORT_FIELDS)
        writer.writeheader()
        writer.writerows(data)


def export_results(repos: list[dict[str, Any]], path: str) -> None:
    """Auto-detect format from path extension and export."""
    ext = os.path.splitext(path)[1].lower()
    if ext == ".json":
        export_json(repos, path)
    elif ext == ".csv":
        export_csv(repos, path)
    else:
        raise ValueError(f"Unsupported format '{ext}'. Use .json or .csv.")


# ---------------------------------------------------------------------------
# Notification helpers
# ---------------------------------------------------------------------------

def _load_last_seen() -> set[str]:
    """Load the set of previously seen repo full_names."""
    if not NOTIFY_FILE.exists():
        return set()
    try:
        data = json.loads(NOTIFY_FILE.read_text(encoding="utf-8"))
        return set(data) if isinstance(data, list) else set()
    except (json.JSONDecodeError, OSError):
        return set()


def _save_last_seen(names: set[str]) -> None:
    """Save the set of seen repo full_names."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    NOTIFY_FILE.write_text(json.dumps(list(names)), encoding="utf-8")


def check_new_repos(
    repos: list[dict[str, Any]], console: Console
) -> list[dict[str, Any]]:
    """Compare repos with last seen set and highlight new ones.

    Returns the list of NEW repos (not seen before).
    """
    last_seen = _load_last_seen()
    current_names = {r.get("full_name", "") for r in repos}
    new_repos = [r for r in repos if r.get("full_name", "") not in last_seen]

    _save_last_seen(current_names | last_seen)

    if new_repos and last_seen:
        console.print(
            f"\n[bold bright_green]🔔 {len(new_repos)} new repo(s) "
            f"since last check![/bold bright_green]"
        )
        for r in new_repos:
            name = r.get("full_name", "")
            stars = _format_stars(r.get("stargazers_count", 0))
            console.print(f"  [green]✨ {name}[/green] — ⭐ {stars}")
        console.print()

    return new_repos


# ---------------------------------------------------------------------------
# Interactive TUI helpers
# ---------------------------------------------------------------------------

def show_repo_detail(repo: dict[str, Any], console: Console) -> None:
    """Print detailed information about a single repository."""
    name = repo.get("full_name", "N/A")
    desc = repo.get("description") or "No description"
    stars = _format_stars(repo.get("stargazers_count", 0))
    forks = _format_stars(repo.get("forks_count", 0))
    lang = repo.get("language") or "N/A"
    url = repo.get("html_url", "")
    created = repo.get("created_at", "N/A")
    topics = ", ".join(repo.get("topics", [])) or "None"
    license_name = (repo.get("license") or {}).get("name", "N/A")
    open_issues = repo.get("open_issues_count", 0)
    watchers = repo.get("watchers_count", 0)
    size_kb = repo.get("size", 0)
    size_mb = f"{size_kb / 1024:.1f} MB" if size_kb > 1024 else f"{size_kb} KB"

    detail = (
        f"[bold cyan]{name}[/bold cyan]\n"
        f"\n"
        f"[white]{desc}[/white]\n"
        f"\n"
        f"  [gold1]⭐ Stars:[/gold1]    {stars}\n"
        f"  [blue]🍴 Forks:[/blue]    {forks}\n"
        f"  [green]💻 Language:[/green]  {lang}\n"
        f"  📝 License:   {license_name}\n"
        f"  🐛 Issues:    {open_issues}\n"
        f"  👀 Watchers:  {watchers}\n"
        f"  📦 Size:      {size_mb}\n"
        f"  🏷️  Topics:    {topics}\n"
        f"  📅 Created:   {created}\n"
        f"\n"
        f"  [link={url}]🔗 {url}[/link]"
    )

    console.print()
    console.print(
        Panel(
            detail,
            title="[bold]Repository Details[/bold]",
            border_style="cyan",
            expand=False,
            padding=(1, 3),
        )
    )
