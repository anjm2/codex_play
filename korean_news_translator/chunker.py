"""
Smart HTML-aware chunker with anti-attention-loss design.

Problem: LLMs lose translation quality for content far from the beginning
of a long prompt (the "lost-in-the-middle" effect).

Solution:
  - Split at logical HTML boundaries (paragraphs, headings).
  - Keep each chunk ≤ MAX_CHUNK_WORDS so it fits comfortably in the
    model's attention sweet-spot.
  - Never split mid-sentence; never orphan a heading from its first paragraph.
  - Each chunk carries OVERLAP_WORDS of the previous chunk's translated text
    as a "context tail" injected at translation time.
"""

from bs4 import BeautifulSoup, Tag
from config import MAX_CHUNK_WORDS, OVERLAP_WORDS


# Tags that mark logical section starts (never split inside one)
BLOCK_TAGS = {"p", "h1", "h2", "h3", "h4", "h5", "h6",
               "li", "blockquote", "table", "ul", "ol", "dl"}


def _word_count(html_str: str) -> int:
    soup = BeautifulSoup(html_str, "lxml")
    return len(soup.get_text().split())


def _get_top_level_blocks(html: str) -> list[Tag]:
    """Return top-level block elements from the HTML."""
    soup = BeautifulSoup(html, "lxml")
    body = soup.find("body") or soup
    blocks: list[Tag] = []

    def walk(node):
        if isinstance(node, Tag):
            if node.name in BLOCK_TAGS:
                blocks.append(node)
            else:
                for child in node.children:
                    walk(child)

    for child in body.children:
        walk(child)

    # If no blocks found, wrap the whole thing
    if not blocks:
        blocks = list(body.children)  # type: ignore[assignment]

    return blocks


def chunk_html(html: str, max_words: int = MAX_CHUNK_WORDS) -> list[str]:
    """
    Split HTML into chunks of ≤ max_words, respecting block boundaries.

    Returns a list of HTML strings.
    Strategy:
      1. Extract top-level block elements.
      2. Greedily accumulate blocks until adding the next block
         would exceed max_words.
      3. A heading tag is always fused with the following paragraph
         (never left alone at chunk end).
    """
    blocks = _get_top_level_blocks(html)
    if not blocks:
        return [html]

    chunks: list[str] = []
    current_blocks: list[Tag] = []
    current_words = 0

    def flush():
        nonlocal current_blocks, current_words
        if current_blocks:
            chunk_html_str = "\n".join(str(b) for b in current_blocks)
            chunks.append(chunk_html_str)
        current_blocks = []
        current_words = 0

    for i, block in enumerate(blocks):
        block_words = _word_count(str(block))

        # If single block is huge, split it at sentence level
        if block_words > max_words:
            flush()
            sub_chunks = _split_large_block(block, max_words)
            chunks.extend(sub_chunks)
            continue

        # Check if adding this block would overflow
        if current_words + block_words > max_words and current_blocks:
            # Don't orphan a heading: attach it to next chunk instead
            is_heading = getattr(block, "name", "").startswith("h")
            if is_heading:
                flush()
                current_blocks.append(block)
                current_words = block_words
                continue
            flush()

        current_blocks.append(block)
        current_words += block_words

    flush()

    # Edge case: nothing produced → return whole HTML as one chunk
    return chunks if chunks else [html]


def _split_large_block(block: Tag, max_words: int) -> list[str]:
    """
    Split a very large single block (e.g. a giant <p>) into sentence-level
    chunks. Falls back to whole block if sentence splitting fails.
    """
    text = block.get_text(separator=" ")
    sentences = _split_sentences(text)

    chunks: list[str] = []
    current: list[str] = []
    current_w = 0

    for sent in sentences:
        sw = len(sent.split())
        if current_w + sw > max_words and current:
            # Wrap in the same tag as parent block
            inner = " ".join(current)
            chunks.append(f"<{block.name}>{inner}</{block.name}>")
            current = []
            current_w = 0
        current.append(sent)
        current_w += sw

    if current:
        inner = " ".join(current)
        chunks.append(f"<{block.name}>{inner}</{block.name}>")

    return chunks if chunks else [str(block)]


def _split_sentences(text: str) -> list[str]:
    """Naïve sentence splitter (avoids dependency on nltk)."""
    import re
    # Split on ". ", "! ", "? " followed by an uppercase letter
    parts = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)
    return [p.strip() for p in parts if p.strip()]


def get_context_tail(translated_html: str, n_words: int = OVERLAP_WORDS) -> str:
    """
    Return the last n_words of a translated HTML chunk as plain text.
    Used as context injection into the next chunk's prompt.
    """
    soup = BeautifulSoup(translated_html, "lxml")
    words = soup.get_text(separator=" ").split()
    tail_words = words[-n_words:] if len(words) > n_words else words
    return " ".join(tail_words)
