"""Stage 3 — HTML cleaning pipeline."""

from __future__ import annotations

import zipfile
from pathlib import Path

from bs4 import BeautifulSoup

from kinder.models import Chapter, CleanedDocument, DocumentImage

MIME_MAP = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".svg": "image/svg+xml",
}


def extract_html_zip(zip_path: str) -> tuple[str, dict[str, bytes]]:
    """Extract HTML content and images from a Google Docs HTML export ZIP."""
    images: dict[str, bytes] = {}
    html_content = ""

    with zipfile.ZipFile(zip_path, "r") as zf:
        for name in zf.namelist():
            if name.endswith(".html"):
                html_content = zf.read(name).decode("utf-8")
            elif name.startswith("images/"):
                image_name = Path(name).name
                if image_name:
                    images[image_name] = zf.read(name)

    if not html_content:
        raise ValueError("No HTML file found in the exported ZIP")
    return html_content, images


def strip_google_styles(soup: BeautifulSoup) -> BeautifulSoup:
    """Remove all inline styles, Google class attributes, and empty spans."""
    for style_tag in soup.find_all("style"):
        style_tag.decompose()

    for tag in soup.find_all(True):
        if tag.has_attr("style"):
            del tag["style"]
        if tag.has_attr("class"):
            del tag["class"]

    for span in soup.find_all("span"):
        if not span.attrs:
            span.unwrap()

    return soup


def normalize_headings(soup: BeautifulSoup) -> BeautifulSoup:
    """Ensure heading levels are sequential (no skips)."""
    headings = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
    if not headings:
        return soup

    used_levels = sorted({int(h.name[1]) for h in headings})
    level_map = {level: idx + 1 for idx, level in enumerate(used_levels)}

    for heading in headings:
        old_level = int(heading.name[1])
        new_level = level_map[old_level]
        if new_level != old_level:
            heading.name = f"h{new_level}"

    return soup


def clean_whitespace(soup: BeautifulSoup) -> BeautifulSoup:
    """Remove &nbsp; artifacts and collapse excessive whitespace."""
    for text_node in soup.find_all(string=True):
        cleaned = text_node.replace("\xa0", " ")
        if cleaned != text_node:
            text_node.replace_with(cleaned)

    for p in soup.find_all("p"):
        if not p.get_text(strip=True):
            p.decompose()

    return soup


def detect_chapters(soup: BeautifulSoup, split_level: int = 1) -> list[Chapter]:
    """Split the document into chapters at the specified heading level."""
    split_tag = f"h{split_level}"
    headings = soup.find_all(split_tag)

    if not headings and split_level < 4:
        return detect_chapters(soup, split_level + 1)

    if not headings:
        body = soup.find("body") or soup
        return [Chapter(title="Content", html_content=str(body), level=1)]

    chapters: list[Chapter] = []

    pre_content = []
    for sibling in headings[0].previous_siblings:
        pre_content.append(str(sibling))
    if any(
        BeautifulSoup(c, "html.parser").get_text(strip=True) for c in pre_content
    ):
        chapters.append(
            Chapter(
                title="Frontmatter",
                html_content="".join(reversed(pre_content)),
                level=split_level,
            )
        )

    for heading in headings:
        title = heading.get_text(strip=True)
        content_parts = [str(heading)]
        for sibling in heading.next_siblings:
            if sibling.name and sibling.name in [
                f"h{lvl}" for lvl in range(1, split_level + 1)
            ]:
                break
            content_parts.append(str(sibling))
        chapters.append(
            Chapter(
                title=title,
                html_content="".join(content_parts),
                level=split_level,
            )
        )

    return chapters


def clean_html_export(
    zip_path: str,
    language: str = "en",
    author: str = "",
    chapter_split_level: int = 1,
) -> CleanedDocument:
    """Full HTML cleaning pipeline. Takes an exported ZIP, returns a CleanedDocument."""
    html_content, raw_images = extract_html_zip(zip_path)

    soup = BeautifulSoup(html_content, "html.parser")
    soup = strip_google_styles(soup)
    soup = normalize_headings(soup)
    soup = clean_whitespace(soup)

    first_h1 = soup.find("h1")
    title = first_h1.get_text(strip=True) if first_h1 else Path(zip_path).stem

    chapters = detect_chapters(soup, split_level=chapter_split_level)

    images = []
    for filename, content in raw_images.items():
        suffix = Path(filename).suffix.lower()
        images.append(
            DocumentImage(
                original_filename=filename,
                content=content,
                mime_type=MIME_MAP.get(suffix, "image/png"),
            )
        )

    return CleanedDocument(
        title=title,
        chapters=chapters,
        images=images,
        language=language,
        author=author,
    )
