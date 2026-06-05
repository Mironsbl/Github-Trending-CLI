"""Flask web server for GitHub Trending CLI."""

from __future__ import annotations

import logging
import os
from flask import Flask, jsonify, request, render_template

import github_api
import scraper
import twitter
import utils

# Configure production-grade logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("github_trending_web")

app = Flask(__name__)


@app.route("/")
def index():
    """Serve the main web UI."""
    return render_template("index.html")


@app.route("/api/health")
def health():
    """Health check endpoint for production monitoring."""
    return jsonify({"status": "healthy"})


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
    no_cache = request.args.get("no_cache") == "true"

    min_stars = int(min_stars) if min_stars else None

    # Check cache first if not explicitly bypassed
    if not no_cache:
        cached = utils.read_cache(source, duration, limit, language)
        if cached is not None:
            logger.info("Cache hit for source=%s duration=%s lang=%s", source, duration, language)
            if query:
                cached = scraper.search_repos_by_query(query, cached)
            return jsonify({
                "repos": cached,
                "count": len(cached),
                "source": source,
                "cached": True
            })

    logger.info("Cache miss. Fetching from source=%s duration=%s lang=%s", source, duration, language)

    try:
        if source == "trending":
            repos = scraper.scrape_trending(
                duration=duration,
                language=language,
                limit=limit,
            )
            if not repos:
                logger.warning("Scraper failed or returned no results; falling back to Search API")
                repos = github_api.fetch_trending_repos(
                    duration=duration, limit=limit, language=language,
                    topic=topic, sort=sort, min_stars=min_stars, token=token,
                )
                for r in repos:
                    r["source"] = "api"
            else:
                for r in repos:
                    r["source"] = "trending"
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
            for r in repos:
                r["source"] = "api"

        # Write to cache if results were fetched successfully
        if repos:
            utils.write_cache(repos, source, duration, limit, language)

        if query:
            repos = scraper.search_repos_by_query(query, repos)

        return jsonify({
            "repos": repos,
            "count": len(repos),
            "source": source,
            "cached": False
        })

    except github_api.GitHubAPIError as e:
        logger.error("Error fetching trending repositories: %s", e)
        return jsonify({"error": str(e), "repos": [], "count": 0, "cached": False}), 500


@app.route("/api/tweets")
def api_tweets():
    """Search tweets about a repository."""
    query = request.args.get("q")
    if not query:
        return jsonify({"error": "Missing query parameter 'q'", "tweets": []}), 400

    # Cache tweet search results so we don't spam Nitter instances
    cached = utils.read_cache("tweets", query, 5, None, ttl=1800)  # cache for 30 minutes
    if cached is not None:
        logger.info("Cache hit for tweets: query=%s", query)
        return jsonify({"tweets": cached, "cached": True})

    logger.info("Cache miss for tweets: query=%s. Fetching from Nitter.", query)
    tweets = twitter.search_twitter_mentions(query)

    # Save to cache
    if tweets:
        utils.write_cache(tweets, "tweets", query, 5, None)

    return jsonify({"tweets": tweets, "cached": False})



@app.route("/api/search")
def api_search():
    """API endpoint for searching repos with query params."""
    return api_trending()


def run_server():
    """Start the server using Waitress for production-grade hosting."""
    from waitress import serve
    logger.info("🔥 Starting GitHub Trending Web UI on http://localhost:5000 (powered by Waitress)")
    serve(app, host="127.0.0.1", port=5000)


if __name__ == "__main__":
    logger.info("🔥 Starting GitHub Trending Web UI on http://localhost:5000 (debug/dev mode)")
    app.run(host="127.0.0.1", port=5000, debug=True)
