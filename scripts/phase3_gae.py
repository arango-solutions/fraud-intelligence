#!/usr/bin/env python3
"""
Phase 3 (GAE): compute PageRank + WCC on the fraud graph using the ArangoDB
Graph Analytics Engine (GAE), and write per-node results back so the Analyst-lens
charts in render_interactive_html_reports.py have real data.

Why GAE (not AQL): PageRank is a global iterative centrality and WCC is a global
partition — neither is expressible in AQL. (Pregel is deprecated; GAE is its
replacement.) We reuse the tested client in the sibling project
`~/code/agentic-graph-analytics` (package: graph_analytics_ai) rather than
reimplementing the engine lifecycle / auth / job-polling.

Run it with the sibling project's virtualenv (which has graph_analytics_ai +
deps installed), from the fraud-intelligence repo root so this repo's .env and
scripts/common are picked up:

    cd ~/code/fraud-intelligence
    ~/code/agentic-graph-analytics/.venv/bin/python scripts/phase3_gae.py --dry-run
    ~/code/agentic-graph-analytics/.venv/bin/python scripts/phase3_gae.py            # deploys a GAE engine

Graph modelling:
- PageRank  : vertices=[BankAccount], edges=[transferredTo]         -> field `rank`      -> uc_s01_results
- WCC       : vertices=[BankAccount, DigitalLocation], edges=[accessedFrom] -> field `component` -> uc_s02_results
  (WCC over the device-sharing graph: accounts that share a DigitalLocation
  connect *through* the device node, so the 50-mule ring collapses into one large
  component while unrelated accounts stay tiny — the PRD 'connected by device ID'
  histogram. Running WCC over raw transferredTo instead collapses the whole graph
  into one giant component because of background transfer noise.)
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from common import load_dotenv, get_arango_config, sanitize_url  # noqa: E402


# PageRank -> uc_s01_results (field `rank`); WCC -> uc_s02_results (field `component`).
# These collection names + fields are exactly what scripts/render_interactive_html_reports.py
# reads (_load_rank_series reads d.rank; _load_component_counts reads d.component).
ANALYSES = {
    "pagerank": dict(
        name="UC-S01 Mule Hub (PageRank)",
        algorithm="pagerank",
        vertex_collections=["BankAccount"],
        edge_collections=["transferredTo"],
        target_collection="uc_s01_results",
    ),
    "wcc": dict(
        name="UC-S02 Fraud Ring (WCC)",
        algorithm="wcc",
        vertex_collections=["BankAccount", "DigitalLocation"],
        edge_collections=["accessedFrom"],
        target_collection="uc_s02_results",
    ),
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Compute PageRank/WCC on the fraud graph via the ArangoDB Graph Analytics Engine (GAE).")
    p.add_argument("--algorithm", choices=["pagerank", "wcc", "both"], default="both")
    p.add_argument("--mode", choices=["LOCAL", "REMOTE"], default=None, help="Override MODE for the DB connection")
    p.add_argument("--dry-run", action="store_true", help="Validate imports/config/connection + authenticate; do NOT deploy an engine or run algorithms.")
    p.add_argument("--no-cleanup", action="store_true", help="Leave the GAE engine running after the run (default: auto-cleanup).")
    return p.parse_args()


def _prime_env(cfg) -> None:
    """Map fraud-intelligence .env names onto the names graph_analytics_ai expects."""
    os.environ.setdefault("GAE_DEPLOYMENT_MODE", "self_managed")  # self-managed via GenAI platform (uses ArangoDB JWT)
    os.environ["ARANGO_ENDPOINT"] = cfg.url
    os.environ["ARANGO_DATABASE"] = cfg.database
    os.environ["ARANGO_USER"] = cfg.username           # sibling reads ARANGO_USER, not ARANGO_USERNAME
    os.environ["ARANGO_PASSWORD"] = cfg.password
    os.environ.setdefault("ARANGO_VERIFY_SSL", os.getenv("ARANGO_VERIFY_SSL", "false"))


def main() -> int:
    args = parse_args()
    load_dotenv()
    cfg = get_arango_config(forced_mode=args.mode or os.getenv("ARANGO_MODE") or "REMOTE")
    if not cfg.url or not cfg.password:
        raise SystemExit("ARANGO_ENDPOINT and ARANGO_PASSWORD must be set (check .env).")
    _prime_env(cfg)

    print(f"[phase3-gae] mode={cfg.mode} arango={sanitize_url(cfg.url)} db={cfg.database} "
          f"deployment_mode={os.environ['GAE_DEPLOYMENT_MODE']}")

    try:
        from graph_analytics_ai.gae_orchestrator import GAEOrchestrator, AnalysisConfig
        from graph_analytics_ai.gae_connection import get_gae_connection
    except ModuleNotFoundError as e:
        raise SystemExit(
            f"Could not import graph_analytics_ai ({e}).\n"
            "Run this script with the sibling project's virtualenv, e.g.:\n"
            "  ~/code/agentic-graph-analytics/.venv/bin/python scripts/phase3_gae.py"
        )

    wanted = ["pagerank", "wcc"] if args.algorithm == "both" else [args.algorithm]
    configs = []
    for name in wanted:
        spec = ANALYSES[name]
        configs.append(AnalysisConfig(
            name=spec["name"],
            algorithm=spec["algorithm"],
            vertex_collections=spec["vertex_collections"],
            edge_collections=spec["edge_collections"],
            target_collection=spec["target_collection"],
            load_strategy="collections",
            auto_cleanup=not args.no_cleanup,
        ))

    for c in configs:
        print(f"  - {c.algorithm:8s} V={c.vertex_collections} E={c.edge_collections} "
              f"-> {c.target_collection} (field '{getattr(c, 'result_field', '?')}')")

    if args.dry_run:
        # Construct the connection (validates env + self-managed mode) and authenticate.
        conn = get_gae_connection()
        auth = getattr(conn, "authenticate", None)
        if callable(auth):
            ok = auth()
            print(f"[dry-run] connection={type(conn).__name__} authenticate()={ok}")
        else:
            print(f"[dry-run] connection={type(conn).__name__} constructed (no authenticate() method)")
        print("[dry-run] OK — imports, config, and connection valid. No engine deployed.")
        return 0

    orch = GAEOrchestrator(verbose=True)
    failures = 0
    for c in configs:
        print(f"\n===== Running GAE {c.algorithm} -> {c.target_collection} =====")
        result = orch.run_analysis(c)
        status = getattr(result, "status", None)
        status = getattr(status, "value", status)
        err = getattr(result, "error", None)
        print(f"[result] {c.algorithm}: status={status}")
        # COMPLETED is success; CLEANING_UP is the post-success state entered when
        # auto_cleanup tears the engine down. Only FAILED (or an error) is a failure.
        ok = (str(status).lower() in ("completed", "cleaning_up")) and not err
        if not ok:
            failures += 1
            print(f"[result] {c.algorithm}: error={getattr(result, 'error', None)}")

    print(f"\n[phase3-gae] done. {len(configs) - failures}/{len(configs)} analyses succeeded.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
