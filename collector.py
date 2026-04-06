#!/usr/bin/env python3
"""
Career Radar — News collector

Fetches RSS feeds from multiple sources about US job market:
layoffs, hiring, startups, visas, future of work.
Stores each item in SQLite (radar.db) with deduplication by URL.
"""

from __future__ import annotations

import sqlite3
import re
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Статьи старше этого количества дней не сохраняем
MAX_AGE_DAYS = 30

# Ключевые слова мусорных статей — пропускаем
SKIP_KEYWORDS = [
    "promo code", "best deals", "discount", "coupon", "best laptop",
    "best phone", "best ipad", "best samsung", "best iphone", "gift guide",
    "best garmin", "jump starter", "frame pro", "galaxy s2", "cases for",
    "accessories", "the best ", "to buy", "vs ", "$300", "$200", "$100"
]

import feedparser

DB_PATH = Path(__file__).resolve().parent / "radar.db"

# Browser-like headers so sites don't block us
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/rss+xml, application/xml, text/xml, */*",
}

# (feed_url, category, source_name)
FEEDS: list[tuple[str, str, str]] = [
    # Tech news
    ("https://feeds.feedburner.com/TechCrunch", "tech", "TechCrunch"),
    ("https://www.wired.com/feed/rss", "tech", "Wired"),
    ("https://feeds.arstechnica.com/arstechnica/index", "tech", "Ars Technica"),

    # Layoffs & hiring - Google News RSS (most reliable source)
    ("https://news.google.com/rss/search?q=layoffs+USA+2026&hl=en-US&gl=US&ceid=US:en", "layoffs", "Google News"),
    ("https://news.google.com/rss/search?q=tech+layoffs+2026&hl=en-US&gl=US&ceid=US:en", "layoffs", "Google News"),
    ("https://news.google.com/rss/search?q=hiring+freeze+USA&hl=en-US&gl=US&ceid=US:en", "hiring_freeze", "Google News"),
    ("https://news.google.com/rss/search?q=mass+layoffs+United+States&hl=en-US&gl=US&ceid=US:en", "layoffs", "Google News"),

    # Startups & funding
    ("https://news.google.com/rss/search?q=startup+funding+USA+2026&hl=en-US&gl=US&ceid=US:en", "startup", "Google News"),
    ("https://news.google.com/rss/search?q=new+startup+hiring+USA&hl=en-US&gl=US&ceid=US:en", "startup", "Google News"),

    # Visas & immigration
    ("https://news.google.com/rss/search?q=H1B+visa+2026&hl=en-US&gl=US&ceid=US:en", "visa", "Google News"),
    ("https://news.google.com/rss/search?q=work+visa+USA&hl=en-US&gl=US&ceid=US:en", "visa", "Google News"),
    ("https://news.google.com/rss/search?q=OPT+STEM+visa&hl=en-US&gl=US&ceid=US:en", "visa", "Google News"),

    # Future of work
    ("https://news.google.com/rss/search?q=remote+work+USA+2026&hl=en-US&gl=US&ceid=US:en", "remote_work", "Google News"),
    ("https://news.google.com/rss/search?q=return+to+office+mandate&hl=en-US&gl=US&ceid=US:en", "remote_work", "Google News"),
    ("https://news.google.com/rss/search?q=AI+jobs+future+work&hl=en-US&gl=US&ceid=US:en", "ai_jobs", "Google News"),
]


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_connection()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                source TEXT,
                published_date TEXT,
                summary TEXT,
                category TEXT,
                is_analyzed INTEGER NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL DEFAULT (datetime('now')),
                content TEXT NOT NULL,
                article_count INTEGER NOT NULL DEFAULT 0
            );

            CREATE INDEX IF NOT EXISTS idx_articles_analyzed ON articles(is_analyzed);
            CREATE INDEX IF NOT EXISTS idx_articles_category ON articles(category);
        """)
        conn.commit()
    finally:
        conn.close()


def fetch_feed(url: str) -> feedparser.FeedParserDict:
    """Fetch RSS feed with browser-like headers to avoid blocks."""
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=15) as response:
            data = response.read()
        return feedparser.parse(data)
    except Exception as e:
        print(f"  Error fetching {url}: {e}")
        return feedparser.parse("")


def _parse_published(entry) -> str | None:
    t = getattr(entry, "published_parsed", None) or getattr(entry, "updated_parsed", None)
    if not t:
        return None
    try:
        dt = datetime(*t[:6], tzinfo=timezone.utc)
        return dt.isoformat()
    except (TypeError, ValueError):
        return None


def _summary_from_entry(entry) -> str:
    for attr in ("summary", "description", "content"):
        val = getattr(entry, attr, None)
        if val:
            if isinstance(val, list) and val:
                val = val[0].get("value", "")
            text = str(val).strip()
            if "<" in text:
                text = re.sub(r"<[^>]+>", " ", text)
            return text[:2000]
    return ""


def collect() -> int:
    init_db()
    inserted = 0
    conn = get_connection()

    try:
        for feed_url, category, source_name in FEEDS:
            print(f"Fetching: {source_name} / {category}...")
            parsed = fetch_feed(feed_url)

            if not parsed.entries:
                print(f"  No entries found")
                continue

            print(f"  Found {len(parsed.entries)} entries")

            for entry in parsed.entries:
                link = getattr(entry, "link", None) or ""
                title = (getattr(entry, "title", None) or "Untitled").strip()
                if not link:
                    continue

                # Пропускаем мусорные статьи
                title_lower = title.lower()
                if any(kw in title_lower for kw in SKIP_KEYWORDS):
                    continue

                summary = _summary_from_entry(entry)
                published = _parse_published(entry)

                # Пропускаем статьи старше MAX_AGE_DAYS
                if published:
                    try:
                        pub_dt = datetime.fromisoformat(published)
                        if (datetime.now(timezone.utc) - pub_dt).days > MAX_AGE_DAYS:
                            continue
                    except (ValueError, TypeError):
                        pass

                try:
                    conn.execute("""
                        INSERT INTO articles
                            (title, url, source, published_date, summary, category, is_analyzed)
                        VALUES (?, ?, ?, ?, ?, ?, 0)
                    """, (title, link, source_name, published, summary, category))
                    inserted += 1
                except sqlite3.IntegrityError:
                    pass  # duplicate URL, skip

        conn.commit()
    finally:
        conn.close()

    return inserted


if __name__ == "__main__":
    n = collect()
    print(f"\nDone. Inserted {n} new article(s) into {DB_PATH}.")
