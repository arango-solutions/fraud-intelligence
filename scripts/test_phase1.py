#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from common import (
    ArangoConfig,
    apply_config_to_env,
    get_arango_config,
    load_dotenv,
    sanitize_url,
    wait_for_http_ok,
)

try:
    from arango import ArangoClient  # type: ignore
except Exception:  # pragma: no cover
    ArangoClient = None  # type: ignore


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "docs" / "phase1-validation-report.md"
SMOKE_AQL_PATH = ROOT / "tests" / "test_basic_queries.aql"

# Canonical Phase 1 collections (OWL conventions)
PHASE1_COLLECTIONS: Tuple[str, ...] = (
    # vertices
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
    # edges
    "hasAccount",
    "transferredTo",
    "relatedTo",
    "associatedWith",
    "residesAt",
    "accessedFrom",
    "hasDigitalLocation",
    "mentionedIn",
    "registeredSale",
    "buyerIn",
    "sellerIn",
    "resolvedTo",
)


@dataclass
class StepResult:
    ok: bool
    detail: str = ""


def run(cmd: List[str], env: Optional[Dict[str, str]] = None) -> StepResult:
    try:
        subprocess.run(cmd, cwd=str(ROOT), check=True, env=env or os.environ.copy())
        return StepResult(True)
    except subprocess.CalledProcessError as e:
        return StepResult(False, f"command failed: {' '.join(cmd)} (exit {e.returncode})")


def docker_up(env_override: Optional[Dict[str, str]] = None) -> StepResult:
    return run(["docker", "compose", "up", "-d"], env=env_override)


def run_pytest(integration_only: bool = False) -> StepResult:
    cmd = ["pytest", "-q"]
    if integration_only:
        cmd += ["-m", "integration"]
    return run(cmd)


def connect(cfg: ArangoConfig):
    if ArangoClient is None:
        raise RuntimeError("python-arango not installed")
    client = ArangoClient(hosts=cfg.url)
    return client.db(cfg.database, username=cfg.username, password=cfg.password)


def split_aql_queries(aql_text: str) -> List[str]:
    lines = []
    for line in aql_text.splitlines():
        if line.strip().startswith("//"):
            continue
        lines.append(line)
    cleaned = "\n".join(lines).strip()
    # Split on blank lines where a new query begins with FOR
    chunks: List[str] = []
    buf: List[str] = []
    for line in cleaned.splitlines():
        if not line.strip() and buf:
            chunk = "\n".join(buf).strip()
            if chunk:
                chunks.append(chunk)
            buf = []
            continue
        buf.append(line)
    last = "\n".join(buf).strip()
    if last:
        chunks.append(last)
    # Keep chunks that contain at least one FOR-clause (may start with WITH).
    kept: List[str] = []
    for c in chunks:
        if any(line.lstrip().startswith("FOR ") for line in c.splitlines()):
            kept.append(c)
    return kept


def run_smoke_queries(cfg: ArangoConfig) -> Tuple[StepResult, Dict[str, int]]:
    db = connect(cfg)
    aql = SMOKE_AQL_PATH.read_text(encoding="utf-8")
    queries = split_aql_queries(aql)
    if not queries:
        return StepResult(False, "no queries parsed from tests/test_basic_queries.aql"), {}

    for idx, q in enumerate(queries, start=1):
        cur = db.aql.execute(q)
        first_batch = list(cur)  # exhaust (small limit in queries)
        if len(first_batch) == 0:
            return StepResult(False, f"smoke query #{idx} returned empty result"), {}

    # Counts (useful for report)
    counts: Dict[str, int] = {}
    for name in PHASE1_COLLECTIONS:
        if not db.has_collection(name):
            counts[name] = 0
            continue
        try:
            counts[name] = db.collection(name).count()
        except Exception:
            counts[name] = 0

    return StepResult(True), counts


