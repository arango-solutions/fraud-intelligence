## Phase 3 runbook (Analytics + Risk Intelligence + Three Lenses)

This runbook describes how to run **Phase 3** against AMP/REMOTE and what outputs to expect.

### Non-negotiables

- Do not print or paste secrets from `.env`.
- Use OWL naming conventions (PascalCase vertices; camelCase edges/fields).
- Ontology ingestion remains via **ArangoRDF PGT**.
- Entity Resolution remains via **arango-entity-resolution**.

---

## 1) Run Phase 3 end-to-end (REMOTE)

From repo root:

```bash
python scripts/test_phase3.py --remote-only
```

### Expected outputs

- `docs/phase3-analytics-report.md`
- `docs/phase3-validation-report.md`

### What it does

- Validates connectivity to AMP/REMOTE
- Computes analytics summary counts:
  - circular trading edges
  - mule ring edges and hub count
  - shared device count for mule sources
  - undervalued property sales count
  - ER outputs present (`GoldenRecord`, `resolvedTo`)
- Computes and persists risk fields:
  - `riskDirect`, `riskInferred`, `riskPath`, `riskScore`, `riskReasons`
  - roll up to `GoldenRecord` via inbound `resolvedTo`
- Runs integration tests (`pytest -m integration`)

---

## 2) Run analytics only

```bash
python scripts/phase3_analytics.py --mode REMOTE
```

Output: `docs/phase3-analytics-report.md`

---

## 3) Run risk scoring only

```bash
python scripts/phase3_risk.py --mode REMOTE
```

Notes:
- Safe to rerun; scores are recomputed deterministically.
- Path risk uses multi-source propagation over `transferredTo` from seed accounts.

---

## 4) “Three lenses” demo (MVP)

The Phase 3 MVP app is intended to provide three tabs:
- Investigator
- Analyst
- Executive

See `apps/phase3_demo_app.py` (requires Streamlit).

