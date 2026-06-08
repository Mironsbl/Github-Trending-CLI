"""Tests for github_api.py — fetch_trending_repos, get_rate_limit, error handling."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
import requests

import github_api
from github_api import GitHubAPIError, fetch_trending_repos, get_rate_limit


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mock_response(status_code: int = 200, json_data: dict | None = None, text: str = ""):
    """Create a mock requests.Response."""
    resp = MagicMock(spec=requests.Response)
    resp.status_code = status_code
    resp.json.return_value = json_data or {}
    resp.text = text
    return resp


FAKE_ITEMS = [
    {
        "full_name": "user/repo1",
        "stargazers_count": 100,
        "forks_count": 10,
        "language": "Python",
        "description": "A cool repo",
        "owner": {"login": "user", "type": "User"},
    },
    {
        "full_name": "user/repo2",
        "stargazers_count": 50,
        "forks_count": 5,
        "language": "Go",
        "description": "Another repo",
        "owner": {"login": "user", "type": "User"},
    },
]


# ---------------------------------------------------------------------------
# fetch_trending_repos — success
# ---------------------------------------------------------------------------

class TestFetchTrendingReposSuccess:
    @patch("github_api.requests.get")
    def test_returns_items(self, mock_get):
        mock_get.return_value = _mock_response(200, {"items": FAKE_ITEMS})
        repos = fetch_trending_repos(duration="week", limit=2)
        assert len(repos) == 2
        assert repos[0]["full_name"] == "user/repo1"

    @patch("github_api.requests.get")
    def test_respects_limit(self, mock_get):
        mock_get.return_value = _mock_response(200, {"items": FAKE_ITEMS})
        repos = fetch_trending_repos(duration="week", limit=1)
        assert len(repos) <= 1

    @patch("github_api.requests.get")
    def test_empty_items(self, mock_get):
        mock_get.return_value = _mock_response(200, {"items": []})
        repos = fetch_trending_repos(duration="week", limit=10)
        assert repos == []


# ---------------------------------------------------------------------------
# Query construction
# ---------------------------------------------------------------------------

class TestQueryConstruction:
    @patch("github_api.requests.get")
    def test_language_in_query(self, mock_get):
        mock_get.return_value = _mock_response(200, {"items": []})
        fetch_trending_repos(language="python", limit=5)
        call_args = mock_get.call_args
        query = call_args.kwargs.get("params", call_args[1].get("params", {})).get("q", "")
        assert "language:python" in query

    @patch("github_api.requests.get")
    def test_topic_triggers_pushed_filter(self, mock_get):
        mock_get.return_value = _mock_response(200, {"items": []})
        fetch_trending_repos(topic="machine-learning", limit=5)
        call_args = mock_get.call_args
        query = call_args.kwargs.get("params", call_args[1].get("params", {})).get("q", "")
        assert "topic:machine-learning" in query
        assert "pushed:>" in query

    @patch("github_api.requests.get")
    def test_min_stars_in_query(self, mock_get):
        mock_get.return_value = _mock_response(200, {"items": []})
        fetch_trending_repos(min_stars=100, limit=5)
        call_args = mock_get.call_args
        query = call_args.kwargs.get("params", call_args[1].get("params", {})).get("q", "")
        assert "stars:>=100" in query

    @patch("github_api.requests.get")
    def test_min_and_max_stars_range(self, mock_get):
        mock_get.return_value = _mock_response(200, {"items": []})
        fetch_trending_repos(min_stars=10, max_stars=500, limit=5)
        call_args = mock_get.call_args
        query = call_args.kwargs.get("params", call_args[1].get("params", {})).get("q", "")
        assert "stars:10..500" in query

    @patch("github_api.requests.get")
    def test_author_in_query(self, mock_get):
        mock_get.return_value = _mock_response(200, {"items": []})
        fetch_trending_repos(author="torvalds", limit=5)
        call_args = mock_get.call_args
        query = call_args.kwargs.get("params", call_args[1].get("params", {})).get("q", "")
        assert "user:torvalds" in query

    @patch("github_api.requests.get")
    def test_keyword_in_query(self, mock_get):
        mock_get.return_value = _mock_response(200, {"items": []})
        fetch_trending_repos(query_keyword="fastapi", limit=5)
        call_args = mock_get.call_args
        query = call_args.kwargs.get("params", call_args[1].get("params", {})).get("q", "")
        assert "fastapi" in query

    @patch("github_api.requests.get")
    def test_sort_param(self, mock_get):
        mock_get.return_value = _mock_response(200, {"items": []})
        fetch_trending_repos(sort="forks", limit=5)
        call_args = mock_get.call_args
        params = call_args.kwargs.get("params", call_args[1].get("params", {}))
        assert params.get("sort") == "forks"


# ---------------------------------------------------------------------------
# Token resolution
# ---------------------------------------------------------------------------

class TestTokenResolution:
    @patch("github_api.requests.get")
    def test_explicit_token_used(self, mock_get):
        mock_get.return_value = _mock_response(200, {"items": []})
        fetch_trending_repos(token="ghp_explicit123", limit=1)
        call_args = mock_get.call_args
        headers = call_args.kwargs.get("headers", call_args[1].get("headers", {}))
        assert headers["Authorization"] == "Bearer ghp_explicit123"

    @patch.dict("os.environ", {"GITHUB_TOKEN": "ghp_env456"})
    @patch("github_api.requests.get")
    def test_env_token_fallback(self, mock_get):
        mock_get.return_value = _mock_response(200, {"items": []})
        fetch_trending_repos(limit=1)
        call_args = mock_get.call_args
        headers = call_args.kwargs.get("headers", call_args[1].get("headers", {}))
        assert headers["Authorization"] == "Bearer ghp_env456"

    @patch.dict("os.environ", {}, clear=True)
    @patch("github_api.requests.get")
    def test_no_token_no_auth_header(self, mock_get):
        mock_get.return_value = _mock_response(200, {"items": []})
        # Remove GITHUB_TOKEN if it exists
        import os
        os.environ.pop("GITHUB_TOKEN", None)
        fetch_trending_repos(limit=1)
        call_args = mock_get.call_args
        headers = call_args.kwargs.get("headers", call_args[1].get("headers", {}))
        assert "Authorization" not in headers


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

class TestErrorHandling:
    @patch("github_api.requests.get")
    def test_403_raises(self, mock_get):
        mock_get.return_value = _mock_response(403)
        with pytest.raises(GitHubAPIError, match="rate limit"):
            fetch_trending_repos(limit=5)

    @patch("github_api.requests.get")
    def test_401_raises(self, mock_get):
        mock_get.return_value = _mock_response(401)
        with pytest.raises(GitHubAPIError, match="authentication failed"):
            fetch_trending_repos(limit=5)

    @patch("github_api.requests.get")
    def test_422_raises(self, mock_get):
        mock_get.return_value = _mock_response(422)
        with pytest.raises(GitHubAPIError, match="Invalid query"):
            fetch_trending_repos(limit=5)

    @patch("github_api.requests.get")
    def test_connection_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.ConnectionError("DNS failure")
        with pytest.raises(GitHubAPIError, match="Could not connect"):
            fetch_trending_repos(limit=5)

    @patch("github_api.requests.get")
    def test_timeout_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.Timeout("timed out")
        with pytest.raises(GitHubAPIError, match="timed out"):
            fetch_trending_repos(limit=5)

    @patch("github_api.requests.get")
    def test_unknown_status_raises(self, mock_get):
        mock_get.return_value = _mock_response(500, text="Internal Server Error")
        with pytest.raises(GitHubAPIError, match="status 500"):
            fetch_trending_repos(limit=5)


# ---------------------------------------------------------------------------
# get_rate_limit
# ---------------------------------------------------------------------------

class TestGetRateLimit:
    @patch("github_api.requests.get")
    def test_returns_search_resource(self, mock_get):
        mock_get.return_value = _mock_response(200, {
            "resources": {
                "search": {"limit": 30, "remaining": 28, "reset": 1700000000}
            }
        })
        result = get_rate_limit()
        assert result["limit"] == 30
        assert result["remaining"] == 28

    @patch("github_api.requests.get")
    def test_returns_empty_dict_on_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.ConnectionError()
        result = get_rate_limit()
        assert result == {}

    @patch("github_api.requests.get")
    def test_returns_empty_dict_on_non_200(self, mock_get):
        mock_get.return_value = _mock_response(500)
        result = get_rate_limit()
        assert result == {}

    @patch("github_api.requests.get")
    def test_token_passed_as_header(self, mock_get):
        mock_get.return_value = _mock_response(200, {"resources": {"search": {}}})
        get_rate_limit(token="ghp_test")
        headers = mock_get.call_args.kwargs.get("headers", mock_get.call_args[1].get("headers", {}))
        assert headers["Authorization"] == "Bearer ghp_test"


# ---------------------------------------------------------------------------
# exclude_org filtering
# ---------------------------------------------------------------------------

class TestExcludeOrg:
    @patch("github_api.requests.get")
    def test_filters_big_orgs(self, mock_get):
        items = [
            {"full_name": "google/proj", "owner": {"login": "google"}},
            {"full_name": "indie/proj", "owner": {"login": "indie"}},
        ]
        mock_get.return_value = _mock_response(200, {"items": items})
        repos = fetch_trending_repos(limit=10, exclude_org=True)
        names = [r["full_name"] for r in repos]
        assert "google/proj" not in names
        assert "indie/proj" in names
