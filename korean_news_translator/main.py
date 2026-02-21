#!/usr/bin/env python3
"""
Korean News Translator — main entry point.

Usage:
  # Quick demo: translate 5 real articles from Reuters/Benzinga
  python main.py demo

  # Translate up to N articles (streaming, sequential)
  python main.py translate --count 20

  # Translate up to 500 articles via Anthropic Batch API (50% cost)
  python main.py translate --count 500 --batch

  # Translate from specific feeds
  python main.py translate --feeds reuters_business reuters_technology --count 50

  # Verify previously saved results
  python main.py verify
"""

import argparse
import json
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

OUTPUT_DIR = Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


def cmd_demo(args):
    """Quick demo: fetch 5 real articles and translate them."""
    from fetcher import fetch_news
    from batch import run_batch, _save_result
    from verifier import print_verification_report

    print("━" * 60)
    print("  Korean News Translator — DEMO (5 articles)")
    print("━" * 60)

    articles = fetch_news(
        feeds=["reuters_business", "reuters_technology"],
        per_feed_limit=5,
        max_total=5,
        enrich=True,
    )

    if not articles:
        print("No articles fetched. Check your internet connection / RSS feeds.")
        sys.exit(1)

    print(f"\nFetched {len(articles)} articles. Starting translation…")
    results = run_batch(articles, mode="sequential", run_coherence=True)

    # Save individual HTML files
    for i, r in enumerate(results):
        if "translated_html" in r:
            _save_result(r, i)

    print_verification_report(results)

    # Print a sample translation
    for r in results:
        if r.get("translated_html"):
            from parser import html_to_plain
            print("\n" + "─" * 60)
            print(f"SAMPLE TRANSLATION: {r['title']}")
            print("─" * 60)
            preview = html_to_plain(r["translated_html"])[:800]
            print(preview)
            print("…")
            break

    print(f"\nFull results saved to: {OUTPUT_DIR}/")


def cmd_translate(args):
    """Translate up to args.count articles from selected feeds."""
    from fetcher import fetch_news
    from batch import run_batch, _save_result
    from verifier import print_verification_report

    count = min(args.count, 500)
    feeds = args.feeds if args.feeds else None
    mode  = "batch_api" if args.batch else "sequential"

    print("━" * 60)
    print(f"  Korean News Translator — TRANSLATE ({count} articles, mode={mode})")
    print("━" * 60)

    articles = fetch_news(
        feeds=feeds,
        per_feed_limit=max(count // max(len(feeds) if feeds else 8, 1), 5),
        max_total=count,
        enrich=True,
    )

    if not articles:
        print("No articles fetched. Check feeds / network.")
        sys.exit(1)

    results = run_batch(articles, mode=mode, run_coherence=(not args.no_coherence))

    for i, r in enumerate(results):
        if "translated_html" in r:
            _save_result(r, i)

    print_verification_report(results)
    print(f"\nDone. Results: {OUTPUT_DIR}/results.json")


def cmd_verify(args):
    """Verify previously saved results.json."""
    from verifier import print_verification_report

    path = OUTPUT_DIR / "results.json"
    if not path.exists():
        print(f"No results.json found at {path}. Run 'translate' first.")
        sys.exit(1)

    with open(path, encoding="utf-8") as f:
        results = json.load(f)

    print_verification_report(results)


def main():
    parser = argparse.ArgumentParser(
        description="Korean News Translator — HTML English news → Korean"
    )
    sub = parser.add_subparsers(dest="command")

    # demo
    sub.add_parser("demo", help="Quick demo with 5 real articles")

    # translate
    t = sub.add_parser("translate", help="Translate N articles")
    t.add_argument("--count", type=int, default=10,
                   help="Number of articles to translate (max 500)")
    t.add_argument("--feeds", nargs="+",
                   help="Feed keys: reuters_business reuters_technology yahoo_finance …")
    t.add_argument("--batch", action="store_true",
                   help="Use Anthropic Batch API (50%% cost, slower)")
    t.add_argument("--no-coherence", action="store_true",
                   help="Skip coherence smoothing pass for multi-chunk articles")

    # verify
    sub.add_parser("verify", help="Verify results.json quality scores")

    args = parser.parse_args()

    if args.command == "demo":
        cmd_demo(args)
    elif args.command == "translate":
        cmd_translate(args)
    elif args.command == "verify":
        cmd_verify(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
