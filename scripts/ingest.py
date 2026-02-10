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


# Phase 1 collections (OWL conventions: PascalCase vertices, camelCase edges)
VERTEX_COLLECTIONS = [
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
]

EDGE_COLLECTIONS = [
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
]


NUMERIC_FIELDS = {
    # vertices
    "Person": {"riskScore", "riskDirect", "riskInferred", "riskPath"},
    "WatchlistEntity": {"riskScore", "riskDirect"},
    "BankAccount": {"balance", "avgMonthlyBalance", "riskScore", "riskDirect", "riskInferred", "riskPath"},
    "RealProperty": {"circleRateValue", "marketValue", "riskScore"},
    "Address": {"lat", "long"},
    "Transaction": {"amount"},
    "RealEstateTransaction": {"transactionValue", "riskScore"},
    # edges
    "transferredTo": {"amount"},
    "mentionedIn": {"confidence"},
}

JSON_FIELDS = {
    "Person": {"riskReasons"},
    "WatchlistEntity": {"riskReasons"},
    "RealProperty": {"riskReasons"},
    "RealEstateTransaction": {"riskReasons"},
}

BOOLEAN_FIELDS = {
    "Person": {"isSyntheticDuplicate"},
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
        if k in BOOLEAN_FIELDS.get(collection, set()):
            vv = v.strip().lower()
            if vv in {"true", "1", "yes"}:
                out[k] = True
                continue
            if vv in {"false", "0", "no"}:
                out[k] = False
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
    db.collection("Person").add_persistent_index(["panNumber"], sparse=True)
    db.collection("BankAccount").add_persistent_index(["accountNumber"], sparse=True)
    db.collection("RealProperty").add_persistent_index(["surveyNumber"], sparse=True)
    db.collection("Address").add_persistent_index(["district", "state"])
    db.collection("transferredTo").add_persistent_index(["timestamp"])
    db.collection("transferredTo").add_persistent_index(["amount"])
    # Relationship edges should be idempotent per (_from,_to). Events over time should use `accessedFrom`.
    db.collection("hasDigitalLocation").add_persistent_index(["_from", "_to"], unique=True)


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

