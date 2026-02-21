"""
News fetcher: RSS feeds → list of article dicts.

Each article dict:
{
    "title": str,
    "url":   str,
    "source": str,
    "published": str,
    "html":  str,   # raw HTML of the article body
    "text":  str,   # plain text (fallback)
}
"""

import time
import feedparser
import requests
from bs4 import BeautifulSoup
from typing import Optional

from config import RSS_FEEDS, REQUEST_HEADERS, REQUEST_TIMEOUT


# ─── HTML selectors per domain ───────────────────────────────────────────────
# Maps hostname fragment → CSS selector for the article body element
ARTICLE_SELECTORS = {
    "reuters.com":     ["article.article-body", "div.article-body", "div[data-testid='ArticleBody']"],
    "marketwatch.com": ["div.article__body", "div.story__body"],
    "yahoo.com":       ["div.caas-body", "article"],
    "investing.com":   ["div.articlePage", "section.article_WYSIWYG"],
    "benzinga.com":    ["div.article-content-body", "div.article__body"],
    "seekingalpha.com":["div[data-test-id='article-content']", "div.article-content"],
}

FALLBACK_SELECTOR = "article"


def _get_selector(url: str) -> list[str]:
    for domain, selectors in ARTICLE_SELECTORS.items():
        if domain in url:
            return selectors
    return [FALLBACK_SELECTOR]


def fetch_article_html(url: str, retries: int = 3) -> Optional[str]:
    """Fetch and return the article body HTML for a given URL."""
    for attempt in range(retries):
        try:
            resp = requests.get(
                url,
                headers=REQUEST_HEADERS,
                timeout=REQUEST_TIMEOUT,
                allow_redirects=True,
            )
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "lxml")

            # Try domain-specific selectors first
            for selector in _get_selector(url):
                body = soup.select_one(selector)
                if body:
                    return str(body)

            # Generic fallback: largest <div> or <article>
            for tag in ("article", "main", "div"):
                candidates = soup.find_all(tag)
                if candidates:
                    biggest = max(candidates, key=lambda t: len(t.get_text()))
                    if len(biggest.get_text()) > 200:
                        return str(biggest)

            # Last resort: full body
            body_tag = soup.find("body")
            return str(body_tag) if body_tag else resp.text

        except requests.RequestException as exc:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
            else:
                print(f"  [fetch error] {url}: {exc}")
    return None


def fetch_from_feed(feed_name: str, feed_url: str, limit: int = 50) -> list[dict]:
    """Parse an RSS/Atom feed and return article dicts."""
    articles = []
    try:
        parsed = feedparser.parse(feed_url)
        entries = parsed.entries[:limit]
        print(f"  [{feed_name}] {len(entries)} entries found in feed")
        for entry in entries:
            url = entry.get("link", "")
            title = entry.get("title", "Untitled")
            published = entry.get("published", entry.get("updated", ""))

            # Some feeds include full HTML in summary/content
            html_from_feed = ""
            if hasattr(entry, "content") and entry.content:
                html_from_feed = entry.content[0].get("value", "")
            elif hasattr(entry, "summary"):
                html_from_feed = entry.summary

            articles.append({
                "title": title,
                "url": url,
                "source": feed_name,
                "published": published,
                "html": html_from_feed,
                "text": BeautifulSoup(html_from_feed, "lxml").get_text() if html_from_feed else "",
            })
    except Exception as exc:
        print(f"  [feed error] {feed_name}: {exc}")
    return articles


def enrich_with_full_html(articles: list[dict], max_fetch: int = 500) -> list[dict]:
    """
    For each article, try to fetch the full article HTML if the feed only
    provided a snippet. Respects max_fetch limit.
    """
    enriched = []
    fetched = 0
    for art in articles[:max_fetch]:
        # If feed body is too short, fetch the full page
        if len(art.get("html", "")) < 500 and art.get("url"):
            print(f"  [fetch] {art['title'][:60]}...")
            html = fetch_article_html(art["url"])
            if html:
                art["html"] = html
                art["text"] = BeautifulSoup(html, "lxml").get_text(separator=" ")
            fetched += 1
            time.sleep(0.5)  # polite crawling
        enriched.append(art)
    print(f"  Full-page fetches: {fetched}")
    return enriched


def fetch_news(
    feeds: Optional[list[str]] = None,
    per_feed_limit: int = 30,
    max_total: int = 500,
    enrich: bool = True,
    use_samples_on_failure: bool = True,
) -> list[dict]:
    """
    Fetch news articles from configured RSS feeds.

    Args:
        feeds: List of feed keys from config.RSS_FEEDS (None = all feeds)
        per_feed_limit: Max articles per feed
        max_total: Hard cap on total articles returned
        enrich: Whether to fetch full HTML for short articles
    """
    selected = {k: v for k, v in RSS_FEEDS.items() if feeds is None or k in feeds}
    all_articles: list[dict] = []

    for name, url in selected.items():
        print(f"\n[{name}] Fetching RSS…")
        batch = fetch_from_feed(name, url, limit=per_feed_limit)
        all_articles.extend(batch)
        if len(all_articles) >= max_total:
            break

    # Deduplicate by URL
    seen_urls: set[str] = set()
    unique: list[dict] = []
    for art in all_articles:
        if art["url"] not in seen_urls:
            seen_urls.add(art["url"])
            unique.append(art)

    unique = unique[:max_total]
    print(f"\nTotal unique articles: {len(unique)}")

    if enrich:
        print("\nEnriching with full article HTML…")
        unique = enrich_with_full_html(unique, max_fetch=max_total)

    # Filter out articles with no usable content
    valid = [a for a in unique if len(a.get("html", "") + a.get("text", "")) > 100]
    print(f"Articles with content: {len(valid)}")

    if not valid and use_samples_on_failure:
        print("\nNo articles fetched from RSS (network may be restricted).")
        print("Falling back to built-in sample articles for demonstration.")
        from sample_news import SAMPLE_ARTICLES
        return SAMPLE_ARTICLES[:max_total]

    return valid
