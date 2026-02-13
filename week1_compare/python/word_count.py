#!/usr/bin/env python3
"""Week 1 comparison: simple word frequency + line filtering CLI."""

from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path

WORD_RE = re.compile(r"[A-Za-z]+")


def normalize_words(text: str) -> list[str]:
    return [w.lower() for w in WORD_RE.findall(text)]


def top_words(path: Path, top_n: int) -> list[tuple[str, int]]:
    text = path.read_text(encoding="utf-8")
    counts = Counter(normalize_words(text))
    return counts.most_common(top_n)


def filter_lines(path: Path, keyword: str) -> list[str]:
    return [
        line.rstrip("\n")
        for line in path.read_text(encoding="utf-8").splitlines()
        if keyword.lower() in line.lower()
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Python Week1 word counter")
    parser.add_argument("file", type=Path)
    parser.add_argument("--top", type=int, default=5)
    parser.add_argument("--contains", type=str, default="")
    args = parser.parse_args()

    print("[Top words]")
    for word, count in top_words(args.file, args.top):
        print(f"{word}: {count}")

    if args.contains:
        print("\n[Filtered lines]")
        for line in filter_lines(args.file, args.contains):
            print(line)


if __name__ == "__main__":
    main()
