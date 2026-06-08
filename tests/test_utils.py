"""Tests for utils.py — date helpers, caching, formatting, and export."""

from __future__ import annotations

import csv
import json
import os
import tempfile
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest

import utils


# ---------------------------------------------------------------------------
# get_since_date
# ---------------------------------------------------------------------------

class TestGetSinceDate:
    """Verify get_since_date returns correct YYYY-MM-DD strings."""

    @patch("utils.datetime")
    def test_day(self, mock_dt):
        mock_dt.now.return_value = datetime(2026, 6, 8, tzinfo=timezone.utc)
        mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
        result = utils.get_since_date("day")
        assert result == "2026-06-07"

    @patch("utils.datetime")
    def test_week(self, mock_dt):
        mock_dt.now.return_value = datetime(2026, 6, 8, tzinfo=timezone.utc)
        mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
        result = utils.get_since_date("week")
        assert result == "2026-06-01"

    @patch("utils.datetime")
    def test_month(self, mock_dt):
        mock_dt.now.return_value = datetime(2026, 6, 8, tzinfo=timezone.utc)
        mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
        result = utils.get_since_date("month")
        assert result == "2026-05-09"

    @patch("utils.datetime")
    def test_year(self, mock_dt):
        mock_dt.now.return_value = datetime(2026, 6, 8, tzinfo=timezone.utc)
        mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
        result = utils.get_since_date("year")
        assert result == "2025-06-08"

    @patch("utils.datetime")
    def test_unknown_duration_defaults_to_week(self, mock_dt):
        mock_dt.now.return_value = datetime(2026, 6, 8, tzinfo=timezone.utc)
        mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
        result = utils.get_since_date("century")
        assert result == "2026-06-01"


# ---------------------------------------------------------------------------
# _cache_key
# ---------------------------------------------------------------------------

class TestCacheKey:
    """Verify _cache_key produces deterministic, stable outputs."""

    def test_deterministic(self):
        k1 = utils._cache_key("api", "week", 10, "python")
        k2 = utils._cache_key("api", "week", 10, "python")
        assert k1 == k2

    def test_different_params_yield_different_keys(self):
        k1 = utils._cache_key("api", "week", 10, "python")
        k2 = utils._cache_key("api", "month", 10, "python")
        assert k1 != k2

    def test_none_language_handled(self):
        k = utils._cache_key("api", "week", 10, None)
        assert k.startswith("trending_")
        assert k.endswith(".json")

    def test_format(self):
        k = utils._cache_key("trending", "day", 25, "rust")
        assert k.startswith("trending_")
        assert k.endswith(".json")
        # hex digest portion is 16 chars
        stem = k.removeprefix("trending_").removesuffix(".json")
        assert len(stem) == 16


# ---------------------------------------------------------------------------
# _star_bar
# ---------------------------------------------------------------------------

class TestStarBar:
    """Edge cases for the Unicode bar chart helper."""

    def test_zero_max_count(self):
        assert utils._star_bar(100, 0) == ""

    def test_equal_count_and_max(self):
        bar = utils._star_bar(10, 10, width=10)
        assert bar == "█" * 10

    def test_half_fill(self):
        bar = utils._star_bar(50, 100, width=10)
        filled = bar.count("█")
        empty = bar.count("░")
        assert filled + empty == 10
        assert filled == 5

    def test_small_count_gets_at_least_one_block(self):
        bar = utils._star_bar(1, 10000, width=15)
        assert bar.startswith("█")
        assert len(bar) == 15

    def test_default_width(self):
        bar = utils._star_bar(5, 10)
        assert len(bar) == 15  # default width


# ---------------------------------------------------------------------------
# _format_stars
# ---------------------------------------------------------------------------

class TestFormatStars:
    """Comma-formatted star counts."""

    def test_small_number(self):
        assert utils._format_stars(42) == "42"

    def test_thousands(self):
        assert utils._format_stars(1_234) == "1,234"

    def test_millions(self):
        assert utils._format_stars(1_234_567) == "1,234,567"

    def test_zero(self):
        assert utils._format_stars(0) == "0"


# ---------------------------------------------------------------------------
# _slim_repo
# ---------------------------------------------------------------------------

class TestSlimRepo:
    """Verify only export-relevant fields are kept."""

    def test_selects_correct_fields(self, sample_repos):
        slim = utils._slim_repo(sample_repos[0])
        expected_keys = {
            "full_name", "html_url", "stargazers_count",
            "forks_count", "language", "description", "created_at",
        }
        assert set(slim.keys()) == expected_keys

    def test_missing_fields_become_none(self):
        slim = utils._slim_repo({"full_name": "x/y"})
        assert slim["language"] is None
        assert slim["stargazers_count"] is None


# ---------------------------------------------------------------------------
# export_json / export_csv
# ---------------------------------------------------------------------------

class TestExportJson:
    def test_writes_valid_json(self, sample_repos):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            path = f.name
        try:
            utils.export_json(sample_repos, path)
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
            assert isinstance(data, list)
            assert len(data) == 3
            assert data[0]["full_name"] == "alice/alpha"
            # Only slim fields should be present
            assert "owner" not in data[0]
        finally:
            os.unlink(path)


class TestExportCsv:
    def test_writes_valid_csv(self, sample_repos):
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w") as f:
            path = f.name
        try:
            utils.export_csv(sample_repos, path)
            with open(path, encoding="utf-8", newline="") as fh:
                reader = csv.DictReader(fh)
                rows = list(reader)
            assert len(rows) == 3
            assert rows[0]["full_name"] == "alice/alpha"
            assert rows[1]["language"] == "Rust"
        finally:
            os.unlink(path)


class TestExportResults:
    def test_json_extension(self, sample_repos):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = f.name
        try:
            utils.export_results(sample_repos, path)
            data = json.loads(open(path).read())
            assert len(data) == 3
        finally:
            os.unlink(path)

    def test_csv_extension(self, sample_repos):
        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            path = f.name
        try:
            utils.export_results(sample_repos, path)
            with open(path, newline="") as fh:
                rows = list(csv.DictReader(fh))
            assert len(rows) == 3
        finally:
            os.unlink(path)

    def test_unsupported_extension_raises(self, sample_repos):
        with pytest.raises(ValueError, match="Unsupported format"):
            utils.export_results(sample_repos, "/tmp/out.xml")
