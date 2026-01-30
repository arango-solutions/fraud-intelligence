import csv
import json
from pathlib import Path


def _data_dir() -> Path:
    # Default to repo's committed sample dataset
    return Path(__file__).resolve().parents[1] / "data" / "sample"


def _read_csv(name: str):
    path = _data_dir() / f"{name}.csv"
    assert path.exists(), f"missing {path}"
    with path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def test_cycle_exists():
    edges = _read_csv("transferred_to")
    # detect a directed cycle via simple DFS on a limited subset
    adj = {}
    for e in edges:
        if e.get("scenario") == "cycle":
            adj.setdefault(e["_from"], set()).add(e["_to"])

    assert adj, "no cycle-labeled transfers found"

    visited = set()
    stack = set()

    def dfs(u):
        visited.add(u)
        stack.add(u)
        for v in adj.get(u, []):
            if v not in visited:
                if dfs(v):
                    return True
            elif v in stack:
                return True
        stack.remove(u)
        return False

    assert any(dfs(u) for u in list(adj.keys())), "expected at least one directed cycle"


def test_mule_hub_exists_and_shared_device():
    edges = _read_csv("transferred_to")
    mule_edges = [e for e in edges if e.get("scenario") == "mule"]
    assert len(mule_edges) >= 50, "expected >= 50 mule transfers"

    # hub is the most common _to among mule edges
    counts = {}
    for e in mule_edges:
        counts[e["_to"]] = counts.get(e["_to"], 0) + 1
    hub, hub_in = max(counts.items(), key=lambda kv: kv[1])
    assert hub_in >= 50, "expected a hub receiving >= 50 transfers"

    mule_sources = {e["_from"] for e in mule_edges}

    accessed = _read_csv("accessed_from")
    # account -> digital_location (only for mule sources)
    mule_access = [e for e in accessed if e["_from"] in mule_sources]
    assert mule_access, "expected accessed_from edges for mule accounts"

    targets = {e["_to"] for e in mule_access}
    assert len(targets) == 1, f"expected shared device/ip; got {len(targets)} distinct digital locations"


def test_undervalued_property_exists():
    props = _read_csv("real_property")
    reg = _read_csv("registered_sale")
    txs = {t["_key"]: t for t in _read_csv("real_estate_transaction")}

    # build property -> tx key
    prop_to_tx = {}
    for e in reg:
        # _from: real_property/<key>, _to: real_estate_transaction/<key>
        prop_key = e["_from"].split("/", 1)[1]
        tx_key = e["_to"].split("/", 1)[1]
        prop_to_tx[prop_key] = tx_key

    found = False
    for p in props:
        tx_key = prop_to_tx.get(p["_key"])
        if not tx_key:
            continue
        tx = txs.get(tx_key)
        if not tx:
            continue
        try:
            circle = float(p["circle_rate_value"])
            txn_val = float(tx["transaction_value"])
        except Exception:
            continue
        if txn_val <= circle:
            found = True
            break

    assert found, "expected at least one undervalued property transaction (transaction_value <= circle_rate_value)"

