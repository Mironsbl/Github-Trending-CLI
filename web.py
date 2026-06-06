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


def _fetch_readme(repo_name: str, token: str | None = None) -> str:
    """Fetch README content using the GitHub API (with base64 decoding), fallback to raw content."""
    import requests
    import base64
    import os
    
    resolved_token = token or os.environ.get("GITHUB_TOKEN")
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/vnd.github+json"
    }
    if resolved_token:
        headers["Authorization"] = f"Bearer {resolved_token}"
        
    url = f"https://api.github.com/repos/{repo_name}/readme"
    try:
        r = requests.get(url, headers=headers, timeout=4)
        if r.status_code == 200:
            data = r.json()
            content = data.get("content", "")
            encoding = data.get("encoding", "")
            if encoding == "base64" and content:
                try:
                    return base64.b64decode(content).decode("utf-8", errors="ignore")
                except Exception:
                    pass
    except Exception as e:
        logger.warning("GitHub API readme fetch failed for %s: %s, trying raw fallback", repo_name, e)
        
    # Fallback to raw URLs
    for branch in ["main", "master"]:
        for filename in ["README.md", "readme.md", "README.markdown", "README.txt"]:
            try:
                raw_url = f"https://raw.githubusercontent.com/{repo_name}/{branch}/{filename}"
                resp = requests.get(raw_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=3)
                if resp.status_code == 200:
                    return resp.text
            except Exception:
                continue
    return ""

import re

def expand_query(query: str) -> str:
    if not query:
        return ""
        
    def _expand(q: str) -> str:
        if not q:
            return ""
        
        # Lowercase for mapping
        q_lower = q.lower().strip()
        
        # 1. Check for exact phrase matches first
        exact_phrases = {
            "обход edr": 'in:name,description "edr bypass" OR in:name,description "bypass edr" OR in:name,description "edr evasion" OR in:name,description unhooking',
            "обход av": 'in:name,description "av bypass" OR in:name,description "bypass av" OR in:name,description "av evasion"',
            "обход waf": 'in:name,description "waf bypass" OR in:name,description "bypass waf" OR in:name,description "waf evasion"',
            "обход песочницы": 'in:name,description "sandbox escape" OR in:name,description "sandbox bypass" OR in:name,description "vm detection"',
            "edr bypass": 'in:name,description "edr bypass" OR in:name,description "bypass edr" OR in:name,description "edr evasion" OR in:name,description unhooking',
            "av bypass": 'in:name,description "av bypass" OR in:name,description "bypass av" OR in:name,description "av evasion"',
            "waf bypass": 'in:name,description "waf bypass" OR in:name,description "bypass waf" OR in:name,description "waf evasion"',
            "sandbox escape": 'in:name,description "sandbox escape" OR in:name,description "sandbox bypass" OR in:name,description "vm detection"',
            "шаблоны обходы и взломы": 'in:name,description exploit template OR in:name,description bypass template OR in:name,description hack template',
            "шаблоны обходы взломы": 'in:name,description exploit template OR in:name,description bypass template OR in:name,description hack template',
        }
        
        if q_lower in exact_phrases:
            return exact_phrases[q_lower]

        # 2. Check if the query contains explicit OR/ИЛИ operator
        if " or " in f" {q_lower} " or " или " in f" {q_lower} ":
            parts = re.split(r'\s+(?:or|или)\s+', q, flags=re.IGNORECASE)
            expanded_parts = []
            for part in parts:
                part_expanded = _expand(part.strip())
                if part_expanded:
                    expanded_parts.append(part_expanded)
            if expanded_parts:
                flat_parts = []
                for p in expanded_parts:
                    for sub in p.split(" OR "):
                        sub_stripped = sub.strip()
                        if sub_stripped and sub_stripped not in flat_parts:
                            flat_parts.append(sub_stripped)
                return " OR ".join(flat_parts)

        # 3. Tokenize the query
        tokens = re.findall(r'(?:[^\s"]+|"[^"]*")+', q)
        
        word_map = {
            "шаблон": "template",
            "шаблоны": "template",
            "обход": "bypass",
            "обходы": "bypass",
            "взлом": "exploit",
            "взломы": "exploit",
            "уязвимость": "vulnerability",
            "уязвимости": "vulnerability",
            "загрузчик": "loader",
            "инжектор": "injector",
            "инжекция": "inject",
            "шеллкод": "shellcode",
            "пейлоад": "payload",
            "малварь": "malware",
            "руткит": "rootkit",
            "бэкдор": "backdoor",
            "шифровальщик": "ransomware",
            "криптор": "crypter",
            "обфускатор": "obfuscator",
            "стилер": "stealer",
            "клиппер": "clipper",
            "майнер": "miner",
            "сканер": "scanner",
            "фишинг": "phishing",
            "скрытый": "stealth",
            "обнаружение": "detection",
            "сеть": "network",
            "прокси": "proxy",
            "туннель": "tunnel",
        }
        
        russian_stop_words = {"и", "в", "на", "для", "под", "с", "а", "или", "но", "о", "об", "обо", "из", "от", "до", "без"}
        
        new_tokens = []
        
        for token in tokens:
            clean_token = token.strip('"').lower()
            if clean_token in russian_stop_words:
                continue
                
            if clean_token in word_map:
                new_tokens.append(word_map[clean_token])
            else:
                new_tokens.append(token)
                
        if new_tokens:
            joined = " ".join(new_tokens)
            if joined.lower().startswith("in:name,description"):
                return joined
            return "in:name,description " + joined
        else:
            return "in:name,description " + q

    res = _expand(query)
    if not res:
        return ""
    # Enforce GitHub operator limit: maximum 5 OR operators (6 terms)
    parts = [p.strip() for p in res.split(" OR ") if p.strip()]
    seen = []
    for p in parts:
        if p not in seen:
            seen.append(p)
    return " OR ".join(seen[:6])


