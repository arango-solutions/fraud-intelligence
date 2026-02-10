#!/usr/bin/env python3
"""
Render interactive HTML reports (Plotly) from existing workflow outputs.

This avoids re-running the full agentic workflow / GAE algorithms. It uses:
- Existing markdown reports in fraud_analysis_output/fraud_report_*.md
- Stored result collections in ArangoDB (e.g., uc_s01_results, uc_s02_results, uc_s03_results)

Output:
- Replaces fraud_analysis_output/fraud_report_*.html with an interactive version
- Preserves the previous static HTML as fraud_report_*.static.html (if present)
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from arango import ArangoClient

# `common.py` lives next to this script.
from common import get_arango_config, load_dotenv


_UC_S_RE = re.compile(r"\bUC-?S(\d{2})\b", re.IGNORECASE)
_UC_R_RE = re.compile(r"\bUC-?R(\d{2})\b", re.IGNORECASE)
_UC_NUM_RE = re.compile(r"\bUC-(\d{3})\b", re.IGNORECASE)


def _infer_results_collection(md_text: str, filename: str) -> Optional[str]:
    """
    Infer the stored results collection name from a use case id in the report.

    Supported ids:
    - UC-S01  -> uc_s01_results
    - UC-R01  -> uc_r01_results
    - UC-001  -> uc_001_results
    """
    for s in (md_text, filename):
        m = _UC_S_RE.search(s)
        if m:
            return f"uc_s{m.group(1)}_results"
        m = _UC_R_RE.search(s)
        if m:
            return f"uc_r{m.group(1)}_results"
        m = _UC_NUM_RE.search(s)
        if m:
            return f"uc_{m.group(1)}_results"
    return None


def _aql_first(db, query: str, bind_vars: Optional[Dict[str, Any]] = None) -> Any:
    cur = db.aql.execute(query, bind_vars=bind_vars or {})
    for x in cur:
        return x
    return None


def _collection_fields(db, name: str) -> List[str]:
    doc = _aql_first(db, f"FOR d IN {name} LIMIT 1 RETURN d")
    if not isinstance(doc, dict):
        return []
    return sorted(doc.keys())


def _load_rank_series(db, coll: str, limit: int = 50) -> List[Dict[str, Any]]:
    """
    Load top results for rank-like algorithms.
    """
    q = f"""
    FOR d IN {coll}
      SORT d.rank DESC
      LIMIT @limit
      RETURN {{
        id: d.id,
        key: d._key,
        rank: d.rank
      }}
    """
    return list(db.aql.execute(q, bind_vars={"limit": limit}))


def _load_component_counts(db, coll: str, limit: int = 50) -> List[Dict[str, Any]]:
    q = f"""
    FOR d IN {coll}
      COLLECT c = d.component WITH COUNT INTO n
      SORT n DESC
      LIMIT @limit
      RETURN {{ component: c, count: n }}
    """
    return list(db.aql.execute(q, bind_vars={"limit": limit}))


def _write_interactive_html(
    *,
    md_text: str,
    out_html: Path,
    chart_spec: Dict[str, Any],
) -> None:
    md_json = json.dumps(md_text, ensure_ascii=False)
    chart_json = json.dumps(chart_spec, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Fraud Intelligence Report</title>
  <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
  <script src="https://cdn.plot.ly/plotly-2.32.0.min.js"></script>
  <style>
    :root {{
      --bg: #0b1220;
      --panel: #0f1a33;
      --text: #e6eefc;
      --muted: #9bb0d3;
      --border: rgba(255,255,255,0.10);
      --accent: #7aa2ff;
    }}
    body {{
      margin: 0;
      font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji", "Segoe UI Emoji";
      background: linear-gradient(180deg, var(--bg), #070b14);
      color: var(--text);
    }}
    .wrap {{
      max-width: 1100px;
      margin: 28px auto;
      padding: 0 18px 40px;
    }}
    .grid {{
      display: grid;
      grid-template-columns: 1.2fr 0.8fr;
      gap: 16px;
      align-items: start;
    }}
    .card {{
      background: rgba(255,255,255,0.04);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 16px 16px;
      box-shadow: 0 10px 30px rgba(0,0,0,0.25);
    }}
    .card h2 {{
      margin: 0 0 12px;
      font-size: 14px;
      letter-spacing: 0.08em;
      text-transform: uppercase;
      color: var(--muted);
    }}
    #md {{
      line-height: 1.45;
    }}
    #md h1, #md h2, #md h3 {{
      margin-top: 18px;
    }}
    #md code {{
      background: rgba(122,162,255,0.12);
      border: 1px solid rgba(122,162,255,0.20);
      padding: 1px 6px;
      border-radius: 8px;
      color: var(--text);
    }}
    #md pre {{
      background: rgba(0,0,0,0.25);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 12px;
      overflow: auto;
    }}
    #md table {{
      width: 100%;
      border-collapse: collapse;
      margin: 12px 0;
      font-size: 13px;
    }}
    #md th, #md td {{
      border: 1px solid var(--border);
      padding: 8px;
    }}
    #md th {{
      background: rgba(255,255,255,0.06);
    }}
    .note {{
      color: var(--muted);
      font-size: 12px;
      margin-top: 10px;
    }}
    @media (max-width: 980px) {{
      .grid {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="grid">
      <div class="card">
        <h2>Report</h2>
        <div id="md"></div>
        <div class="note">
          Interactive charts are derived from stored result collections (no algorithm rerun).
        </div>
      </div>
      <div class="card">
        <h2>Interactive charts</h2>
        <div id="chart" style="height: 520px;"></div>
        <div id="chart2" style="height: 360px; margin-top: 14px;"></div>
      </div>
    </div>
  </div>
  <script>
    const md = {md_json};
    const spec = {chart_json};
    document.getElementById("md").innerHTML = marked.parse(md);

    const layoutBase = {{
      paper_bgcolor: "rgba(0,0,0,0)",
      plot_bgcolor: "rgba(255,255,255,0.02)",
      font: {{ color: "#e6eefc" }},
      margin: {{ t: 30, r: 10, b: 70, l: 50 }},
    }};

    function plot(spec, targetId) {{
      if (!spec || !spec.data || spec.data.length === 0) {{
        document.getElementById(targetId).innerHTML = "<div class='note'>No chart data available.</div>";
        return;
      }}
      Plotly.newPlot(targetId, spec.data, {{...layoutBase, ...(spec.layout || {{}})}}, {{
        responsive: true,
        displaylogo: false,
      }});
    }}

    plot(spec.primary, "chart");
    plot(spec.secondary, "chart2");
  </script>
</body>
</html>
"""

    out_html.write_text(html, encoding="utf-8")


