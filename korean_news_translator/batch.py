"""
Batch processor for up to 500 articles.

Two modes:
  A. Sequential streaming (default, ≤50 articles)
     Translates one article at a time. Shows streaming progress.
     Good for quick runs and debugging.

  B. Batch API (50-500 articles, --batch flag)
     Submits all single-chunk articles to the Anthropic Batch API (50% cost).
     Multi-chunk articles fall back to sequential mode since chunks must be
     translated in order (each chunk depends on the previous context).

Usage:
    from batch import run_batch
    results = run_batch(articles, mode="sequential")  # or mode="batch_api"
"""

import json
import os
import time
from pathlib import Path
from typing import Literal

import anthropic
from tqdm import tqdm

from config import MODEL
from chunker import chunk_html
from parser import clean_html
from translator import translate_article, _get_client, _SYSTEM_BLOCK
from verifier import verify_article


OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


# ─── Sequential mode ─────────────────────────────────────────────────────────

def run_sequential(articles: list[dict], run_coherence: bool = True) -> list[dict]:
    """Translate articles one by one, returning results as they complete."""
    results = []
    for i, art in enumerate(tqdm(articles, desc="Translating")):
        try:
            result = translate_article(art, run_coherence=run_coherence)
            result["verification"] = verify_article(result)
            results.append(result)
            _save_result(result, i)
        except Exception as exc:
            print(f"\n  [ERROR] article {i}: {exc}")
            art["error"] = str(exc)
            results.append(art)
    return results


# ─── Batch API mode ──────────────────────────────────────────────────────────

def _build_batch_request(article: dict, custom_id: str) -> dict:
    """Build a single Batch API request dict for a (short) article."""
    from config import CHUNK_PROMPT_TEMPLATE, GLOSSARY_PROMPT
    clean = clean_html(article.get("html", ""))
    chunks = chunk_html(clean)

    # For batch API we only handle single-chunk articles directly
    assert len(chunks) == 1, "Multi-chunk articles must use sequential mode"

    from translator import _glossary_to_str
    title = article.get("title", "")
    source = article.get("source", "")

    user_prompt = CHUNK_PROMPT_TEMPLATE.format(
        title=title,
        source=source,
        chunk_num=1,
        total_chunks=1,
        glossary="없음 (단일 섹션)",
        prev_context="(단일 섹션 기사)",
        chunk_html=chunks[0],
    )

    return {
        "custom_id": custom_id,
        "params": {
            "model": MODEL,
            "max_tokens": 8192,
            "system": _SYSTEM_BLOCK,
            "messages": [{"role": "user", "content": user_prompt}],
        },
    }


