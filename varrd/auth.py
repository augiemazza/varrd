"""Credential management for VARRD.

Auth flow:
1. First API call with no auth -> server auto-creates anonymous agent -> returns JWT
2. Client saves JWT to ~/.varrd/credentials
3. Subsequent calls use stored JWT
4. If user has an API key, they pass it to VARRD(api_key="...")
"""

import json
import os
from pathlib import Path

CREDENTIALS_DIR = Path.home() / ".varrd"
CREDENTIALS_FILE = CREDENTIALS_DIR / "credentials"


def get_credentials() -> dict | None:
    """Load stored credentials from ~/.varrd/credentials.

    Returns dict with 'token' and optionally 'passkey', or None.
    """
    if not CREDENTIALS_FILE.exists():
        return None
    try:
        data = json.loads(CREDENTIALS_FILE.read_text(encoding="utf-8"))
        if isinstance(data, dict) and data.get("token"):
            return data
    except (json.JSONDecodeError, OSError):
        pass
    return None


def save_credentials(token: str, passkey: str | None = None):
    """Save JWT (and optional passkey) to ~/.varrd/credentials."""
    CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)
    data = {"token": token}
    if passkey:
        data["passkey"] = passkey
    CREDENTIALS_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    # Restrict permissions on Unix
    try:
        CREDENTIALS_FILE.chmod(0o600)
    except OSError:
        pass


def clear_credentials():
    """Delete stored credentials."""
    if CREDENTIALS_FILE.exists():
        CREDENTIALS_FILE.unlink()


def get_token() -> str | None:
    """Get just the JWT token, checking env var first then stored credentials."""
    # 1. Environment variable
    env_key = os.environ.get("VARRD_API_KEY")
    if env_key:
        return env_key

    # 2. Stored credentials
    creds = get_credentials()
    if creds:
        return creds["token"]

    return None
