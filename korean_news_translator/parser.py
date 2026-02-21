"""
HTML parser: clean article HTML for translation.

Removes boilerplate (nav, ads, footers, scripts) while preserving the
semantic content elements that need translation.
"""

from bs4 import BeautifulSoup, Comment, NavigableString, Tag


# Tags whose entire subtree should be removed (non-content)
# Note: do NOT include html/body — lxml always wraps in these
REMOVE_TAGS = {
    "script", "style", "noscript", "iframe", "form", "button",
    "nav", "footer", "aside", "figure",
    "svg", "canvas", "video", "audio", "source", "track",
    "meta", "link", "head",
}

# CSS classes/ids that signal boilerplate (partial match)
BOILERPLATE_SIGNALS = {
    "ad", "ads", "advertisement", "advert",
    "newsletter", "subscribe", "subscription",
    "related", "recommended", "more-stories",
    "social", "share", "sharing",
    "cookie", "gdpr", "consent",
    "sidebar", "widget", "promo",
    "nav", "navigation", "menu",
    "footer", "header", "masthead",
    "comment", "comments", "disqus",
}

# Tags whose TEXT content should be translated (allow-list)
TRANSLATE_TAGS = {
    "p", "h1", "h2", "h3", "h4", "h5", "h6",
    "li", "td", "th", "caption",
    "blockquote", "figcaption", "dt", "dd",
    "span", "a", "strong", "em", "b", "i",
    "label", "title",
}


def _is_boilerplate(tag: Tag) -> bool:
    """Return True if a tag looks like boilerplate by class/id signals."""
    for attr in ("class", "id"):
        val = tag.get(attr, "")
        if isinstance(val, list):
            val = " ".join(val)
        val = val.lower()
        if any(signal in val for signal in BOILERPLATE_SIGNALS):
            return True
    return False


def clean_html(raw_html: str) -> str:
    """
    Clean article HTML:
    1. Remove non-content tags
    2. Remove boilerplate sections
    3. Remove HTML comments
    4. Return clean HTML string
    """
    soup = BeautifulSoup(raw_html, "lxml")

    # Remove comments
    for comment in soup.find_all(string=lambda t: isinstance(t, Comment)):
        comment.extract()

    # Remove non-content tags
    for tag in REMOVE_TAGS:
        for el in soup.find_all(tag):
            el.decompose()

    # Remove boilerplate divs/sections
    for el in soup.find_all(True):
        if el.name in ("div", "section", "aside", "nav") and _is_boilerplate(el):
            el.decompose()

    # Remove empty tags (no text content)
    for el in soup.find_all(True):
        if el.name not in ("img", "br", "hr"):
            if not el.get_text(strip=True):
                el.decompose()

    # Return only the body content (avoid wrapping html/head/body tags)
    body = soup.find("body")
    if body:
        return "".join(str(c) for c in body.children)
    return str(soup)


def extract_paragraphs(html: str) -> list[dict]:
    """
    Extract paragraph-level elements from cleaned HTML.

    Returns list of:
    {
        "tag": str,        # e.g. "p", "h2"
        "html": str,       # outer HTML of the element
        "text": str,       # plain text
        "word_count": int,
    }
    """
    soup = BeautifulSoup(html, "lxml")
    results = []

    for el in soup.find_all(TRANSLATE_TAGS):
        # Skip nested translatable tags (only take outermost)
        parent_translatable = el.find_parent(TRANSLATE_TAGS - {el.name})
        if parent_translatable:
            continue

        text = el.get_text(separator=" ", strip=True)
        if len(text) < 10:
            continue

        results.append({
            "tag": el.name,
            "html": str(el),
            "text": text,
            "word_count": len(text.split()),
        })

    return results


def html_to_plain(html: str) -> str:
    """Convert HTML to plain text (for word counting and previews)."""
    return BeautifulSoup(html, "lxml").get_text(separator=" ", strip=True)


def extract_title_and_first_para(html: str) -> tuple[str, str]:
    """Extract article title and first substantial paragraph for glossary extraction."""
    soup = BeautifulSoup(html, "lxml")

    # Title
    title_tag = soup.find("h1") or soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else ""

    # First paragraph with enough content
    first_para = ""
    for p in soup.find_all(["p", "div"]):
        text = p.get_text(strip=True)
        if len(text.split()) > 20:
            first_para = text[:600]
            break

    return title, first_para
