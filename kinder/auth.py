"""
auth.py
-------
OAuth 2.0 user-account authentication for the Google Drive API.

Replaces the service-account approach. Token is loaded from disk on every run
and refreshed automatically if expired. The user only sees a browser prompt
on the very first run (or after token deletion / access revocation).

Public API (unchanged from service-account version):
    build_drive_service() -> googleapiclient.discovery.Resource
"""

import json
import sys
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# ── Configuration ─────────────────────────────────────────────────────────────

SCOPES = ["https://www.googleapis.com/auth/drive.file"]

# Default token location — can be overridden via build_drive_service(token_path=...)
DEFAULT_TOKEN_PATH = Path.home() / ".config" / "pdf_to_kindle" / "token.json"


# ── Public entry point ────────────────────────────────────────────────────────

def build_drive_service(token_path: Path | None = None):
    """
    Load credentials from disk, refresh if expired, and return a Drive v3 client.

    Raises:
        FileNotFoundError: if token.json doesn't exist (user hasn't run generate_token.py yet).
        google.auth.exceptions.RefreshError: if the refresh token has been revoked.
    """
    token_path = Path(token_path) if token_path else DEFAULT_TOKEN_PATH
    creds = _load_credentials(token_path)
    creds = _refresh_if_needed(creds, token_path)
    return build("drive", "v3", credentials=creds)


# ── Internal helpers ──────────────────────────────────────────────────────────

def _load_credentials(token_path: Path) -> Credentials:
    """Read token.json and deserialize into a Credentials object."""
    if not token_path.exists():
        _abort_with_instructions(token_path)

    raw = token_path.read_text()
    try:
        info = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"token.json is malformed: {e}") from e

    creds = Credentials.from_authorized_user_info(info, SCOPES)

    if not creds.refresh_token:
        # This shouldn't happen if generate_token.py was used, but guard it.
        raise ValueError(
            "token.json contains no refresh token. "
            "Delete token.json and re-run generate_token.py."
        )

    return creds


def _refresh_if_needed(creds: Credentials, token_path: Path) -> Credentials:
    """Silently refresh the access token if it's expired or about to expire."""
    if not creds.valid:
        creds.refresh(Request())
        # Persist the updated access token (refresh token stays the same)
        token_path.write_text(creds.to_json())

    return creds


def _abort_with_instructions(token_path: Path) -> None:
    print(
        f"\n[pdf_to_kindle] Google Drive authorization required.\n"
        f"No token found at: {token_path}\n\n"
        f"Run this once to authorize:\n"
        f"  python generate_token.py --client-secret path/to/client_secret.json\n",
        file=sys.stderr,
    )
    sys.exit(1)