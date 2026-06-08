"""Tests for web.py — Flask endpoint smoke tests."""

from __future__ import annotations

import json
from unittest.mock import patch, MagicMock

import pytest


class TestIndexPage:
    """GET / should return the main HTML page."""

    def test_returns_200(self, flask_app):
        resp = flask_app.get("/")
        assert resp.status_code == 200
        assert b"html" in resp.data.lower() or b"<!doctype" in resp.data.lower()


class TestHealthEndpoint:
    """GET /api/health should return JSON with status."""

    def test_returns_json_with_status(self, flask_app):
        resp = flask_app.get("/api/health")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert "status" in data
        assert data["status"] == "healthy"

    def test_content_type_is_json(self, flask_app):
        resp = flask_app.get("/api/health")
        assert "application/json" in resp.content_type


class TestApiTrending:
    """GET /api/trending should return a proper JSON structure."""

    @patch("web.github_api.fetch_trending_repos")
    @patch("web.utils.read_cache", return_value=None)
    def test_returns_repos_key(self, _mock_cache, mock_fetch, flask_app):
        mock_fetch.return_value = [
            {
                "full_name": "test/repo",
                "stargazers_count": 100,
                "forks_count": 10,
                "language": "Python",
                "description": "Test",
            }
        ]
        resp = flask_app.get("/api/trending?source=api&limit=1")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert "repos" in data
        assert "count" in data
        assert isinstance(data["repos"], list)

    @patch("web.github_api.fetch_trending_repos")
    @patch("web.utils.read_cache", return_value=None)
    def test_returns_count(self, _mock_cache, mock_fetch, flask_app):
        mock_fetch.return_value = [
            {"full_name": "a/b", "stargazers_count": 1, "forks_count": 0, "language": "Go", "description": "x"},
            {"full_name": "c/d", "stargazers_count": 2, "forks_count": 0, "language": "Go", "description": "y"},
        ]
        resp = flask_app.get("/api/trending?source=api&limit=5")
        data = json.loads(resp.data)
        assert data["count"] == 2

    @patch("web.github_api.fetch_trending_repos")
    @patch("web.utils.read_cache", return_value=None)
    def test_source_field_present(self, _mock_cache, mock_fetch, flask_app):
        mock_fetch.return_value = []
        resp = flask_app.get("/api/trending?source=api")
        data = json.loads(resp.data)
        assert "source" in data

    @patch("web.github_api.fetch_trending_repos")
    @patch("web.utils.read_cache")
    def test_cache_hit(self, mock_cache, mock_fetch, flask_app):
        cached_repos = [
            {"full_name": "cached/repo", "stargazers_count": 999, "forks_count": 0, "language": "Rust", "description": "cached"},
        ]
        mock_cache.return_value = cached_repos
        resp = flask_app.get("/api/trending?source=api&limit=1")
        data = json.loads(resp.data)
        assert data["cached"] is True
        assert data["repos"][0]["full_name"] == "cached/repo"
        mock_fetch.assert_not_called()


class TestAuthEndpoints:
    """Tests for auth endpoints: /api/auth/google, status, and logout."""

    def test_status_unauthenticated(self, flask_app):
        resp = flask_app.get("/api/auth/status")
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data["authenticated"] is False
        assert data["user"] is None

    def test_google_login_mock(self, flask_app):
        # Authenticate using the developer mock token
        resp = flask_app.post(
            "/api/auth/google",
            data=json.dumps({"token": "mock_sandbox_token"}),
            content_type="application/json",
        )
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data["status"] == "success"
        assert data["user"]["email"] == "developer@example.com"

        # Verify status endpoint reflects successful authentication
        resp_status = flask_app.get("/api/auth/status")
        data_status = json.loads(resp_status.data)
        assert data_status["authenticated"] is True
        assert data_status["user"]["email"] == "developer@example.com"

        # Log out
        resp_logout = flask_app.post("/api/auth/logout")
        assert resp_logout.status_code == 200
        data_logout = json.loads(resp_logout.data)
        assert data_logout["status"] == "success"

        # Verify status endpoint shows unauthenticated after logout
        resp_status_after = flask_app.get("/api/auth/status")
        data_status_after = json.loads(resp_status_after.data)
        assert data_status_after["authenticated"] is False


class TestWatchlistApi:
    """Tests for SQLite-backed persistent watchlist API endpoints."""

    def test_watchlist_unauthorized(self, flask_app):
        # GET returns 401 unauthorized
        resp_get = flask_app.get("/api/watchlist")
        assert resp_get.status_code == 401

        # POST returns 401 unauthorized
        resp_post = flask_app.post(
            "/api/watchlist",
            data=json.dumps({"repo": {"full_name": "test/repo"}}),
            content_type="application/json",
        )
        assert resp_post.status_code == 401

    def test_watchlist_crud_lifecycle(self, flask_app):
        # 1. Login
        flask_app.post(
            "/api/auth/google",
            data=json.dumps({"token": "mock_sandbox_token"}),
            content_type="application/json",
        )

        # 2. GET empty watchlist
        resp_get_empty = flask_app.get("/api/watchlist")
        assert resp_get_empty.status_code == 200
        data_empty = json.loads(resp_get_empty.data)
        assert "watchlist" in data_empty
        assert len(data_empty["watchlist"]) == 0

        # 3. Add item to watchlist
        test_repo = {
            "full_name": "miron/my-awesome-project",
            "html_url": "https://github.com/miron/my-awesome-project",
            "language": "Python",
            "stars": 123
        }
        resp_post = flask_app.post(
            "/api/watchlist",
            data=json.dumps({"repo": test_repo}),
            content_type="application/json",
        )
        assert resp_post.status_code == 200

        # 4. GET watchlist containing item
        resp_get = flask_app.get("/api/watchlist")
        assert resp_get.status_code == 200
        data_wl = json.loads(resp_get.data)
        assert len(data_wl["watchlist"]) == 1
        assert data_wl["watchlist"][0]["full_name"] == "miron/my-awesome-project"

        # 5. Delete item from watchlist
        resp_delete = flask_app.delete("/api/watchlist?repo_name=miron/my-awesome-project")
        assert resp_delete.status_code == 200

        # 6. GET empty watchlist again
        resp_get_after = flask_app.get("/api/watchlist")
        data_after = json.loads(resp_get_after.data)
        assert len(data_after["watchlist"]) == 0

        # 7. Clean up logout
        flask_app.post("/api/auth/logout")


