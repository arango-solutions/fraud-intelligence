#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
from urllib.parse import urlparse

from common import apply_config_to_env, get_arango_config, load_dotenv, sanitize_url

try:
    from arango import ArangoClient  # type: ignore
except Exception:  # pragma: no cover
    ArangoClient = None  # type: ignore


WHITELIST = {
    # vertex
    "person",
    "organization",
    "watchlist_entity",
    "bank_account",
    "real_property",
    "address",
    "digital_location",
    "transaction",
    "real_estate_transaction",
    "document",
    "golden_record",
    # edges
    "has_account",
    "transferred_to",
    "related_to",
    "associated_with",
    "resides_at",
    "accessed_from",
    "has_digital_location",
    "mentioned_in",
    "registered_sale",
    "buyer_in",
    "seller_in",
    "resolved_to",
}


def env(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise SystemExit(f"Missing required environment variable: {name}")
    return v


def is_local(url: str) -> bool:
    u = urlparse(url)
    host = u.hostname or ""
    return host in {"localhost", "127.0.0.1"}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Safely reset demo collections (truncate) in ArangoDB.")
    p.add_argument("--execute", action="store_true", help="Actually truncate (default is dry-run)")
    p.add_argument("--confirm", action="store_true", help="Required with --execute")
    p.add_argument("--allow-remote", action="store_true", help="Allow non-local ARANGO_URL (extra risk)")
    return p.parse_args()


def main() -> None:
    if ArangoClient is None:
        raise SystemExit(
            "python-arango is not installed. Install dependencies:\n  pip install -r requirements.txt"
        )

    args = parse_args()

    load_dotenv()
    cfg = get_arango_config()
    apply_config_to_env(cfg)

    arango_url = env("ARANGO_URL")
    username = env("ARANGO_USERNAME")
    password = env("ARANGO_PASSWORD")
    db_name = os.getenv("ARANGO_DATABASE") or os.getenv("ARANGO_DB") or ""
    if not db_name:
        raise SystemExit("Missing required environment variable: ARANGO_DATABASE (or ARANGO_DB)")

    if not is_local(arango_url) and not args.allow_remote:
        raise SystemExit(
            f"Refusing to run against non-local ARANGO_URL={sanitize_url(arango_url)}. Use --allow-remote if you are sure."
        )

    client = ArangoClient(hosts=arango_url)
    db = client.db(db_name, username=username, password=password)

    existing = {c["name"] for c in db.collections()}
    targets = sorted([c for c in existing if c in WHITELIST])

    if not targets:
        print("No whitelisted demo collections found.")
        return

    print("Will truncate collections:")
    for t in targets:
        print(f"- {t} ({db.collection(t).count()} docs)")

    if not args.execute:
        print("Dry-run only. Re-run with --execute --confirm to truncate.")
        return

    if not args.confirm:
        raise SystemExit("Refusing to truncate without --confirm.")

    for t in targets:
        db.collection(t).truncate()
        print(f"truncated: {t}")

    print("Reset complete.")


if __name__ == "__main__":
    main()

