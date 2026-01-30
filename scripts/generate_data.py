#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

try:
    from faker import Faker  # type: ignore
except Exception:  # pragma: no cover
    Faker = None  # type: ignore


PAN_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def iso(ts: dt.datetime) -> str:
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=dt.timezone.utc)
    return ts.astimezone(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write_csv(path: Path, fieldnames: List[str], rows: Iterable[Dict[str, Any]]) -> int:
    ensure_dir(path.parent)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        n = 0
        for r in rows:
            w.writerow({k: ("" if v is None else v) for k, v in r.items()})
            n += 1
    return n


def key(prefix: str, seed: int, idx: int) -> str:
    return f"{prefix}_{seed}_{idx:06d}"


def doc_id(collection: str, _key: str) -> str:
    return f"{collection}/{_key}"


def gen_pan(rng: random.Random) -> str:
    letters = "".join(rng.choice(PAN_CHARS) for _ in range(5))
    digits = "".join(str(rng.randint(0, 9)) for _ in range(4))
    last = rng.choice(PAN_CHARS)
    return f"{letters}{digits}{last}"


def masked_aadhaar(rng: random.Random) -> str:
    last4 = "".join(str(rng.randint(0, 9)) for _ in range(4))
    return f"XXXX-XXXX-{last4}"


@dataclass(frozen=True)
class Sizes:
    persons: int
    organizations: int
    watchlist: int
    accounts: int
    properties: int
    addresses: int
    digital_locations: int
    documents: int
    background_transfers: int


SAMPLE = Sizes(
    persons=380,
    organizations=30,
    watchlist=10,
    accounts=450,
    properties=50,
    addresses=200,
    digital_locations=25,
    documents=10,
    background_transfers=1400,
)

DEMO = Sizes(
    persons=8000,
    organizations=600,
    watchlist=200,
    accounts=9000,
    properties=1000,
    addresses=4000,
    digital_locations=500,
    documents=200,
    background_transfers=27000,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate synthetic fraud-intelligence datasets (CSV).")
    p.add_argument("--output", required=True, help="Output directory (e.g., data/sample)")
    p.add_argument("--seed", type=int, default=42, help="Deterministic seed")
    p.add_argument("--size", choices=["sample", "demo"], default="sample")
    p.add_argument("--force", action="store_true", help="Overwrite existing CSVs in output dir")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    out_dir = Path(args.output)
    ensure_dir(out_dir)
    rng = random.Random(args.seed)
    if Faker is None:
        # Minimal fallback if dependencies aren't installed yet.
        class _MiniFaker:
            def __init__(self, seed: int) -> None:
                self._rng = random.Random(seed)

            def name(self) -> str:
                first = ["Amit", "Priya", "Rajesh", "Neha", "Sanjay", "Kiran", "Anita", "Vijay"]
                last = ["Kumar", "Sharma", "Patel", "Gupta", "Singh", "Iyer", "Reddy", "Das"]
                return f"{self._rng.choice(first)} {self._rng.choice(last)}"

            def company(self) -> str:
                base = ["Sunrise", "Lotus", "BluePeak", "Riverstone", "Cedar", "Aster", "Nimbus"]
                suffix = ["Industries", "Holdings", "Trading", "Services", "Ventures"]
                return f"{self._rng.choice(base)} {self._rng.choice(suffix)}"

            def street_address(self) -> str:
                return f"{self._rng.randint(1, 200)} {self._rng.choice(['MG Road','Link Road','Station Rd','Market St'])}"

        faker = _MiniFaker(args.seed)  # type: ignore
    else:
        faker = Faker("en_IN")
        faker.seed_instance(args.seed)

    sizes = SAMPLE if args.size == "sample" else DEMO

    # Guard against accidental overwrite.
    if not args.force and any(out_dir.glob("*.csv")):
        raise SystemExit(f"Refusing to overwrite existing CSVs in {out_dir}. Use --force.")

    now = dt.datetime.now(dt.timezone.utc)

    # ------------------------------------------------------------------
    # Addresses
    # ------------------------------------------------------------------
    districts = ["Mumbai_South", "Thane_West", "Andheri_East", "Bandra_Kurla", "Navi_Mumbai"]
    state = "Maharashtra"

    address_rows: List[Dict[str, Any]] = []
    for i in range(sizes.addresses):
        district = rng.choice(districts)
        # Rough Mumbai lat/long bounds
        lat = rng.uniform(18.88, 19.30)
        lon = rng.uniform(72.77, 73.05)
        address_rows.append(
            {
                "_key": key("addr", args.seed, i),
                "street": faker.street_address(),
                "city": "Mumbai",
                "district": district,
                "state": state,
                "pincode": f"{rng.randint(400001, 400110)}",
                "lat": round(lat, 6),
                "long": round(lon, 6),
            }
        )

    # ------------------------------------------------------------------
    # Digital locations
    # ------------------------------------------------------------------
    def rand_mac() -> str:
        return ":".join(f"{rng.randint(0,255):02x}" for _ in range(6))

    digital_rows: List[Dict[str, Any]] = []
    for i in range(sizes.digital_locations):
        digital_rows.append(
            {
                "_key": key("dig", args.seed, i),
                "ip_address": f"10.{rng.randint(0,255)}.{rng.randint(0,255)}.{rng.randint(1,254)}",
                "device_id": key("device", args.seed, i),
                "mac_address": rand_mac(),
            }
        )

    # Reserve one shared device for mule ring (ensures tests can assert it).
    mule_shared_digital_key = key("dig", args.seed, sizes.digital_locations)
    digital_rows.append(
        {
            "_key": mule_shared_digital_key,
            "ip_address": "10.10.10.10",
            "device_id": f"shared_device_{args.seed}",
            "mac_address": "aa:bb:cc:dd:ee:ff",
        }
    )

    # ------------------------------------------------------------------
    # People
    # ------------------------------------------------------------------
    person_rows: List[Dict[str, Any]] = []
    base_people = sizes.persons
    benami_variations = max(1, int(base_people * 0.05))

    for i in range(base_people):
        pkey = key("person", args.seed, i)
        person_rows.append(
            {
                "_key": pkey,
                "name": faker.name(),
                "pan_number": gen_pan(rng),
                "aadhaar_masked": masked_aadhaar(rng),
                "risk_score": 0,
                "risk_direct": "",
                "risk_inferred": "",
                "risk_path": "",
                "risk_reasons": "",
            }
        )

    # Add Benami variations (duplicate-ish identities, often missing PAN).
    for j in range(benami_variations):
        src = person_rows[j]
        base_name = src["name"]
        parts = base_name.split()
        short_name = f"{parts[0][0]}. {parts[-1]}" if len(parts) >= 2 else base_name
        pkey = key("person", args.seed, base_people + j)
        person_rows.append(
            {
                "_key": pkey,
                "name": short_name,
                "pan_number": "",  # missing PAN
                "aadhaar_masked": masked_aadhaar(rng),
                "risk_score": 0,
                "risk_reasons": json.dumps(["benami_variation"]),
            }
        )

    # ------------------------------------------------------------------
    # Organizations
    # ------------------------------------------------------------------
    org_types = ["Legitimate", "Shell", "UtilityCompany", "Retailer"]
    org_rows: List[Dict[str, Any]] = []
    for i in range(sizes.organizations):
        org_rows.append(
            {
                "_key": key("org", args.seed, i),
                "name": faker.company(),
                "org_type": rng.choice(org_types),
                "risk_score": 0,
            }
        )

    # ------------------------------------------------------------------
    # Watchlist entries (seed risk)
    # ------------------------------------------------------------------
    watchlist_rows: List[Dict[str, Any]] = []
    reasons = ["Wilful Defaulter", "Shell Company Director", "Sanctions List", "Defaulter"]
    for i in range(sizes.watchlist):
        rs = rng.randint(80, 100)
        watchlist_rows.append(
            {
                "_key": key("watch", args.seed, i),
                "name": faker.name(),
                "listing_reason": rng.choice(reasons),
                "risk_score": rs,
                "risk_direct": rs,
                "risk_reasons": json.dumps(["watchlist_seed"]),
            }
        )

    # ------------------------------------------------------------------
    # Bank accounts
    # ------------------------------------------------------------------
    account_types = ["Savings", "Current", "NRE"]
    bank_account_rows: List[Dict[str, Any]] = []
    for i in range(sizes.accounts):
        bank_account_rows.append(
            {
                "_key": key("acct", args.seed, i),
                "account_number": f"{rng.randint(10**11, 10**12 - 1)}",
                "account_type": rng.choice(account_types),
                "balance": round(rng.uniform(5000, 5_000_000), 2),
                "avg_monthly_balance": round(rng.uniform(5000, 2_000_000), 2),
                "risk_score": 0,
            }
        )

    # Preselect fraud anchors (stable + testable)
    mule_count = 50
    hub_account_key = bank_account_rows[10]["_key"]
    mule_account_keys = [bank_account_rows[i]["_key"] for i in range(100, 100 + mule_count)]

    # ------------------------------------------------------------------
    # Ownership edges: person -> bank_account
    # ------------------------------------------------------------------
    has_account_rows: List[Dict[str, Any]] = []
    for i, acct in enumerate(bank_account_rows):
        person = person_rows[i % len(person_rows)]
        has_account_rows.append(
            {
                "_from": doc_id("person", person["_key"]),
                "_to": doc_id("bank_account", acct["_key"]),
                "ownership_type": "Primary",
            }
        )

    # ------------------------------------------------------------------
    # related_to edges (some social ties)
    # ------------------------------------------------------------------
    related_rows: List[Dict[str, Any]] = []
    for i in range(min(100, len(person_rows) // 3)):
        a = person_rows[i]["_key"]
        b = person_rows[i + 1]["_key"]
        related_rows.append(
            {
                "_from": doc_id("person", a),
                "_to": doc_id("person", b),
                "relation_type": "Sibling",
            }
        )

    # ------------------------------------------------------------------
    # Access events: bank_account -> digital_location
    # ------------------------------------------------------------------
    accessed_from_rows: List[Dict[str, Any]] = []
    for acct in bank_account_rows[: min(len(bank_account_rows), 2000 if args.size == "demo" else 200)]:
        if acct["_key"] in mule_account_keys:
            # Mule accounts will get a dedicated shared device edge below.
            continue
        d = rng.choice(digital_rows)
        accessed_from_rows.append(
            {
                "_from": doc_id("bank_account", acct["_key"]),
                "_to": doc_id("digital_location", d["_key"]),
                "access_timestamp": iso(now - dt.timedelta(days=rng.randint(0, 60))),
                "access_type": rng.choice(["Login", "Transaction"]),
            }
        )

    # ------------------------------------------------------------------
    # Fraud scenario A: circular trading (closed loop transfers)
    # ------------------------------------------------------------------
    transferred_to_rows: List[Dict[str, Any]] = []
    cycle_accounts = [bank_account_rows[i]["_key"] for i in [0, 1, 2, 3]]
    cycle_amounts = [3_000_000, 3_000_000, 2_500_000, 2_500_000]  # sum = 11,000,000 (> 1 crore)
    cycle_ts = now - dt.timedelta(days=2)
    for i in range(4):
        src = cycle_accounts[i]
        dst = cycle_accounts[(i + 1) % 4]
        transferred_to_rows.append(
            {
                "_from": doc_id("bank_account", src),
                "_to": doc_id("bank_account", dst),
                "amount": cycle_amounts[i],
                "timestamp": iso(cycle_ts + dt.timedelta(minutes=i * 10)),
                "txn_type": "NEFT",
                "scenario": "cycle",
            }
        )

    # ------------------------------------------------------------------
    # Fraud scenario B: mule ring (50 mules -> 1 hub within 24h, shared device)
    # ------------------------------------------------------------------
    mule_start = now - dt.timedelta(days=1)
    for i, mule_key in enumerate(mule_account_keys):
        # Ensure shared device link (and keep it testable)
        accessed_from_rows.append(
            {
                "_from": doc_id("bank_account", mule_key),
                "_to": doc_id("digital_location", mule_shared_digital_key),
                "access_timestamp": iso(mule_start + dt.timedelta(minutes=i)),
                "access_type": "Transaction",
            }
        )
        transferred_to_rows.append(
            {
                "_from": doc_id("bank_account", mule_key),
                "_to": doc_id("bank_account", hub_account_key),
                "amount": round(rng.uniform(5000, 50_000), 2),
                "timestamp": iso(mule_start + dt.timedelta(minutes=i)),
                "txn_type": "UPI",
                "scenario": "mule",
            }
        )

    # ------------------------------------------------------------------
    # Background transfers (noise)
    # ------------------------------------------------------------------
    for i in range(sizes.background_transfers):
        src = rng.choice(bank_account_rows)["_key"]
        dst = rng.choice(bank_account_rows)["_key"]
        if src == dst:
            continue
        transferred_to_rows.append(
            {
                "_from": doc_id("bank_account", src),
                "_to": doc_id("bank_account", dst),
                "amount": round(rng.uniform(100, 200_000), 2),
                "timestamp": iso(now - dt.timedelta(days=rng.randint(0, 60), minutes=rng.randint(0, 1440))),
                "txn_type": rng.choice(["NEFT", "RTGS", "UPI", "IMPS"]),
                "scenario": "background",
            }
        )

    # ------------------------------------------------------------------
    # Real estate + undervalued property
    # ------------------------------------------------------------------
    property_rows: List[Dict[str, Any]] = []
    real_estate_tx_rows: List[Dict[str, Any]] = []
    registered_sale_rows: List[Dict[str, Any]] = []
    buyer_in_rows: List[Dict[str, Any]] = []
    seller_in_rows: List[Dict[str, Any]] = []

    undervalued_count = max(1, int(sizes.properties * 0.02))

    for i in range(sizes.properties):
        prop_key = key("prop", args.seed, i)
        district = rng.choice(districts)
        circle_rate = rng.randint(5_000_000, 30_000_000)
        is_undervalued = i < undervalued_count
        market_value = circle_rate if is_undervalued else int(circle_rate * rng.uniform(1.2, 2.0))
        risk_score = 35 if is_undervalued else 0
        risk_reasons = json.dumps(["undervalued_property"]) if is_undervalued else ""
        property_rows.append(
            {
                "_key": prop_key,
                "survey_number": f"SVY-{args.seed}-{i:06d}",
                "district": district,
                "state": state,
                "pincode": f"{rng.randint(400001, 400110)}",
                "circle_rate_value": circle_rate,
                "market_value": market_value,
                "risk_score": risk_score,
                "risk_reasons": risk_reasons,
            }
        )

        tx_key = key("retx", args.seed, i)
        tx_value = circle_rate if is_undervalued else market_value
        payment_method = "Mixed" if is_undervalued else "Bank Transfer"
        real_estate_tx_rows.append(
            {
                "_key": tx_key,
                "transaction_value": tx_value,
                "timestamp": iso(now - dt.timedelta(days=rng.randint(0, 180))),
                "payment_method": payment_method,
                "risk_score": 45 if is_undervalued else 0,
                "risk_reasons": json.dumps(["undervalued_transaction"]) if is_undervalued else "",
            }
        )
        registered_sale_rows.append(
            {
                "_from": doc_id("real_property", prop_key),
                "_to": doc_id("real_estate_transaction", tx_key),
            }
        )
        buyer = rng.choice(person_rows)["_key"]
        seller = rng.choice(person_rows)["_key"]
        buyer_in_rows.append({"_from": doc_id("person", buyer), "_to": doc_id("real_estate_transaction", tx_key)})
        seller_in_rows.append({"_from": doc_id("person", seller), "_to": doc_id("real_estate_transaction", tx_key)})

    # ------------------------------------------------------------------
    # Documents (optional evidence)
    # ------------------------------------------------------------------
    document_rows: List[Dict[str, Any]] = []
    mentioned_in_rows: List[Dict[str, Any]] = []
    for i in range(sizes.documents):
        doc_key = key("doc", args.seed, i)
        doc_type = "TitleDeed" if i < (sizes.documents // 2) else "NewsArticle"
        title = f"{doc_type} {i}"
        content = (
            f"Sale deed for property {property_rows[i % len(property_rows)]['survey_number']}."
            if doc_type == "TitleDeed"
            else f"Market rumors suggest {org_rows[i % len(org_rows)]['name']} is involved in layering."
        )
        document_rows.append(
            {
                "_key": doc_key,
                "doc_type": doc_type,
                "title": title,
                "content": content,
                "timestamp": iso(now - dt.timedelta(days=rng.randint(0, 365))),
            }
        )
        # Link a property or org to the doc (GraphRAG placeholder)
        if doc_type == "TitleDeed":
            mentioned_in_rows.append(
                {
                    "_from": doc_id("real_property", property_rows[i % len(property_rows)]["_key"]),
                    "_to": doc_id("document", doc_key),
                    "mention_type": "Direct",
                    "confidence": 1.0,
                }
            )
        else:
            mentioned_in_rows.append(
                {
                    "_from": doc_id("organization", org_rows[i % len(org_rows)]["_key"]),
                    "_to": doc_id("document", doc_key),
                    "mention_type": "Direct",
                    "confidence": 0.7,
                }
            )

    # Placeholder collections for Phase 1 (produced empty)
    transaction_rows: List[Dict[str, Any]] = []
    for i in range(min(100, 0 if args.size == "sample" else 2000)):
        transaction_rows.append(
            {
                "_key": key("txn", args.seed, i),
                "amount": round(rng.uniform(100, 200_000), 2),
                "timestamp": iso(now - dt.timedelta(days=rng.randint(0, 60))),
                "txn_type": rng.choice(["NEFT", "RTGS", "UPI", "IMPS"]),
            }
        )

    golden_rows: List[Dict[str, Any]] = []
    resolved_to_rows: List[Dict[str, Any]] = []
    has_digital_location_rows: List[Dict[str, Any]] = []
    resides_at_rows: List[Dict[str, Any]] = []
    associated_with_rows: List[Dict[str, Any]] = []

    # residences for persons
    for p in person_rows:
        addr = rng.choice(address_rows)["_key"]
        resides_at_rows.append({"_from": doc_id("person", p["_key"]), "_to": doc_id("address", addr)})

    # has_digital_location for mule people (linking a few persons to shared device, useful for ER)
    for i in range(min(20, len(person_rows))):
        if i % 4 == 0:
            has_digital_location_rows.append(
                {
                    "_from": doc_id("person", person_rows[i]["_key"]),
                    "_to": doc_id("digital_location", mule_shared_digital_key),
                }
            )

    # some person -> org associations
    for i in range(min(30, len(person_rows), len(org_rows))):
        associated_with_rows.append(
            {
                "_from": doc_id("person", person_rows[i]["_key"]),
                "_to": doc_id("organization", org_rows[i % len(org_rows)]["_key"]),
                "role": rng.choice(["Director", "Employee", "Partner"]),
            }
        )

    # ------------------------------------------------------------------
    # Write all CSVs
    # ------------------------------------------------------------------
    outputs = [
        ("address.csv", ["_key", "street", "city", "district", "state", "pincode", "lat", "long"], address_rows),
        ("digital_location.csv", ["_key", "ip_address", "device_id", "mac_address"], digital_rows),
        (
            "person.csv",
            ["_key", "name", "pan_number", "aadhaar_masked", "risk_score", "risk_direct", "risk_inferred", "risk_path", "risk_reasons"],
            person_rows,
        ),
        ("organization.csv", ["_key", "name", "org_type", "risk_score"], org_rows),
        ("watchlist_entity.csv", ["_key", "name", "listing_reason", "risk_score", "risk_direct", "risk_reasons"], watchlist_rows),
        ("bank_account.csv", ["_key", "account_number", "account_type", "balance", "avg_monthly_balance", "risk_score"], bank_account_rows),
        (
            "real_property.csv",
            ["_key", "survey_number", "district", "state", "pincode", "circle_rate_value", "market_value", "risk_score", "risk_reasons"],
            property_rows,
        ),
        (
            "real_estate_transaction.csv",
            ["_key", "transaction_value", "timestamp", "payment_method", "risk_score", "risk_reasons"],
            real_estate_tx_rows,
        ),
        ("document.csv", ["_key", "doc_type", "title", "content", "timestamp"], document_rows),
        ("transaction.csv", ["_key", "amount", "timestamp", "txn_type"], transaction_rows),
        ("golden_record.csv", ["_key", "canonical_name"], golden_rows),
        ("has_account.csv", ["_from", "_to", "ownership_type"], has_account_rows),
        ("transferred_to.csv", ["_from", "_to", "amount", "timestamp", "txn_type", "scenario"], transferred_to_rows),
        ("related_to.csv", ["_from", "_to", "relation_type"], related_rows),
        ("associated_with.csv", ["_from", "_to", "role"], associated_with_rows),
        ("resides_at.csv", ["_from", "_to"], resides_at_rows),
        ("accessed_from.csv", ["_from", "_to", "access_timestamp", "access_type"], accessed_from_rows),
        ("has_digital_location.csv", ["_from", "_to"], has_digital_location_rows),
        ("mentioned_in.csv", ["_from", "_to", "mention_type", "confidence"], mentioned_in_rows),
        ("registered_sale.csv", ["_from", "_to"], registered_sale_rows),
        ("buyer_in.csv", ["_from", "_to"], buyer_in_rows),
        ("seller_in.csv", ["_from", "_to"], seller_in_rows),
        ("resolved_to.csv", ["_from", "_to"], resolved_to_rows),
    ]

    counts: Dict[str, int] = {}
    for filename, fields, rows in outputs:
        n = write_csv(out_dir / filename, fields, rows)
        counts[filename] = n

    meta = {
        "seed": args.seed,
        "size": args.size,
        "generated_at": iso(now),
        "counts": counts,
    }
    (out_dir / "metadata.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"Wrote {len(outputs)} CSVs to {out_dir}")


if __name__ == "__main__":
    main()

