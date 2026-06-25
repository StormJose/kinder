"""
generate_token.py
-----------------
Run this ONCE locally to authorize your Google account and produce token.json.
After that, the main pipeline will refresh the token silently on every run.

Usage:
    python generate_token.py --client-secret path/to/client_secret.json

The script will:
  1. Open your browser to Google's consent screen.
  2. Ask you to log in and authorize Drive access.
  3. Save the resulting token (access + refresh) to ~/.config/pdf_to_kindle/token.json
"""

import argparse
import json
import os
import sys
from pathlib import Path

from google_auth_oauthlib.flow import InstalledAppFlow

# ── Scopes ────────────────────────────────────────────────────────────────────
# drive.file  → read/write only files this app creates (temporary OCR docs)
# If you later add the Drive-output feature (upload AZW3 back to user's Drive),
# this scope already covers it — no re-authorization needed.
SCOPES = ["https://www.googleapis.com/auth/drive.file"]

# ── Token storage location ────────────────────────────────────────────────────
TOKEN_DIR = Path.home() / ".config" / "pdf_to_kindle"
TOKEN_PATH = TOKEN_DIR / "token.json"


def main():
    parser = argparse.ArgumentParser(description="Authorize Google Drive access for pdf_to_kindle.")
    parser.add_argument(
        "--client-secret",
        required=True,
        metavar="PATH",
        help="Path to the client_secret.json downloaded from GCP Console.",
    )
    parser.add_argument(
        "--token-out",
        default=str(TOKEN_PATH),
        metavar="PATH",
        help=f"Where to save the token (default: {TOKEN_PATH})",
    )
    args = parser.parse_args()

    client_secret_path = Path(args.client_secret)
    if not client_secret_path.exists():
        print(f"ERROR: client_secret.json not found at: {client_secret_path}", file=sys.stderr)
        sys.exit(1)

    token_out = Path(args.token_out)
    token_out.parent.mkdir(parents=True, exist_ok=True)

    print("Opening your browser for Google authorization...")
    print(f"Scopes requested: {SCOPES}\n")

    # InstalledAppFlow handles the local redirect server automatically.
    # It opens the browser, waits for the callback, and exchanges the code
    # for access + refresh tokens — all in one call.
    flow = InstalledAppFlow.from_client_secrets_file(
        str(client_secret_path),
        scopes=SCOPES,
    )

    # port=0 lets the OS pick a free port, which avoids conflicts.
    creds = flow.run_local_server(port=0, prompt="consent")

    # Persist the full credentials object (access token + refresh token + expiry)
    token_out.write_text(creds.to_json())
    os.chmod(token_out, 0o600)  # owner read/write only — protect the refresh token

    print(f"\n✓ Authorization successful.")
    print(f"  Token saved to: {token_out}")
    print(f"  Refresh token present: {'yes' if creds.refresh_token else 'NO — re-run with prompt=consent'}")
    print("\nYou won't need to re-authorize unless you revoke access or delete the token file.")


if __name__ == "__main__":
    main()