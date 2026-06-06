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
app.config['TEMPLATES_AUTO_RELOAD'] = True


@app.route("/")
def index():
    """Serve the main web UI."""
    return render_template("index.html")


@app.route("/api/health")
def health():
    """Health check endpoint for production monitoring."""
    return jsonify({"status": "healthy"})


def _calculate_hotness(r: dict) -> float:
    """Calculate hotness score (hype index) for sorting."""
    stars_period = r.get("stars_period") or 0
    stargazers = r.get("stargazers_count") or r.get("stars") or 0
    forks = r.get("forks_count") or r.get("forks") or 0
    if stars_period > 0:
        return float(stars_period * 10 + forks * 2)
    else:
        return float(stargazers * 0.1 + forks * 0.5)


def _fetch_readme(repo_name: str) -> str:
    """Fetch README.md from GitHub raw content (tries main, then master)."""
    import requests
    headers = {"User-Agent": "Mozilla/5.0"}
    for branch in ["main", "master"]:
        for filename in ["README.md", "readme.md"]:
            try:
                url = f"https://raw.githubusercontent.com/{repo_name}/{branch}/{filename}"
                r = requests.get(url, headers=headers, timeout=3)
                if r.status_code == 200:
                    return r.text
            except Exception:
                continue
    return ""


