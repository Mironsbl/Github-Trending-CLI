"""Twitter/X search module using public Nitter RSS instances with fallback."""

from __future__ import annotations

import logging
import urllib.parse
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger("github_trending_twitter")

# A list of active public Nitter instances for redundancy
NITTER_INSTANCES = [
    "nitter.poast.org",
    "nitter.privacydev.net",
    "nitter.no-logs.com",
    "nitter.perennialte.ch",
]


def search_twitter_mentions(query: str) -> list[dict[str, str]]:
    """Search Twitter/X for mentions of a repository/topic.

    Uses public Nitter RSS feeds. If all instances fail, returns generated mock posts
    and a flag indicating fallback mode.
    """
    encoded_query = urllib.parse.quote(query)
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36"
    }

    for instance in NITTER_INSTANCES:
        url = f"https://{instance}/search/rss?q={encoded_query}"
        try:
            logger.info("Attempting Twitter search via Nitter instance: %s", instance)
            resp = requests.get(url, headers=headers, timeout=5)
            if resp.status_code == 200:
                tweets = _parse_nitter_rss(resp.text, instance, query)
                if tweets:
                    logger.info("Successfully fetched %d tweets from %s", len(tweets), instance)
                    return tweets
        except Exception as e:
            logger.warning("Nitter instance %s failed: %s", instance, e)

    # Fallback: if all instances fail, return generated mockup tweets
    logger.warning("All Nitter instances failed. Using fallback mock tweets.")
    return _generate_mock_tweets(query)


def _parse_nitter_rss(xml_content: str, instance: str, query: str) -> list[dict[str, str]]:
    """Parse Nitter RSS XML and return list of tweet dicts."""
    soup = BeautifulSoup(xml_content, "xml")
    items = soup.find_all("item")
    tweets = []

    for item in items[:5]:  # Limit to top 5 tweets
        title = item.find("title")
        link = item.find("link")
        description = item.find("description")
        creator = item.find("dc:creator") or item.find("creator")
        pub_date = item.find("pubDate")

        author = creator.text.strip() if creator else "unknown"
        # Extract name from title or link if creator not found
        if author == "unknown" and link:
            # e.g., https://nitter.net/username/status/123...
            parts = link.text.split("/")
            if len(parts) > 3:
                author = f"@{parts[3]}"
        
        if not author.startswith("@"):
            author = f"@{author}"

        text = description.text.strip() if description else (title.text.strip() if title else "")
        # Clean HTML tags from description if bs4 parsed it raw
        if "<" in text:
            text = BeautifulSoup(text, "html.parser").get_text()

        # Clean title prefix if present in text
        if text.startswith(f"{author}:"):
            text = text[len(author)+1:].strip()

        date_str = pub_date.text.strip() if pub_date else "Just now"

        tweets.append({
            "author": author,
            "text": text,
            "date": date_str,
            "url": link.text.strip() if link else f"https://x.com/search?q={urllib.parse.quote(query)}",
            "is_mock": "false"
        })

    return tweets


def _generate_mock_tweets(query: str) -> list[dict[str, str]]:
    """Generate professional/interesting mock tweets about the query repository."""
    return [
        {
            "author": "@dev_guru",
            "text": f"Just discovered {query} on GitHub. The codebase looks super clean and the performance is amazing! Check it out.",
            "date": "2 hours ago",
            "url": f"https://x.com/search?q={urllib.parse.quote(query)}",
            "is_mock": "true"
        },
        {
            "author": "@oss_insider",
            "text": f"🔥 {query} is trending today! Seems like a game-changer for this domain. Anyone using it in production yet?",
            "date": "5 hours ago",
            "url": f"https://x.com/search?q={urllib.parse.quote(query)}",
            "is_mock": "true"
        },
        {
            "author": "@tech_cruncher",
            "text": f"If you are looking for a modern solution, {query} is absolutely worth looking at. Already has thousands of stars!",
            "date": "1 day ago",
            "url": f"https://x.com/search?q={urllib.parse.quote(query)}",
            "is_mock": "true"
        }
    ]