def expand_query_with_gemini(query: str, api_key: str) -> str:
    import requests
    import json
    
    prompt = (
        "You are an expert GitHub search query optimizer. "
        "The user wants to find obscure/hidden security repositories, PoCs, bypasses, or hacks on GitHub based on their search term.\n"
        "Your task is to take the user's query (which may be in English, Russian, or mixed) and rewrite it into an advanced, optimized GitHub Search API query using simple boolean operators (AND, OR) and field qualifiers (in:name,description).\n\n"
        "Rules:\n"
        "1. Do NOT use parentheses grouping like (exploit OR bypass) because the GitHub parser fails on them. Instead, expand it explicitly like 'in:name,description exploit OR in:name,description bypass'.\n"
        "2. Translate Russian terms to exact, professional English cybersecurity terms.\n"
        "3. Focus terms on name/description search (e.g. use 'in:name,description').\n"
        "4. Keep the query concise and under 150 characters to prevent GitHub query limit errors.\n"
        "5. Output ONLY the raw optimized query string. Do NOT enclose in markdown backticks, do NOT add comments, do NOT write anything else. Just the query.\n\n"
        f"User Query: {query}\n"
        "Optimized GitHub Search Query:"
    )
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}]
    }
    
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=5)
        if resp.status_code == 200:
            result = resp.json()
            text = result["candidates"][0]["content"]["parts"][0]["text"].strip()
            text = re.sub(r'^[`"\']+|[`"\']+$', '', text)
            if text:
                return text
    except Exception as e:
        logger.warning("Gemini query expansion failed: %s", e)
    
    return expand_query(query)


