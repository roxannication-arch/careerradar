#!/usr/bin/env python3
"""
Career Radar — AI analyzer

Reads articles where is_analyzed = 0, sends them in batches to Anthropic Claude,
asks for US job-market patterns and strategic insight, saves one insight row per
batch and marks those articles as analyzed.
"""

import os
import sqlite3
from pathlib import Path

from anthropic import Anthropic
from dotenv import load_dotenv

# Load ANTHROPIC_API_KEY from .env in this folder
load_dotenv(Path(__file__).resolve().parent / ".env")

from collector import get_connection, init_db

# Model id you specified (Anthropic API name)
MODEL = "claude-sonnet-4-20250514"
# How many articles to group per API call (tune for cost vs. context)
BATCH_SIZE = 8


def fetch_unanalyzed_batch(conn: sqlite3.Connection, limit: int) -> list[sqlite3.Row]:
    """Return up to `limit` articles that still need analysis."""
    cur = conn.execute(
        """
        SELECT id, title, url, source, published_date, summary, category
        FROM articles
        WHERE is_analyzed = 0
        ORDER BY COALESCE(published_date, '') DESC
        LIMIT ?
        """,
        (limit,),
    )
    return cur.fetchall()


def build_prompt(rows: list[sqlite3.Row]) -> str:
    """
    Build the user message: article snippets Claude should reason over.

    We keep it concise to save tokens while preserving signal.
    """
    lines = []
    for i, r in enumerate(rows, start=1):
        lines.append(
            f"--- Article {i} ---\n"
            f"Title: {r['title']}\n"
            f"Source: {r['source']} | Category: {r['category']}\n"
            f"URL: {r['url']}\n"
            f"Published: {r['published_date'] or 'unknown'}\n"
            f"Summary: {(r['summary'] or '')[:1200]}\n"
        )
    body = "\n".join(lines)
    return (
        "Ты — аналитик рынка труда США. Пишешь ТОЛЬКО на русском языке.\n\n"
        "Вот свежие новости. Проанализируй их и ответь СТРОГО в этом формате — три раздела с заголовками:\n\n"
        "## Паттерн дня\n"
        "[2-3 предложения: какой главный паттерн ты видишь в этих новостях? Найди неочевидную связь между событиями. Например: компания X увольняет → что это значит для рынка в целом?]\n\n"
        "## Стратегический вывод\n"
        "[3-4 предложения: что это означает прямо сейчас для тех кто ищет работу в США или работает в найме? Конкретно, без воды.]\n\n"
        "## Идея для контента\n"
        "[1 конкретная идея поста для соцсетей на основе этих новостей. Напиши тему и один острый заголовок.]\n\n"
        f"{body}"
    )


def run_batch(client: Anthropic, rows: list[sqlite3.Row]) -> str:
    """Call Claude once for this batch; return the assistant text."""
    user_prompt = build_prompt(rows)
    message = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        messages=[{"role": "user", "content": user_prompt}],
    )
    # Concatenate text blocks (Claude may return multiple blocks)
    parts = []
    for block in message.content:
        if hasattr(block, "text"):
            parts.append(block.text)
    return "\n".join(parts).strip()


def analyze() -> int:
    """
    Process all unanalyzed articles in batches.

    Returns the number of new insight rows inserted.
    """
    init_db()
    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        raise SystemExit(
            "Missing ANTHROPIC_API_KEY. Copy .env.example to .env and add your key."
        )

    client = Anthropic(api_key=api_key)
    conn = get_connection()
    insights_written = 0

    try:
        while True:
            batch = fetch_unanalyzed_batch(conn, BATCH_SIZE)
            if not batch:
                break

            text = run_batch(client, batch)
            ids = [r["id"] for r in batch]

            conn.execute(
                "INSERT INTO insights (content, article_count) VALUES (?, ?)",
                (text, len(batch)),
            )

            placeholders = ",".join("?" * len(ids))
            conn.execute(
                f"UPDATE articles SET is_analyzed = 1 WHERE id IN ({placeholders})",
                ids,
            )
            conn.commit()
            insights_written += 1
            print(f"Analyzed batch of {len(batch)} article(s); insight #{insights_written} saved.")

    finally:
        conn.close()

    return insights_written


if __name__ == "__main__":
    # Run after collector:  python analyzer.py
    # Requires .env with ANTHROPIC_API_KEY
    n = analyze()
    print(f"Done. Wrote {n} insight batch(es).")
