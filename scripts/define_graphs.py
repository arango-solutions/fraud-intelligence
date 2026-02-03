#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
import xml.etree.ElementTree as ET
from dataclasses import asdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional

from common import ArangoConfig, apply_config_to_env, get_arango_config, load_dotenv, sanitize_url

try:
    from arango import ArangoClient  # type: ignore
except Exception:  # pragma: no cover
    ArangoClient = None  # type: ignore


ROOT = Path(__file__).resolve().parents[1]
OWL_PATH = ROOT / "ontology" / "fraud-intelligence.owl"

# Phase 1 data collections (OWL conventions)
DATA_VERTICES: List[str] = [
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

DATA_EDGES: List[Dict] = [
    {"edge_collection": "hasAccount", "from_vertex_collections": ["Person", "Organization"], "to_vertex_collections": ["BankAccount"]},
    {"edge_collection": "transferredTo", "from_vertex_collections": ["BankAccount"], "to_vertex_collections": ["BankAccount"]},
    {"edge_collection": "relatedTo", "from_vertex_collections": ["Person"], "to_vertex_collections": ["Person"]},
    {"edge_collection": "associatedWith", "from_vertex_collections": ["Person"], "to_vertex_collections": ["Organization"]},
    {"edge_collection": "residesAt", "from_vertex_collections": ["Person"], "to_vertex_collections": ["Address"]},
    {"edge_collection": "accessedFrom", "from_vertex_collections": ["BankAccount"], "to_vertex_collections": ["DigitalLocation"]},
    {"edge_collection": "hasDigitalLocation", "from_vertex_collections": ["Person"], "to_vertex_collections": ["DigitalLocation"]},
    {"edge_collection": "mentionedIn", "from_vertex_collections": ["Person", "Organization", "RealProperty", "BankAccount"], "to_vertex_collections": ["Document"]},
    {"edge_collection": "registeredSale", "from_vertex_collections": ["RealProperty"], "to_vertex_collections": ["RealEstateTransaction"]},
    {"edge_collection": "buyerIn", "from_vertex_collections": ["Person", "Organization"], "to_vertex_collections": ["RealEstateTransaction"]},
    {"edge_collection": "sellerIn", "from_vertex_collections": ["Person", "Organization"], "to_vertex_collections": ["RealEstateTransaction"]},
    {"edge_collection": "resolvedTo", "from_vertex_collections": ["Person"], "to_vertex_collections": ["GoldenRecord"]},
]

# Ontology graph is created by ArangoRDF (PGT). We do not hard-code its collections
# because ArangoRDF's mapping may evolve (e.g., it uses `Property` as the unified
# collection for ontology properties).


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Define OntologyGraph / DataGraph / KnowledgeGraph in ArangoDB.")
    p.add_argument("--mode", choices=["LOCAL", "REMOTE"], help="Override MODE for Arango connection")
    p.add_argument("--force", action="store_true", help="Re-load ontology vertices/edges (truncate ontology edge collections first)")
    p.add_argument(
        "--with-type-edges",
        action="store_true",
        help="Create KnowledgeGraph instanceOf edges from data vertices to ontology Class nodes (edge collection: instanceOf)",
    )
    return p.parse_args()


def connect(cfg: ArangoConfig):
    if ArangoClient is None:
        raise SystemExit("python-arango not installed. Install: pip install -r requirements.txt")
    client = ArangoClient(hosts=cfg.url)
    db = client.db(cfg.database, username=cfg.username, password=cfg.password)
    return db


def ensure_collection(db, name: str, edge: bool = False) -> None:
    if db.has_collection(name):
        return
    db.create_collection(name, edge=edge)


def upsert_many(col, docs: Iterable[Dict], chunk: int = 2000) -> None:
    buf: List[Dict] = []
    for d in docs:
        buf.append(d)
        if len(buf) >= chunk:
            res = col.import_bulk(buf, on_duplicate="update")
            if isinstance(res, dict) and res.get("errors"):
                raise RuntimeError(f"Bulk import errors in {col.name}: {res}")
            buf = []
    if buf:
        res = col.import_bulk(buf, on_duplicate="update")
        if isinstance(res, dict) and res.get("errors"):
            raise RuntimeError(f"Bulk import errors in {col.name}: {res}")


def load_ontology_as_data(db, force: bool) -> None:
    """
    Load ontology into ArangoDB using ArangoRDF (PGT transformation).

    Rationale:
    - This repo is intended to demonstrate ArangoDB's RDF/semantic capabilities.
    - ArangoRDF's PGT transformation produces a proper property-graph representation
      of the ontology (including rdf:type-driven collection mapping and connected topology).
    """
    if not OWL_PATH.exists():
        raise SystemExit(f"Missing ontology file: {OWL_PATH}")

    try:
        from rdflib import Graph  # type: ignore
        from arango_rdf import ArangoRDF  # type: ignore
    except Exception as e:  # pragma: no cover
        raise SystemExit(
            "Missing dependency for ArangoRDF ontology ingestion. "
            "Install: pip install -r requirements.txt"
        ) from e

    g = Graph()
    # rdflib can parse RDF/XML directly from .owl files
    g.parse(str(OWL_PATH), format="xml")

    adb_rdf = ArangoRDF(db)
    # overwrite_graph is destructive; use `--force` to opt in.
    adb_rdf.rdf_to_arangodb_by_pgt(name="OntologyGraph", rdf_graph=g, overwrite_graph=bool(force))


def ensure_graph(db, name: str, edge_definitions: List[Dict]) -> None:
    if not db.has_graph(name):
        db.create_graph(name, edge_definitions=edge_definitions)
        return
    g = db.graph(name)
    existing = {ed["edge_collection"] for ed in g.edge_definitions()}
    for ed in edge_definitions:
        ec = ed["edge_collection"]
        if ec in existing:
            g.replace_edge_definition(ec, ed["from_vertex_collections"], ed["to_vertex_collections"])
        else:
            g.create_edge_definition(ec, ed["from_vertex_collections"], ed["to_vertex_collections"])


def create_type_edges(db) -> None:
    """
    Create data-to-ontology links (instance → Class).

    NOTE: ArangoRDF uses the `type` edge collection internally for ontology resources.
    To avoid conflicting edge-definition reuse across named graphs, we keep a separate
    edge collection for instance typing.
    """
    ensure_collection(db, "instanceOf", edge=True)
    inst_col = db.collection("instanceOf")

    if not db.has_collection("Class"):
        print("[WARN] Missing 'Class' collection; skipping instanceOf edges")
        return
    class_col = db.collection("Class")

    # Derived edges; safe to rebuild deterministically.
    try:
        inst_col.truncate()
    except Exception:
        # If truncate is not permitted (managed restrictions), fall back to upsert-y import.
        pass

    def resolve_class_id(label: str) -> Optional[str]:
        """
        Prefer ArangoRDF PGT Class nodes (typically have `_uri`/`_label`) and fall back
        to any legacy Class docs (may have `uri`/`label`).
        """
        q = """
FOR c IN Class
  FILTER (HAS(c, "_label") && c._label == @n)
     OR (HAS(c, "label") && c.label == @n)
     OR (HAS(c, "_uri") && LIKE(c._uri, CONCAT("%#", @n), true))
     OR (HAS(c, "uri") && c.uri == CONCAT("#", @n))
  SORT HAS(c, "_uri") DESC, HAS(c, "_label") DESC
  LIMIT 1
  RETURN c._id
"""
        res = list(db.aql.execute(q, bind_vars={"n": label}))
        return res[0] if res else None

    batch: List[Dict] = []
    batch_size = 2000

    for vcoll in DATA_VERTICES:
        if not db.has_collection(vcoll):
            continue

        to_id = resolve_class_id(vcoll)
        if not to_id:
            print(f"[WARN] No ontology Class match for '{vcoll}'; skipping instanceOf edges for this collection")
            continue

        # If a legacy stub Class doc exists (keyed by the local name) but ArangoRDF
        # resolved to a different Class document (typically hash-keyed), remove the stub
        # to avoid a disjoint duplicate Class in the visualizer.
        expected_stub_id = f"Class/{vcoll}"
        if to_id != expected_stub_id:
            try:
                stub = class_col.get(vcoll)
                if stub and ("_uri" not in stub) and ("_label" not in stub) and stub.get("uri") == f"#{vcoll}":
                    class_col.delete(vcoll)
            except Exception:
                pass

        for doc in db.collection(vcoll).all():
            from_id = doc["_id"]
            key = f"{from_id.replace('/', '_')}__{to_id.replace('/', '_')}"
            batch.append({"_key": key, "_from": from_id, "_to": to_id})
            if len(batch) >= batch_size:
                inst_col.import_bulk(batch, on_duplicate="update")
                batch = []

    if batch:
        inst_col.import_bulk(batch, on_duplicate="update")


def main() -> None:
    load_dotenv()
    args = parse_args()

    cfg = get_arango_config(forced_mode=args.mode)
    apply_config_to_env(cfg)
    print(f"mode={cfg.mode} arango={sanitize_url(cfg.url)} db={cfg.database}")

    db = connect(cfg)

    # ArangoRDF (PGT) creates OntologyGraph and will attach edge collections (e.g. domain/range/subClassOf)
    # to that graph. ArangoDB does not allow an edge collection to be used in edge definitions across
    # multiple named graphs simultaneously. Since our KnowledgeGraph also reuses these ontology edge
    # collections, delete the dependent graphs first when forcing a re-load.
    if args.force:
        for gname in ["KnowledgeGraph", "OntologyGraph"]:
            if db.has_graph(gname):
                db.delete_graph(gname, drop_collections=False)

    # Ensure ontology is ingested via ArangoRDF PGT (creates OntologyGraph).
    load_ontology_as_data(db, force=args.force)

    if args.with_type_edges:
        create_type_edges(db)

    # Create the three named graphs.
    # OntologyGraph is created by ArangoRDF; do not override its edge definitions here.
    ensure_graph(db, "DataGraph", DATA_EDGES)
    # Build KnowledgeGraph by reusing the exact ontology edge definitions produced by ArangoRDF
    # (avoids edge-definition conflicts).
    onto_edge_defs: List[Dict] = []
    if db.has_graph("OntologyGraph"):
        onto_edge_defs = db.graph("OntologyGraph").edge_definitions()
    knowledge_edges: List[Dict] = onto_edge_defs + DATA_EDGES
    if args.with_type_edges:
        knowledge_edges = knowledge_edges + [
            {"edge_collection": "instanceOf", "from_vertex_collections": DATA_VERTICES, "to_vertex_collections": ["Class"]}
        ]
    ensure_graph(db, "KnowledgeGraph", knowledge_edges)

    print("Created/updated: OntologyGraph, DataGraph, KnowledgeGraph")


if __name__ == "__main__":
    sys.exit(main())

