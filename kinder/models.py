"""Data models shared across pipeline stages."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class DocumentImage:
    """An image extracted from the Google Doc HTML export."""

    original_filename: str
    content: bytes
    mime_type: str
    epub_filename: str = ""


@dataclass
class Chapter:
    """A chapter detected from the heading hierarchy."""

    title: str
    html_content: str
    level: int = 1


@dataclass
class CleanedDocument:
    """The output of the HTML cleaning stage."""

    title: str
    chapters: list[Chapter] = field(default_factory=list)
    images: list[DocumentImage] = field(default_factory=list)
    language: str = "en"
    author: str = ""
    cover_image: DocumentImage | None = None
