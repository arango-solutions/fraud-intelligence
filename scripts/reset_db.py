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


# Phase 1 whitelist (PascalCase naming per PRD canonical schema)
WHITELIST = {
    # vertex collections
    "Person",
    "Organization",
    "WatchlistEntity",
    "BankAccount",
    "RealProperty",
    "Address",
    "DigitalLocation",
    "Transaction",
    "RealEstateTransaction",
    "Document",
    "GoldenRecord",
    # edge collections
    "hasAccount",
    "transferredTo",
    "relatedTo",
    "associatedWith",
    "residesAt",
    "accessedFrom",
    "hasDigitalLocation",
    "mentionedIn",
    "registeredSale",
    "buyerIn",
    "sellerIn",
    "resolvedTo",
}

# Legacy snake_case collections (for optional cleanup)
LEGACY_COLLECTIONS = {
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
    p = argparse.ArgumentParser(description="Safely reset Phase 1 collections (truncate) in ArangoDB.")
    p.add_argument("--mode", choices=["LOCAL", "REMOTE"], help="Operation mode (default: infer from config)")
    p.add_argument("--execute", action="store_true", help="Actually truncate (default is dry-run)")
    p.add_argument("--confirm", action="store_true", help="Required with --execute")
    p.add_argument("--confirm-remote", action="store_true", help="Required when --mode=REMOTE")
    p.add_argument("--cleanup-legacy", action="store_true", help="Also remove legacy snake_case collections")
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

    # Determine mode (explicit arg or infer from config)
    mode = args.mode or cfg.mode
    if mode not in {"LOCAL", "REMOTE"}:
        mode = "LOCAL"

    arango_url = env("ARANGO_URL")
    username = env("ARANGO_USERNAME")
    password = env("ARANGO_PASSWORD")
    db_name = os.getenv("ARANGO_DATABASE") or os.getenv("ARANGO_DB") or ""
    if not db_name:
        raise SystemExit("Missing required environment variable: ARANGO_DATABASE (or ARANGO_DB)")

    # Safety checks for REMOTE mode
    if mode == "REMOTE":
        if not args.confirm_remote:
            raise SystemExit(
                f"REMOTE mode requires --confirm-remote flag. "
                f"Refusing to operate on remote database without explicit confirmation."
            )
        if is_local(arango_url):
            raise SystemExit(
                "REMOTE mode requires a non-local ARANGO_URL. Refusing to operate on localhost/127.0.0.1."
            )
        if db_name != "fraud-intelligence":
            raise SystemExit(
                f"REMOTE mode only allowed for database 'fraud-intelligence', "
                f"but database is '{db_name}'. Refusing to proceed."
            )

    # For LOCAL mode, warn if URL looks remote (but allow with explicit mode=LOCAL)
    if mode == "LOCAL" and not is_local(arango_url):
        print(f"Warning: ARANGO_URL={sanitize_url(arango_url)} appears remote, but mode=LOCAL.")
        print("If this is incorrect, use --mode REMOTE --confirm-remote")

    client = ArangoClient(hosts=arango_url)
    db = client.db(db_name, username=username, password=password)

    existing = {c["name"] for c in db.collections()}
    targets = sorted([c for c in existing if c in WHITELIST])

    if not targets:
        print("No whitelisted Phase 1 collections found.")
        return

    print(f"Mode: {mode}")
    print(f"ArangoDB: {sanitize_url(arango_url)}")
    print(f"Database: {db_name}")
    print(f"Will truncate collections:")
    for t in targets:
        print(f"- {t} ({db.collection(t).count()} docs)")

    # Legacy cleanup option
    legacy_targets = []
    if args.cleanup_legacy:
        legacy_targets = sorted([c for c in existing if c in LEGACY_COLLECTIONS])
        if legacy_targets:
            print(f"\nWill also remove legacy collections:")
            for t in legacy_targets:
                print(f"- {t} ({db.collection(t).count()} docs)")

    if not args.execute:
        print("\nDry-run only. Re-run with --execute --confirm to truncate.")
        return

    if not args.confirm:
        raise SystemExit("Refusing to truncate without --confirm.")

    # Truncate whitelisted collections
    for t in targets:
        db.collection(t).truncate()
        print(f"truncated: {t}")

    # Remove legacy collections if requested
    if legacy_targets:
        for t in legacy_targets:
            db.delete_collection(t)
            print(f"deleted legacy: {t}")

    print("Reset complete.")


if __name__ == "__main__":
    main()