def run_batch_api(articles: list[dict]) -> list[dict]:
    """
    Use the Anthropic Batch API for articles that fit in a single chunk.
    Multi-chunk articles are translated sequentially.
    50% cost reduction on all batch requests.
    """
    from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
    from anthropic.types.messages.batch_create_params import Request

    client = _get_client()

    # Separate single-chunk vs multi-chunk articles
    single_chunk: list[tuple[int, dict]] = []
    multi_chunk:  list[tuple[int, dict]] = []

    print("\nAnalyzing article chunk counts…")
    for i, art in enumerate(articles):
        clean = clean_html(art.get("html", ""))
        n_chunks = len(chunk_html(clean))
        if n_chunks == 1:
            single_chunk.append((i, art))
        else:
            multi_chunk.append((i, art))

    print(f"  Single-chunk (batch): {len(single_chunk)}")
    print(f"  Multi-chunk  (sequential): {len(multi_chunk)}")

    results: dict[int, dict] = {}

    # ── Batch API for single-chunk articles ──────────────────────────────
    if single_chunk:
        print(f"\nSubmitting {len(single_chunk)} articles to Batch API…")
        requests_list = []
        id_map: dict[str, int] = {}

        for idx, (orig_i, art) in enumerate(single_chunk):
            cid = f"article-{orig_i:04d}"
            id_map[cid] = orig_i
            req = _build_batch_request(art, cid)
            requests_list.append(
                Request(
                    custom_id=cid,
                    params=MessageCreateParamsNonStreaming(
                        model=req["params"]["model"],
                        max_tokens=req["params"]["max_tokens"],
                        system=req["params"]["system"],
                        messages=req["params"]["messages"],
                    ),
                )
            )

        batch = client.messages.batches.create(requests=requests_list)
        print(f"  Batch ID: {batch.id} | Status: {batch.processing_status}")

        # Poll for completion
        while True:
            batch = client.messages.batches.retrieve(batch.id)
            counts = batch.request_counts
            print(
                f"  [{batch.processing_status}] "
                f"processing={counts.processing} "
                f"succeeded={counts.succeeded} "
                f"errored={counts.errored}"
            )
            if batch.processing_status == "ended":
                break
            time.sleep(30)

        # Collect results
        for result in client.messages.batches.results(batch.id):
            orig_i = id_map.get(result.custom_id, -1)
            art = articles[orig_i] if orig_i >= 0 else {}
            if result.result.type == "succeeded":
                translated_html = ""
                for block in result.result.message.content:
                    if block.type == "text":
                        translated_html += block.text
                merged = {
                    **art,
                    "translated_html": translated_html.strip(),
                    "chunks_count": 1,
                    "glossary": [],
                }
                merged["verification"] = verify_article(merged)
                results[orig_i] = merged
            else:
                print(f"  [batch error] {result.custom_id}: {result.result}")
                results[orig_i] = {**art, "error": str(result.result)}

    # ── Sequential for multi-chunk articles ──────────────────────────────
    if multi_chunk:
        print(f"\nTranslating {len(multi_chunk)} multi-chunk articles sequentially…")
        for orig_i, art in tqdm(multi_chunk):
            try:
                result = translate_article(art, run_coherence=True)
                result["verification"] = verify_article(result)
                results[orig_i] = result
                _save_result(result, orig_i)
            except Exception as exc:
                print(f"\n  [ERROR] article {orig_i}: {exc}")
                results[orig_i] = {**art, "error": str(exc)}

    # Reconstruct ordered list
    ordered = [results.get(i, articles[i]) for i in range(len(articles))]
    return ordered


# ─── Entry point ─────────────────────────────────────────────────────────────

def run_batch(
    articles: list[dict],
    mode: Literal["sequential", "batch_api"] = "sequential",
    run_coherence: bool = True,
) -> list[dict]:
    """
    Translate a list of articles.

    Args:
        articles:      List of article dicts (from fetcher.py)
        mode:          "sequential" or "batch_api"
        run_coherence: Whether to run coherence smoothing for multi-chunk articles

    Returns:
        List of article dicts with "translated_html" and "verification" keys added.
    """
    print(f"\n{'='*60}")
    print(f"Batch translation: {len(articles)} articles | mode={mode}")
    print(f"{'='*60}")

    if mode == "batch_api":
        results = run_batch_api(articles)
    else:
        results = run_sequential(articles, run_coherence=run_coherence)

    # Save full results JSON
    out_path = OUTPUT_DIR / "results.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"\nResults saved → {out_path}")

    return results


def _save_result(result: dict, index: int):
    """Save a single translated article to the output directory."""
    slug = f"{index:04d}"
    out_path = OUTPUT_DIR / f"{slug}.html"
    html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>{result.get('title', '')}</title>
  <style>
    body {{ font-family: 'Nanum Gothic', sans-serif; max-width: 800px; margin: 40px auto; line-height: 1.8; }}
    .meta {{ color: #666; font-size: 0.9em; margin-bottom: 20px; }}
    .original-title {{ font-size: 0.8em; color: #999; }}
  </style>
</head>
<body>
  <div class="meta">
    <strong>출처:</strong> {result.get('source', '')} |
    <strong>원문 URL:</strong> <a href="{result.get('url', '')}">{result.get('url', '')}</a> |
    <strong>발행일:</strong> {result.get('published', '')}
  </div>
  <h1>{result.get('title', '')}</h1>
  <div class="original-title">원문 제목: {result.get('title', '')}</div>
  <hr>
  <div class="article-body">
    {result.get('translated_html', '')}
  </div>
</body>
</html>"""
    out_path.write_text(html_content, encoding="utf-8")
