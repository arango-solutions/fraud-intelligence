## Phase 2: Entity Resolution runbook

### Goal

Populate:
- `GoldenRecord` (vertex collection)
- `resolvedTo` (edge collection) linking `Person` → `GoldenRecord`

All ER functionality (blocking/similarity/clustering/golden persistence) comes from the `arango-entity-resolution` library.

### Install dependencies

```bash
python -m pip install -r requirements.txt
```

### Run on AMP (REMOTE)

```bash
python scripts/test_phase2.py --remote-only
```

This will:
- Connect to ArangoDB
- (Idempotently) insert a small number of synthetic duplicate-ish `Person` records for demo
- Run ER and persist `GoldenRecord` + `resolvedTo`
- Run integration tests (including Phase 2 assertions)
- Write `docs/phase2-validation-report.md`

### Run locally (optional)

```bash
python scripts/test_phase2.py --local-only
```

### Visualizer (AMP only)

Open the AMP Visualizer and use `KnowledgeGraph`:
- Start at a `Person`
- Traverse `resolvedTo` to a `GoldenRecord`

