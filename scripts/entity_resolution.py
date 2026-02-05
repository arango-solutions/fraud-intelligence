#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import sys
import time
from dataclasses import asdict, dataclass
from typing import Dict, List, Optional, Tuple

from common import apply_config_to_env, get_arango_config, load_dotenv, sanitize_url

try:
    from arango import ArangoClient  # type: ignore
except Exception:  # pragma: no cover
    ArangoClient = None  # type: ignore


@dataclass
class StepResult:
    ok: bool
    detail: str = ""


def connect(arango_url: str, username: str, password: str, db_name: str):
    if ArangoClient is None:  # pragma: no cover
        raise RuntimeError("python-arango not installed")
    client = ArangoClient(hosts=arango_url)
    return client.db(db_name, username=username, password=password)


def ensure_collection(db, name: str, edge: bool) -> None:
    if db.has_collection(name):
        return
    db.create_collection(name, edge=edge)


def ensure_person_overlap(db, overlap_count: int) -> int:
    """
    Create deterministic synthetic duplicate-ish Person docs (idempotent).

    This is strictly data preparation to demonstrate ER; all ER logic remains in the library.
    """
    # 1) Create a deterministic set of duplicate-ish Person documents.
    q_insert = """
LET base = (
  FOR p IN Person
    FILTER p.panNumber != null
    FILTER !STARTS_WITH(p._key, "dup_")
    SORT p._key
    LIMIT @n
    RETURN p
)
FOR p IN base
  LET doc = UNSET(p, ["_id", "_rev"])
  LET dupKey = CONCAT("dup_", p._key)
  INSERT MERGE(
    doc,
    {
      _key: dupKey,
      isSyntheticDuplicate: true,
      duplicateOf: p._id,
      dataSource: "phase2",
      sourceId: dupKey
    }
  ) INTO Person
  OPTIONS { overwriteMode: "ignore" }
  RETURN NEW._key
"""
    created = list(db.aql.execute(q_insert, bind_vars={"n": int(overlap_count)}))

    # 2) Ensure synthetic duplicates are not isolated: copy key relationship edges
    # from the original person to the duplicate (idempotent via UPSERT).
    q_edges = """
FOR d IN Person
  FILTER d.isSyntheticDuplicate == true
  FILTER STARTS_WITH(d._key, "dup_")
  LET origId = d.duplicateOf
  FILTER origId != null

  FOR r IN residesAt
    FILTER r._from == origId
    UPSERT { _from: d._id, _to: r._to }
      INSERT { _from: d._id, _to: r._to }
      UPDATE {}
    IN residesAt

  FOR aw IN associatedWith
    FILTER aw._from == origId
    UPSERT { _from: d._id, _to: aw._to, role: aw.role }
      INSERT MERGE(
        { _from: d._id, _to: aw._to },
        UNSET(aw, ["_id","_key","_rev","_from","_to"])
      )
      UPDATE {}
    IN associatedWith

  FOR hdl IN hasDigitalLocation
    FILTER hdl._from == origId
    UPSERT { _from: d._id, _to: hdl._to }
      INSERT { _from: d._id, _to: hdl._to }
      UPDATE {}
    IN hasDigitalLocation

  RETURN 1
"""
    # Run repair even if no new duplicates were created (fixes earlier runs).
    list(db.aql.execute(q_edges))

    # 3) For synthetic duplicates, create separate BankAccounts (idempotent) and link via hasAccount.
    #
    # Rationale:
    # - `hasAccount` is a relationship and should remain idempotent.
    # - For the demo, duplicate customer profiles can have distinct accounts (account fragmentation / proxy behavior),
    #   which makes “before vs after” ER more visually impactful.
    #
    # NOTE: We skip "Victor Tella" here because we assign his two aliases to specific cycle accounts below.
    q_dup_accounts = """
FOR d IN Person
  FILTER d.isSyntheticDuplicate == true
  FILTER STARTS_WITH(d._key, "dup_")
  FILTER d.name != "Victor Tella"

  LET acctKey = CONCAT("dup_acct_", SUBSTRING(d._key, 4))
  LET acctId = CONCAT("BankAccount/", acctKey)
  LET acctNum = CONCAT("DUP-", SUBSTRING(MD5(d._id), 0, 12))

  INSERT {
    _key: acctKey,
    accountNumber: acctNum,
    accountType: "Savings",
    balance: 0,
    avgMonthlyBalance: 0,
    dataSource: "phase2",
    sourceId: acctKey
  } INTO BankAccount
  OPTIONS { overwriteMode: "ignore" }

  UPSERT { _from: d._id, _to: acctId, ownershipType: "Primary" }
    INSERT {
      _key: MD5(CONCAT_SEPARATOR("|", d._id, acctId, "Primary")),
      _from: d._id,
      _to: acctId,
      ownershipType: "Primary"
    }
    UPDATE {}
  IN hasAccount

  RETURN 1
"""
    list(db.aql.execute(q_dup_accounts))

    # 4) Demo-specific: ensure the two "Victor Tella" aliases have separate accounts that participate
    # in a directed cycle, so the Visualizer canvas action can detect cycles from that account without
    # relying on the generator "cycle" tag.
    q_victor_remove = """
WITH Person, hasAccount
LET victors = (
  FOR p IN Person
    FILTER p.name == "Victor Tella"
    SORT p._key ASC
    LIMIT 2
    RETURN p._id
)
FILTER LENGTH(victors) == 2

FOR ha IN hasAccount
  FILTER ha._from IN victors
  REMOVE ha IN hasAccount
  RETURN 1
"""
    list(db.aql.execute(q_victor_remove))

    q_victor_insert = """
WITH Person, hasAccount
LET victors = (
  FOR p IN Person
    FILTER p.name == "Victor Tella"
    SORT p._key ASC
    LIMIT 2
    RETURN p._id
)
FILTER LENGTH(victors) == 2

LET a1 = "BankAccount/acct_42_000000"
LET a2 = "BankAccount/acct_42_000001"

FOR pair IN [
  { pid: victors[0], acct: a1 },
  { pid: victors[1], acct: a2 }
]
  UPSERT { _from: pair.pid, _to: pair.acct, ownershipType: "Primary" }
    INSERT {
      _key: MD5(CONCAT_SEPARATOR("|", pair.pid, pair.acct, "Primary")),
      _from: pair.pid,
      _to: pair.acct,
      ownershipType: "Primary"
    }
    UPDATE {}
  IN hasAccount

  RETURN 1
"""
    list(db.aql.execute(q_victor_insert))

    # Clean up any pre-existing duplicate edges produced by earlier runs.
    # Keep the lexicographically smallest _key within each equivalence class.
    q_dedupe = """
// Deduplicate associatedWith for dup people by (_from,_to,role)
FOR g IN (
  FOR e IN associatedWith
    FILTER STARTS_WITH(e._from, "Person/dup_")
    COLLECT f = e._from, t = e._to, r = e.role INTO grp = e
    FILTER LENGTH(grp) > 1
    LET keys = (FOR x IN grp SORT x._key ASC RETURN x._key)
    LET keep = FIRST(keys)
    FOR k IN keys
      FILTER k != keep
      REMOVE { _key: k } IN associatedWith
    RETURN 1
)
RETURN SUM(g)
"""
    list(db.aql.execute(q_dedupe))

    return len(created)