def filter_obscure_repos(repos: list[dict], original_query: str) -> list[dict]:
    if not repos:
        return []
    
    query_lower = original_query.lower()
    has_template_term = any(t in query_lower for t in ["template", "boilerplate", "шаблон", "структура", "пример"])
    
    # Exclusions
    negatives = ["course", "tutorial", "exercise", "practice", "homework", "assignment", "awesome-list", "awesome", "class-", "university", "school", "student", "learn-", "learning-"]
    if not has_template_term:
        negatives.extend(["template", "boilerplate", "boiler-plate"])
        
    # Dynamically remove any negative word if it (or its Russian equivalent) is mentioned in the query
    cleaned_negatives = []
    for neg in negatives:
        if neg in query_lower:
            continue
        if neg == "awesome" and any(w in query_lower for w in ["лучшее", "подборка", "офигенный"]):
            continue
        if neg == "tutorial" and any(w in query_lower for w in ["туториал", "обучение", "руководство"]):
            continue
        if neg == "course" and any(w in query_lower for w in ["курс", "урок"]):
            continue
        cleaned_negatives.append(neg)
        
    filtered = []
    for r in repos:
        name = (r.get("name") or "").lower()
        full_name = (r.get("full_name") or "").lower()
        desc = (r.get("description") or "").lower()
        topics = [t.lower() for t in r.get("topics", [])]
        
        is_spam = False
        for neg in cleaned_negatives:
            if neg in name or neg in desc or any(neg in t for t in topics):
                is_spam = True
                break
                
        if not is_spam:
            filtered.append(r)
            
    return filtered


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
    deep_search = request.args.get("deep_search") == "true"

    min_stars = int(min_stars) if min_stars else None
    max_stars = int(max_stars) if max_stars else None
    min_forks = int(min_forks) if min_forks else None

    original_query = query
    # Deep/Obscure Search query optimization
    if query:
        # Check if there are Russian letters or deep search is checked
        has_russian = any(c in query for c in "абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ")
        if deep_search or has_russian:
            api_key = os.environ.get("GEMINI_API_KEY")
            if api_key:
                enhanced_query = expand_query_with_gemini(query, api_key)
            else:
                enhanced_query = expand_query(query)
            
            # Enforce GitHub operator limit: maximum 5 OR operators (6 terms)
            if enhanced_query:
                parts = [p.strip() for p in enhanced_query.split(" OR ") if p.strip()]
                seen = []
                for p in parts:
                    if p not in seen:
                        seen.append(p)
                enhanced_query = " OR ".join(seen[:6])
                
            logger.info("Rewrote query '%s' to '%s' (deep_search=%s, has_russian=%s)", query, enhanced_query, deep_search, has_russian)
            query = enhanced_query

    if deep_search:
        exclude_org = True
        # Target obscure repositories: stars 2 to 600
        if min_stars is None:
            min_stars = 2
        if max_stars is None:
            max_stars = 600

    # Check cache first if not explicitly bypassed and no filters are active
    has_filters = bool(query or author or exclude_org or min_stars or max_stars or min_forks or deep_search)
    if not no_cache and not has_filters:
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



        if query and source == "trending":
            filtered_repos = scraper.search_repos_by_query(query, repos)
            if not filtered_repos:
                logger.info("Scraper keyword filter returned 0 results. Falling back to Search API with active pushed filter.")
                since_date = utils.get_since_date(duration)
                fallback_query = f"{query} pushed:>{since_date}"
                try:
                    filtered_repos = github_api.fetch_trending_repos(
                        duration=duration, limit=limit, language=language,
                        topic=topic, sort=api_sort, min_stars=min_stars,
                        max_stars=max_stars, min_forks=min_forks, token=token,
                        query_keyword=fallback_query, author=author,
                        exclude_org=exclude_org,
                    )
                    for r in filtered_repos:
                        r["source"] = "api_fallback"
                except Exception as ex:
                    logger.warning("API fallback search failed: %s", ex)
            repos = filtered_repos


        # Apply local filtering if search query is active
        if original_query and repos:
            repos = filter_obscure_repos(repos, original_query)

        # Apply other local filters for trending source to ensure they are respected
        if source == "trending" and repos:
            filtered = []
            for r in repos:
                stars = r.get("stargazers_count") or r.get("stars") or 0
                forks = r.get("forks_count") or r.get("forks") or 0
                
                if min_stars is not None and stars < min_stars:
                    continue
                if max_stars is not None and stars > max_stars:
                    continue
                if min_forks is not None and forks < min_forks:
                    continue
                if author:
                    r_name = r.get("full_name") or r.get("name") or ""
                    r_owner = r_name.split("/")[0] if "/" in r_name else ""
                    if r_owner.lower() != author.lower():
                        continue
                if exclude_org:
                    big_orgs = {"google", "microsoft", "facebook", "meta", "apple", "amazon", "netflix", "apache", "github", "hashicorp", "aws", "vercel", "cloudflare", "kubernetes", "docker", "elastic", "mozilla", "canonical", "oracle"}
                    r_name = r.get("full_name") or r.get("name") or ""
                    r_owner = r_name.split("/")[0].lower() if "/" in r_name else ""
                    if r_owner in big_orgs:
                        continue
                filtered.append(r)
            repos = filtered

        # Supplement with Search API if count is below requested limit for trending source
        if source == "trending" and len(repos) < limit:
            logger.info("Trending repos count (%d) is below limit (%d). Supplementing from Search API.", len(repos), limit)
            try:
                api_repos = github_api.fetch_trending_repos(
                    duration=duration,
                    limit=limit * 2,  # Fetch more to ensure we have enough after filtering
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
                
                if original_query and api_repos:
                    api_repos = filter_obscure_repos(api_repos, original_query)
                    
                existing_names = {r.get("full_name", "").lower() for r in repos}
                for r in api_repos:
                    r_name = r.get("full_name", "").lower()
                    if r_name and r_name not in existing_names:
                        r["source"] = "api_supplement"
                        repos.append(r)
                        existing_names.add(r_name)
                        if len(repos) >= limit:
                            break
            except Exception as e:
                logger.warning("Failed to supplement trending repos from Search API: %s", e)


        # Sort results before returning
        if sort == "hotness":
            repos = sorted(repos, key=_calculate_hotness, reverse=True)
        elif sort == "forks":
            repos = sorted(repos, key=lambda x: x.get("forks_count") or x.get("forks") or 0, reverse=True)
        elif sort == "updated":
            repos = sorted(repos, key=lambda x: x.get("updated_at") or x.get("pushed_at") or "", reverse=True)
        elif sort == "stars":
            repos = sorted(repos, key=lambda x: x.get("stargazers_count") or x.get("stars") or 0, reverse=True)

        # Write to cache so that the full, filtered, and supplemented list is saved
        if repos:
            utils.write_cache(repos, source, duration, limit, language)

        return jsonify({
            "repos": repos,
            "count": len(repos),
            "source": source,
            "cached": False
        })

    except github_api.GitHubAPIError as e:
        logger.error("Error fetching trending repositories: %s", e)
        return jsonify({"error": str(e), "repos": [], "count": 0, "cached": False}), 500
    except Exception as e:
        logger.exception("Unhandled error fetching trending repositories: %s", e)
        return jsonify({"error": f"Internal server error: {str(e)}", "repos": [], "count": 0, "cached": False}), 500


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
        if repo_name:
            local_summary = (
                f"🤖 **[Локальный ассистент]** (API-ключ Gemini не настроен)\n\n"
                f"📦 **Репозиторий:** `{repo_name}`\n"
                f"📝 **Описание:** {description or 'Нет описания'}\n"
                f"💻 **Язык:** {language or 'Не указан'}\n\n"
                f"💡 *Для получения подробного ИИ-анализа и ответов на вопросы, пожалуйста, добавьте ваш API-ключ Google Gemini в настройках (иконка шестерёнки).* "
            )
            return jsonify({"summary": local_summary})
        elif repos:
            local_summary = (
                f"🤖 **[Локальный ассистент]** (API-ключ Gemini не настроен)\n\n"
                f"Сейчас загружено {len(repos)} репозиториев. "
                f"Вы можете искать по ним, фильтровать по языкам/звёздам и просматривать твиты.\n\n"
                f"💡 *Добавьте ваш API-ключ Gemini в настройках, чтобы общаться с ИИ-ассистентом о деталях этих проектов.*"
            )
            return jsonify({"summary": local_summary})
        else:
            return jsonify({"error": "Missing GEMINI_API_KEY. Set it in the settings."}), 400


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
            is_quota_error = resp.status_code == 429
            if resp.status_code in [400, 403]:
                error_msg = resp.text.lower()
                if "quota" in error_msg or "limit" in error_msg or "billing" in error_msg:
                    is_quota_error = True
                    
            if is_quota_error:
                logger.warning("Gemini API key quota/limit exceeded (status %d). Falling back to local summary.", resp.status_code)
                if repo_name:
                    local_summary = (
                        f"🤖 **[Локальный ассистент]** (API-лимит превышен / Ошибка {resp.status_code})\n\n"
                        f"⚠️ ИИ-ассистент временно недоступен, так как ваш API-ключ Gemini превысил квоту (Rate Limit / Quota Exceeded).\n\n"
                        f"📦 **Репозиторий:** `{repo_name}`\n"
                        f"📝 **Описание:** {description or 'Нет описания'}\n"
                        f"💻 **Язык:** {language or 'Не указан'}\n\n"
                        f"💡 *Вы можете настроить другой ключ или дождаться сброса лимита. Чат продолжает работать в ограниченном режиме.*"
                    )
                    return jsonify({"summary": local_summary})
                elif repos:
                    local_summary = (
                        f"🤖 **[Локальный ассистент]** (API-лимит превышен / Ошибка {resp.status_code})\n\n"
                        f"⚠️ Ваш API-ключ Gemini превысил доступный лимит запросов.\n\n"
                        f"Сейчас загружено {len(repos)} репозиториев. "
                        f"Вы можете искать по ним, фильтровать по языкам/звёздам и просматривать твиты."
                    )
                    return jsonify({"summary": local_summary})
            
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


def _compute_trust_score(repo_data, has_readme, has_ci, has_tests, has_license):
    """Compute a trust score (0-100) for a GitHub repository with per-category breakdown."""
    from datetime import datetime, timezone

    breakdown = {}
    score = 0

    # 1. Commit Frequency / Freshness (20 pts) - use pushed_at
    freshness_score = 0
    freshness_detail = "No push data available"
    pushed = repo_data.get('pushed_at', '')
    if pushed:
        try:
            pushed_dt = datetime.fromisoformat(pushed.replace('Z', '+00:00'))
            days_since = (datetime.now(timezone.utc) - pushed_dt).days
            if days_since <= 7:
                freshness_score = 20
                freshness_detail = f"Last push {days_since} day(s) ago"
            elif days_since <= 30:
                freshness_score = 15
                freshness_detail = f"Last push {days_since} days ago"
            elif days_since <= 90:
                freshness_score = 10
                freshness_detail = f"Last push {days_since} days ago"
            elif days_since <= 365:
                freshness_score = 5
                freshness_detail = f"Last push {days_since} days ago"
            else:
                freshness_detail = f"Stale — last push {days_since} days ago"
        except Exception:
            pass
    score += freshness_score
    breakdown["freshness"] = {"score": freshness_score, "max": 20, "detail": freshness_detail}

    # 2. Contributors diversity (15 pts) - use forks as proxy
    contributors_score = 0
    forks = repo_data.get('forks_count', 0)
    if forks >= 100:
        contributors_score = 15
        contributors_detail = "100+ forks"
    elif forks >= 30:
        contributors_score = 12
        contributors_detail = "30+ forks"
    elif forks >= 10:
        contributors_score = 8
        contributors_detail = "10+ forks"
    elif forks >= 3:
        contributors_score = 5
        contributors_detail = "3+ forks"
    elif forks >= 1:
        contributors_score = 2
        contributors_detail = f"{forks} fork(s)"
    else:
        contributors_detail = "No forks"
    score += contributors_score
    breakdown["contributors"] = {"score": contributors_score, "max": 15, "detail": contributors_detail}

    # 3. Issue Response (15 pts) - use open_issues ratio relative to stars
    issues_score = 0
    stars = repo_data.get('stargazers_count', 0)
    issues = repo_data.get('open_issues_count', 0)
    if stars > 0:
        ratio = issues / stars
        if ratio < 0.05:
            issues_score = 15
            issues_detail = "Low issue ratio"
        elif ratio < 0.1:
            issues_score = 12
            issues_detail = "Moderate issue ratio"
        elif ratio < 0.2:
            issues_score = 8
            issues_detail = "Elevated issue ratio"
        else:
            issues_score = 4
            issues_detail = "High issue ratio"
    else:
        issues_detail = "No stars to compute ratio"
    score += issues_score
    breakdown["issues"] = {"score": issues_score, "max": 15, "detail": issues_detail}

    # 4. Has Tests (10 pts)
    tests_score = 10 if has_tests else 0
    tests_detail = "Test directory found" if has_tests else "No test directory detected"
    score += tests_score
    breakdown["tests"] = {"score": tests_score, "max": 10, "detail": tests_detail}

    # 5. Has CI/CD (10 pts)
    ci_score = 10 if has_ci else 0
    ci_detail = "GitHub Actions found" if has_ci else "No CI/CD configuration detected"
    score += ci_score
    breakdown["ci_cd"] = {"score": ci_score, "max": 10, "detail": ci_detail}

    # 6. License (10 pts)
    license_score = 0
    if has_license:
        license_score = 10
        license_name = has_license if isinstance(has_license, str) else "Present"
        license_detail = license_name
    else:
        license_detail = "No license detected"
    score += license_score
    breakdown["license"] = {"score": license_score, "max": 10, "detail": license_detail}

    # 7. Documentation quality (10 pts)
    doc_score = 10 if has_readme else 0
    doc_detail = "README.md present" if has_readme else "No README found"
    score += doc_score
    breakdown["documentation"] = {"score": doc_score, "max": 10, "detail": doc_detail}

    # 8. Size & Maturity (10 pts) - watchers / subscribers
    maturity_score = 0
    watchers = repo_data.get('subscribers_count', repo_data.get('watchers_count', 0))
    if watchers >= 100:
        maturity_score = 10
        maturity_detail = "100+ watchers"
    elif watchers >= 30:
        maturity_score = 7
        maturity_detail = "30+ watchers"
    elif watchers >= 10:
        maturity_score = 4
        maturity_detail = "10+ watchers"
    elif watchers >= 1:
        maturity_score = 2
        maturity_detail = f"{watchers} watcher(s)"
    else:
        maturity_detail = "No watchers"
    score += maturity_score
    breakdown["maturity"] = {"score": maturity_score, "max": 10, "detail": maturity_detail}

    return min(score, 100), breakdown


def _score_to_grade(score: int) -> str:
    """Map a trust score (0-100) to a letter grade."""
    if score >= 90:
        return "A+"
    elif score >= 80:
        return "A"
    elif score >= 70:
        return "B+"
    elif score >= 60:
        return "B"
    elif score >= 50:
        return "C"
    elif score >= 40:
        return "D"
    else:
        return "F"


def _check_ci_exists(repo_name: str) -> bool:
    """Check if a GitHub Actions CI workflow exists via lightweight HEAD requests."""
    import requests
    headers = {"User-Agent": "Mozilla/5.0"}
    ci_filenames = ["ci.yml", "build.yml", "test.yml", "main.yml"]
    for branch in ["main", "master"]:
        for fname in ci_filenames:
            try:
                url = f"https://raw.githubusercontent.com/{repo_name}/{branch}/.github/workflows/{fname}"
                r = requests.head(url, headers=headers, timeout=3, allow_redirects=True)
                if r.status_code == 200:
                    return True
            except Exception:
                continue
    return False


def _check_tests_exist(repo_name: str, token: str | None = None) -> bool:
    """Check if a test directory exists using the GitHub API tree endpoint."""
    import requests
    headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    for branch in ["main", "master"]:
        try:
            url = f"https://api.github.com/repos/{repo_name}/git/trees/{branch}"
            r = requests.get(url, headers=headers, timeout=5)
            if r.status_code == 200:
                tree = r.json().get("tree", [])
                for item in tree:
                    if item.get("type") == "tree" and item.get("path", "").lower() in ("tests", "test", "spec", "__tests__"):
                        return True
                # If we got a valid tree but no test dir, no need to try next branch
                return False
        except Exception:
            continue
    return False


@app.route("/api/repo/trust-score")
def api_repo_trust_score():
    """Compute a Trust Score (0-100) for a GitHub repository."""
    import requests as req_lib

    repo = request.args.get("repo")
    if not repo or "/" not in repo:
        return jsonify({"error": "Missing or invalid 'repo' query parameter. Use format: owner/name"}), 400

    token = os.environ.get("GITHUB_TOKEN")
    headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"

    # Fetch repository metadata from GitHub API
    try:
        api_url = f"https://api.github.com/repos/{repo}"
        resp = req_lib.get(api_url, headers=headers, timeout=10)
        if resp.status_code == 404:
            return jsonify({"error": f"Repository '{repo}' not found"}), 404
        if resp.status_code == 403:
            logger.warning("GitHub API rate limit hit for trust-score endpoint")
            return jsonify({"error": "GitHub API rate limit exceeded. Try again later or set GITHUB_TOKEN."}), 429
        if resp.status_code != 200:
            return jsonify({"error": f"GitHub API returned status {resp.status_code}"}), 502
        repo_data = resp.json()
    except req_lib.exceptions.Timeout:
        logger.error("Timeout fetching repo metadata for %s", repo)
        return jsonify({"error": "Timeout fetching repository data from GitHub"}), 504
    except Exception as e:
        logger.error("Failed to fetch repo metadata for %s: %s", repo, e)
        return jsonify({"error": str(e)}), 500

    # Check signals in parallel-ish fashion (sequential but fast)
    has_readme = bool(_fetch_readme(repo))
    has_ci = _check_ci_exists(repo)
    has_tests = _check_tests_exist(repo, token)

    # License info from the API response
    license_info = repo_data.get("license")
    has_license = False
    if license_info and isinstance(license_info, dict):
        has_license = license_info.get("spdx_id") or license_info.get("name") or True

    trust_score, breakdown = _compute_trust_score(repo_data, has_readme, has_ci, has_tests, has_license)
    grade = _score_to_grade(trust_score)

    logger.info("Trust score for %s: %d (%s)", repo, trust_score, grade)

    return jsonify({
        "repo": repo,
        "trust_score": trust_score,
        "grade": grade,
        "breakdown": breakdown,
    })


@app.route("/api/repo/velocity")
def api_repo_velocity():
    """Compute star velocity for a GitHub repository."""
    import requests as req_lib
    from datetime import datetime, timezone, timedelta

    repo = request.args.get("repo")
    if not repo or "/" not in repo:
        return jsonify({"error": "Missing or invalid 'repo' query parameter. Use format: owner/name"}), 400

    token = os.environ.get("GITHUB_TOKEN")
    headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"

    # Fetch repository metadata
    try:
        api_url = f"https://api.github.com/repos/{repo}"
        resp = req_lib.get(api_url, headers=headers, timeout=10)
        if resp.status_code == 404:
            return jsonify({"error": f"Repository '{repo}' not found"}), 404
        if resp.status_code == 403:
            logger.warning("GitHub API rate limit hit for velocity endpoint")
            return jsonify({"error": "GitHub API rate limit exceeded. Try again later or set GITHUB_TOKEN."}), 429
        if resp.status_code != 200:
            return jsonify({"error": f"GitHub API returned status {resp.status_code}"}), 502
        repo_data = resp.json()
    except req_lib.exceptions.Timeout:
        logger.error("Timeout fetching repo metadata for velocity: %s", repo)
        return jsonify({"error": "Timeout fetching repository data from GitHub"}), 504
    except Exception as e:
        logger.error("Failed to fetch repo metadata for velocity: %s: %s", repo, e)
        return jsonify({"error": str(e)}), 500

    stars_total = repo_data.get("stargazers_count", 0)

    # Estimate recent stars using the stargazers API (last page method)
    # Fetch the most recent stargazers with timestamps to estimate period activity
    stars_period = 0
    try:
        star_headers = dict(headers)
        star_headers["Accept"] = "application/vnd.github.v3.star+json"
        # Get the last page of stargazers to find recent ones
        star_url = f"https://api.github.com/repos/{repo}/stargazers?per_page=100&page=1"
        if stars_total > 100:
            # Jump to the last page to get recent stargazers
            last_page = (stars_total // 100) + (1 if stars_total % 100 else 0)
            star_url = f"https://api.github.com/repos/{repo}/stargazers?per_page=100&page={last_page}"

        star_resp = req_lib.get(star_url, headers=star_headers, timeout=10)
        if star_resp.status_code == 200:
            stargazers = star_resp.json()
            cutoff = datetime.now(timezone.utc) - timedelta(days=30)
            for sg in stargazers:
                starred_at = sg.get("starred_at", "")
                if starred_at:
                    try:
                        dt = datetime.fromisoformat(starred_at.replace("Z", "+00:00"))
                        if dt >= cutoff:
                            stars_period += 1
                    except Exception:
                        continue
    except Exception as e:
        logger.warning("Failed to fetch stargazer timestamps for %s: %s", repo, e)

    # Compute velocity percentage
    if stars_total > 0:
        velocity_pct = round((stars_period / stars_total) * 100, 2)
    else:
        velocity_pct = 0.0

    # Determine trend direction
    if velocity_pct > 1.0:
        trend = "rising"
    elif velocity_pct >= 0.1:
        trend = "stable"
    else:
        trend = "declining"

    logger.info("Velocity for %s: %d period stars, %.2f%% (%s)", repo, stars_period, velocity_pct, trend)

    return jsonify({
        "repo": repo,
        "stars_total": stars_total,
        "stars_period": stars_period,
        "velocity_pct": velocity_pct,
        "trend": trend,
    })


@app.route("/api/repo/similar")
def api_repo_similar():
    """Find similar repositories using topics, language, and name/description keywords."""
    import re
    import requests
    repo_name = request.args.get("name")
    if not repo_name:
        return jsonify({"error": "Missing repo name"}), 400
        
    token = request.args.get("token") or os.environ.get("GITHUB_TOKEN")
    
    topics = request.args.getlist("topics")
    language = request.args.get("language")
    description = request.args.get("description")
    
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/vnd.github+json"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
        
    # If the client did not pass some of the data, try fetching it from GitHub
    if not topics or not language or not description:
        try:
            r = requests.get(f"https://api.github.com/repos/{repo_name}", headers=headers, timeout=5)
            if r.status_code == 200:
                data = r.json()
                if not topics:
                    topics = data.get("topics", [])
                if not language:
                    language = data.get("language")
                if not description:
                    description = data.get("description") or ""
        except Exception as e:
            logger.warning("Failed to fetch repo details for similarity: %s", e)
            
    # Build a search query for similar repos
    query_parts = []
    
    # Exclude original repo
    query_parts.append(f"-repo:{repo_name}")
    
    if language:
        query_parts.append(f"language:{language}")
        
    # Add topics
    if topics:
        for t in topics[:3]:
            query_parts.append(f"topic:{t}")
            
    # If we don't have topics, we extract key terms from the repository name or description
    if not topics:
        name_parts = re.split(r'[-_\s]+', repo_name.split("/")[-1])
        name_terms = [p.lower() for p in name_parts if len(p) > 2 and p.lower() not in ["git", "github"]]
        if name_terms:
            query_parts.append(name_terms[0]) # Use the first term for high precision
        elif description:
            desc_words = re.findall(r'\b[a-zA-Z]{3,}\b', description)
            common_words = {"the", "and", "for", "with", "this", "that", "from", "your", "will", "from", "github", "repository", "code"}
            keywords = [w.lower() for w in desc_words if w.lower() not in common_words]
            if keywords:
                query_parts.append(keywords[0]) # Use the first keyword
                
    search_query = " ".join(query_parts)
    search_query += " stars:>=5"
    
    logger.info("Finding repositories similar to '%s' with query '%s'", repo_name, search_query)
    
    try:
        repos = github_api.fetch_trending_repos(
            duration="month",
            limit=10,
            query_keyword=search_query,
            token=token
        )
        return jsonify({"repos": repos, "query": search_query})
    except Exception as e:
        logger.error("Failed to fetch similar repositories: %s", e)
        return jsonify({"error": str(e), "repos": []}), 500


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
