"""Tests for the HTML cleaning pipeline."""

from bs4 import BeautifulSoup

from kinder.cleaning import (
    clean_whitespace,
    detect_chapters,
    normalize_headings,
    strip_google_styles,
)


class TestStripGoogleStyles:
    def test_removes_inline_styles(self):
        html = '<p style="font-size:11pt;">Hello</p>'
        soup = BeautifulSoup(html, "html.parser")
        result = strip_google_styles(soup)
        assert not result.find("p").has_attr("style")

    def test_removes_class_attributes(self):
        html = '<p class="c4"><span class="c1">Text</span></p>'
        soup = BeautifulSoup(html, "html.parser")
        result = strip_google_styles(soup)
        assert not result.find("p").has_attr("class")

    def test_unwraps_empty_spans(self):
        html = "<p><span>Text</span></p>"
        soup = BeautifulSoup(html, "html.parser")
        result = strip_google_styles(soup)
        assert result.find("span") is None
        assert result.get_text() == "Text"

    def test_removes_style_block(self):
        html = "<style>.c1 { font-size: 11pt; }</style><p>Hello</p>"
        soup = BeautifulSoup(html, "html.parser")
        result = strip_google_styles(soup)
        assert result.find("style") is None


class TestNormalizeHeadings:
    def test_fills_gaps(self):
        html = "<h1>Title</h1><h3>Subtitle</h3><h5>Sub-sub</h5>"
        soup = BeautifulSoup(html, "html.parser")
        result = normalize_headings(soup)
        tags = [h.name for h in result.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])]
        assert tags == ["h1", "h2", "h3"]

    def test_no_headings_is_noop(self):
        html = "<p>Just a paragraph</p>"
        soup = BeautifulSoup(html, "html.parser")
        result = normalize_headings(soup)
        assert str(result) == html

    def test_contiguous_headings_unchanged(self):
        html = "<h1>One</h1><h2>Two</h2>"
        soup = BeautifulSoup(html, "html.parser")
        result = normalize_headings(soup)
        tags = [h.name for h in result.find_all(["h1", "h2"])]
        assert tags == ["h1", "h2"]


class TestCleanWhitespace:
    def test_replaces_nbsp(self):
        html = "<p>Hello\xa0World</p>"
        soup = BeautifulSoup(html, "html.parser")
        result = clean_whitespace(soup)
        assert result.get_text() == "Hello World"

    def test_removes_empty_paragraphs(self):
        html = "<p>Content</p><p>   </p><p>More</p>"
        soup = BeautifulSoup(html, "html.parser")
        result = clean_whitespace(soup)
        paragraphs = result.find_all("p")
        assert len(paragraphs) == 2


class TestDetectChapters:
    def test_splits_at_h1(self):
        html = "<h1>Ch 1</h1><p>Text 1</p><h1>Ch 2</h1><p>Text 2</p>"
        soup = BeautifulSoup(html, "html.parser")
        chapters = detect_chapters(soup, split_level=1)
        assert len(chapters) == 2
        assert chapters[0].title == "Ch 1"
        assert chapters[1].title == "Ch 2"

    def test_falls_back_to_h2_when_no_h1(self):
        html = "<h2>Section A</h2><p>Content A</p><h2>Section B</h2><p>Content B</p>"
        soup = BeautifulSoup(html, "html.parser")
        chapters = detect_chapters(soup, split_level=1)
        assert len(chapters) == 2

    def test_no_headings_returns_single_chapter(self):
        html = "<p>Just text</p>"
        soup = BeautifulSoup(html, "html.parser")
        chapters = detect_chapters(soup, split_level=1)
        assert len(chapters) == 1
        assert chapters[0].title == "Content"

    def test_frontmatter_before_first_heading(self):
        html = "<p>Preface text</p><h1>Chapter 1</h1><p>Body</p>"
        soup = BeautifulSoup(html, "html.parser")
        chapters = detect_chapters(soup, split_level=1)
        assert chapters[0].title == "Frontmatter"
        assert len(chapters) == 2
