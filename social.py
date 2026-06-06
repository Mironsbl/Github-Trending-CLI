"""Hacker News and Reddit search integrations for fetching repository discussions."""

from __future__ import annotations

import logging
import urllib.parse
import requests
from datetime import datetime, timezone

logger = logging.getLogger("github_trending_social")


def search_hacker_news(repo_full_name: str) -> list[dict[str, Any]]:
    """Search Hacker News (via Algolia API) for submissions mentioning the repository."""
    results = []
    
    # Try searching by URL
    queries = [
        f"github.com/{repo_full_name}",
        repo_full_name.split("/")[-1] # fallback to repo name
    ]

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    for idx, query in enumerate(queries):
        encoded_query = urllib.parse.quote(query)
        # We query stories (tags=story)
        url = f"https://hn.algolia.com/api/v1/search?query={encoded_query}&tags=story"
        
        try:
            resp = requests.get(url, headers=headers, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                hits = data.get("hits", [])
                for hit in hits[:5]:  # top 5 discussions
                    title = hit.get("title")
                    object_id = hit.get("objectID")
                    points = hit.get("points", 0)
                    comments = hit.get("num_comments", 0)
                    created_at_ts = hit.get("created_at_i")
                    
                    created_str = "Unknown date"
                    if created_at_ts:
                        created_str = datetime.fromtimestamp(created_at_ts, tz=timezone.utc).strftime("%Y-%m-%d")

                    hn_url = f"https://news.ycombinator.com/item?id={object_id}"
                    results.append({
                        "title": title,
                        "url": hn_url,
                        "score": points,
                        "comments": comments,
                        "date": created_str,
                        "source": "Hacker News"
                    })
                
                # If we got results on the first (precise) query, don't run the fallback
                if results and idx == 0:
                    break
        except Exception as e:
            logger.warning("Hacker News search failed for %s: %s", query, e)
            
    return results


def search_reddit(repo_full_name: str) -> list[dict[str, Any]]:
    """Search Reddit for mentions or submissions of the repository URL."""
    results = []
    
    # Search for the github URL
    query = f"github.com/{repo_full_name}"
    encoded_query = urllib.parse.quote(query)
    url = f"https://www.reddit.com/search.json?q={encoded_query}&limit=5"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 (GitHub-Trending-CLI-Dev)"
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            children = data.get("data", {}).get("children", [])
            for child in children:
                post = child.get("data", {})
                title = post.get("title")
                permalink = post.get("permalink")
                subreddit = post.get("subreddit_name_prefixed")
                score = post.get("score", 0)
                comments = post.get("num_comments", 0)
                created_utc = post.get("created_utc")
                
                created_str = "Unknown date"
                if created_utc:
                    created_str = datetime.fromtimestamp(created_utc, tz=timezone.utc).strftime("%Y-%m-%d")

                reddit_url = f"https://www.reddit.com{permalink}"
                results.append({
                    "title": f"[{subreddit}] {title}",
                    "url": reddit_url,
                    "score": score,
                    "comments": comments,
                    "date": created_str,
                    "source": "Reddit"
                })
    except Exception as e:
        logger.warning("Reddit search failed for %s: %s", query, e)
        
    return results
