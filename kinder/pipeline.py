"""Pipeline orchestrator — ties all stages together."""

from __future__ import annotations

import logging
import tempfile
from pathlib import Path

import click

from kinder.calibre import convert_to_format
from kinder.cleaning import clean_html_export
from kinder.drive import ocr_pdf_to_epub, ocr_pdf_to_html
from kinder.epub import assemble_epub

logger = logging.getLogger(__name__)


def run_pipeline(config: dict) -> str:
    """Execute the full conversion pipeline. Returns the path to the output file."""
    tmp_dir = tempfile.mkdtemp(prefix="kinder-")
    pdf_path = Path(config["pdf_path"])
    token_path = Path(config["token_path"]) if config.get("token_path") else None

    if config["quick"]:
        click.echo("Uploading PDF and exporting as ePub (quick mode)...")
        epub_bytes = ocr_pdf_to_epub(
            pdf_path, ocr_language=config["language"], token_path=token_path
        )
        epub_path = str(Path(tmp_dir) / "output.epub")
        Path(epub_path).write_bytes(epub_bytes)
        click.echo("Export complete.")
    else:
        click.echo("Uploading PDF to Google Drive for OCR conversion...")
        html_zip_bytes = ocr_pdf_to_html(
            pdf_path, ocr_language=config["language"], token_path=token_path
        )

        print("html_zip_bytes")
        print(html_zip_bytes)
        click.echo("OCR conversion complete.")

        zip_path = str(Path(tmp_dir) / "export.zip")
        Path(zip_path).write_bytes(html_zip_bytes)

        click.echo("Cleaning HTML and detecting chapters...")
        cleaned = clean_html_export(
            zip_path,
            language=config["language"],
            author=config["author"],
            chapter_split_level=config["chapter_level"],
        )
        if config.get("title"):
            cleaned.title = config["title"]

        click.echo(
            f"Found {len(cleaned.chapters)} chapters, {len(cleaned.images)} images."
        )

        click.echo("Assembling ePub...")
        epub_path = str(Path(tmp_dir) / "output.epub")
        assemble_epub(cleaned, epub_path)

    if config["output_format"] == "epub":
        final_path = config["output"]
        Path(epub_path).rename(final_path)
    else:
        click.echo(f"Converting to {config['output_format'].upper()}...")
        final_path = config["output"]
        convert_to_format(epub_path, final_path)

    click.echo(f"Done! Output: {final_path}")
    return final_path