def write_report(local: Dict, remote: Dict) -> None:
    def section(title: str, data: Dict) -> str:
        if not data:
            return f"## {title}\n\n- **Status:** not run\n\n"
        lines = [f"## {title}", ""]
        lines.append(f"- **Status:** {'PASS' if data.get('ok') else 'FAIL'}")
        if data.get("mode"):
            lines.append(f"- **Mode:** {data['mode']}")
        if data.get("arango_url"):
            lines.append(f"- **ArangoDB:** `{data['arango_url']}`")
        if data.get("db"):
            lines.append(f"- **Database:** `{data['db']}`")
        lines.append("")

        for k in [
            "docker",
            "generate",
            "ingest",
            "define_graphs",
            "install_themes",
            "pytest",
            "pytest_integration",
            "smoke_queries",
        ]:
            if k in data:
                v = data[k]
                status = "PASS" if v.get("ok") else "FAIL"
                detail = v.get("detail", "")
                lines.append(f"- **{k}**: {status}" + (f" — {detail}" if detail else ""))
        if data.get("counts"):
            lines.append("")
            lines.append("### Collection counts")
            lines.append("")
            for name in sorted(data["counts"].keys()):
                lines.append(f"- `{name}`: {data['counts'][name]}")
        lines.append("")
        return "\n".join(lines)

    content = "\n".join(
        [
            "# Phase 1 validation report",
            "",
            "This report is generated by `scripts/test_phase1.py`.",
            "",
            section("LOCAL (Docker)", local),
            section("REMOTE (Managed)", remote),
        ]
    )
    REPORT_PATH.write_text(content, encoding="utf-8")


