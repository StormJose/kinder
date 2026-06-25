"""CLI entry point."""

from __future__ import annotations

from pathlib import Path

import click

from kinder.pipeline import run_pipeline


@click.command()
@click.argument("pdf_path", type=click.Path(exists=True))
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default=None,
    help="Output file path. Defaults to input name with format extension.",
)
@click.option(
    "--format",
    "-f",
    "output_format",
    type=click.Choice(["azw3", "epub", "mobi"]),
    default="azw3",
    help="Output format (default: azw3).",
)
@click.option(
    "--token-path",
    type=click.Path(),
    envvar="KINDER_TOKEN_PATH",
    default=None,
    help=(
        "Path to OAuth token.json. Defaults to "
        "~/.config/pdf_to_kindle/token.json. "
        "Run generate_token.py once to create it."
    ),
)
@click.option(
    "--language",
    "-l",
    default="en",
    help="Document language as BCP 47 code (default: en).",
)
@click.option("--author", "-a", default="", help="Author name for ePub metadata.")
@click.option(
    "--title",
    "-t",
    default=None,
    help="Book title. Defaults to first H1 or filename.",
)
@click.option(
    "--chapter-level",
    type=click.IntRange(1, 4),
    default=1,
    help="Heading level for chapter splits (1=H1, 2=H2, etc.).",
)
@click.option(
    "--quick",
    is_flag=True,
    help="Quick mode: use Google's direct ePub export (less control).",
)
def convert(
    pdf_path: str,
    output: str | None,
    output_format: str,
    token_path: str | None,
    language: str,
    author: str,
    title: str | None,
    chapter_level: int,
    quick: bool,
) -> None:
    """Convert a PDF to a Kindle-ready ebook."""
    if output is None:
        output = str(Path(pdf_path).with_suffix(f".{output_format}"))

    config = {
        "pdf_path": pdf_path,
        "output": output,
        "output_format": output_format,
        "token_path": token_path,
        "language": language,
        "author": author,
        "title": title,
        "chapter_level": chapter_level,
        "quick": quick,
    }

    run_pipeline(config)
