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

# Ontology-as-data collections (for OntologyGraph / KnowledgeGraph)
ONTO_VERTICES: List[str] = ["Class", "ObjectProperty", "DatatypeProperty", "Ontology"]
ONTO_EDGE_DEFS: List[Dict] = [
    {"edge_collection": "domain", "from_vertex_collections": ["ObjectProperty", "DatatypeProperty"], "to_vertex_collections": ["Class"]},
    {"edge_collection": "range", "from_vertex_collections": ["ObjectProperty"], "to_vertex_collections": ["Class"]},
    {"edge_collection": "subClassOf", "from_vertex_collections": ["Class"], "to_vertex_collections": ["Class"]},
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Define OntologyGraph / DataGraph / KnowledgeGraph in ArangoDB.")
    p.add_argument("--mode", choices=["LOCAL", "REMOTE"], help="Override MODE for Arango connection")
    p.add_argument("--force", action="store_true", help="Re-load ontology vertices/edges (truncate ontology edge collections first)")
    p.add_argument(
        "--with-type-edges",
        action="store_true",
        help="Create KnowledgeGraph type edges from data vertices to Class nodes (edge collection: type)",
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
            col.import_bulk(buf, overwrite=True)
            buf = []
    if buf:
        col.import_bulk(buf, overwrite=True)


def load_ontology_as_data(db, force: bool) -> None:
    """
    Load a minimal ontology-as-data representation:
    - Classes → `Class`
    - ObjectProperties → `ObjectProperty`
    - DatatypeProperties → `DatatypeProperty`
    - Domain/range/subClassOf edges
    """
    for v in ONTO_VERTICES:
        ensure_collection(db, v, edge=False)
    for e in ["domain", "range", "subClassOf", "type"]:
        # `type` is optional (used only when --with-type-edges)
        ensure_collection(db, e, edge=True)

    if force:
        for e in ["domain", "range", "subClassOf", "type"]:
            if db.has_collection(e):
                db.collection(e).truncate()

    if not OWL_PATH.exists():
        raise SystemExit(f"Missing ontology file: {OWL_PATH}")

    ns = {
        "owl": "http://www.w3.org/2002/07/owl#",
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    }
    tree = ET.parse(str(OWL_PATH))
    root = tree.getroot()

    def local_name(uri: str) -> str:
        # handles "#Foo" and "...#Foo"
        if "#" in uri:
            return uri.split("#", 1)[1]
        return uri.rsplit("/", 1)[-1]

    # Ontology singleton
    ensure_collection(db, "Ontology", edge=False)
    db.collection("Ontology").import_bulk(
        [{"_key": "fraud-intelligence", "label": "Fraud Intelligence Ontology", "uri": "http://www.semanticweb.org/fraud-intelligence#"}],
        overwrite=True,
    )

    # Classes
    classes = []
    subclasses: List[Dict] = []
    for cls in root.findall(".//owl:Class", ns):
        about = cls.attrib.get(f"{{{ns['rdf']}}}about")
        if not about:
            continue
        name = local_name(about)
        classes.append({"_key": name, "label": name, "uri": about})
        for sc in cls.findall("./rdfs:subClassOf", ns):
            res = sc.attrib.get(f"{{{ns['rdf']}}}resource")
            if not res:
                continue
            parent = local_name(res)
            subclasses.append({"_from": f"Class/{name}", "_to": f"Class/{parent}"})

    upsert_many(db.collection("Class"), classes)
    upsert_many(db.collection("subClassOf"), subclasses)

    # ObjectProperties and DatatypeProperties
    obj_props = []
    dt_props = []
    domains: List[Dict] = []
    ranges: List[Dict] = []

    for op in root.findall(".//owl:ObjectProperty", ns):
        about = op.attrib.get(f"{{{ns['rdf']}}}about")
        if not about:
            continue
        name = local_name(about)
        obj_props.append({"_key": name, "label": name, "uri": about})
        for d in op.findall("./rdfs:domain", ns):
            res = d.attrib.get(f"{{{ns['rdf']}}}resource")
            if res:
                domains.append({"_from": f"ObjectProperty/{name}", "_to": f"Class/{local_name(res)}"})
        for r in op.findall("./rdfs:range", ns):
            res = r.attrib.get(f"{{{ns['rdf']}}}resource")
            if res:
                ranges.append({"_from": f"ObjectProperty/{name}", "_to": f"Class/{local_name(res)}"})

    for dp in root.findall(".//owl:DatatypeProperty", ns):
        about = dp.attrib.get(f"{{{ns['rdf']}}}about")
        if not about:
            continue
        name = local_name(about)
        dt_props.append({"_key": name, "label": name, "uri": about})
        for d in dp.findall("./rdfs:domain", ns):
            res = d.attrib.get(f"{{{ns['rdf']}}}resource")
            if res:
                domains.append({"_from": f"DatatypeProperty/{name}", "_to": f"Class/{local_name(res)}"})

    upsert_many(db.collection("ObjectProperty"), obj_props)
    upsert_many(db.collection("DatatypeProperty"), dt_props)
    upsert_many(db.collection("domain"), domains)
    upsert_many(db.collection("range"), ranges)


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
    ensure_collection(db, "type", edge=True)
    type_col = db.collection("type")

    docs: List[Dict] = []
    for vcoll in DATA_VERTICES:
        if not db.has_collection(vcoll):
            continue
        # Ensure class node exists
        if db.has_collection("Class"):
            db.collection("Class").import_bulk([{"_key": vcoll, "label": vcoll, "uri": f"#{vcoll}"}], overwrite=True)
        for doc in db.collection(vcoll).all():
            from_id = doc["_id"]
            to_id = f"Class/{vcoll}"
            key = f"{from_id.replace('/', '_')}__{vcoll}"
            docs.append({"_key": key, "_from": from_id, "_to": to_id})

    if docs:
        # overwrite=True updates existing edges by _key
        type_col.import_bulk(docs, overwrite=True)


def main() -> None:
    load_dotenv()
    args = parse_args()

    cfg = get_arango_config(forced_mode=args.mode)
    apply_config_to_env(cfg)
    print(f"mode={cfg.mode} arango={sanitize_url(cfg.url)} db={cfg.database}")

    db = connect(cfg)

    # Ensure ontology-as-data is present (needed for OntologyGraph and KnowledgeGraph themes)
    load_ontology_as_data(db, force=args.force)

    if args.with_type_edges:
        create_type_edges(db)

    # Create the three named graphs
    ensure_graph(db, "OntologyGraph", ONTO_EDGE_DEFS)
    ensure_graph(db, "DataGraph", DATA_EDGES)
    knowledge_edges = ONTO_EDGE_DEFS + DATA_EDGES
    if args.with_type_edges:
        knowledge_edges = knowledge_edges + [{"edge_collection": "type", "from_vertex_collections": DATA_VERTICES, "to_vertex_collections": ["Class"]}]
    ensure_graph(db, "KnowledgeGraph", knowledge_edges)

    print("Created/updated: OntologyGraph, DataGraph, KnowledgeGraph")


if __name__ == "__main__":
    sys.exit(main())

