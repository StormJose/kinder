"""Stage 4 — ePub assembly with ebooklib."""

from __future__ import annotations

from ebooklib import epub

from kinder.models import CleanedDocument

DEFAULT_CSS = """
body {
    font-family: serif;
    line-height: 1.6;
    margin: 0;
    padding: 0;
}

h1 { font-size: 1.8em; margin: 1.5em 0 0.5em; text-align: center; }
h2 { font-size: 1.4em; margin: 1.2em 0 0.4em; }
h3 { font-size: 1.2em; margin: 1em 0 0.3em; }
h4, h5, h6 { font-size: 1.1em; margin: 0.8em 0 0.2em; }

p { margin: 0.5em 0; text-align: justify; text-indent: 1.5em; }
h1 + p, h2 + p, h3 + p { text-indent: 0; }

img { max-width: 100%; height: auto; display: block; margin: 1em auto; }

table { border-collapse: collapse; width: 100%; margin: 1em 0; }
th, td { border: 1px solid #ccc; padding: 0.4em 0.6em; text-align: left; }
th { font-weight: bold; background-color: #f0f0f0; }

ul, ol { margin: 0.5em 0; padding-left: 2em; }
li { margin: 0.2em 0; }

a { color: inherit; text-decoration: underline; }

blockquote { margin: 1em 2em; font-style: italic; }
"""


def assemble_epub(doc: CleanedDocument, output_path: str) -> str:
    """Assemble a CleanedDocument into an ePub file."""
    book = epub.EpubBook()

    book.set_identifier(f"kinder-convert-{hash(doc.title)}")
    book.set_title(doc.title)
    book.set_language(doc.language)
    if doc.author:
        book.add_author(doc.author)

    style = epub.EpubItem(
        uid="style",
        file_name="style/default.css",
        media_type="text/css",
        content=DEFAULT_CSS.encode("utf-8"),
    )
    book.add_item(style)

    for img in doc.images:
        epub_img = epub.EpubImage(
            uid=f"img-{img.original_filename}",
            file_name=f"images/{img.original_filename}",
            media_type=img.mime_type,
            content=img.content,
        )
        book.add_item(epub_img)

    if doc.cover_image:
        book.set_cover(
            f"images/{doc.cover_image.original_filename}",
            doc.cover_image.content,
        )

    epub_chapters = []
    for i, chapter in enumerate(doc.chapters):
        epub_chapter = epub.EpubHtml(
            title=chapter.title,
            file_name=f"chapter_{i:02d}.xhtml",
            lang=doc.language,
        )
        body_html = f"<h2>{chapter.title}</h2>\n{chapter.html_content}"
        epub_chapter.set_content(body_html.encode("utf-8"))
        epub_chapter.add_item(style)
        book.add_item(epub_chapter)
        epub_chapters.append(epub_chapter)

    book.toc = [
        epub.Link(ch.file_name, ch.title, f"ch-{i}")
        for i, ch in enumerate(epub_chapters)
    ]

    book.spine = ["nav"] + epub_chapters

    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    epub.write_epub(output_path, book)
    return output_path