def run_mode(mode: str, data_dir: Path, force_ingest: bool, do_docker: bool) -> Dict:
    cfg = get_arango_config(forced_mode=mode)
    apply_config_to_env(cfg)

    result: Dict = {
        "mode": cfg.mode,
        "arango_url": sanitize_url(cfg.url),
        "db": cfg.database,
        "ok": True,
    }

    if cfg.mode == "LOCAL" and do_docker:
        # Choose a host port for Docker binding.
        # If ARANGO_PORT is set by the user, respect it; otherwise avoid 8529 if already in use.
        import socket
        from urllib.parse import urlparse

        desired_port = os.getenv("ARANGO_PORT")
        if not desired_port:
            u = urlparse(cfg.url)
            host = u.hostname or "localhost"
            port = u.port or 8529
            s = socket.socket()
            try:
                s.settimeout(0.5)
                s.connect((host, port))
                # Something is already listening on default port; choose fallback.
                desired_port = "8530"
            except Exception:
                desired_port = str(port)
            finally:
                try:
                    s.close()
                except Exception:
                    pass

        env_override = os.environ.copy()
        env_override["ARANGO_PORT"] = desired_port
        # Ensure our scripts talk to the same host port.
        env_override["ARANGO_URL"] = f"http://localhost:{desired_port}"
        # Ensure Docker uses a local-only password and our scripts use the same.
        env_override["ARANGO_DOCKER_PASSWORD"] = env_override.get("ARANGO_DOCKER_PASSWORD") or "changeme"
        env_override["ARANGO_PASSWORD"] = env_override["ARANGO_DOCKER_PASSWORD"]
        os.environ["ARANGO_PORT"] = desired_port
        os.environ["ARANGO_URL"] = env_override["ARANGO_URL"]
        os.environ["ARANGO_DOCKER_PASSWORD"] = env_override["ARANGO_DOCKER_PASSWORD"]
        os.environ["ARANGO_PASSWORD"] = env_override["ARANGO_DOCKER_PASSWORD"]
        cfg = get_arango_config(forced_mode="LOCAL")
        apply_config_to_env(cfg)
        result["arango_url"] = sanitize_url(cfg.url)

        r = docker_up(env_override=env_override)
        result["docker"] = asdict(r)
        if not r.ok:
            result["ok"] = False
            return result
        try:
            wait_for_http_ok(cfg.url, timeout_s=90)
        except Exception as e:
            result["docker"] = {"ok": False, "detail": str(e)}
            result["ok"] = False
            return result

    # Generate data
    gen = run(
        [
            sys.executable,
            "scripts/generate_data.py",
            "--output",
            str(data_dir),
            "--size",
            "sample",
            "--seed",
            "42",
            "--force",
        ]
    )
    result["generate"] = asdict(gen)
    if not gen.ok:
        result["ok"] = False
        return result

    # Ingest
    ingest_cmd = [sys.executable, "scripts/ingest.py", "--data-dir", str(data_dir)]
    if force_ingest:
        ingest_cmd.append("--force")
    ing = run(ingest_cmd)
    result["ingest"] = asdict(ing)
    if not ing.ok:
        result["ok"] = False
        return result

    # Optional: create named graphs + install Visualizer themes (AMP recommended)
    if os.getenv("PHASE1_INSTALL_VISUALIZER") == "1":
        if cfg.mode == "REMOTE":
            g1 = run([sys.executable, "scripts/define_graphs.py", "--mode", "REMOTE", "--with-type-edges"])
            result["define_graphs"] = asdict(g1)
            if not g1.ok:
                result["ok"] = False
                return result
            g2 = run([sys.executable, "scripts/install_graph_themes.py", "--mode", "REMOTE"])
            result["install_themes"] = asdict(g2)
            if not g2.ok:
                result["ok"] = False
                return result
        else:
            # Local Docker typically doesn't expose the Visualizer; keep this a no-op.
            result["define_graphs"] = {"ok": True, "detail": "skipped (LOCAL)"}
            result["install_themes"] = {"ok": True, "detail": "skipped (LOCAL)"}

    # Tests
    pt = run_pytest(integration_only=False)
    result["pytest"] = asdict(pt)
    if not pt.ok:
        result["ok"] = False
        return result

    pti = run_pytest(integration_only=True)
    result["pytest_integration"] = asdict(pti)
    if not pti.ok:
        result["ok"] = False
        return result

    # Smoke AQL
    try:
        sq, counts = run_smoke_queries(cfg)
        result["smoke_queries"] = asdict(sq)
        result["counts"] = counts
        if not sq.ok:
            result["ok"] = False
    except Exception as e:
        result["smoke_queries"] = {"ok": False, "detail": str(e)}
        result["ok"] = False

    return result


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run Phase 1 tests for LOCAL then REMOTE.")
    p.add_argument("--data-dir", default="data/sample", help="Dataset directory")
    p.add_argument("--local-only", action="store_true", help="Only run LOCAL")
    p.add_argument("--remote-only", action="store_true", help="Only run REMOTE")
    p.add_argument("--remote-force", action="store_true", help="Allow --force ingest in REMOTE (dangerous)")
    p.add_argument(
        "--install-visualizer",
        action="store_true",
        help="After ingest, create OntologyGraph/DataGraph/KnowledgeGraph and install themes (REMOTE only).",
    )
    p.add_argument("--no-docker", action="store_true", help="Skip docker compose up for LOCAL")
    return p.parse_args()


def main() -> None:
    # Load .env (but never print it)
    load_dotenv()

    args = parse_args()
    if args.install_visualizer:
        # Plumb through without changing function signatures.
        os.environ["PHASE1_INSTALL_VISUALIZER"] = "1"
    data_dir = ROOT / args.data_dir

    local: Dict = {}
    remote: Dict = {}

    if not args.remote_only:
        local = run_mode("LOCAL", data_dir=data_dir, force_ingest=True, do_docker=not args.no_docker)

    if not args.local_only:
        remote = run_mode(
            "REMOTE",
            data_dir=data_dir,
            force_ingest=bool(args.remote_force),
            do_docker=False,
        )

    write_report(local=local, remote=remote)

    ok = True
    if local and not local.get("ok"):
        ok = False
    if remote and not remote.get("ok"):
        ok = False

    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

