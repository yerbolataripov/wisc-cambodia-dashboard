"""
Centralised JSON datastore for the dashboard.

Two backends:
- LOCAL FILES (default for dev): reads from / writes to ``data/<filename>.json``.
- GIST (when Streamlit secrets ``GIST_ID`` and ``GH_TOKEN`` are set): reads/writes
  the same file names as files inside a single private GitHub Gist.

The Gist backend lets a deployed Streamlit Cloud app persist edits across
container rebuilds (the local filesystem there is ephemeral). All callers go
through ``load_json`` / ``save_json`` and stay agnostic of the backend.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any
from urllib import error as _err
from urllib import request as _req

import streamlit as st

DATA_DIR = Path(__file__).parent.parent / "data"
GIST_API = "https://api.github.com/gists"


# ---------------------------------------------------------------------------
# Backend detection
# ---------------------------------------------------------------------------
def _gist_creds() -> tuple[str, str] | None:
    """Return (gist_id, token) if Streamlit secrets are configured, else None."""
    try:
        gid = st.secrets.get("GIST_ID")
        tok = st.secrets.get("GH_TOKEN")
    except (FileNotFoundError, AttributeError):
        return None
    if gid and tok:
        return str(gid), str(tok)
    return None


def backend() -> str:
    """Return 'gist' or 'local' — used for status/debugging UI."""
    return "gist" if _gist_creds() else "local"


# ---------------------------------------------------------------------------
# Gist client (raw urllib, no extra dep)
# ---------------------------------------------------------------------------
def _gist_get(gid: str, token: str) -> dict[str, Any]:
    req = _req.Request(
        f"{GIST_API}/{gid}",
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "wisc-dashboard",
        },
    )
    with _req.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _gist_patch(gid: str, token: str, files_payload: dict[str, dict]) -> None:
    body = json.dumps({"files": files_payload}).encode("utf-8")
    req = _req.Request(
        f"{GIST_API}/{gid}",
        data=body,
        method="PATCH",
        headers={
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "User-Agent": "wisc-dashboard",
        },
    )
    with _req.urlopen(req, timeout=20) as resp:
        resp.read()  # drain


# ---------------------------------------------------------------------------
# Public API — load_json / save_json
# ---------------------------------------------------------------------------
@st.cache_data(ttl=30, show_spinner=False)
def _gist_load_all(gist_id: str, token: str, _bust: int) -> dict[str, str]:
    """Fetch the entire Gist once and return {filename: content_text}.
    ``_bust`` is just there to let callers force-refresh by changing the value.
    """
    payload = _gist_get(gist_id, token)
    return {name: meta.get("content", "") for name, meta in payload.get("files", {}).items()}


def _read_local(filename: str) -> dict:
    with open(DATA_DIR / filename, "r", encoding="utf-8") as f:
        return json.load(f)


def _write_local(filename: str, data: dict) -> None:
    with open(DATA_DIR / filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_json(filename: str) -> dict:
    """Load a JSON file by name (e.g. ``"sales_scripts.json"``).

    Reads from the Gist if Streamlit secrets are present; otherwise reads from
    the local ``data/`` directory.
    """
    creds = _gist_creds()
    if not creds:
        return _read_local(filename)

    gist_id, token = creds
    bust = st.session_state.get("_gist_bust", 0)
    try:
        files = _gist_load_all(gist_id, token, bust)
        if filename not in files:
            # New file added locally but not yet pushed to Gist — fall back to local
            return _read_local(filename)
        return json.loads(files[filename])
    except (_err.HTTPError, _err.URLError, ValueError):
        # Network problem — degrade gracefully to whatever ships in the repo
        return _read_local(filename)


def save_json(filename: str, data: dict) -> None:
    """Persist a JSON file. Writes to the Gist when configured, else local."""
    creds = _gist_creds()
    if not creds:
        _write_local(filename, data)
        return

    gist_id, token = creds
    payload = {filename: {"content": json.dumps(data, ensure_ascii=False, indent=2)}}
    _gist_patch(gist_id, token, payload)
    # Force the next load to re-fetch
    st.session_state["_gist_bust"] = int(time.time())
    try:
        _gist_load_all.clear()
    except Exception:
        pass
