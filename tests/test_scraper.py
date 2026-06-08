"""Tests for scraper.py — _parse_int, search_repos_by_query, scrape_trending."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

import scraper


# ---------------------------------------------------------------------------
# _parse_int
# ---------------------------------------------------------------------------

class TestParseInt:
    """Verify the helper that normalises human-readable numbers to ints."""

    def test_plain_number(self):
        assert scraper._parse_int("42") == 42

    def test_comma_separated(self):
        assert scraper._parse_int("1,234") == 1234

    def test_k_suffix(self):
        assert scraper._parse_int("12.5k") == 12500

    def test_k_suffix_integer(self):
        assert scraper._parse_int("3k") == 3000

    def test_empty_string(self):
        assert scraper._parse_int("") == 0

    def test_whitespace(self):
        assert scraper._parse_int("   ") == 0

    def test_non_numeric(self):
        assert scraper._parse_int("abc") == 0

    def test_zero(self):
        assert scraper._parse_int("0") == 0

    def test_large_comma(self):
        assert scraper._parse_int("1,234,567") == 1234567


# ---------------------------------------------------------------------------
# search_repos_by_query
# ---------------------------------------------------------------------------

class TestSearchReposByQuery:
    """Test the local keyword/OR filter."""

    REPOS = [
        {"full_name": "user/fastapi-app", "description": "A web framework"},
        {"full_name": "user/django-rest", "description": "REST API toolkit"},
        {"full_name": "user/react-app", "description": "Frontend UI library"},
    ]

    def test_empty_query_returns_all(self):
        result = scraper.search_repos_by_query("", self.REPOS)
        assert len(result) == 3

    def test_name_match(self):
        result = scraper.search_repos_by_query("fastapi", self.REPOS)
        assert len(result) == 1
        assert result[0]["full_name"] == "user/fastapi-app"

    def test_description_match(self):
        result = scraper.search_repos_by_query("web framework", self.REPOS)
        assert len(result) == 1
        assert result[0]["full_name"] == "user/fastapi-app"

    def test_case_insensitive(self):
        result = scraper.search_repos_by_query("DJANGO", self.REPOS)
        assert len(result) == 1

    def test_or_operator(self):
        result = scraper.search_repos_by_query("fastapi OR react", self.REPOS)
        assert len(result) == 2
        names = {r["full_name"] for r in result}
        assert "user/fastapi-app" in names
        assert "user/react-app" in names

    def test_no_match(self):
        result = scraper.search_repos_by_query("nonexistent", self.REPOS)
        assert result == []

    def test_none_description_handled(self):
        repos = [{"full_name": "x/y", "description": None}]
        result = scraper.search_repos_by_query("test", repos)
        assert result == []


# ---------------------------------------------------------------------------
# scrape_trending
# ---------------------------------------------------------------------------

class TestScrapeTrending:
    """Test scrape_trending with mocked HTTP responses."""

    SAMPLE_HTML = """
    <html><body>
    <article class="Box-row">
      <h2><a href="/alice/awesome-project">alice / awesome-project</a></h2>
      <p>An awesome project for testing</p>
      <span itemprop="programmingLanguage">Python</span>
      <a class="Link--muted" href="/alice/awesome-project/stargazers">1,234</a>
      <a class="Link--muted" href="/alice/awesome-project/forks">56</a>
      <span class="d-inline-block float-sm-right">789 stars today</span>
    </article>
    <article class="Box-row">
      <h2><a href="/bob/cool-tool">bob / cool-tool</a></h2>
      <p>A cool command line tool</p>
      <span itemprop="programmingLanguage">Rust</span>
      <a class="Link--muted" href="/bob/cool-tool/stargazers">567</a>
      <a class="Link--muted" href="/bob/cool-tool/network">12</a>
    </article>
    </body></html>
    """

    @patch("scraper.requests.get")
    def test_parses_repos(self, mock_get):
        resp = MagicMock()
        resp.status_code = 200
        resp.text = self.SAMPLE_HTML
        resp.raise_for_status = MagicMock()
        mock_get.return_value = resp

        repos = scraper.scrape_trending(duration="week", limit=10)

        assert len(repos) == 2
        assert repos[0]["full_name"] == "alice/awesome-project"
        assert repos[0]["language"] == "Python"
        assert repos[0]["stargazers_count"] == 1234
        assert repos[0]["forks_count"] == 56
        assert repos[0]["html_url"] == "https://github.com/alice/awesome-project"
        assert repos[1]["full_name"] == "bob/cool-tool"

    @patch("scraper.requests.get")
    def test_limit_respected(self, mock_get):
        resp = MagicMock()
        resp.status_code = 200
        resp.text = self.SAMPLE_HTML
        resp.raise_for_status = MagicMock()
        mock_get.return_value = resp

        repos = scraper.scrape_trending(duration="day", limit=1)
        assert len(repos) == 1

    @patch("scraper.requests.get")
    def test_network_error_returns_empty(self, mock_get):
        mock_get.side_effect = scraper.requests.exceptions.ConnectionError("Connection refused")
        repos = scraper.scrape_trending()
        assert repos == []

    @patch("scraper.requests.get")
    def test_language_url(self, mock_get):
        resp = MagicMock()
        resp.status_code = 200
        resp.text = "<html><body></body></html>"
        resp.raise_for_status = MagicMock()
        mock_get.return_value = resp

        scraper.scrape_trending(language="python")
        call_args = mock_get.call_args
        url = call_args[0][0] if call_args[0] else call_args.kwargs.get("url", "")
        assert "trending/python" in url

    @patch("scraper.requests.get")
    def test_stars_period_parsed(self, mock_get):
        resp = MagicMock()
        resp.status_code = 200
        resp.text = self.SAMPLE_HTML
        resp.raise_for_status = MagicMock()
        mock_get.return_value = resp

        repos = scraper.scrape_trending()
        # First article has "789 stars today"
        assert repos[0]["stars_period"] == 789
