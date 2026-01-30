#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

from common import apply_config_to_env, get_arango_config, load_dotenv, sanitize_url

try:
    from arango import ArangoClient  # type: ignore
except Exception as e:  # pragma: no cover
    ArangoClient = None  # type: ignore


VERTEX_COLLECTIONS = [
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
]

EDGE_COLLECTIONS = [
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
]


NUMERIC_FIELDS = {
    # vertices
    "person": {"risk_score", "risk_direct", "risk_inferred", "risk_path"},
    "watchlist_entity": {"risk_score", "risk_direct"},
    "bank_account": {"balance", "avg_monthly_balance", "risk_score", "risk_direct", "risk_inferred", "risk_path"},
    "real_property": {"circle_rate_value", "market_value", "risk_score"},
    "address": {"lat", "long"},
    "transaction": {"amount"},
    "real_estate_transaction": {"transaction_value", "risk_score"},
    # edges
    "transferred_to": {"amount"},
    "mentioned_in": {"confidence"},
}

JSON_FIELDS = {
    "person": {"risk_reasons"},
    "watchlist_entity": {"risk_reasons"},
    "real_property": {"risk_reasons"},
    "real_estate_transaction": {"risk_reasons"},
}


def env_any(*names: str, default: Optional[str] = None) -> str:
    for name in names:
        v = os.getenv(name)
        if v is not None and v != "":
            return v
    if default is None:
        raise SystemExit(f"Missing required environment variable(s): {', '.join(names)}")
    return default


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Ingest Phase 1 CSV data into ArangoDB.")
    p.add_argument("--data-dir", required=True, help="Directory containing CSVs (e.g., data/sample)")
    p.add_argument("--force", action="store_true", help="Truncate existing collections before import")
    p.add_argument("--validate-only", action="store_true", help="Only validate (no import)")
    return p.parse_args()


def to_number(s: str) -> Any:
    if s == "" or s is None:
        return None
    try:
        if "." in s:
            return float(s)
        return int(s)
    except Exception:
        try:
            return float(s)
        except Exception:
            return s


def convert_row(collection: str, row: Dict[str, str]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    for k, v in row.items():
        if v == "":
            continue
        if k in NUMERIC_FIELDS.get(collection, set()):
            out[k] = to_number(v)
            continue
        if k in JSON_FIELDS.get(collection, set()):
            try:
                out[k] = json.loads(v)
            except Exception:
                out[k] = v
            continue
        out[k] = v
    return out


def read_csv(path: Path) -> Tuple[List[str], List[Dict[str, Any]]]:
    with path.open("r", newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        rows = [dict(row) for row in r]
        return (r.fieldnames or []), rows


def ensure_schema(db) -> None:
    # collections
    for name in VERTEX_COLLECTIONS:
        if not db.has_collection(name):
            db.create_collection(name)
    for name in EDGE_COLLECTIONS:
        if not db.has_collection(name):
            db.create_collection(name, edge=True)

    # indexes (idempotent)
    db.collection("person").add_persistent_index(["pan_number"], sparse=True)
    db.collection("bank_account").add_persistent_index(["account_number"], sparse=True)
    db.collection("real_property").add_persistent_index(["survey_number"], sparse=True)
    db.collection("address").add_persistent_index(["district", "state"])
    db.collection("transferred_to").add_persistent_index(["timestamp"])
    db.collection("transferred_to").add_persistent_index(["amount"])


def import_collection(db, name: str, csv_path: Path, force: bool) -> int:
    col = db.collection(name)
    if col.count() > 0:
        if not force:
            print(f"skip {name}: already has {col.count()} docs (use --force to reimport)")
            return 0
        print(f"truncate {name} (had {col.count()} docs)")
        col.truncate()

    _, raw_rows = read_csv(csv_path)
    docs = [convert_row(name, row) for row in raw_rows]

    # Import in batches to avoid huge requests.
    batch = 2000
    inserted = 0
    for i in range(0, len(docs), batch):
        chunk = docs[i : i + batch]
        res = col.import_bulk(chunk)
        inserted += int(res.get("created", 0))
        if res.get("errors", 0):
            raise RuntimeError(f"Import errors in {name}: {res}")
    return inserted


def main() -> None:
    if ArangoClient is None:
        raise SystemExit(
            "python-arango is not installed. Install dependencies:\n  pip install -r requirements.txt"
        )

    args = parse_args()
    data_dir = Path(args.data_dir)
    if not data_dir.exists():
        raise SystemExit(f"data-dir does not exist: {data_dir}")

    # Load .env without printing secrets.
    load_dotenv()
    cfg = get_arango_config()
    apply_config_to_env(cfg)

    arango_url = env_any("ARANGO_URL")
    username = env_any("ARANGO_USERNAME")
    password = env_any("ARANGO_PASSWORD")
    db_name = env_any("ARANGO_DATABASE", "ARANGO_DB")

    print(f"mode={cfg.mode} arango={sanitize_url(arango_url)} db={db_name}")

    client = ArangoClient(hosts=arango_url)
    sys_db = client.db("_system", username=username, password=password)

    # Create DB if possible (remote may deny).
    if not sys_db.has_database(db_name):
        try:
            sys_db.create_database(db_name)
            print(f"created database: {db_name}")
        except Exception as e:
            raise SystemExit(
                f"Database {db_name} does not exist and could not be created: {e}"
            )

    db = client.db(db_name, username=username, password=password)
    ensure_schema(db)

    if args.validate_only:
        print("validate-only: schema ensured")
        return

    # Determine which CSVs exist
    csv_files = {p.name: p for p in data_dir.glob("*.csv")}
    expected = [f"{name}.csv" for name in VERTEX_COLLECTIONS + EDGE_COLLECTIONS]
    missing = [f for f in expected if f not in csv_files]
    if missing:
        raise SystemExit(f"Missing CSV files in {data_dir}: {missing}")

    total_inserted = 0
    for name in VERTEX_COLLECTIONS + EDGE_COLLECTIONS:
        inserted = import_collection(db, name, csv_files[f"{name}.csv"], force=args.force)
        total_inserted += inserted
        if inserted:
            print(f"imported {inserted} into {name}")

    # Basic validation summary
    print("----")
    print("Import summary")
    for name in VERTEX_COLLECTIONS + EDGE_COLLECTIONS:
        print(f"{name}: {db.collection(name).count()}")
    print(f"total inserted: {total_inserted}")


if __name__ == "__main__":
    main()

