"""Tests for ePub assembly."""

import tempfile
import zipfile
from pathlib import Path

from kinder.epub import assemble_epub
from kinder.models import Chapter, CleanedDocument


def test_assemble_epub_creates_valid_file():
    doc = CleanedDocument(
        title="Test Book",
        chapters=[
            Chapter(title="Chapter 1", html_content="<h1>Chapter 1</h1><p>Hello</p>"),
            Chapter(title="Chapter 2", html_content="<h1>Chapter 2</h1><p>World</p>"),
        ],
        language="en",
        author="Test Author",
    )

    with tempfile.TemporaryDirectory() as tmp:
        out = str(Path(tmp) / "test.epub")
        result = assemble_epub(doc, out)
        assert Path(result).exists()

        with zipfile.ZipFile(result) as zf:
            names = zf.namelist()
            assert "mimetype" in names
            assert any("chapter_00" in n for n in names)
            assert any("chapter_01" in n for n in names)
