"""Scraper for the real GitHub Trending page (github.com/trending)."""

from __future__ import annotations

from typing import Any

import requests
from bs4 import BeautifulSoup


TRENDING_URL = "https://github.com/trending"

# Map our duration names to GitHub's 'since' param
_SINCE_MAP = {
    "day": "daily",
    "week": "weekly",
    "month": "monthly",
    "year": "monthly",  # GitHub only supports daily/weekly/monthly
    "daily": "daily",
    "weekly": "weekly",
    "monthly": "monthly",
}


def scrape_trending(
    duration: str = "week",
    language: str | None = None,
    limit: int = 25,
) -> list[dict[str, Any]]:
    """Scrape the GitHub Trending page and return repo dicts.

    Args:
        duration: One of 'day', 'week', 'month', 'year'.
        language: Optional language filter (e.g. 'python').
        limit: Maximum number of repos to return.

    Returns:
        A list of repo dicts with keys compatible with the GitHub Search API format.
    """
    since = _SINCE_MAP.get(duration, "weekly")

    params: dict[str, str] = {"since": since}
    if language:
        params["spoken_language_code"] = ""

    url = TRENDING_URL
    if language:
        url = f"{TRENDING_URL}/{language.lower()}"

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml",
        "Accept-Language": "en-US,en;q=0.9",
    }

    try:
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        resp.raise_for_status()
    except requests.RequestException:
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    articles = soup.select("article.Box-row")

    repos: list[dict[str, Any]] = []
    for article in articles[:limit]:
        repo = _parse_article(article, since)
        if repo:
            repos.append(repo)

    return repos


def _parse_article(article: Any, since: str) -> dict[str, Any] | None:
    """Parse a single trending article element into a repo dict."""
    try:
        # Repo name: h2 > a
        name_el = article.select_one("h2 a")
        if not name_el:
            return None
        full_name = name_el.get("href", "").strip("/")
        if not full_name:
            return None

        # Description
        desc_el = article.select_one("p")
        description = desc_el.get_text(strip=True) if desc_el else ""

        # Language
        lang_el = article.select_one("[itemprop='programmingLanguage']")
        language = lang_el.get_text(strip=True) if lang_el else None

        # Stars & forks from the links
        links = article.select("a.Link--muted")
        total_stars = 0
        forks = 0
        for link in links:
            href = link.get("href", "")
            text = link.get_text(strip=True).replace(",", "")
            if "/stargazers" in href:
                total_stars = _parse_int(text)
            elif "/forks" in href or "/network" in href:
                forks = _parse_int(text)

        # Stars today/this week/this month
        stars_today_el = article.select_one("span.d-inline-block.float-sm-right")
        stars_period = 0
        stars_period_label = ""
        if stars_today_el:
            raw = stars_today_el.get_text(strip=True)
            parts = raw.split(" star")
            if parts:
                stars_period = _parse_int(parts[0])
                stars_period_label = raw

        # Built-by avatars
        built_by = []
        for img in article.select("a img[data-hovercard-type='user']"):
            alt = img.get("alt", "").lstrip("@")
            if alt:
                built_by.append(alt)

        return {
            "full_name": full_name,
            "html_url": f"https://github.com/{full_name}",
            "description": description,
            "language": language,
            "stargazers_count": total_stars,
            "forks_count": forks,
            "stars_period": stars_period,
            "stars_today": stars_period,
            "stars_period_label": stars_period_label,
            "built_by": built_by,
            "source": "trending",
        }
    except Exception:
        return None


def _parse_int(s: str) -> int:
    """Parse a string like '1,234' or '12.5k' into an integer."""
    s = s.strip().replace(",", "").lower()
    if not s:
        return 0
    try:
        if s.endswith("k"):
            return int(float(s[:-1]) * 1000)
        return int(s)
    except ValueError:
        return 0


def search_repos_by_query(
    query: str,
    repos: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Filter repos by keyword in name or description (supports OR terms)."""
    if not query:
        return repos
    
    import re
    # Split query by ' OR ' (case-insensitive)
    terms = [t.strip().lower() for t in re.split(r'\s+or\s+', query, flags=re.IGNORECASE)]
    # Filter out empty terms
    terms = [t for t in terms if t]
    
    if not terms:
        return repos
        
    filtered = []
    for r in repos:
        name_lower = r.get("full_name", "").lower()
        desc_lower = (r.get("description") or "").lower()
        
        # Check if any of the terms are matched
        match = False
        for term in terms:
            if term in name_lower or term in desc_lower:
                match = True
                break
        if match:
            filtered.append(r)
            
    return filtered


def fetch_trending_with_fallback(
    since: str = "weekly",
    language: str | None = None,
    limit: int = 25,
    query: str | None = None,
    token: str | None = None,
    topic: str | None = None,
    sort: str = "stars",
    min_stars: int | None = None,
) -> list[dict[str, Any]]:
    """Fetch trending repositories from scraper first, with fallback to Search API.

    Args:
        since: Time period ('daily', 'weekly', 'monthly').
        language: Optional language filter (e.g. 'python').
        limit: Number of repositories to return.
        query: Optional keyword search in results.
        token: Optional GitHub token.
        topic: Optional topic filter (for API fallback).
        sort: Sort field (for API fallback).
        min_stars: Minimum stars (for API fallback).

    Returns:
        A list of repository dicts.
    """
    import github_api

    duration_map = {
        "daily": "day",
        "weekly": "week",
        "monthly": "month",
    }
    duration = duration_map.get(since, "week")

    # Try scraping first
    repos = scrape_trending(duration=duration, language=language, limit=limit)

    if not repos:
        # Fallback to GitHub Search API
        repos = github_api.fetch_trending_repos(
            duration=duration,
            limit=limit,
            language=language,
            topic=topic,
            sort=sort,
            min_stars=min_stars,
            token=token,
        )
        for r in repos:
            r["source"] = "api"
    else:
        for r in repos:
            r["source"] = "trending"

    # Filter by query if present
    if query:
        repos = search_repos_by_query(query, repos)

    return repos
