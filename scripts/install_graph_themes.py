#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import json
import re
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

# Additional, opt-in themes installed as isDefault=False (selected via the Legend).
# The risk heatmap colors entities by riskScore (requires Phase 3 risk scoring).
RISK_HEATMAP_THEME: Path = ROOT / "docs" / "themes" / "risk_heatmap_theme.json"
ADDITIONAL_THEMES: Dict[str, List[Path]] = {
    "DataGraph": [RISK_HEATMAP_THEME],
    "KnowledgeGraph": [RISK_HEATMAP_THEME],
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
        stable_key = re.sub(r"[^a-z0-9]+", "_", f"{graph_name}_{name}".lower()).strip("_")
        doc = {
            "_key": stable_key,
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


def _slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def _upsert_query(
    queries_col,
    vp_query_col,
    vp_id: str,
    graph_name: str,
    name: str,
    description: str,
    query_text: str,
    bind_vars: Dict,
    now: str,
) -> str:
    """Upsert a _queries doc and link to viewpoint via _viewpointQueries. Returns query _id."""
    stable_key = _slugify(f"{graph_name}_{name}")
    existing = list(queries_col.find({"_key": stable_key}))
    if not existing:
        existing = list(queries_col.find({"name": name, "graphId": graph_name}))

    if existing:
        existing = sorted(existing, key=lambda d: d.get("_key", ""))
        for extra in existing[1:]:
            try:
                for edge in vp_query_col.find({"_to": extra["_id"]}):
                    vp_query_col.delete(edge["_key"])
                queries_col.delete(extra["_key"])
            except Exception:
                pass
        doc = {
            "_key": existing[0]["_key"],
            "_id": existing[0]["_id"],
            "graphId": graph_name,
            "name": name,
            "title": name,
            "description": description,
            "queryText": query_text,
            "bindVariables": bind_vars,
            "createdAt": existing[0].get("createdAt", now),
            "updatedAt": now,
        }
        queries_col.replace(doc, check_rev=False)
        query_id = existing[0]["_id"]
    else:
        doc = {
            "_key": stable_key,
            "graphId": graph_name,
            "name": name,
            "title": name,
            "description": description,
            "queryText": query_text,
            "bindVariables": bind_vars,
            "createdAt": now,
            "updatedAt": now,
        }
        res = queries_col.insert(doc)
        query_id = res["_id"]

    if not list(vp_query_col.find({"_from": vp_id, "_to": query_id})):
        vp_query_col.insert({"_from": vp_id, "_to": query_id, "createdAt": now, "updatedAt": now})
    return query_id


def install_ontology_saved_queries(db, graph_name: str, vertex_colls: Set[str], edge_colls: Set[str]) -> None:
    """Install saved queries into the Graph Visualizer Queries panel for OntologyGraph."""
    ensure_collection(db, "_queries", edge=False)
    ensure_collection(db, "_viewpointQueries", edge=True)
    queries_col = db.collection("_queries")
    vp_query_col = db.collection("_viewpointQueries")
    vp_id = ensure_default_viewpoint(db, graph_name)
    now = datetime.utcnow().isoformat() + "Z"

    with_clause = "WITH " + ", ".join(sorted(vertex_colls | edge_colls))
    edge_union = "\n".join(
        f"  (FOR d IN {ec} RETURN d)," for ec in sorted(edge_colls)
    ).rstrip(",")

    entire_query = f"""{with_clause}
FOR e IN UNION_DISTINCT(
{edge_union}
)
RETURN e"""
    _upsert_query(
        queries_col, vp_query_col, vp_id, graph_name,
        "Show Entire Ontology",
        "Load all classes, properties, and their relationships",
        entire_query,
        {},
        now,
    )

    # Bound the traversal: an unbounded 1..10 ANY with no uniqueness options
    # enumerates every path and explodes (query gets killed) even on a tiny
    # ontology. uniqueVertices:"global" + bfs visits each node once; depth 5 is
    # plenty to reach all properties/superclasses of a Class.
    below_class_query = f"""{with_clause}
FOR c IN Class
  FILTER c._label == @className OR LIKE(c._uri, CONCAT("%#", @className), true)
  FOR v, e IN 1..5 ANY c GRAPH "{graph_name}"
    OPTIONS {{ uniqueVertices: "global", uniqueEdges: "path", bfs: true }}
    RETURN DISTINCT e"""
    _upsert_query(
        queries_col, vp_query_col, vp_id, graph_name,
        "Show Ontology Below Class",
        "Show all classes and properties reachable from the selected class",
        below_class_query,
        {"className": "Person"},
        now,
    )


def install_data_graph_saved_queries(db, graph_name: str, vertex_colls: Set[str], edge_colls: Set[str]) -> None:
    """Install demo-aligned saved queries for DataGraph / KnowledgeGraph Queries panel."""
    ensure_collection(db, "_queries", edge=False)
    ensure_collection(db, "_viewpointQueries", edge=True)
    queries_col = db.collection("_queries")
    vp_query_col = db.collection("_viewpointQueries")
    vp_id = ensure_default_viewpoint(db, graph_name)
    now = datetime.utcnow().isoformat() + "Z"

    with_clause = "WITH " + ", ".join(sorted(vertex_colls | edge_colls))

    # UC1: Find Victor Tella (synthetic alias) — starting point for circular trading demo
    if "Person" in vertex_colls:
        _upsert_query(
            queries_col, vp_query_col, vp_id, graph_name,
            "UC1: Find Victor Tella",
            "Locate the synthetic alias used as the starting point for the circular trading demo",
            f"""{with_clause}
FOR p IN Person
  FILTER p.name == @name
  FILTER p.isSyntheticDuplicate == true
  SORT p._key ASC
  LIMIT 1
  RETURN p""",
            {"name": "Victor Tella"},
            now,
        )

    # UC2a: Top fan-out accounts (mule hub discovery). Return the outgoing transfer
    # edges of the busiest source accounts so the Visualizer renders the hub + spokes.
    if "transferredTo" in edge_colls:
        _upsert_query(
            queries_col, vp_query_col, vp_id, graph_name,
            "UC2: Top Fan-Out Accounts",
            "Find accounts with the most outgoing transfers (potential mule hubs)",
            f"""WITH BankAccount, transferredTo
FOR e IN transferredTo
  COLLECT acct = e._from WITH COUNT INTO outDegree
  SORT outDegree DESC
  LIMIT @limit
  FOR v, edge IN 1..1 OUTBOUND acct transferredTo
    RETURN edge""",
            {"limit": 3},
            now,
        )

        # UC2b: Top fan-in accounts (collection points). Return incoming edges.
        _upsert_query(
            queries_col, vp_query_col, vp_id, graph_name,
            "UC2: Top Fan-In Accounts",
            "Find accounts with the most incoming transfers (potential collection points)",
            f"""WITH BankAccount, transferredTo
FOR e IN transferredTo
  COLLECT acct = e._to WITH COUNT INTO inDegree
  SORT inDegree DESC
  LIMIT @limit
  FOR v, edge IN 1..1 INBOUND acct transferredTo
    RETURN edge""",
            {"limit": 3},
            now,
        )

    # UC3: Undervalued property sales (circle rate evasion). Return the
    # property→transaction path so both nodes and the edge render on the canvas.
    if "RealProperty" in vertex_colls and "registeredSale" in edge_colls:
        _upsert_query(
            queries_col, vp_query_col, vp_id, graph_name,
            "UC3: Undervalued Property Sales",
            "Find properties where sale value is suspiciously below the circle rate value",
            f"""WITH RealProperty, RealEstateTransaction, registeredSale
FOR p IN RealProperty
  FILTER p.circleRateValue != null AND p.circleRateValue > 0
  FOR tx, e, path IN 1..1 OUTBOUND p registeredSale
    FILTER tx.transactionValue != null
    LET ratio = tx.transactionValue / p.circleRateValue
    FILTER ratio < 0.8
    SORT ratio ASC
    LIMIT @limit
    RETURN path""",
            {"limit": 5},
            now,
        )

    # UC4: Highest-risk entities (algorithm-assisted pivot). Returns the actual
    # Person nodes ranked by the riskScore written in Phase 3, so they render and
    # can be expanded. (Requires Phase 3 risk scoring to have run.)
    if "Person" in vertex_colls:
        _upsert_query(
            queries_col, vp_query_col, vp_id, graph_name,
            "UC4: Highest-Risk Entities",
            "Top people ranked by computed riskScore (requires Phase 3 analytics/risk run)",
            f"""WITH Person
FOR p IN Person
  FILTER p.riskScore != null
  SORT p.riskScore DESC
  LIMIT @limit
  RETURN p""",
            {"limit": 10},
            now,
        )

    # Account transfer chain (smoke traversal — good general starting point).
    # Return the full 2-hop path so Person, both accounts, and the edges render.
    if "Person" in vertex_colls and "hasAccount" in edge_colls and "transferredTo" in edge_colls:
        _upsert_query(
            queries_col, vp_query_col, vp_id, graph_name,
            "Account Transfer Chain",
            "Traverse Person → BankAccount → transfer targets (basic connectivity check)",
            f"""WITH Person, BankAccount, hasAccount, transferredTo
FOR p IN Person
  FOR v, e, path IN 2..2 OUTBOUND p hasAccount, transferredTo
    LIMIT @limit
    RETURN path""",
            {"limit": 10},
            now,
        )

    # ========== NEW: Indications and Warnings Queries ==========

    # I&W 1.1: Circular Transaction Patterns (HEADLINE indication).
    # Hunting query (no node selection needed): detect directed transfer cycles
    # and return the full path so the loop renders on the canvas. Bounded depth +
    # uniqueEdges:"path" + LIMIT keep it from exploding on background noise.
    if "BankAccount" in vertex_colls and "transferredTo" in edge_colls:
        _upsert_query(
            queries_col, vp_query_col, vp_id, graph_name,
            "[I&W] Circular Transaction Patterns",
            "Detect closed-loop (round-trip) transfer cycles between accounts — a classic laundering indication",
            f"""WITH BankAccount, transferredTo
FOR start IN BankAccount
  FOR v, e, p IN @minLen..@maxLen OUTBOUND start transferredTo
    OPTIONS {{ uniqueEdges: "path", uniqueVertices: "none" }}
    FILTER v._id == start._id
    LIMIT @limit
    RETURN p""",
            {"minLen": 2, "maxLen": 6, "limit": 10},
            now,
        )

    # I&W 2.3: Gateway Accounts (High In + Out Degree)
    if "BankAccount" in vertex_colls and "transferredTo" in edge_colls:
        _upsert_query(
            queries_col, vp_query_col, vp_id, graph_name,
            "[I&W] Gateway Accounts (Pass-Through Intermediaries)",
            "Find accounts with both high inbound and outbound transfers (classic layering pattern)",
            f"""{with_clause}
LET analysis = (
  FOR acct IN BankAccount
    LET inDeg = LENGTH(FOR e IN transferredTo FILTER e._to == acct._id RETURN 1)
    LET outDeg = LENGTH(FOR e IN transferredTo FILTER e._from == acct._id RETURN 1)
    FILTER inDeg >= @minInDegree AND outDeg >= @minOutDegree
    SORT (inDeg + outDeg) DESC
    RETURN acct._id
)
FOR item IN analysis LIMIT @limit
  FOR v, e, p IN 1..1 ANY item transferredTo
    RETURN p""",
            {"minInDegree": 3, "minOutDegree": 3, "limit": 5},
            now,
        )

        # I&W 3.1: Rapid Inbound Bursts (collection velocity). Surfaces accounts
        # that RECEIVE many transfers inside a single hour — a money-mule
        # collection hub absorbing many small deposits fast. Returns the inbound
        # edges so the burst renders.
        _upsert_query(
            queries_col, vp_query_col, vp_id, graph_name,
            "[I&W] Rapid Inbound Bursts (Collection Velocity)",
            "Find accounts receiving many transfers within a single hour (high-velocity collection — mule hub absorbing deposits)",
            f"""{with_clause}
FOR e IN transferredTo
  COLLECT dst = e._to, timeWindow = DATE_TRUNC(e.timestamp, "hour") WITH COUNT INTO burstSize
  FILTER burstSize >= @minBurstSize
  SORT burstSize DESC, timeWindow DESC
  LIMIT @limit
  FOR edge IN transferredTo
    FILTER edge._to == dst AND DATE_TRUNC(edge.timestamp, "hour") == timeWindow
    LIMIT 60
    RETURN edge""",
            {"minBurstSize": 5, "limit": 3},
            now,
        )

        # I&W 3.2: Structuring Chains (Amount Decay)
        _upsert_query(
            queries_col, vp_query_col, vp_id, graph_name,
            "[I&W] Structuring Chains (Amount Decay Pattern)",
            "Find 3-hop chains where the transfer amount decays at each hop (fee extraction / skimming). Returns the full path so the chain renders.",
            f"""WITH BankAccount, transferredTo
FOR start IN BankAccount
  FOR v, e, p IN 3..3 OUTBOUND start transferredTo
    OPTIONS {{ uniqueVertices: "path", uniqueEdges: "path" }}
    FILTER p.edges[1].amount < p.edges[0].amount * @decay
    FILTER p.edges[2].amount < p.edges[1].amount * @decay
    LIMIT @limit
    RETURN p""",
            {"decay": 0.95, "limit": 5},
            now,
        )

        # I&W 3.3: Round Amount Transfers
        _upsert_query(
            queries_col, vp_query_col, vp_id, graph_name,
            "[I&W] Round Amount Transfers (Suspiciously Uniform)",
            "Find large transfers in exact round thousands (intentional, non-organic amounts — common in structured laundering)",
            f"""WITH BankAccount, transferredTo
FOR e IN transferredTo
  LET remainder = e.amount - FLOOR(e.amount / 1000) * 1000
  FILTER remainder == 0
  FILTER e.amount >= @minAmount
  SORT e.amount DESC
  LIMIT @limit
  RETURN e""",
            {"minAmount": 100000, "limit": 25},
            now,
        )

    # I&W 2.3: Shared Device Mule Ring
    if "BankAccount" in vertex_colls and "DigitalLocation" in vertex_colls and "accessedFrom" in edge_colls and "transferredTo" in edge_colls:
        _upsert_query(
            queries_col, vp_query_col, vp_id, graph_name,
            "[I&W] Shared Device Mule Ring",
            "Find a single device/IP accessed by many distinct accounts (coordinated mule ring). Returns access edges so the device hub + spokes render.",
            f"""WITH BankAccount, DigitalLocation, accessedFrom
FOR dev IN DigitalLocation
  LET accessors = (FOR e IN accessedFrom FILTER e._to == dev._id RETURN e)
  FILTER LENGTH(accessors) >= @minAccounts
  SORT LENGTH(accessors) DESC
  LIMIT @limit
  FOR e IN accessors
    RETURN e""",
            {"minAccounts": 5, "limit": 2},
            now,
        )

    # I&W 5.1: High-Risk Aliases (Entity Resolution)
    if "Person" in vertex_colls and "GoldenRecord" in vertex_colls and "resolvedTo" in edge_colls:
        _upsert_query(
            queries_col, vp_query_col, vp_id, graph_name,
            "[I&W] Suspect Aliases (High-Risk Consolidations)",
            "Find GoldenRecords with multiple Person aliases (benami/proxy identity pattern)",
            f"""{with_clause}
FOR gr IN GoldenRecord
  LET personCount = LENGTH(FOR v, e IN 1..1 INBOUND gr resolvedTo FILTER IS_SAME_COLLECTION("Person", v) RETURN 1)
  FILTER personCount >= 2
  LET riskReasons = FLATTEN(
    FOR v, e IN 1..1 INBOUND gr resolvedTo
      FILTER IS_SAME_COLLECTION("Person", v)
      RETURN v.riskReasons || []
  )
  SORT gr.riskScore DESC
  LIMIT @limit
  FOR v, e, p IN 1..1 INBOUND gr resolvedTo
    FILTER IS_SAME_COLLECTION("Person", v)
    RETURN p""",
            {"limit": 10},
            now,
        )

    # I&W 5.2: Risk Propagation (Guilt by Association).
    # NOTE: WatchlistEntity has no edges in this data model — watchlist hits are
    # recorded as riskScore/riskReasons on Person. So we seed from the highest-risk
    # Person and walk the relatedTo (Person->Person) network. Returns paths so the
    # seed + connected (risk-inheriting) people render.
    if "Person" in vertex_colls and "relatedTo" in edge_colls:
        _upsert_query(
            queries_col, vp_query_col, vp_id, graph_name,
            "[I&W] Risk Propagation (Guilt by Association)",
            "Walk the associate network of the highest-risk people to surface entities that inherit risk by association",
            f"""WITH Person, relatedTo
FOR seed IN Person
  FILTER seed.riskScore != null AND seed.riskScore >= @minRisk
  SORT seed.riskScore DESC
  LIMIT @seedLimit
  FOR v, e, p IN 1..@depth ANY seed relatedTo
    OPTIONS {{ uniqueVertices: "path", bfs: true }}
    LIMIT @limit
    RETURN p""",
            {"minRisk": 50, "seedLimit": 3, "depth": 2, "limit": 25},
            now,
        )

    # ===== GAE-derived indications (require scripts/phase3_gae.py to have run) =====
    # phase3_gae.py computes PageRank/WCC on the ArangoDB Graph Analytics Engine and
    # writes the scores back onto the nodes (BankAccount.pagerankScore,
    # {BankAccount,DigitalLocation}.wccComponent). These queries surface those
    # results as graph elements in the Visualizer.

    # PageRank: the highest-influence accounts are the mule hubs. Return the top
    # accounts with their inbound transfers so the hub + spokes render.
    if "BankAccount" in vertex_colls and "transferredTo" in edge_colls:
        _upsert_query(
            queries_col, vp_query_col, vp_id, graph_name,
            "[I&W] Top Mule Hubs (PageRank)",
            "Highest-PageRank accounts (GAE) — money-mule collection hubs. Requires scripts/phase3_gae.py.",
            f"""WITH BankAccount, transferredTo
FOR acct IN BankAccount
  FILTER acct.pagerankScore != null
  SORT acct.pagerankScore DESC
  LIMIT @limit
  FOR v, e, p IN 1..1 INBOUND acct transferredTo
    LIMIT @edgesPerHub
    RETURN p""",
            {"limit": 5, "edgesPerHub": 25},
            now,
        )

    # WCC: the largest weakly-connected component in the device-sharing graph is the
    # coordinated mule ring. Return the ring accounts + their shared-device edges.
    if "BankAccount" in vertex_colls and "DigitalLocation" in vertex_colls and "accessedFrom" in edge_colls:
        _upsert_query(
            queries_col, vp_query_col, vp_id, graph_name,
            "[I&W] Fraud Ring (WCC Community)",
            "The largest weakly-connected component (GAE WCC over shared devices) — the coordinated mule ring. Requires scripts/phase3_gae.py.",
            f"""WITH BankAccount, DigitalLocation, accessedFrom
LET topComp = FIRST(
  FOR a IN BankAccount
    FILTER a.wccComponent != null
    COLLECT c = a.wccComponent WITH COUNT INTO n
    SORT n DESC
    LIMIT 1
    RETURN c
)
FOR acct IN BankAccount
  FILTER acct.wccComponent == topComp
  FOR v, e, p IN 1..1 OUTBOUND acct accessedFrom
    RETURN p""",
            {},
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

            # Upstream: trace where the money in this account CAME FROM.
            _upsert_canvas_action(
                canvas_col, vp_act_col, vp_id, graph_name,
                "[BankAccount] Trace Funding Sources (upstream)",
                "Walk inbound transfers up to N hops to reveal who funded the selected account.",
                f"""{with_clause}
FOR node IN @nodes
  FILTER IS_SAME_COLLECTION("BankAccount", node)
  FOR v, e, p IN 1..@depth INBOUND node transferredTo
    OPTIONS {{ uniqueVertices: "path", bfs: true }}
    LIMIT @limit
    RETURN p""",
                {"nodes": [], "depth": 3, "limit": 50},
                now,
            )

            # Downstream: trace where the money WENT.
            _upsert_canvas_action(
                canvas_col, vp_act_col, vp_id, graph_name,
                "[BankAccount] Trace Downstream Flow",
                "Walk outbound transfers up to N hops to reveal where funds were moved.",
                f"""{with_clause}
FOR node IN @nodes
  FILTER IS_SAME_COLLECTION("BankAccount", node)
  FOR v, e, p IN 1..@depth OUTBOUND node transferredTo
    OPTIONS {{ uniqueVertices: "path", bfs: true }}
    LIMIT @limit
    RETURN p""",
                {"nodes": [], "depth": 3, "limit": 50},
                now,
            )

        if v_coll == "BankAccount" and "hasAccount" in edge_colls:
            # Pivot from an account to its owner and the owner's other accounts.
            _upsert_canvas_action(
                canvas_col, vp_act_col, vp_id, graph_name,
                "[BankAccount] Show Owner & Linked Accounts",
                "Reveal the account holder and all other accounts they control.",
                f"""{with_clause}
FOR node IN @nodes
  FILTER IS_SAME_COLLECTION("BankAccount", node)
  FOR v, e, p IN 1..2 ANY node hasAccount
    LIMIT @limit
    RETURN p""",
                {"nodes": [], "limit": 50},
                now,
            )

        if v_coll == "BankAccount" and "accessedFrom" in edge_colls:
            # Surface accounts that share a device/IP with the selected account.
            _upsert_canvas_action(
                canvas_col, vp_act_col, vp_id, graph_name,
                "[BankAccount] Show Co-Accessed Accounts (shared device)",
                "Reveal the device/IP this account used and every other account accessed from it (mule ring detection).",
                f"""{with_clause}
FOR node IN @nodes
  FILTER IS_SAME_COLLECTION("BankAccount", node)
  FOR v, e, p IN 1..2 ANY node accessedFrom
    LIMIT @limit
    RETURN p""",
                {"nodes": [], "limit": 50},
                now,
            )

        if v_coll == "Person" and "resolvedTo" in edge_colls:
            # Reveal hidden identities: person -> golden record -> other aliases.
            _upsert_canvas_action(
                canvas_col, vp_act_col, vp_id, graph_name,
                "[Person] Reveal Aliases (Golden Record)",
                "Pivot through the resolved Golden Record to expose other identities/aliases of this person.",
                f"""{with_clause}
FOR node IN @nodes
  FILTER IS_SAME_COLLECTION("Person", node)
  FOR v, e, p IN 1..2 ANY node resolvedTo
    LIMIT @limit
    RETURN p""",
                {"nodes": [], "limit": 25},
                now,
            )

        if v_coll == "Person" and "hasAccount" in edge_colls and "transferredTo" in edge_colls:
            # From a person to their accounts and where those accounts send money.
            _upsert_canvas_action(
                canvas_col, vp_act_col, vp_id, graph_name,
                "[Person] Show Accounts & Money Flows",
                "Expand a person to their bank accounts and the transfers those accounts make.",
                f"""{with_clause}
FOR node IN @nodes
  FILTER IS_SAME_COLLECTION("Person", node)
  FOR v, e, p IN 1..2 OUTBOUND node hasAccount, transferredTo
    LIMIT @limit
    RETURN p""",
                {"nodes": [], "limit": 50},
                now,
            )

        if v_coll == "Person" and "relatedTo" in edge_colls:
            # Associate network for guilt-by-association investigation.
            _upsert_canvas_action(
                canvas_col, vp_act_col, vp_id, graph_name,
                "[Person] Show Associate Network",
                "Walk the relatedTo network to surface known associates (guilt-by-association).",
                f"""{with_clause}
FOR node IN @nodes
  FILTER IS_SAME_COLLECTION("Person", node)
  FOR v, e, p IN 1..@depth ANY node relatedTo
    OPTIONS {{ uniqueVertices: "path", bfs: true }}
    LIMIT @limit
    RETURN p""",
                {"nodes": [], "depth": 2, "limit": 50},
                now,
            )


def _install_one_theme(
    theme_col,
    theme_path: Path,
    graph_name: str,
    vertex_colls: Set[str],
    edge_colls: Set[str],
    is_default: bool,
) -> None:
    """Upsert a single theme (by name + graphId) for a graph. Exactly one theme
    per graph should be isDefault=True (the built-in/base theme); opt-in themes
    such as the risk heatmap are installed as isDefault=False."""
    if not theme_path.exists():
        raise SystemExit(f"Missing theme file: {theme_path}")

    raw = json.loads(theme_path.read_text(encoding="utf-8"))
    theme = prune_theme(raw, vertex_colls, edge_colls)
    theme["graphId"] = graph_name
    now = datetime.utcnow().isoformat() + "Z"
    theme["updatedAt"] = now
    theme["isDefault"] = is_default
    ensure_visualizer_shape(theme)

    existing = list(theme_col.find({"name": theme["name"], "graphId": graph_name}))
    if existing:
        theme["_key"] = existing[0]["_key"]
        theme["_id"] = existing[0]["_id"]
        theme["createdAt"] = existing[0].get("createdAt", now)
        theme_col.replace(theme, check_rev=False)
        print(f"[Updated Theme] {graph_name}::{theme['name']} (default={is_default})")
    else:
        theme["createdAt"] = now
        theme_col.insert(theme)
        print(f"[Installed Theme] {graph_name}::{theme['name']} (default={is_default})")


def install_themes(db) -> None:
    ensure_collection(db, "_graphThemeStore", edge=False)
    theme_col = db.collection("_graphThemeStore")

    for graph_name, theme_path in THEMES.items():
        if not theme_path.exists():
            raise SystemExit(f"Missing theme file: {theme_path}")
        if not db.has_graph(graph_name):
            print(f"[SKIP] Graph '{graph_name}' does not exist")
            continue

        vertex_colls, edge_colls = get_graph_schema(db, graph_name)
        # OntologyGraph: restrict to metadata only (no Person, Organization, etc.)
        if graph_name == "OntologyGraph":
            vertex_colls = vertex_colls & ONTOLOGY_VERTEX_COLLECTIONS
            edge_colls = edge_colls & ONTOLOGY_EDGE_COLLECTIONS

        # Base theme (the only isDefault=True theme for this graph).
        _install_one_theme(theme_col, theme_path, graph_name, vertex_colls, edge_colls, is_default=True)

        # Opt-in additional themes (isDefault=False) — e.g. the risk heatmap.
        for extra_path in ADDITIONAL_THEMES.get(graph_name, []):
            _install_one_theme(theme_col, extra_path, graph_name, vertex_colls, edge_colls, is_default=False)

        install_canvas_actions(db, graph_name, vertex_colls, edge_colls)

        if graph_name == "OntologyGraph":
            install_ontology_saved_queries(db, graph_name, vertex_colls, edge_colls)
        else:
            install_data_graph_saved_queries(db, graph_name, vertex_colls, edge_colls)


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