def run_er(
    *,
    db,
    blocking_fields: List[str],
    similarity_field_weights: Dict[str, float],
    similarity_threshold: float,
    similarity_edge_collection: str,
    cluster_collection: str,
    golden_collection: str,
    resolved_edge_collection: str,
    min_cluster_size: int,
) -> Dict[str, int]:
    # IMPORTANT: this script is named `entity_resolution.py`, which would otherwise
    # shadow the installed `entity_resolution` package (the ER library). Ensure
    # the scripts directory is not the first import path before importing.
    from pathlib import Path

    scripts_dir = str(Path(__file__).resolve().parent)
    if sys.path and os.path.abspath(sys.path[0]) == os.path.abspath(scripts_dir):
        sys.path.append(sys.path.pop(0))

    import entity_resolution as er  # late import so requirements are clear

    ensure_collection(db, similarity_edge_collection, edge=True)
    ensure_collection(db, cluster_collection, edge=False)
    ensure_collection(db, golden_collection, edge=False)
    ensure_collection(db, resolved_edge_collection, edge=True)

    # 1) Blocking: candidate pairs (keys)
    blocking = er.CollectBlockingStrategy(
        db=db,
        collection="Person",
        blocking_fields=blocking_fields,
        min_block_size=2,
        max_block_size=5000,
    )
    raw_candidates = list(blocking.generate_candidates())
    candidate_pairs: List[Tuple[str, str]] = []
    for c in raw_candidates:
        # CollectBlockingStrategy typically returns dicts with doc keys
        if isinstance(c, dict):
            k1 = c.get("doc1_key") or c.get("key1")
            k2 = c.get("doc2_key") or c.get("key2")
            if k1 and k2:
                candidate_pairs.append((str(k1), str(k2)))

    # 2) Similarity scoring
    sim = er.BatchSimilarityService(
        db=db,
        collection="Person",
        field_weights=similarity_field_weights,
        similarity_algorithm="jaro_winkler",
    )
    matches = sim.compute_similarities(candidate_pairs=candidate_pairs, threshold=float(similarity_threshold))

    # 3) Persist similarity edges
    edge_service = er.SimilarityEdgeService(
        db=db,
        edge_collection=similarity_edge_collection,
        vertex_collection="Person",
        use_deterministic_keys=True,
    )
    edges_created = edge_service.create_edges(
        matches=matches,
        metadata={
            "method": "phase2_er",
            "algorithm": "weighted_field_similarity:jaro_winkler",
            "threshold": float(similarity_threshold),
        },
        bidirectional=True,
    )

    # 4) Clustering -> cluster_collection
    clustering = er.WCCClusteringService(
        db=db,
        edge_collection=similarity_edge_collection,
        cluster_collection=cluster_collection,
        vertex_collection="Person",
        min_cluster_size=int(min_cluster_size),
        use_bulk_fetch=True,
    )
    clusters = clustering.cluster(store_results=True, truncate_existing=True)

    # 5) Golden records + resolvedTo edges (library capability)
    persistence = er.GoldenRecordPersistenceService(
        db=db,
        source_collection="Person",
        cluster_collection=cluster_collection,
        golden_collection=golden_collection,
        resolved_edge_collection=resolved_edge_collection,
        include_fields=list(similarity_field_weights.keys()),
        include_provenance=False,
    )
    persisted = persistence.run(run_id=None, min_cluster_size=int(min_cluster_size))

    return {
        "candidate_pairs": len(candidate_pairs),
        "matches": len(matches),
        "similarity_edges_written": int(edges_created),
        "clusters": len(clusters),
        "golden_records_upserted": int(persisted.get("golden_records_upserted", 0)),
        "resolved_edges_upserted": int(persisted.get("resolved_edges_upserted", 0)),
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Phase 2: Entity Resolution for Person -> GoldenRecord.")
    p.add_argument("--mode", choices=["LOCAL", "REMOTE"], default=None, help="Override MODE from .env")
    p.add_argument("--ensure-overlap", action="store_true", help="Create synthetic Person duplicates (idempotent).")
    p.add_argument("--overlap-count", type=int, default=50, help="Number of Person records to duplicate.")
    p.add_argument("--blocking-fields", default="panNumber", help="Comma-separated blocking fields.")
    p.add_argument("--similarity-threshold", type=float, default=0.95, help="Similarity threshold (0..1).")
    p.add_argument("--similarity-edge-collection", default="similarToPerson", help="Edge collection for similarity.")
    p.add_argument("--cluster-collection", default="personClusters", help="Document collection for cluster results.")
    p.add_argument("--golden-collection", default="GoldenRecord", help="Golden record vertex collection.")
    p.add_argument("--resolved-edge-collection", default="resolvedTo", help="Edge collection linking Person -> GoldenRecord.")
    p.add_argument("--min-cluster-size", type=int, default=2, help="Minimum cluster size for persistence.")
    return p.parse_args()


def main() -> None:
    load_dotenv()
    args = parse_args()

    cfg = get_arango_config(forced_mode=args.mode)
    apply_config_to_env(cfg)

    if ArangoClient is None:  # pragma: no cover
        raise SystemExit("python-arango not installed")

    if not cfg.url:
        raise SystemExit("ARANGO_URL is not set")

    # Never print secrets; sanitize URL.
    print(f"[phase2] mode={cfg.mode} arango={sanitize_url(cfg.url)} db={cfg.database}")

    try:
        db = connect(cfg.url, cfg.username, cfg.password, cfg.database)
    except Exception as e:
        raise SystemExit(f"failed to connect to arango: {e}")

    started = time.time()
    created_dups = 0
    if args.ensure_overlap:
        created_dups = ensure_person_overlap(db, overlap_count=args.overlap_count)

    blocking_fields = [f.strip() for f in (args.blocking_fields or "").split(",") if f.strip()]
    if not blocking_fields:
        raise SystemExit("blocking fields cannot be empty")

    # Field weights: favor exact identifier when present.
    # Keep this conservative for demo: panNumber dominates, name is a small tie-breaker.
    weights: Dict[str, float] = {}
    if "panNumber" in blocking_fields:
        weights["panNumber"] = 0.9
        weights["name"] = 0.1
    else:
        # Fallback: whatever they passed.
        for f in blocking_fields:
            weights[f] = 1.0

    out = run_er(
        db=db,
        blocking_fields=blocking_fields,
        similarity_field_weights=weights,
        similarity_threshold=args.similarity_threshold,
        similarity_edge_collection=args.similarity_edge_collection,
        cluster_collection=args.cluster_collection,
        golden_collection=args.golden_collection,
        resolved_edge_collection=args.resolved_edge_collection,
        min_cluster_size=args.min_cluster_size,
    )

    out["synthetic_duplicates_created"] = int(created_dups)
    out["runtime_seconds"] = round(time.time() - started, 2)
    print(out)


if __name__ == "__main__":
    main()

