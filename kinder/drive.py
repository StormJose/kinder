"""
drive.py
--------
Google Drive OCR integration — user-account (OAuth 2.0) version.

Changes from the service-account version:
  - Auth comes from auth.build_drive_service(), not a service account key file.
  - `supportsAllDrives` parameter removed from all calls (no longer needed).
  - `parents` no longer set to a Shared Drive ID — files land in the user's My Drive.
  - Everything else (upload, export, 10MB fallback, delete-in-finally) is identical.
"""

import io
import tempfile
import zipfile
from pathlib import Path

from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload

from kinder.auth import build_drive_service

# MIME types
_PDF_MIME = "application/pdf"
_GDOC_MIME = "application/vnd.google-apps.document"
_HTML_ZIP_MIME = "application/zip"
_EPUB_MIME = "application/epub+zip"


def ocr_pdf_to_html(
    pdf_path: Path,
    ocr_language: str = "pt",
    token_path: Path | None = None,
) -> bytes:
    """
    Upload a PDF, convert it via Google Drive OCR, export as HTML zip,
    and return the raw zip bytes. The temporary Google Doc is always deleted.

    Args:
        pdf_path:     Path to the local PDF file.
        ocr_language: BCP 47 language code hint for OCR (e.g. "pt", "en", "es").
        token_path:   Optional path to token.json. Defaults to
                      ~/.config/pdf_to_kindle/token.json.

    Returns:
        Raw bytes of the exported HTML zip (contains an .html file + images/ folder).
    """
    service = build_drive_service(token_path=token_path)
    file_id = None

    try:
        file_id = _upload_and_convert(service, pdf_path, ocr_language)
        return _export_html(service, file_id)
    finally:
        if file_id:
            _delete_doc(service, file_id)


def ocr_pdf_to_epub(
    pdf_path: Path,
    ocr_language: str = "pt",
    token_path: Path | None = None,
) -> bytes:
    """
    Path A (--quick mode): upload, convert, export directly as ePub bytes.
    Less control over output but three stages instead of five.
    """
    service = build_drive_service(token_path=token_path)
    file_id = None

    try:
        file_id = _upload_and_convert(service, pdf_path, ocr_language)
        return _export_content(service, file_id, _EPUB_MIME)
    finally:
        if file_id:
            _delete_doc(service, file_id)


# ── Internal helpers ──────────────────────────────────────────────────────────

def _upload_and_convert(service, pdf_path: Path, ocr_language: str) -> str:
    """
    Upload the PDF as a Google Doc (triggering OCR) and return the new file ID.

    CHANGED from service-account version:
      - Removed: `"parents": [SHARED_DRIVE_ID]`  — files go to My Drive instead
      - Removed: `supportsAllDrives=True`         — not needed for My Drive
    """
    file_metadata = {
        "name": pdf_path.stem,   # Doc title = PDF filename without extension
        "mimeType": _GDOC_MIME,  # This tells Drive to OCR-convert, not just store
    }
    media = MediaFileUpload(
        str(pdf_path),
        mimetype=_PDF_MIME,
        resumable=True,
    )
    result = (
        service.files()
        .create(
            body=file_metadata,
            media_body=media,
            fields="id",
            ocrLanguage=ocr_language,
   
        )
        .execute()
    )
    return result["id"]


def _export_html(service, file_id: str) -> bytes:
    """Export the Google Doc as an HTML zip, falling back to exportLinks if >10MB."""
    try:
        return _export_content(service, file_id, _HTML_ZIP_MIME)
    except HttpError as e:
        if _is_size_limit_error(e):
            return _export_via_link(service, file_id, _HTML_ZIP_MIME)
        raise


def _export_content(service, file_id: str, mime_type: str) -> bytes:
    """
    Download exported content via files.export (hard 10MB limit).

    CHANGED from service-account version:
      - Removed: `supportsAllDrives=True`
    """
    request = service.files().export_media(fileId=file_id, mimeType=mime_type)
    buffer = io.BytesIO()
    downloader = MediaIoBaseDownload(buffer, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    return buffer.getvalue()


def _export_via_link(service, file_id: str, mime_type: str) -> bytes:
    """
    Large-file fallback: get the exportLinks URL and stream from it directly.
    Bypasses the 10MB files.export ceiling.

    CHANGED from service-account version:
      - Removed: `supportsAllDrives=True` from files.get call
    """
    meta = (
        service.files()
        .get(
            fileId=file_id,
            fields="exportLinks",
            # supportsAllDrives=True  ← REMOVED
        )
        .execute()
    )
    export_url = meta.get("exportLinks", {}).get(mime_type)
    if not export_url:
        raise RuntimeError(f"No export link found for MIME type: {mime_type}")

    # Use the authorized HTTP client from the service object to fetch the URL
    http = service._http  # pylint: disable=protected-access
    response, content = http.request(export_url)
    if response.status != 200:
        raise RuntimeError(f"Export link fetch failed with status {response.status}")
    return content


def _delete_doc(service, file_id: str) -> None:
    """
    Permanently delete the temporary Google Doc from the user's Drive.
    Always called in a finally block — must not raise.

    CHANGED from service-account version:
      - Removed: `supportsAllDrives=True`
    """
    try:
        service.files().delete(fileId=file_id).execute()
    except Exception as exc:  # noqa: BLE001
        # Log but don't re-raise — a failed cleanup shouldn't abort a successful conversion
        print(f"[drive] Warning: could not delete temporary doc {file_id}: {exc}")


def _is_size_limit_error(error: HttpError) -> bool:
    """Detect the exportSizeLimitExceeded error code."""
    try:
        reason = error.error_details[0].get("reason", "")
        return reason == "exportSizeLimitExceeded"
    except (IndexError, AttributeError, TypeError):
        return "exportSizeLimitExceeded" in str(error)