def _build_chart_spec(algorithm: str, results: Dict[str, Any]) -> Dict[str, Any]:
    algo = algorithm.lower().strip()
    if algo == "pagerank":
        series = results.get("top") or []
        x = [str(r.get("id") or r.get("key") or "") for r in series]
        y = [float(r.get("rank") or 0) for r in series]
        primary = {
            "data": [
                {
                    "type": "bar",
                    "x": x,
                    "y": y,
                    "marker": {"color": "#7aa2ff"},
                    "hovertemplate": "id=%{x}<br>rank=%{y}<extra></extra>",
                }
            ],
            "layout": {
                "title": "Top entities by PageRank",
                "xaxis": {"title": "Entity id", "tickangle": 45},
                "yaxis": {"title": "PageRank"},
            },
        }
        secondary = {
            "data": [
                {
                    "type": "histogram",
                    "x": y,
                    "marker": {"color": "rgba(122,162,255,0.55)"},
                }
            ],
            "layout": {
                "title": "Distribution (top-N PageRank values)",
                "xaxis": {"title": "PageRank"},
                "yaxis": {"title": "Count"},
            },
        }
        return {"primary": primary, "secondary": secondary}

    if algo == "wcc":
        comps = results.get("components") or []
        x = [str(r.get("component")) for r in comps]
        y = [int(r.get("count") or 0) for r in comps]
        primary = {
            "data": [
                {
                    "type": "bar",
                    "x": x,
                    "y": y,
                    "marker": {"color": "#35d0ba"},
                    "hovertemplate": "component=%{x}<br>count=%{y}<extra></extra>",
                }
            ],
            "layout": {
                "title": "Largest connected components (WCC)",
                "xaxis": {"title": "Component id", "tickangle": 45},
                "yaxis": {"title": "Vertices in component"},
            },
        }
        secondary = {
            "data": [
                {
                    "type": "pie",
                    "labels": x[:12],
                    "values": y[:12],
                    "textinfo": "label+percent",
                }
            ],
            "layout": {"title": "Component size share (top components)"},
        }
        return {"primary": primary, "secondary": secondary}

    # Fallback: no charts
    return {"primary": {"data": []}, "secondary": {"data": []}}


def main() -> int:
    load_dotenv()
    cfg = get_arango_config(forced_mode="REMOTE")

    client = ArangoClient(hosts=cfg.url)
    db = client.db(cfg.database, username=cfg.username, password=cfg.password)

    out_dir = Path("fraud_analysis_output")
    if not out_dir.exists():
        raise SystemExit("fraud_analysis_output/ not found; run the workflow first.")

    md_files = sorted(out_dir.glob("fraud_report_*.md"))
    if not md_files:
        raise SystemExit("No fraud_report_*.md files found in fraud_analysis_output/.")

    for md_path in md_files:
        md_text = md_path.read_text(encoding="utf-8")
        coll = _infer_results_collection(md_text, md_path.name)
        if not coll or not db.has_collection(coll):
            # No stored results => can't plot interactively
            chart_spec = {"primary": {"data": []}, "secondary": {"data": []}}
            algorithm = "unknown"
        else:
            fields = _collection_fields(db, coll)
            algorithm = "pagerank" if "rank" in fields else ("wcc" if "component" in fields else "unknown")

            results: Dict[str, Any] = {}
            if algorithm == "pagerank":
                results["top"] = _load_rank_series(db, coll, limit=50)
            elif algorithm == "wcc":
                results["components"] = _load_component_counts(db, coll, limit=50)

            chart_spec = _build_chart_spec(algorithm, results)

        # Preserve existing html if present
        html_path = md_path.with_suffix(".html")
        static_path = md_path.with_name(md_path.stem + ".static.html")
        if html_path.exists() and not static_path.exists():
            html_path.replace(static_path)

        _write_interactive_html(md_text=md_text, out_html=html_path, chart_spec=chart_spec)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

