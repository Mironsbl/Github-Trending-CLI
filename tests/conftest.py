"""Shared pytest fixtures for the GitHub Trending CLI test suite."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Ensure the project root is on sys.path so that `import utils`, `import web`, etc. work.
PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


@pytest.fixture()
def sample_repos() -> list[dict]:
    """Return a list of 3 mock repository dicts matching the GitHub API shape."""
    return [
        {
            "full_name": "alice/alpha",
            "html_url": "https://github.com/alice/alpha",
            "stargazers_count": 5200,
            "forks_count": 310,
            "language": "Python",
            "description": "A fast async framework",
            "created_at": "2025-11-01T00:00:00Z",
            "topics": ["async", "framework"],
            "license": {"name": "MIT"},
            "open_issues_count": 12,
            "watchers_count": 5200,
            "size": 2048,
            "owner": {"login": "alice", "type": "User"},
        },
        {
            "full_name": "bob/beta",
            "html_url": "https://github.com/bob/beta",
            "stargazers_count": 1800,
            "forks_count": 95,
            "language": "Rust",
            "description": "Blazingly fast CLI tool for linting",
            "created_at": "2026-01-15T00:00:00Z",
            "topics": ["cli", "linter"],
            "license": {"name": "Apache-2.0"},
            "open_issues_count": 4,
            "watchers_count": 1800,
            "size": 512,
            "owner": {"login": "bob", "type": "User"},
        },
        {
            "full_name": "carol/gamma",
            "html_url": "https://github.com/carol/gamma",
            "stargazers_count": 900,
            "forks_count": 42,
            "language": "Go",
            "description": "Lightweight container orchestration",
            "created_at": "2026-03-20T00:00:00Z",
            "topics": ["containers", "devops"],
            "license": {"name": "BSD-3-Clause"},
            "open_issues_count": 7,
            "watchers_count": 900,
            "size": 1024,
            "owner": {"login": "carol", "type": "User"},
        },
    ]


@pytest.fixture()
def flask_app():
    """Create a Flask test client for the web app."""
    from web import app

    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client
