from __future__ import annotations

import os
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional
from urllib.parse import urlparse, urlunparse


@dataclass(frozen=True)
class ArangoConfig:
    mode: str  # LOCAL | REMOTE
    url: str
    username: str
    password: str
    database: str


def load_dotenv(dotenv_path: Optional[Path] = None) -> None:
    """
    Minimal .env loader.
    - Does NOT print values.
    - Does NOT overwrite already-set environment variables.
    """
    if dotenv_path is None:
        dotenv_path = Path(__file__).resolve().parents[1] / ".env"
    if not dotenv_path.exists():
        return

    for line in dotenv_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        if not k:
            continue
        os.environ.setdefault(k, v)


def sanitize_url(url: str) -> str:
    """
    Remove userinfo from URL so we can safely print it.
    """
    try:
        u = urlparse(url)
        netloc = u.hostname or ""
        if u.port:
            netloc = f"{netloc}:{u.port}"
        return urlunparse((u.scheme, netloc, u.path, u.params, u.query, u.fragment))
    except Exception:
        # Best-effort redaction of credentials if present.
        return re.sub(r"//[^/@]+@", "//***@", url)


def get_mode() -> str:
    return (os.getenv("MODE") or os.getenv("ARANGO_MODE") or "LOCAL").strip().upper()


def _first(*vals: Optional[str]) -> Optional[str]:
    for v in vals:
        if v is not None and v != "":
            return v
    return None


def get_arango_config(forced_mode: Optional[str] = None) -> ArangoConfig:
    """
    Resolve mode-aware configuration.

    Supports common env layouts:
    - MODE=LOCAL|REMOTE (or ARANGO_MODE)
    - LOCAL_ARANGO_URL / LOCAL_ARANGO_ENDPOINT
    - ARANGO_URL / ARANGO_ENDPOINT
    - ARANGO_DATABASE (preferred) or ARANGO_DB (legacy)
    """
    mode = (forced_mode or get_mode()).strip().upper()
    if mode not in {"LOCAL", "REMOTE"}:
        mode = "LOCAL"

    # LOCAL overrides
    local_url = _first(os.getenv("LOCAL_ARANGO_URL"), os.getenv("LOCAL_ARANGO_ENDPOINT"))
    local_user = _first(os.getenv("LOCAL_ARANGO_USERNAME"), os.getenv("LOCAL_ARANGO_USER"))
    local_pass = _first(os.getenv("LOCAL_ARANGO_PASSWORD"), os.getenv("LOCAL_ARANGO_PASS"))
    local_db = _first(os.getenv("LOCAL_ARANGO_DATABASE"), os.getenv("LOCAL_ARANGO_DB"))

    # REMOTE / default
    url = _first(os.getenv("ARANGO_URL"), os.getenv("ARANGO_ENDPOINT"))
    user = _first(os.getenv("ARANGO_USERNAME"), os.getenv("ARANGO_USER"), "root")
    passwd = _first(os.getenv("ARANGO_PASSWORD"), os.getenv("ARANGO_PASS"), "")
    db = _first(os.getenv("ARANGO_DATABASE"), os.getenv("ARANGO_DB"), "fraud_intelligence")

    if mode == "LOCAL":
        port = os.getenv("ARANGO_PORT")
        default_local = f"http://localhost:{port}" if port else "http://localhost:8529"
        return ArangoConfig(
            mode="LOCAL",
            url=_first(local_url, url, default_local) or default_local,
            username=_first(local_user, user, "root") or "root",
            password=_first(local_pass, passwd, "") or "",
            database=_first(local_db, db, "fraud_intelligence") or "fraud_intelligence",
        )

    # REMOTE: prefer the non-LOCAL values. If user kept only ARANGO_* variables, those will be used.
    return ArangoConfig(
        mode="REMOTE",
        url=_first(url, local_url) or "",
        username=user or "root",
        password=passwd or "",
        database=db or "fraud_intelligence",
    )


def apply_config_to_env(cfg: ArangoConfig) -> None:
    """
    Normalize the env vars our scripts/tests use.
    Never prints secrets.
    """
    os.environ["MODE"] = cfg.mode
    os.environ["ARANGO_URL"] = cfg.url
    os.environ["ARANGO_USERNAME"] = cfg.username
    os.environ["ARANGO_PASSWORD"] = cfg.password
    # Support both names; prefer ARANGO_DATABASE going forward.
    os.environ["ARANGO_DATABASE"] = cfg.database
    os.environ["ARANGO_DB"] = cfg.database


def wait_for_http_ok(url: str, timeout_s: int = 60) -> None:
    """
    Poll ArangoDB /_api/version until reachable.
    """
    import urllib.request
    import urllib.error

    deadline = time.time() + timeout_s
    last_err: Optional[Exception] = None
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"{url.rstrip('/')}/_api/version", timeout=3) as resp:
                if 200 <= resp.status < 300:
                    return
        except urllib.error.HTTPError as e:
            # ArangoDB may be up but require auth; 401 indicates the server is reachable.
            if getattr(e, "code", None) == 401:
                return
            last_err = e
            time.sleep(1)
        except Exception as e:
            last_err = e
            time.sleep(1)
    raise RuntimeError(f"Timed out waiting for ArangoDB at {sanitize_url(url)}: {last_err}")

