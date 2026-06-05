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
    min_forks = request.args.get("min_forks")
    source = request.args.get("source", "api")
    query = request.args.get("query") or None
    token = request.args.get("token") or os.environ.get("GITHUB_TOKEN")
    no_cache = request.args.get("no_cache") == "true"

    min_stars = int(min_stars) if min_stars else None
    min_forks = int(min_forks) if min_forks else None

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
                    topic=topic, sort=sort, min_stars=min_stars,
                    min_forks=min_forks, token=token,
                    query_keyword=query,
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
                min_forks=min_forks,
                token=token,
                query_keyword=query,
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


@app.route("/api/ai/summarize", methods=["POST"])
def api_ai_summarize():
    """Use Gemini API to summarize or answer questions about repositories (supports history and global search context)."""
    import requests
    data = request.json or {}
    repo_name = data.get("name")
    description = data.get("description")
    language = data.get("language")
    user_query = data.get("query")
    history = data.get("history") or []
    repos = data.get("repos") or []

    api_key = os.environ.get("GEMINI_API_KEY") or request.headers.get("X-Gemini-Key")
    if not api_key:
        return jsonify({"error": "Missing GEMINI_API_KEY. Set it in the environment or provide it in settings."}), 400

    # 1. Base instruction / context message to set the behavior
    if repo_name:
        context_text = (
            f"You are an AI coding assistant. The user is asking about the GitHub repository '{repo_name}'.\n"
            f"Description: {description}\n"
            f"Primary Language: {language}\n\n"
            f"Answer the user's questions or request concisely, accurately, and professionally in Russian. "
            f"If they ask for code, write clean code snippets using Markdown syntax. Avoid unnecessary chit-chat."
        )
    elif repos:
        # Construct context with currently loaded repositories (up to 30 to stay within prompt token bounds)
        repos_str = "\n".join([
            f"- {r.get('full_name') or r.get('name')} ({r.get('language')}): {r.get('description')} [⭐ {r.get('stargazers_count') or r.get('stars', 0)}]"
            for r in repos[:30]
        ])
        context_text = (
            f"You are an AI assistant helping developers browse trending GitHub repositories.\n"
            f"Here is the list of currently loaded repositories on the page:\n{repos_str}\n\n"
            f"Answer the user's questions or request about these repositories. Keep your answers concise, "
            f"professional, and in Russian. Use markdown formatting and lists where appropriate."
        )
    else:
        context_text = (
            "You are an AI coding assistant. Answer the user's questions about software development, "
            "GitHub, or coding. Keep answers concise, professional, and in Russian."
        )

    # 2. Structure contents for Gemini API (contents schema expects alternative user/model roles)
    contents = []
    
    # We add context as a user message and a model acknowledgment to seed the persona
    contents.append({
        "role": "user",
        "parts": [{"text": context_text}]
    })
    contents.append({
        "role": "model",
        "parts": [{"text": "Понял! Я готов проанализировать репозитории и ответить на любые вопросы на русском языке."}]
    })

    # Add conversation history
    for msg in history:
        # Map roles correctly to Gemini API ("user" and "model")
        role = "user" if msg.get("role") == "user" else "model"
        contents.append({
            "role": role,
            "parts": [{"text": msg.get("text", "")}]
        })

    # Add the current user query (if it's not already in history)
    if user_query:
        contents.append({
            "role": "user",
            "parts": [{"text": user_query}]
        })
    else:
        # If no query is provided, we default to requesting a summary of the selected repo
        summary_request = (
            "Summarize this repository. Provide a concise summary in Russian (3-4 bullet points) explaining:\n"
            "1. What problem it solves.\n"
            "2. Who it is for.\n"
            "3. A quick installation/run command (e.g. pip install or npm install).\n"
            "Use emoji. Keep it brief and visually clean."
        )
        contents.append({
            "role": "user",
            "parts": [{"text": summary_request}]
        })

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": contents
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=15)
        if resp.status_code == 200:
            result = resp.json()
            try:
                text = result["candidates"][0]["content"]["parts"][0]["text"]
                return jsonify({"summary": text})
            except (KeyError, IndexError):
                return jsonify({"error": "Failed to parse Gemini API response. Check model availability."}), 502
        else:
            return jsonify({"error": f"Gemini API returned status {resp.status_code}: {resp.text[:200]}"}), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route("/api/search")
def api_search():
    """API endpoint for searching repos with query params."""
    return api_trending()


@app.route("/api/trends")
def api_trends():
    """API endpoint to get active Twitter/X trending topics."""
    # Read the latest loaded repositories from cache to extract trends
    import json
    from pathlib import Path
    
    repos = []
    cache_dir = Path.home() / ".cache" / "github-trending-cli"
    if cache_dir.exists():
        files = list(cache_dir.glob("trending_*.json"))
        if files:
            files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            for file in files:
                try:
                    data = json.loads(file.read_text(encoding="utf-8"))
                    if isinstance(data, list) and len(data) > 0 and ("full_name" in data[0] or "name" in data[0]):
                        repos = data
                        break
                except Exception:
                    continue

    logger.info("Generating Twitter/Dev trends based on %d cached repositories", len(repos))
    trends = twitter.fetch_twitter_trends(repos)
        
    return jsonify({"trends": trends, "cached": False})


def run_server():
    """Start the server using Waitress for production-grade hosting."""
    from waitress import serve
    logger.info("🔥 Starting GitHub Trending Web UI on http://localhost:5000 (powered by Waitress)")
    serve(app, host="127.0.0.1", port=5000)


if __name__ == "__main__":
    logger.info("🔥 Starting GitHub Trending Web UI on http://localhost:5000 (debug/dev mode)")
    app.run(host="127.0.0.1", port=5000, debug=True)
