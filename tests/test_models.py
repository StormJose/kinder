"""Tests for data models."""

from kinder.models import Chapter, CleanedDocument, DocumentImage


def test_cleaned_document_defaults():
    doc = CleanedDocument(title="Test")
    assert doc.title == "Test"
    assert doc.chapters == []
    assert doc.images == []
    assert doc.language == "en"
    assert doc.author == ""
    assert doc.cover_image is None


def test_chapter_defaults():
    ch = Chapter(title="Intro", html_content="<p>Hello</p>")
    assert ch.level == 1


def test_document_image_defaults():
    img = DocumentImage(
        original_filename="img.png", content=b"data", mime_type="image/png"
    )
    assert img.epub_filename == ""
