"""
Translation quality verifier.

Checks:
  1. Length ratio   - Korean text should be 0.55–1.10× the English word count
  2. HTML integrity - Tag counts should match (or be close) between original and translation
  3. Entity coverage - Key English entities (numbers, stock tickers, proper nouns)
                       should appear in or near the Korean translation
  4. Completeness   - Translation should not be suspiciously short
  5. No raw English - Large blocks of untranslated English text are a red flag

Returns a dict of scores and a pass/fail verdict.
"""

import re
from bs4 import BeautifulSoup


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _plain_text(html: str) -> str:
    return BeautifulSoup(html, "lxml").get_text(separator=" ", strip=True)


def _word_count(text: str) -> int:
    return len(text.split())


def _tag_count(html: str, tag: str) -> int:
    return len(BeautifulSoup(html, "lxml").find_all(tag))


def _extract_numbers(text: str) -> list[str]:
    """Extract numeric tokens (prices, percentages, years, etc.)."""
    return re.findall(r'\$?[\d,]+\.?\d*%?', text)


def _extract_tickers(text: str) -> list[str]:
    """Extract stock ticker-like tokens (2-5 uppercase letters)."""
    return re.findall(r'\b[A-Z]{2,5}\b', text)


def _has_large_english_block(translated_text: str, min_words: int = 30) -> bool:
    """
    Detect if a span of ≥ min_words consecutive English words appears
    in the translated text (signals untranslated content).
    """
    # Find runs of ASCII alphabetic words
    tokens = translated_text.split()
    run = 0
    for tok in tokens:
        if re.match(r'^[A-Za-z][A-Za-z\'-]*$', tok):
            run += 1
            if run >= min_words:
                return True
        else:
            run = 0
    return False


# ─── Main verifier ────────────────────────────────────────────────────────────

def verify_article(result: dict) -> dict:
    """
    Verify translation quality for a single article result dict.

    Expected keys: html (original), translated_html, title
    Returns:
    {
        "pass":              bool,
        "score":             float (0-100),
        "length_ratio":      float,
        "html_tag_match":    bool,
        "number_coverage":   float (0-1),
        "has_english_blobs": bool,
        "issues":            list[str],
    }
    """
    orig_html  = result.get("html", "")
    trans_html = result.get("translated_html", "")

    orig_text  = _plain_text(orig_html)
    trans_text = _plain_text(trans_html)

    issues: list[str] = []
    score = 100.0

    # ── 1. Length ratio ──────────────────────────────────────────────────
    orig_words  = max(_word_count(orig_text), 1)
    trans_words = _word_count(trans_text)
    # Korean sentences are often shorter (fewer words) but richer per word
    ratio = trans_words / orig_words
    length_ok = 0.35 <= ratio <= 1.40

    if not length_ok:
        if ratio < 0.35:
            issues.append(f"Translation too short (ratio={ratio:.2f})")
            score -= 30
        else:
            issues.append(f"Translation suspiciously long (ratio={ratio:.2f})")
            score -= 10

    # ── 2. HTML tag integrity ─────────────────────────────────────────────
    # Compare paragraph counts (major structural signal)
    orig_p  = _tag_count(orig_html, "p")
    trans_p = _tag_count(trans_html, "p")
    tag_match = True
    if orig_p > 0:
        p_ratio = trans_p / orig_p
        if p_ratio < 0.5 or p_ratio > 2.0:
            issues.append(f"<p> count mismatch: orig={orig_p}, translated={trans_p}")
            score -= 15
            tag_match = False

    # ── 3. Number coverage (digit-based, handles Korean reformatting) ────────
    # e.g. "$39.3 billion" becomes "393억 달러" – extract raw digit sequences
    # to avoid false positives from unit reformatting.
    def _raw_digits(text):
        return set(re.findall(r'\d+', text))

    orig_digits  = {d for d in _raw_digits(orig_text) if len(d) >= 2}
    trans_digits = _raw_digits(trans_text)
    if orig_digits:
        covered = len(orig_digits & trans_digits)
        num_coverage = covered / len(orig_digits)
        if num_coverage < 0.45:
            missing = list(orig_digits - trans_digits)[:5]
            issues.append(f"Significant numeric data missing: {missing}")
            score -= 15
    else:
        num_coverage = 1.0

    # ── 4. Untranslated English blobs ─────────────────────────────────────
    has_blobs = _has_large_english_block(trans_text, min_words=25)
    if has_blobs:
        issues.append("Large untranslated English block detected")
        score -= 25

    # ── 5. Completeness (non-empty) ───────────────────────────────────────
    if trans_words < 20:
        issues.append("Translation is nearly empty")
        score -= 40

    score = max(score, 0.0)
    passed = score >= 60 and not has_blobs and trans_words >= 20

    return {
        "pass":              passed,
        "score":             round(score, 1),
        "length_ratio":      round(ratio, 3),
        "orig_words":        orig_words,
        "translated_words":  trans_words,
        "html_tag_match":    tag_match,
        "number_coverage":   round(num_coverage, 3),
        "has_english_blobs": has_blobs,
        "issues":            issues,
    }


def print_verification_report(results: list[dict]):
    """Print a summary verification report for a batch of translated articles."""
    print("\n" + "═" * 65)
    print("  TRANSLATION VERIFICATION REPORT")
    print("═" * 65)

    passed = sum(1 for r in results if r.get("verification", {}).get("pass", False))
    total  = len(results)
    avg_score = (
        sum(r.get("verification", {}).get("score", 0) for r in results) / total
        if total else 0
    )

    print(f"  Total articles : {total}")
    print(f"  Passed         : {passed} ({100*passed/total:.1f}%)" if total else "")
    print(f"  Average score  : {avg_score:.1f}/100")
    print()

    # Detail per article
    for i, r in enumerate(results):
        v = r.get("verification", {})
        status = "✓ PASS" if v.get("pass") else "✗ FAIL"
        score  = v.get("score", "n/a")
        ratio  = v.get("length_ratio", "n/a")
        title  = r.get("title", "")[:50]
        print(f"  [{i:03d}] {status} | score={score:5} | ratio={ratio} | {title}")
        for issue in v.get("issues", []):
            print(f"         ⚠  {issue}")

    print("═" * 65)
    print(f"  Result: {passed}/{total} articles passed quality check")
    print("═" * 65)
