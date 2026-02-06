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

From repo root:

```bash
python scripts/test_phase1.py --remote-only --install-visualizer
python scripts/test_phase2.py --remote-only
python scripts/test_phase3.py --remote-only
```

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

Use the detailed script:
- `docs/demo/demo-investigator-script.md`

Minimum click-path summary:

1. Visualizer → open **KnowledgeGraph**
2. Search `Victor Tella` → add **Person** synthetic alias node
3. Run **`[Person] Expand Relationships`** → reach `BankAccount`
4. Right-click `BankAccount` → run **`[BankAccount] Find cycles (AQL)`** → cycle path returned

---

## Analyst + Executive demo flow (reports + app)

Use:
- `docs/demo/demo-analyst-executive-script.md`
- `docs/demo/demo-app-runbook.md`

Run the app:

```bash
streamlit run apps/phase3_demo_app.py
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

