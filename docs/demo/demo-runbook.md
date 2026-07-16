## Fraud Intelligence demo runbook (devops-managed cluster)

This is the consolidated, repeatable runbook for the end-to-end demo on the non‑AMP devops-managed cluster.

### Rules (non-negotiable)

- Do not paste secrets (no `.env`, no tokens, no passwords).
- Treat URLs/hosts as sensitive; redact if sharing externally.

---

## Pre-demo checklist

- Python environment is ready:

```bash
pip install -r requirements.txt
```

- `.env` is configured locally for the cluster:
  - `MODE=REMOTE`
  - `ARANGO_URL`, `ARANGO_DATABASE`, `ARANGO_USERNAME`, `ARANGO_PASSWORD`

- (Recommended) Start fresh browser session and open ArangoDB Web UI.

---

## Exact commands (REMOTE)

From repo root — **one command** to run all three phases:

```bash
python scripts/setup_demo.py
```

Or to resume from a specific phase (e.g. if Phase 1 already completed):

```bash
python scripts/setup_demo.py --from-phase 2
```

<details>
<summary>Individual phase commands (advanced)</summary>

```bash
python scripts/test_phase1.py --remote-only --install-visualizer
python scripts/test_phase2.py --remote-only
python scripts/test_phase3.py --remote-only
```

</details>

Expected outputs:

- Phase 1: data present + ontology ingested via **ArangoRDF PGT** + graphs/themes/canvas actions installed.
- Phase 2: `GoldenRecord` vertices + `resolvedTo` edges populated (idempotent reruns).
- Phase 3: analytics + risk fields written; reports generated.

Reports:
- `docs/phase1-validation-report.md`
- `docs/phase2-validation-report.md`
- `docs/phase3-analytics-report.md`
- `docs/phase3-validation-report.md`

---

## Investigator demo flow (Visualizer)

Two complementary flows are installed in the Visualizer (Queries panel + canvas
actions + themes). See:
- `docs/demo/demo-investigator-script.md` — detailed script
- `docs/INDICATIONS_AND_WARNINGS_GUIDE.md` — the `[I&W]` query catalog + walkthrough
- `docs/visualization_runbook.md` — themes, saved queries, canvas actions, install

**Flow A — suspect-first (classic):**

1. Visualizer → open **KnowledgeGraph**
2. Search `Victor Tella` → add **Person** synthetic alias node
3. Run **`[Person] Expand Relationships`** → reach `BankAccount`
4. Right-click `BankAccount` → run **`[BankAccount] Find cycles (AQL)`** → cycle path returned

**Flow B — indication-first (red flag → suspect):**

1. Visualizer → open **DataGraph** (or KnowledgeGraph) → **Queries** panel
2. Run **`[I&W] Circular Transaction Patterns`** → a laundering loop renders
3. Right-click a loop account → canvas actions (`Show Owner & Linked Accounts`,
   `Trace Funding Sources`, `Show Co-Accessed Accounts`) to expand the ring
4. Pivot via `[I&W] Suspect Aliases` / `[Person] Reveal Aliases` until the
   network resolves to Victor Tella
5. (Optional) Legend → switch to the **Risk Heatmap** theme to recolor by `riskScore`

> Risk-based queries/theme (`[I&W] Risk Propagation`, `UC4: Highest-Risk
> Entities`, Risk Heatmap) require **Phase 3 risk scoring** to have run on this
> database — see the troubleshooting note below.

---

## Analyst + Executive demo flow (reports + app)

Use:
- `docs/demo/demo-analyst-executive-script.md`
- `docs/demo/demo-app-runbook.md`

Run the app:

```bash
streamlit run apps/phase3_demo_app.py
```

### Analyst charts: compute PageRank + WCC via the Graph Analytics Engine (GAE)

