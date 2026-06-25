"""Stage 5 — Format conversion via Calibre ebook-convert CLI."""

from __future__ import annotations

import os
import shutil
import subprocess


def check_calibre_installed() -> bool:
    """Return True if Calibre's ebook-convert is available on PATH."""
    if shutil.which("ebook-convert") is not None:
        return True
    custom_path =  os.environ.get("CALIBRE_PATH")
    if custom_path and os.path.exists(custom_path):
        return True

    return False

def convert_to_format(epub_path: str, output_path: str) -> str:
    """Convert an ePub to the target format using Calibre's ebook-convert."""
    if not check_calibre_installed():
        raise RuntimeError(
            "Calibre's ebook-convert not found on PATH. "
            "Install Calibre from https://calibre-ebook.com/download"
        )

    result = subprocess.run(
        ["ebook-convert", epub_path, output_path],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Calibre conversion failed:\n{result.stderr}")
    return output_path
