"""Flask web server for GitHub Trending CLI."""

from __future__ import annotations

import os
from flask import Flask, jsonify, request, render_template

import github_api
import scraper

app = Flask(__name__)


@app.route("/")
def index():
    """Serve the main web UI."""
    return render_template("index.html")


@app.route("/api/trending")
def api_trending():
    """API endpoint for trending repos."""
    duration = request.args.get("duration", "week")
    limit = int(request.args.get("limit", "25"))
    language = request.args.get("language") or None
    topic = request.args.get("topic") or None
    sort = request.args.get("sort", "stars")
    min_stars = request.args.get("min_stars")
    source = request.args.get("source", "api")
    query = request.args.get("query") or None
    token = request.args.get("token") or os.environ.get("GITHUB_TOKEN")

    min_stars = int(min_stars) if min_stars else None

    try:
        if source == "trending":
            repos = scraper.scrape_trending(
                duration=duration,
                language=language,
                limit=limit,
            )
            if not repos:
                repos = github_api.fetch_trending_repos(
                    duration=duration, limit=limit, language=language,
                    topic=topic, sort=sort, min_stars=min_stars, token=token,
                )
        else:
            repos = github_api.fetch_trending_repos(
                duration=duration,
                limit=limit,
                language=language,
                topic=topic,
                sort=sort,
                min_stars=min_stars,
                token=token,
            )

        if query:
            repos = scraper.search_repos_by_query(query, repos)

        return jsonify({"repos": repos, "count": len(repos), "source": source})

    except github_api.GitHubAPIError as e:
        return jsonify({"error": str(e), "repos": [], "count": 0}), 500


@app.route("/api/search")
def api_search():
    """API endpoint for searching repos with query params."""
    return api_trending()


def run_server():
    """Start the Flask server."""
    app.run(host="127.0.0.1", port=5000, debug=False)


if __name__ == "__main__":
    print("\n🔥 GitHub Trending Web UI → http://localhost:5000\n")
    app.run(host="127.0.0.1", port=5000, debug=True)