The Analyst-lens **Mule Hub (PageRank)** and **Fraud Ring (WCC)** charts
(`fraud_report_2.html` / `fraud_report_3.html`) read per-node scores from
`uc_s01_results` (`rank`) and `uc_s02_results` (`component`). These are computed
on the **ArangoDB Graph Analytics Engine (GAE)** — PageRank/WCC are global graph
algorithms, not AQL-expressible (Pregel is deprecated; GAE replaces it).

Run **before** showing the Analyst charts (and **re-run after any data reload** —
results are keyed to the current graph and go stale). Requires the sibling
project's virtualenv, which has the `graph_analytics_ai` client + deps:

```bash
# from repo root; uses this repo's .env
~/code/agentic-graph-analytics/.venv/bin/python scripts/phase3_gae.py            # PageRank + WCC
~/code/agentic-graph-analytics/.venv/bin/python scripts/phase3_gae.py --dry-run  # validate config/engine only, no deploy
```

It deploys a short-lived GAE engine on the cluster and auto-tears-it-down
(~$0.001/run). Then regenerate the report HTML:

```bash
~/code/agentic-graph-analytics/.venv/bin/python scripts/render_interactive_html_reports.py
```

WCC runs over the **device-sharing projection** (`[BankAccount, DigitalLocation]`
+ `accessedFrom`) so the mule ring separates as one large component; running it
over raw `transferredTo` would collapse into a single giant component.

`phase3_gae.py` also **writes the scores back onto the graph nodes**
(`BankAccount.pagerankScore`, `{BankAccount,DigitalLocation}.wccComponent`), which
power two **Visualizer** saved queries — **`[I&W] Top Mule Hubs (PageRank)`** and
**`[I&W] Fraud Ring (WCC Community)`**. To refresh just the node scores after a
data reload without redeploying an engine:

```bash
~/code/agentic-graph-analytics/.venv/bin/python scripts/phase3_gae.py --write-back-only
```

---

## Demo rehearsal checklist (exact click-paths)

See:
- `docs/demo/demo-rehearsal-checklist.md`

---

## Troubleshooting (common failures)

### Canvas actions missing / not updated

- Reinstall themes/actions (REMOTE):

```bash
python scripts/install_graph_themes.py --mode REMOTE
```

### Graphs missing

- Recreate named graphs (REMOTE):

```bash
python scripts/define_graphs.py --mode REMOTE --force
```

### Cycle action returns no results

- The selected account may not be part of a directed cycle within the default `maxDepth`.
- Try the other Victor alias’s account or increase `maxDepth` (keep `limit` small).

### Streamlit app shows empty metrics

- Ensure Phase 3 has run successfully:

```bash
python scripts/test_phase3.py --remote-only
```

### Risk Propagation / UC4 empty, or Risk Heatmap renders flat (all green)

- `riskScore` is not populated (it resets to 0 whenever data is regenerated/reloaded).
- Re-run Phase 3 risk scoring against the cluster:

```bash
python scripts/phase3_risk.py --mode REMOTE
```

### Analyst PageRank / WCC charts are empty

- `fraud_report_2.html` (PageRank) / `fraud_report_3.html` (WCC) plot from the
  `uc_s01_results` / `uc_s02_results` collections. If those are missing/stale,
  run the GAE step then regenerate the reports:

```bash
~/code/agentic-graph-analytics/.venv/bin/python scripts/phase3_gae.py
~/code/agentic-graph-analytics/.venv/bin/python scripts/render_interactive_html_reports.py
```

- If `phase3_gae.py` cannot import `graph_analytics_ai`, run it with the sibling
  project's virtualenv (shown above), not the system `python`.

### Saved query renders an empty canvas

- The Queries panel only draws vertices/edges/paths. A query that returns scalar
  or aggregate objects shows nothing — this is by design. All shipped `UC*` and
  `[I&W]` queries return graph elements; see `docs/INDICATIONS_AND_WARNINGS_GUIDE.md`.
- The two data-dependent `[I&W]` queries (Gateway Accounts, Structuring Chains)
  can be empty if no matching data exists — lower their thresholds or skip them.

