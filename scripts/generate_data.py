#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
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

def edge_key_md5(*parts: Any) -> str:
    """
    Deterministic edge key.
    Use md5 so keys are compact and AQL-friendly (MD5() can reproduce the same key).
    """
    s = "|".join("" if p is None else str(p) for p in parts)
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def dedupe_edges(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    De-duplicate edges by `_key` while preserving order.
    """
    seen = set()
    out: List[Dict[str, Any]] = []
    for r in rows:
        k = r.get("_key")
        if not k:
            continue
        if k in seen:
            continue
        seen.add(k)
        out.append(r)
    return out


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

    # Use a deterministic "base time" so generated CSVs are stable for a given seed.
    # This prevents `data/sample/` from changing on every run.
    now = dt.datetime(2026, 1, 1, tzinfo=dt.timezone.utc) + dt.timedelta(seconds=args.seed)

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
                "ipAddress": f"10.{rng.randint(0,255)}.{rng.randint(0,255)}.{rng.randint(1,254)}",
                "deviceId": key("device", args.seed, i),
                "macAddress": rand_mac(),
            }
        )

    # Reserve one shared device for mule ring (ensures tests can assert it).
    mule_shared_digital_key = key("dig", args.seed, sizes.digital_locations)
    digital_rows.append(
        {
            "_key": mule_shared_digital_key,
            "ipAddress": "10.10.10.10",
            "deviceId": f"shared_device_{args.seed}",
            "macAddress": "aa:bb:cc:dd:ee:ff",
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
                "panNumber": gen_pan(rng),
                "aadhaarMasked": masked_aadhaar(rng),
                "isSyntheticDuplicate": False,
                "riskScore": 0,
                "riskDirect": "",
                "riskInferred": "",
                "riskPath": "",
                "riskReasons": "",
            }
        )

    # Deterministic demo anchor: Victor Tella (two aliases) for Use Case 1.
    # We place them at the beginning so their owned accounts are stable and easy to find.
    # Both are marked as synthetic duplicates so the investigator query can filter on it.
    if len(person_rows) >= 2:
        shared_pan = gen_pan(rng)
        person_rows[0].update(
            {
                "name": "Victor Tella",
                "panNumber": shared_pan,
                "isSyntheticDuplicate": True,
            }
        )
        person_rows[1].update(
            {
                "name": "Victor Tella",
                "panNumber": shared_pan,
                "isSyntheticDuplicate": True,
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
                "panNumber": "",  # missing PAN
                "aadhaarMasked": masked_aadhaar(rng),
                "isSyntheticDuplicate": True,
                "riskScore": 0,
                "riskReasons": json.dumps(["benami_variation"]),
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
                "orgType": rng.choice(org_types),
                "riskScore": 0,
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
                "listingReason": rng.choice(reasons),
                "riskScore": rs,
                "riskDirect": rs,
                "riskReasons": json.dumps(["watchlist_seed"]),
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
                "accountNumber": f"{rng.randint(10**11, 10**12 - 1)}",
                "accountType": rng.choice(account_types),
                "balance": round(rng.uniform(5000, 5_000_000), 2),
                "avgMonthlyBalance": round(rng.uniform(5000, 2_000_000), 2),
                "riskScore": 0,
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
        _from = doc_id("Person", person["_key"])
        _to = doc_id("BankAccount", acct["_key"])
        has_account_rows.append(
            {
                "_key": edge_key_md5(_from, _to, "Primary"),
                "_from": _from,
                "_to": _to,
                "ownershipType": "Primary",
            }
        )

    # ------------------------------------------------------------------
    # related_to edges (some social ties)
    # ------------------------------------------------------------------
    related_rows: List[Dict[str, Any]] = []
    for i in range(min(100, len(person_rows) // 3)):
        a = person_rows[i]["_key"]
        b = person_rows[i + 1]["_key"]
        _a = doc_id("Person", a)
        _b = doc_id("Person", b)
        left, right = sorted([_a, _b])
        related_rows.append(
            {
                "_key": edge_key_md5(left, right, "Sibling"),
                "_from": _a,
                "_to": _b,
                "relationType": "Sibling",
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
        _from = doc_id("BankAccount", acct["_key"])
        _to = doc_id("DigitalLocation", d["_key"])
        ts = iso(now - dt.timedelta(days=rng.randint(0, 60)))
        at = rng.choice(["Login", "Transaction"])
        accessed_from_rows.append(
            {
                "_key": edge_key_md5(_from, _to, ts, at),
                "_from": _from,
                "_to": _to,
                "accessTimestamp": ts,
                "accessType": at,
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
        _from = doc_id("BankAccount", src)
        _to = doc_id("BankAccount", dst)
        ts = iso(cycle_ts + dt.timedelta(minutes=i * 10))
        transferred_to_rows.append(
            {
                "_key": edge_key_md5(_from, _to, ts, cycle_amounts[i], "NEFT", "cycle"),
                "_from": _from,
                "_to": _to,
                "amount": cycle_amounts[i],
                "timestamp": ts,
                "txnType": "NEFT",
                "scenario": "cycle",
            }
        )

    # ------------------------------------------------------------------
    # Fraud scenario B: mule ring (50 mules -> 1 hub within 24h, shared device)
    # ------------------------------------------------------------------
    mule_start = now - dt.timedelta(days=1)
    for i, mule_key in enumerate(mule_account_keys):
        # Ensure shared device link (and keep it testable)
        _from = doc_id("BankAccount", mule_key)
        _to = doc_id("DigitalLocation", mule_shared_digital_key)
        ts = iso(mule_start + dt.timedelta(minutes=i))
        accessed_from_rows.append(
            {
                "_key": edge_key_md5(_from, _to, ts, "Transaction"),
                "_from": _from,
                "_to": _to,
                "accessTimestamp": ts,
                "accessType": "Transaction",
            }
        )
        _to_acct = doc_id("BankAccount", hub_account_key)
        amt = round(rng.uniform(5000, 50_000), 2)
        transferred_to_rows.append(
            {
                "_key": edge_key_md5(_from, _to_acct, ts, amt, "UPI", "mule"),
                "_from": _from,
                "_to": _to_acct,
                "amount": amt,
                "timestamp": ts,
                "txnType": "UPI",
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
        _from = doc_id("BankAccount", src)
        _to = doc_id("BankAccount", dst)
        ts = iso(now - dt.timedelta(days=rng.randint(0, 60), minutes=rng.randint(0, 1440)))
        txn_type = rng.choice(["NEFT", "RTGS", "UPI", "IMPS"])
        amt = round(rng.uniform(100, 200_000), 2)
        transferred_to_rows.append(
            {
                "_key": edge_key_md5(_from, _to, ts, amt, txn_type, "background"),
                "_from": _from,
                "_to": _to,
                "amount": amt,
                "timestamp": ts,
                "txnType": txn_type,
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

    # Ensure the sample dataset contains enough "circle rate evasion" examples
    # to make the demo query return multiple rows.
    undervalued_count = max(5, int(sizes.properties * 0.02))

    for i in range(sizes.properties):
        prop_key = key("prop", args.seed, i)
        district = rng.choice(districts)
        circle_rate = rng.randint(5_000_000, 30_000_000)
        is_undervalued = i < undervalued_count
        # Market value is typically higher than the government minimum circle rate.
        market_value = int(circle_rate * rng.uniform(1.2, 2.0))
        risk_score = 35 if is_undervalued else 0
        risk_reasons = json.dumps(["undervalued_property"]) if is_undervalued else ""
        property_rows.append(
            {
                "_key": prop_key,
                "surveyNumber": f"SVY-{args.seed}-{i:06d}",
                "district": district,
                "state": state,
                "pincode": f"{rng.randint(400001, 400110)}",
                "circleRateValue": circle_rate,
                "marketValue": market_value,
                "riskScore": risk_score,
                "riskReasons": risk_reasons,
            }
        )

        tx_key = key("retx", args.seed, i)
        # Circle-rate evasion: transaction recorded below circle rate (e.g., "cash component").
        # Non-undervalued transactions are recorded near market value.
        tx_value = int(circle_rate * rng.uniform(0.6, 0.95)) if is_undervalued else market_value
        payment_method = "Mixed" if is_undervalued else "Bank Transfer"
        real_estate_tx_rows.append(
            {
                "_key": tx_key,
                "transactionValue": tx_value,
                "timestamp": iso(now - dt.timedelta(days=rng.randint(0, 180))),
                "paymentMethod": payment_method,
                "riskScore": 45 if is_undervalued else 0,
                "riskReasons": json.dumps(["undervalued_transaction"]) if is_undervalued else "",
            }
        )
        registered_sale_rows.append(
            {
                "_key": edge_key_md5(doc_id("RealProperty", prop_key), doc_id("RealEstateTransaction", tx_key)),
                "_from": doc_id("RealProperty", prop_key),
                "_to": doc_id("RealEstateTransaction", tx_key),
            }
        )
        buyer = rng.choice(person_rows)["_key"]
        seller = rng.choice(person_rows)["_key"]
        b_from = doc_id("Person", buyer)
        s_from = doc_id("Person", seller)
        tx_to = doc_id("RealEstateTransaction", tx_key)
        buyer_in_rows.append({"_key": edge_key_md5(b_from, tx_to), "_from": b_from, "_to": tx_to})
        seller_in_rows.append({"_key": edge_key_md5(s_from, tx_to), "_from": s_from, "_to": tx_to})

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
            f"Sale deed for property {property_rows[i % len(property_rows)]['surveyNumber']}."
            if doc_type == "TitleDeed"
            else f"Market rumors suggest {org_rows[i % len(org_rows)]['name']} is involved in layering."
        )
        document_rows.append(
            {
                "_key": doc_key,
                "docType": doc_type,
                "title": title,
                "content": content,
                "timestamp": iso(now - dt.timedelta(days=rng.randint(0, 365))),
            }
        )
        # Link a property or org to the doc (GraphRAG placeholder)
        if doc_type == "TitleDeed":
            mentioned_in_rows.append(
                {
                    "_key": edge_key_md5(
                        doc_id("RealProperty", property_rows[i % len(property_rows)]["_key"]),
                        doc_id("Document", doc_key),
                        "Direct",
                    ),
                    "_from": doc_id("RealProperty", property_rows[i % len(property_rows)]["_key"]),
                    "_to": doc_id("Document", doc_key),
                    "mentionType": "Direct",
                    "confidence": 1.0,
                }
            )
        else:
            mentioned_in_rows.append(
                {
                    "_key": edge_key_md5(
                        doc_id("Organization", org_rows[i % len(org_rows)]["_key"]),
                        doc_id("Document", doc_key),
                        "Direct",
                    ),
                    "_from": doc_id("Organization", org_rows[i % len(org_rows)]["_key"]),
                    "_to": doc_id("Document", doc_key),
                    "mentionType": "Direct",
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
                "txnType": rng.choice(["NEFT", "RTGS", "UPI", "IMPS"]),
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
        _from = doc_id("Person", p["_key"])
        _to = doc_id("Address", addr)
        resides_at_rows.append({"_key": edge_key_md5(_from, _to), "_from": _from, "_to": _to})

    # Emit only Address rows that are actually referenced.
    # This prevents "orphan" Address nodes with no edges in the graph visualizer.
    used_address_ids = {e["_to"] for e in resides_at_rows}
    address_rows = [a for a in address_rows if doc_id("Address", a["_key"]) in used_address_ids]

    # has_digital_location for mule people (linking a few persons to shared device, useful for ER)
    for i in range(min(20, len(person_rows))):
        if i % 4 == 0:
            _from = doc_id("Person", person_rows[i]["_key"])
            _to = doc_id("DigitalLocation", mule_shared_digital_key)
            has_digital_location_rows.append(
                {
                    "_key": edge_key_md5(_from, _to),
                    "_from": _from,
                    "_to": _to,
                }
            )

    # some person -> org associations
    for i in range(min(30, len(person_rows), len(org_rows))):
        _from = doc_id("Person", person_rows[i]["_key"])
        _to = doc_id("Organization", org_rows[i % len(org_rows)]["_key"])
        role = rng.choice(["Director", "Employee", "Partner"])
        associated_with_rows.append(
            {
                "_key": edge_key_md5(_from, _to, role),
                "_from": _from,
                "_to": _to,
                "role": role,
            }
        )

    # ------------------------------------------------------------------
    # Write all CSVs
    # ------------------------------------------------------------------
    outputs = [
        ("Address.csv", ["_key", "street", "city", "district", "state", "pincode", "lat", "long"], address_rows),
        ("DigitalLocation.csv", ["_key", "ipAddress", "deviceId", "macAddress"], digital_rows),
        (
            "Person.csv",
            [
                "_key",
                "name",
                "panNumber",
                "aadhaarMasked",
                "isSyntheticDuplicate",
                "riskScore",
                "riskDirect",
                "riskInferred",
                "riskPath",
                "riskReasons",
            ],
            person_rows,
        ),
        ("Organization.csv", ["_key", "name", "orgType", "riskScore"], org_rows),
        ("WatchlistEntity.csv", ["_key", "name", "listingReason", "riskScore", "riskDirect", "riskReasons"], watchlist_rows),
        ("BankAccount.csv", ["_key", "accountNumber", "accountType", "balance", "avgMonthlyBalance", "riskScore"], bank_account_rows),
        (
            "RealProperty.csv",
            ["_key", "surveyNumber", "district", "state", "pincode", "circleRateValue", "marketValue", "riskScore", "riskReasons"],
            property_rows,
        ),
        (
            "RealEstateTransaction.csv",
            ["_key", "transactionValue", "timestamp", "paymentMethod", "riskScore", "riskReasons"],
            real_estate_tx_rows,
        ),
        ("Document.csv", ["_key", "docType", "title", "content", "timestamp"], document_rows),
        ("Transaction.csv", ["_key", "amount", "timestamp", "txnType"], transaction_rows),
        ("GoldenRecord.csv", ["_key", "canonicalName"], golden_rows),
        ("hasAccount.csv", ["_key", "_from", "_to", "ownershipType"], dedupe_edges(has_account_rows)),
        ("transferredTo.csv", ["_key", "_from", "_to", "amount", "timestamp", "txnType", "scenario"], dedupe_edges(transferred_to_rows)),
        ("relatedTo.csv", ["_key", "_from", "_to", "relationType"], dedupe_edges(related_rows)),
        ("associatedWith.csv", ["_key", "_from", "_to", "role"], dedupe_edges(associated_with_rows)),
        ("residesAt.csv", ["_key", "_from", "_to"], dedupe_edges(resides_at_rows)),
        ("accessedFrom.csv", ["_key", "_from", "_to", "accessTimestamp", "accessType"], dedupe_edges(accessed_from_rows)),
        ("hasDigitalLocation.csv", ["_key", "_from", "_to"], dedupe_edges(has_digital_location_rows)),
        ("mentionedIn.csv", ["_key", "_from", "_to", "mentionType", "confidence"], dedupe_edges(mentioned_in_rows)),
        ("registeredSale.csv", ["_key", "_from", "_to"], dedupe_edges(registered_sale_rows)),
        ("buyerIn.csv", ["_key", "_from", "_to"], dedupe_edges(buyer_in_rows)),
        ("sellerIn.csv", ["_key", "_from", "_to"], dedupe_edges(seller_in_rows)),
        ("resolvedTo.csv", ["_from", "_to"], resolved_to_rows),
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

