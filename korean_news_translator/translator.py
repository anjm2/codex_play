"""
Core translation engine using Claude Opus 4.6.

Anti-attention-loss pipeline:
  1. Extract a glossary from the article title + first paragraph
     (one fast API call, ensures consistent proper-noun translation).
  2. Translate each HTML chunk sequentially:
     - Inject: title, source, chunk index, glossary, prev-chunk tail (overlap).
     - Use streaming + get_final_message() to avoid HTTP timeouts.
     - Prompt caching on the large system prompt saves ~80% input cost.
  3. For articles >1 chunk, run a lightweight coherence pass to smooth
     the chunk seams.
"""

import json
import os
import anthropic
from dotenv import load_dotenv

from config import (
    MODEL, SYSTEM_PROMPT,
    CHUNK_PROMPT_TEMPLATE, COHERENCE_PROMPT, GLOSSARY_PROMPT,
)
from chunker import chunk_html, get_context_tail
from parser import clean_html, extract_title_and_first_para

load_dotenv()

_client: anthropic.Anthropic | None = None


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    return _client


# ─── System prompt block (with cache_control) ───────────────────────────────
_SYSTEM_BLOCK = [
    {
        "type": "text",
        "text": SYSTEM_PROMPT,
        "cache_control": {"type": "ephemeral"},
    }
]


def extract_glossary(title: str, first_para: str) -> list[dict]:
    """
    Ask Claude to extract key proper nouns / terms and their Korean translations
    from the article title and first paragraph.

    Returns a list of {"en": ..., "ko": ...} dicts.
    """
    client = _get_client()
    prompt = GLOSSARY_PROMPT.format(title=title, first_para=first_para[:500])

    try:
        resp = client.messages.create(
            model=MODEL,
            max_tokens=512,
            system=_SYSTEM_BLOCK,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = resp.content[0].text.strip()
        # Find the JSON array in the response
        start = raw.find("[")
        end = raw.rfind("]") + 1
        if start >= 0 and end > start:
            return json.loads(raw[start:end])
    except Exception as exc:
        print(f"  [glossary] extraction failed: {exc}")
    return []


def _glossary_to_str(glossary: list[dict]) -> str:
    if not glossary:
        return "없음"
    return "\n".join(f"• {g['en']} → {g['ko']}" for g in glossary)


def translate_chunk(
    chunk_html: str,
    chunk_num: int,
    total_chunks: int,
    title: str,
    source: str,
    glossary: list[dict],
    prev_context: str,
) -> str:
    """
    Translate a single HTML chunk to Korean using Claude Opus 4.6.

    Uses:
    - Adaptive thinking for nuanced translation decisions
    - Streaming + get_final_message() to avoid timeouts on long chunks
    - Prompt caching on system prompt
    """
    client = _get_client()

    user_prompt = CHUNK_PROMPT_TEMPLATE.format(
        title=title,
        source=source,
        chunk_num=chunk_num,
        total_chunks=total_chunks,
        glossary=_glossary_to_str(glossary),
        prev_context=prev_context if prev_context else "(첫 번째 섹션)",
        chunk_html=chunk_html,
    )

    try:
        with client.messages.stream(
            model=MODEL,
            max_tokens=8192,
            thinking={"type": "adaptive"},
            system=_SYSTEM_BLOCK,
            messages=[{"role": "user", "content": user_prompt}],
        ) as stream:
            final = stream.get_final_message()

        # Extract only text blocks (skip thinking blocks)
        translation = ""
        for block in final.content:
            if block.type == "text":
                translation += block.text

        return translation.strip()

    except anthropic.APIError as exc:
        print(f"  [translate_chunk] API error on chunk {chunk_num}: {exc}")
        return chunk_html  # Return original HTML on failure


def coherence_pass(assembled_html: str) -> str:
    """
    Light coherence pass to smooth seams between translated chunks.
    Only called for multi-chunk articles.
    """
    client = _get_client()

    # Skip if the assembled HTML is very short
    if len(assembled_html.split()) < 200:
        return assembled_html

    prompt = COHERENCE_PROMPT.format(assembled_html=assembled_html)

    try:
        with client.messages.stream(
            model=MODEL,
            max_tokens=16384,
            thinking={"type": "adaptive"},
            system=_SYSTEM_BLOCK,
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            final = stream.get_final_message()

        result = ""
        for block in final.content:
            if block.type == "text":
                result += block.text
        return result.strip() if result.strip() else assembled_html

    except anthropic.APIError as exc:
        print(f"  [coherence_pass] API error: {exc}")
        return assembled_html


def translate_article(article: dict, run_coherence: bool = True) -> dict:
    """
    Full pipeline: clean → chunk → glossary → translate → (coherence) → assemble.

    Args:
        article: dict with keys: title, html, source, url, published
        run_coherence: whether to run a coherence smoothing pass

    Returns:
        article dict with added keys:
          - "translated_html": final Korean HTML
          - "chunks_count": number of chunks processed
          - "glossary": extracted glossary
    """
    raw_html = article.get("html", "")
    title = article.get("title", "")
    source = article.get("source", "")

    print(f"\n  [translate] '{title[:60]}'")

    # 1. Clean HTML
    clean = clean_html(raw_html)

    # 2. Extract title and first para for glossary
    art_title, first_para = extract_title_and_first_para(clean)
    if not art_title:
        art_title = title

    # 3. Extract glossary
    glossary = extract_glossary(art_title, first_para)
    print(f"  [glossary] {len(glossary)} terms: {[g['en'] for g in glossary[:5]]}")

    # 4. Chunk the HTML
    chunks = chunk_html(clean)
    n = len(chunks)
    print(f"  [chunks]   {n} chunk(s)")

    # 5. Translate chunk by chunk, carrying context forward
    translated_chunks: list[str] = []
    prev_context = ""

    for i, chunk in enumerate(chunks, start=1):
        print(f"    chunk {i}/{n}…", end=" ", flush=True)
        translated = translate_chunk(
            chunk_html=chunk,
            chunk_num=i,
            total_chunks=n,
            title=art_title,
            source=source,
            glossary=glossary,
            prev_context=prev_context,
        )
        translated_chunks.append(translated)
        # Carry last OVERLAP_WORDS as context into next chunk
        prev_context = get_context_tail(translated)
        print("done")

    # 6. Assemble
    assembled = "\n".join(translated_chunks)

    # 7. Coherence pass (only for multi-chunk articles)
    if run_coherence and n > 1:
        print("  [coherence] smoothing seams…")
        assembled = coherence_pass(assembled)

    return {
        **article,
        "translated_html": assembled,
        "chunks_count": n,
        "glossary": glossary,
    }