@app.route("/api/trending")
def api_trending():
    """API endpoint for trending repos."""
    duration = request.args.get("duration", "week")
    limit = int(request.args.get("limit", "25"))
    language = request.args.get("language") or None
    topic = request.args.get("topic") or None
    sort = request.args.get("sort", "stars")
    min_stars = request.args.get("min_stars")
    max_stars = request.args.get("max_stars")
    min_forks = request.args.get("min_forks")
    exclude_org = request.args.get("exclude_org") == "true"
    source = request.args.get("source", "api")
    query = request.args.get("query") or None
    author = request.args.get("author") or None
    token = request.args.get("token") or os.environ.get("GITHUB_TOKEN")
    no_cache = request.args.get("no_cache") == "true"

    min_stars = int(min_stars) if min_stars else None
    max_stars = int(max_stars) if max_stars else None
    min_forks = int(min_forks) if min_forks else None

    # Check cache first if not explicitly bypassed
    if not no_cache and not author and not exclude_org and max_stars is None and not (source == "api" and query):
        cached = utils.read_cache(source, duration, limit, language)
        if cached is not None:
            logger.info("Cache hit for source=%s duration=%s lang=%s", source, duration, language)
            if query and source == "trending":
                cached = scraper.search_repos_by_query(query, cached)
            
            # Sort cached results
            if sort == "hotness":
                cached = sorted(cached, key=_calculate_hotness, reverse=True)
            elif sort == "forks":
                cached = sorted(cached, key=lambda x: x.get("forks_count") or x.get("forks") or 0, reverse=True)
            elif sort == "updated":
                cached = sorted(cached, key=lambda x: x.get("updated_at") or x.get("pushed_at") or "", reverse=True)
            elif sort == "stars":
                cached = sorted(cached, key=lambda x: x.get("stargazers_count") or x.get("stars") or 0, reverse=True)
                
            return jsonify({
                "repos": cached,
                "count": len(cached),
                "source": source,
                "cached": True
            })

    logger.info("Cache miss. Fetching from source=%s duration=%s lang=%s", source, duration, language)

    try:
        api_sort = "stars" if sort == "hotness" else sort
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
                    topic=topic, sort=api_sort, min_stars=min_stars,
                    max_stars=max_stars,
                    min_forks=min_forks, token=token,
                    query_keyword=query, author=author,
                    exclude_org=exclude_org,
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
                sort=api_sort,
                min_stars=min_stars,
                max_stars=max_stars,
                min_forks=min_forks,
                token=token,
                query_keyword=query,
                author=author,
                exclude_org=exclude_org,
            )
            for r in repos:
                r["source"] = "api"

        # Write to cache if results were fetched successfully
        if repos:
            utils.write_cache(repos, source, duration, limit, language)

        if query and source == "trending":
            repos = scraper.search_repos_by_query(query, repos)

        # Sort results before returning
        if sort == "hotness":
            repos = sorted(repos, key=_calculate_hotness, reverse=True)
        elif sort == "forks":
            repos = sorted(repos, key=lambda x: x.get("forks_count") or x.get("forks") or 0, reverse=True)
        elif sort == "updated":
            repos = sorted(repos, key=lambda x: x.get("updated_at") or x.get("pushed_at") or "", reverse=True)
        elif sort == "stars":
            repos = sorted(repos, key=lambda x: x.get("stargazers_count") or x.get("stars") or 0, reverse=True)

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

    # Fetch README.md if we are analyzing a specific repo
    readme_content = ""
    if repo_name:
        try:
            readme_content = _fetch_readme(repo_name)
            if readme_content:
                readme_content = readme_content[:20000] # Limit to 20k characters
        except Exception as e:
            logger.warning("Failed to fetch README for %s: %s", repo_name, e)

    # 1. Base instruction / context message to set the behavior
    if repo_name:
        context_text = (
            f"You are an AI coding assistant. The user is asking about the GitHub repository '{repo_name}'.\n"
            f"Description: {description}\n"
            f"Primary Language: {language}\n"
        )
        if readme_content:
            context_text += f"\n--- README.md ---\n{readme_content}\n--- END OF README.md ---\n"
            
        context_text += (
            f"\nAnswer the user's questions or request concisely, accurately, and professionally in Russian. "
            f"Focus on practical aspects (installation, main features, usage, architecture) based on the README.md if available. "
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


def _fetch_github_file(repo_name: str, filename: str) -> str:
    """Fetch a specific file from raw GitHub content (tries main, then master)."""
    import requests
    headers = {"User-Agent": "Mozilla/5.0"}
    for branch in ["main", "master"]:
        try:
            url = f"https://raw.githubusercontent.com/{repo_name}/{branch}/{filename}"
            r = requests.get(url, headers=headers, timeout=3)
            if r.status_code == 200:
                return r.text
        except Exception:
            continue
    return ""


@app.route("/api/history")
def api_history():
    """Retrieve trending repositories snapshots from SQLite db."""
    import db
    search = request.args.get("search") or None
    limit = request.args.get("limit", "100")
    try:
        limit = int(limit)
    except ValueError:
        limit = 100
    
    try:
        history = db.get_history(limit=limit, search_query=search)
        return jsonify({"history": history, "count": len(history)})
    except Exception as e:
        logger.error("Failed to fetch history: %s", e)
        return jsonify({"error": str(e), "history": [], "count": 0}), 500


@app.route("/api/history/trends")
def api_history_trends():
    """Get stars and hype growth over time for a repository."""
    import db
    repo = request.args.get("repo")
    if not repo:
        return jsonify({"error": "Missing 'repo' query parameter"}), 400
    try:
        trends = db.get_trends_over_time(repo)
        return jsonify({"repo": repo, "trends": trends})
    except Exception as e:
        logger.error("Failed to fetch historical trends for %s: %s", repo, e)
        return jsonify({"error": str(e)}), 500


@app.route("/api/social/discussions")
def api_social_discussions():
    """Get Hacker News, Reddit, and Twitter discussions for a repository."""
    import social
    import twitter
    repo = request.args.get("repo")
    if not repo:
        return jsonify({"error": "Missing 'repo' query parameter"}), 400

    # Cache results so we don't spam endpoints
    cache_key = f"social_disc_{repo.replace('/', '_')}"
    cached = utils.read_cache("social", cache_key, 1, None, ttl=1800) # cache for 30m
    if cached is not None:
        return jsonify(cached)

    try:
        hn = social.search_hacker_news(repo)
        reddit = social.search_reddit(repo)
        
        # Fallback query Nitter for tweets
        repo_name_only = repo.split("/")[-1]
        tweets = twitter.search_twitter_mentions(repo_name_only)
        
        data = {
            "hn": hn,
            "reddit": reddit,
            "twitter": tweets
        }
        
        # Write to cache
        utils.write_cache(data, "social", cache_key, 1, None)
        return jsonify(data)
    except Exception as e:
        logger.error("Failed to fetch social discussions: %s", e)
        return jsonify({"error": str(e), "hn": [], "reddit": [], "twitter": []}), 500


@app.route("/api/ai/compare", methods=["POST"])
def api_ai_compare():
    """AI side-by-side comparison of multiple repositories."""
    import requests
    data = request.json or {}
    repos_list = data.get("repos") or []
    if not repos_list or len(repos_list) < 2:
        return jsonify({"error": "Please select at least 2 repositories to compare."}), 400
    
    api_key = os.environ.get("GEMINI_API_KEY") or request.headers.get("X-Gemini-Key")
    if not api_key:
        return jsonify({"error": "Missing GEMINI_API_KEY. Set it in the environment or provide it in settings."}), 400

    # Gather info and readmes
    comparison_context = ""
    for r in repos_list[:3]: # Limit to 3 repos for context size
        name = r.get("full_name") or r.get("name")
        desc = r.get("description", "")
        lang = r.get("language", "")
        
        readme = _fetch_readme(name)
        if readme:
            readme = readme[:8000] # Limit to 8k chars each
            
        comparison_context += f"### Repository: {name}\n"
        comparison_context += f"Description: {desc}\n"
        comparison_context += f"Primary Language: {lang}\n"
        if readme:
            comparison_context += f"README Snippet:\n{readme}\n"
        comparison_context += "\n---\n\n"

    prompt = (
        "You are an expert software architect. Perform a side-by-side comparison of the following repositories in Russian.\n"
        "1. Start with a markdown comparison table comparing: Primary Language, Target Audience, Key Feature, Complexity (Low/Medium/High), Active Maintenance (Yes/No/Unknown).\n"
        "2. Detail the core differences in architecture, design approach, and use cases.\n"
        "3. Provide clear recommendations: when to choose which repository.\n"
        "Keep it highly technical, visually clean, and structured. Use emojis where appropriate."
    )

    contents = [
        {"role": "user", "parts": [{"text": f"Here is the context of the repositories:\n\n{comparison_context}\n\n{prompt}"}]}
    ]

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    
    try:
        resp = requests.post(url, json={"contents": contents}, headers=headers, timeout=20)
        if resp.status_code == 200:
            result = resp.json()
            text = result["candidates"][0]["content"]["parts"][0]["text"]
            return jsonify({"comparison": text})
        else:
            return jsonify({"error": f"Gemini API returned status code {resp.status_code}: {resp.text}"}), resp.status_code
    except Exception as e:
        logger.error("Failed to generate AI comparison: %s", e)
        return jsonify({"error": str(e)}), 500


@app.route("/api/ai/security", methods=["POST"])
def api_ai_security():
    """Use Gemini to audit repository's dependency manifest and provide security assessment."""
    import requests
    data = request.json or {}
    repo_name = data.get("name")
    if not repo_name:
        return jsonify({"error": "Missing 'name' in request body"}), 400

    api_key = os.environ.get("GEMINI_API_KEY") or request.headers.get("X-Gemini-Key")
    if not api_key:
        return jsonify({"error": "Missing GEMINI_API_KEY. Set it in the environment or provide it in settings."}), 400

    # Try to find a dependency file
    manifest_files = [
        "package.json",
        "requirements.txt",
        "Cargo.toml",
        "go.mod",
        "pyproject.toml",
        "Gemfile",
        "composer.json"
    ]
    
    manifest_content = ""
    found_file = ""
    for filename in manifest_files:
        content = _fetch_github_file(repo_name, filename)
        if content:
            manifest_content = content[:15000] # Limit size
            found_file = filename
            break
            
    if not manifest_content:
        return jsonify({
            "error": "No dependency manifest file (package.json, requirements.txt, Cargo.toml, go.mod etc.) found in the root of the repository."
        }), 404

    prompt = (
        f"You are a security auditor. Analyze the following dependency file ({found_file}) for the repository '{repo_name}' in Russian.\n"
        f"Manifest Content:\n```\n{manifest_content}\n```\n\n"
        "Provide a structured audit:\n"
        "1. **Security Health Score**: Give an overall grade (A+, A, B, C, D, F) and brief explanation.\n"
        "2. **Core Dependencies**: List the major external packages used and what they do.\n"
        "3. **Security Assessment / Risks**: Highlight any known security risks, overly broad permissions, deprecated packages, or potential attack vectors (like supply chain attacks, typo-squatting potential, or unsafe default setups).\n"
        "4. **Recommendations**: Give actionable advice on how to secure this project's dependencies.\n"
        "Format using markdown. Be professional, direct, and detailed."
    )

    contents = [
        {"role": "user", "parts": [{"text": prompt}]}
    ]

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    
    try:
        resp = requests.post(url, json={"contents": contents}, headers=headers, timeout=20)
        if resp.status_code == 200:
            result = resp.json()
            text = result["candidates"][0]["content"]["parts"][0]["text"]
            return jsonify({"security_audit": text, "file_found": found_file})
        else:
            return jsonify({"error": f"Gemini API returned status code {resp.status_code}: {resp.text}"}), resp.status_code
    except Exception as e:
        logger.error("Failed to generate AI security audit: %s", e)
        return jsonify({"error": str(e)}), 500


def run_server():
    """Start the server using Waitress for production-grade hosting."""
    from waitress import serve
    port = int(os.environ.get("PORT", 5050))
    host = os.environ.get("HOST", "0.0.0.0")
    logger.info("🔥 Starting GitHub Trending Web UI on http://%s:%d (powered by Waitress)", host, port)
    serve(app, host=host, port=port)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5050))
    host = os.environ.get("HOST", "127.0.0.1")
    logger.info("🔥 Starting GitHub Trending Web UI on http://%s:%d (debug/dev mode)", host, port)
    app.run(host=host, port=port, debug=True)
