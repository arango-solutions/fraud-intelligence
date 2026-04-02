#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from common import ArangoConfig, apply_config_to_env, get_arango_config, load_dotenv, sanitize_url

try:
    from arango import ArangoClient  # type: ignore
except Exception:  # pragma: no cover
    ArangoClient = None  # type: ignore


ROOT = Path(__file__).resolve().parents[1]

# Ontology-only collections (metadata). OntologyGraph theme and canvas actions use these only.
ONTOLOGY_VERTEX_COLLECTIONS: frozenset = frozenset({
    "Class", "Property", "Ontology", "ObjectProperty", "DatatypeProperty", "OntologyGraph_UnknownResource",
})
ONTOLOGY_EDGE_COLLECTIONS: frozenset = frozenset({"domain", "range", "subClassOf", "type"})

THEMES: Dict[str, Path] = {
    "OntologyGraph": ROOT / "docs" / "themes" / "ontology_theme.json",
    "DataGraph": ROOT / "docs" / "themes" / "datagraph_theme.json",
    "KnowledgeGraph": ROOT / "docs" / "themes" / "knowledgegraph_theme.json",
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Install graph themes + default viewpoint/actions into ArangoDB Visualizer collections.")
    p.add_argument("--mode", choices=["LOCAL", "REMOTE"], help="Override MODE for Arango connection")
    return p.parse_args()


def connect(cfg: ArangoConfig):
    if ArangoClient is None:
        raise SystemExit("python-arango not installed. Install: pip install -r requirements.txt")
    client = ArangoClient(hosts=cfg.url)
    return client.db(cfg.database, username=cfg.username, password=cfg.password)


def ensure_collection(db, name: str, edge: bool = False) -> None:
    if db.has_collection(name):
        return
    # ArangoDB reserves leading '_' for system collections.
    db.create_collection(name, edge=edge, system=name.startswith("_"))


def get_graph_schema(db, graph_name: str) -> Tuple[Set[str], Set[str]]:
    if not db.has_graph(graph_name):
        return set(), set()
    g = db.graph(graph_name)
    vertex_colls = set(g.vertex_collections())
    edge_defs = g.edge_definitions()
    edge_colls = set(ed["edge_collection"] for ed in edge_defs)
    return vertex_colls, edge_colls


def prune_theme(theme_raw: Dict, vertex_colls: Set[str], edge_colls: Set[str]) -> Dict:
    theme = copy.deepcopy(theme_raw)
    if "nodeConfigMap" in theme:
        theme["nodeConfigMap"] = {k: v for k, v in theme["nodeConfigMap"].items() if k in vertex_colls}
    if "edgeConfigMap" in theme:
        theme["edgeConfigMap"] = {k: v for k, v in theme["edgeConfigMap"].items() if k in edge_colls}
    return theme


def ensure_visualizer_shape(theme: Dict) -> None:
    # Match Arango Visualizer expectations: ensure optional fields exist.
    for node_cfg in theme.get("nodeConfigMap", {}).values():
        node_cfg.setdefault("rules", [])
        node_cfg.setdefault("hoverInfoAttributes", [])
    for edge_cfg in theme.get("edgeConfigMap", {}).values():
        edge_cfg.setdefault("rules", [])
        edge_cfg.setdefault("hoverInfoAttributes", [])
        edge_cfg.setdefault("arrowStyle", {"sourceArrowShape": "none", "targetArrowShape": "triangle"})
        edge_cfg.setdefault("labelStyle", {"color": "#1d2531"})


def ensure_default_viewpoint(db, graph_name: str) -> str:
    ensure_collection(db, "_viewpoints", edge=False)
    vp_col = db.collection("_viewpoints")

    existing = list(vp_col.find({"graphId": graph_name, "name": "Default"}))
    if existing:
        return existing[0]["_id"]

    now = datetime.utcnow().isoformat() + "Z"
    res = vp_col.insert(
        {
            "graphId": graph_name,
            "name": "Default",
            "description": f"Default viewpoint for {graph_name}",
            "createdAt": now,
            "updatedAt": now,
        }
    )
    return res["_id"]


def _upsert_canvas_action(
    canvas_col,
    vp_act_col,
    vp_id: str,
    graph_name: str,
    name: str,
    description: str,
    query_text: str,
    bind_vars: Dict,
    now: str,
) -> str:
    """Upsert a canvas action and link to viewpoint. Returns action _id."""
    existing = list(canvas_col.find({"name": name, "graphId": graph_name}))
    if existing:
        existing = sorted(existing, key=lambda d: d.get("_key", ""))
        for extra in existing[1:]:
            try:
                canvas_col.delete(extra["_key"])
            except Exception:
                pass
        doc = {
            "graphId": graph_name,
            "name": name,
            "description": description,
            "queryText": query_text,
            "bindVariables": bind_vars,
            "updatedAt": now,
            "_key": existing[0]["_key"],
            "_id": existing[0]["_id"],
            "createdAt": existing[0].get("createdAt", now),
        }
        canvas_col.replace(doc, check_rev=False)
        action_id = existing[0]["_id"]
    else:
        doc = {
            "graphId": graph_name,
            "name": name,
            "description": description,
            "queryText": query_text,
            "bindVariables": bind_vars,
            "createdAt": now,
            "updatedAt": now,
        }
        res = canvas_col.insert(doc)
        action_id = res["_id"]
    if not list(vp_act_col.find({"_from": vp_id, "_to": action_id})):
        vp_act_col.insert({"_from": vp_id, "_to": action_id, "createdAt": now, "updatedAt": now})
    return action_id


def install_ontology_graph_actions(db, graph_name: str) -> None:
    """
    Install canvas actions for OntologyGraph (metadata only).
    Uses simple FOR node IN @nodes format. Ontology vertex types only.
    Removes any existing actions for data collections (Person, Organization, etc.).
    """
    ensure_collection(db, "_canvasActions", edge=False)
    ensure_collection(db, "_viewpointActions", edge=True)
    canvas_col = db.collection("_canvasActions")
    vp_act_col = db.collection("_viewpointActions")
    vp_id = ensure_default_viewpoint(db, graph_name)
    now = datetime.utcnow().isoformat() + "Z"

    # Remove non-ontology expand actions (Person, Organization, etc. don't belong)
    ontology_actions = {f"[{c}] Expand Relationships" for c in ONTOLOGY_VERTEX_COLLECTIONS}
    for doc in canvas_col.find({"graphId": graph_name}):
        name = doc.get("name", "")
        if name.endswith("Expand Relationships") and name not in ontology_actions:
            try:
                canvas_col.delete(doc["_key"])
                # Remove viewpoint link
                for edge in vp_act_col.find({"_to": doc["_id"]}):
                    vp_act_col.delete(edge["_key"])
            except Exception:
                pass

    # Ontology edges only (from original artifacts)
    onto_edges = "domain, range, subClassOf, type"
    onto_edges_no_type = "domain, range, subClassOf"
    with_ontology = "WITH Class, DatatypeProperty, ObjectProperty, Ontology, OntologyGraph_UnknownResource, Property, domain, range, subClassOf, type"

    # Default: simple FOR node IN @nodes, RETURN e
    default_query = f"""{with_ontology}
FOR node IN @nodes
  FOR v, e IN 1..2 ANY node GRAPH "{graph_name}"
  LIMIT 100
  RETURN e"""
    _upsert_canvas_action(
        canvas_col, vp_act_col, vp_id, graph_name,
        "Find 2-hop neighbors (default)",
        "Find 2-hop neighbors of the selected nodes",
        default_query,
        {"nodes": []},
        now,
    )

    # Class, Property, Ontology, OntologyGraph_UnknownResource: filter on node, edges domain/range/subClassOf/type
    for v_coll in ["Class", "Property", "Ontology", "OntologyGraph_UnknownResource"]:
        query = f"""{with_ontology}
FOR node IN @nodes
  FILTER IS_SAME_COLLECTION("{v_coll}", node)
  FOR v, e, p IN 1..1 ANY node {onto_edges}
  LIMIT 20
  RETURN p"""
        _upsert_canvas_action(
            canvas_col, vp_act_col, vp_id, graph_name,
            f"[{v_coll}] Expand Relationships",
            f"Expand related entities for {v_coll}",
            query,
            {"nodes": []},
            now,
        )

    # DatatypeProperty, ObjectProperty: filter on traversed vertex v (from original)
    with_props = "WITH Class, DatatypeProperty, ObjectProperty, domain, range, subClassOf"
    for v_coll in ["DatatypeProperty", "ObjectProperty"]:
        query = f"""{with_props}
FOR node IN @nodes
  FOR v, e, p IN 1..1 ANY node {onto_edges_no_type}
  FILTER IS_SAME_COLLECTION("{v_coll}", v)
  LIMIT 20
  RETURN p"""
        _upsert_canvas_action(
            canvas_col, vp_act_col, vp_id, graph_name,
            f"[{v_coll}] Expand Relationships",
            f"Expand related entities for {v_coll}",
            query,
            {"nodes": []},
            now,
        )


def install_canvas_actions(db, graph_name: str, vertex_colls: Set[str], edge_colls: Set[str]) -> None:
    """Install canvas actions. OntologyGraph uses ontology-only logic; others use generic logic."""
    if graph_name == "OntologyGraph":
        install_ontology_graph_actions(db, graph_name)
        return

    ensure_collection(db, "_canvasActions", edge=False)
    ensure_collection(db, "_viewpointActions", edge=True)
    canvas_col = db.collection("_canvasActions")
    vp_act_col = db.collection("_viewpointActions")
    vp_id = ensure_default_viewpoint(db, graph_name)

    edge_list_str = ", ".join(sorted(edge_colls))
    with_clause = "WITH " + ", ".join(sorted(vertex_colls | edge_colls))
    now = datetime.utcnow().isoformat() + "Z"

    # Simple format: FOR node IN @nodes (node selector provides array of selected nodes)
    default_title = "Find 2-hop neighbors (default)"
    default_query = f"""{with_clause}
FOR node IN @nodes
  FOR v, e IN 1..2 ANY node GRAPH "{graph_name}"
  LIMIT 100
  RETURN e"""
    _upsert_canvas_action(
        canvas_col, vp_act_col, vp_id, graph_name,
        default_title,
        "Find 2-hop neighbors of the selected nodes",
        default_query,
        {"nodes": []},
        now,
    )

    for v_coll in sorted(vertex_colls):
        action_title = f"[{v_coll}] Expand Relationships"
        query = f"""{with_clause}
FOR node IN @nodes
  FILTER IS_SAME_COLLECTION("{v_coll}", node)
  FOR v, e, p IN 1..1 ANY node {edge_list_str}
  LIMIT 20
  RETURN p"""
        _upsert_canvas_action(
            canvas_col, vp_act_col, vp_id, graph_name,
            action_title,
            f"Expand related entities for {v_coll}",
            query,
            {"nodes": []},
            now,
        )

        if v_coll == "BankAccount" and "transferredTo" in edge_colls:
            cycle_title = "[BankAccount] Find cycles (AQL)"
            cycle_query = f"""{with_clause}
FOR start IN @nodes
  FILTER IS_SAME_COLLECTION("BankAccount", start)
  FOR v, e, p IN 3..@maxDepth OUTBOUND start transferredTo
    OPTIONS {{ uniqueVertices: "none", uniqueEdges: "path" }}
    FILTER v._id == start
    LIMIT @limit
    RETURN p"""
            _upsert_canvas_action(
                canvas_col, vp_act_col, vp_id, graph_name,
                cycle_title,
                "Find directed transfer cycles returning to the selected BankAccount (AQL traversal).",
                cycle_query,
                {"nodes": [], "maxDepth": 6, "limit": 5},
                now,
            )


def install_themes(db) -> None:
    ensure_collection(db, "_graphThemeStore", edge=False)
    theme_col = db.collection("_graphThemeStore")

    for graph_name, theme_path in THEMES.items():
        if not theme_path.exists():
            raise SystemExit(f"Missing theme file: {theme_path}")
        if not db.has_graph(graph_name):
            print(f"[SKIP] Graph '{graph_name}' does not exist")
            continue

        raw = json.loads(theme_path.read_text(encoding="utf-8"))
        vertex_colls, edge_colls = get_graph_schema(db, graph_name)
        # OntologyGraph: restrict to metadata only (no Person, Organization, etc.)
        if graph_name == "OntologyGraph":
            vertex_colls = vertex_colls & ONTOLOGY_VERTEX_COLLECTIONS
            edge_colls = edge_colls & ONTOLOGY_EDGE_COLLECTIONS
        theme = prune_theme(raw, vertex_colls, edge_colls)
        theme["graphId"] = graph_name
        now = datetime.utcnow().isoformat() + "Z"
        theme["createdAt"] = now
        theme["updatedAt"] = now
        theme["isDefault"] = True
        ensure_visualizer_shape(theme)

        existing = list(theme_col.find({"name": theme["name"], "graphId": graph_name}))
        if existing:
            theme["_key"] = existing[0]["_key"]
            theme["_id"] = existing[0]["_id"]
            theme_col.replace(theme, check_rev=False)
            print(f"[Updated Theme] {graph_name}::{theme['name']}")
        else:
            theme_col.insert(theme)
            print(f"[Installed Theme] {graph_name}::{theme['name']}")

        install_canvas_actions(db, graph_name, vertex_colls, edge_colls)


def main() -> None:
    load_dotenv()
    args = parse_args()
    cfg = get_arango_config(forced_mode=args.mode)
    apply_config_to_env(cfg)
    print(f"mode={cfg.mode} arango={sanitize_url(cfg.url)} db={cfg.database}")

    db = connect(cfg)
    install_themes(db)


if __name__ == "__main__":
    sys.exit(main())

