"""GitHub Search API wrapper with token support, topic/sort/min-stars filters."""

from __future__ import annotations

import os
from typing import Any

import requests

import utils


class GitHubAPIError(Exception):
    """Raised on any GitHub API or network-level failure."""


def fetch_trending_repos(
    duration: str = "week",
    limit: int = 10,
    language: str | None = None,
    topic: str | None = None,
    sort: str = "stars",
    min_stars: int | None = None,
    min_forks: int | None = None,
    token: str | None = None,
    query_keyword: str | None = None,
) -> list[dict[str, Any]]:
    """Fetch trending repositories from the GitHub Search API.

    Args:
        duration: Time range — 'day', 'week', 'month', or 'year'.
        limit: Maximum number of repositories to return (1–100).
        language: Optional language filter (e.g. 'python').
        topic: Optional topic filter (e.g. 'machine-learning').
        sort: Sort field — 'stars', 'forks', or 'updated'.
        min_stars: Minimum star count filter.
        min_forks: Minimum fork count filter.
        token: Optional GitHub personal-access token.
        query_keyword: Optional keyword query.

    Returns:
        A list of repository dicts as returned by the GitHub API.

    Raises:
        GitHubAPIError: On network problems, rate limiting, or unexpected status.
    """
    since_date = utils.get_since_date(duration)
    query = f"created:>{since_date}"

    if query_keyword:
        query += f" {query_keyword}"
    if language:
        query += f" language:{language}"
    if topic:
        query += f" topic:{topic}"
    if min_stars is not None and min_stars > 0:
        query += f" stars:>={min_stars}"
    if min_forks is not None and min_forks > 0:
        query += f" forks:>={min_forks}"

    # Resolve token: explicit arg → env var → unauthenticated
    resolved_token = token or os.environ.get("GITHUB_TOKEN")

    headers: dict[str, str] = {"Accept": "application/vnd.github+json"}
    if resolved_token:
        headers["Authorization"] = f"Bearer {resolved_token}"

    url = "https://api.github.com/search/repositories"
    repos: list[dict[str, Any]] = []
    page = 1
    
    # Calculate how many pages we need, fetching up to 100 per page
    import math
    per_page = min(limit, 100)
    pages_needed = math.ceil(limit / per_page) if per_page > 0 else 1
    
    while len(repos) < limit and page <= pages_needed:
        current_limit = min(limit - len(repos), 100)
        params: dict[str, str | int] = {
            "q": query,
            "sort": sort,
            "order": "desc",
            "per_page": current_limit,
            "page": page,
        }
    
        try:
            response = requests.get(url, params=params, headers=headers, timeout=15)
    
            if response.status_code == 403:
                if repos:
                    # Return partial results if we hit a rate limit midway
                    break
                raise GitHubAPIError(
                    "GitHub API rate limit exceeded. "
                    "Wait a few minutes or supply a token with --token / GITHUB_TOKEN."
                )
    
            if response.status_code == 401:
                raise GitHubAPIError(
                    "GitHub API authentication failed. Check your token."
                )
    
            if response.status_code == 422:
                raise GitHubAPIError(
                    "Invalid query parameters. Check --topic and --language values."
                )
    
            if response.status_code != 200:
                if repos:
                    break
                raise GitHubAPIError(
                    f"GitHub API returned status {response.status_code}: "
                    f"{response.text[:200]}"
                )
    
            data = response.json()
            items = data.get("items", [])
            if not items:
                break
            
            repos.extend(items)
            page += 1
    
        except requests.exceptions.ConnectionError:
            if repos:
                return repos
            raise GitHubAPIError(
                "Could not connect to GitHub. Check your internet connection."
            )
        except requests.exceptions.Timeout:
            if repos:
                return repos
            raise GitHubAPIError(
                "GitHub API request timed out. Try again later."
            )
        except requests.exceptions.RequestException as exc:
            if repos:
                return repos
            raise GitHubAPIError(f"Unexpected network error: {exc}")
    
    return repos


def get_rate_limit(token: str | None = None) -> dict[str, Any]:
    """Check current GitHub API rate limit status.

    Args:
        token: Optional GitHub personal-access token.

    Returns:
        Dict with 'limit', 'remaining', 'reset' keys.
    """
    resolved_token = token or os.environ.get("GITHUB_TOKEN")
    headers: dict[str, str] = {"Accept": "application/vnd.github+json"}
    if resolved_token:
        headers["Authorization"] = f"Bearer {resolved_token}"

    try:
        resp = requests.get(
            "https://api.github.com/rate_limit",
            headers=headers,
            timeout=10,
        )
        if resp.status_code == 200:
            return resp.json().get("resources", {}).get("search", {})
    except requests.exceptions.RequestException:
        pass
    return {}
