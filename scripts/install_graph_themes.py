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


def install_canvas_actions(db, graph_name: str, vertex_colls: Set[str], edge_colls: Set[str]) -> None:
    ensure_collection(db, "_canvasActions", edge=False)
    ensure_collection(db, "_viewpointActions", edge=True)

    canvas_col = db.collection("_canvasActions")
    vp_act_col = db.collection("_viewpointActions")
    vp_id = ensure_default_viewpoint(db, graph_name)

    edge_list_str = ", ".join(sorted(edge_colls))
    now = datetime.utcnow().isoformat() + "Z"

    for v_coll in sorted(vertex_colls):
        action_title = f"[{v_coll}] Expand Relationships"
        query = f"""FOR node IN @nodes
  FOR v, e, p IN 1..1 ANY node
    {edge_list_str}
    FILTER IS_SAME_COLLECTION("{v_coll}", v)
    LIMIT 20
    RETURN p"""

        action_doc = {
            "name": action_title,
            "description": f"Expand related entities for {v_coll}",
            "queryText": query,
            "graphId": graph_name,
            "bindVariables": {"nodes": ""},
            "updatedAt": now,
        }

        existing = list(canvas_col.find({"name": action_title, "graphId": graph_name}))
        if existing:
            action_doc["_key"] = existing[0]["_key"]
            action_doc["_id"] = existing[0]["_id"]
            canvas_col.replace(action_doc)
            action_id = existing[0]["_id"]
        else:
            action_doc["createdAt"] = now
            res = canvas_col.insert(action_doc)
            action_id = res["_id"]

        if not list(vp_act_col.find({"_from": vp_id, "_to": action_id})):
            vp_act_col.insert({"_from": vp_id, "_to": action_id, "createdAt": now, "updatedAt": now})


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
            theme_col.replace(theme)
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

