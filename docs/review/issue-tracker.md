## Review issue tracker (Lead agent)

Scope: `fraud-intelligence` repo (latest `main`), AMP/REMOTE validation. This tracker is the single source of truth for findings and follow-ups.

### Evidence snapshot

- **Phase 1 REMOTE**: PASS (`docs/phase1-validation-report.md`)
  - `pytest`: **12 passed**
  - `pytest -m integration`: **7 passed, 5 deselected** (expected: only tests marked `integration` are selected)
- **Phase 2 REMOTE**: PASS (`docs/phase2-validation-report.md`)
  - ER run produced: `clusters=50`, `golden_records_upserted=50`, `resolved_edges_upserted=100`
  - `pytest -m integration`: **7 passed, 5 deselected**

### Status legend

- **P0**: demo-breaking / correctness bug
- **P1**: significant deviation / high risk
- **P2**: important improvement
- **P3**: nice-to-have / cleanup

---

## P0 (must fix)

(none currently open)

---

## P1 (high priority)

### P1-1: Ontology `Class` display + typing edges must use ArangoRDF PGT shape (`_label/_uri`)

- **Symptom**: Visualizer themes and `instanceOf` edges could point at “legacy stub” `Class` docs (`label/uri`) instead of ArangoRDF PGT `Class` docs (`_label/_uri`), creating disjoint/duplicate Class nodes.
- **Fix applied**:
  - `scripts/define_graphs.py`: `instanceOf` now links to the ArangoRDF PGT `Class` documents and removes stub `Class/<Name>` docs when safe.
  - Themes updated to prefer `_label/_uri` for `Class` (fallbacks kept in hover info).
- **Verification on AMP**:
  - No remaining stub `Class/<Name>` docs for data collections.
  - Sampled `instanceOf` edges point to `Class` docs with `_label`.

---

## P2 (important)

### P2-1: AQL portability — avoid unavailable string helpers

- **Symptom**: `ERR 1540 usage of unknown function 'ENDS_WITH()'` on AMP cluster.
- **Fix applied**: Replaced `ENDS_WITH()` usage with `LIKE(..., true)` in `scripts/define_graphs.py` class resolution.
- **Verification**: `scripts/define_graphs.py --mode REMOTE --with-type-edges` succeeds.

### P2-2: Deprecation warnings in ingestion indexes

- **Symptom**: `add_persistent_index` emits deprecation warnings.
- **Impact**: noise only (no functional breakage).
- **Recommendation**: switch to `add_index({"type":"persistent","fields":[...], ...})` to reduce log noise.

---

## P3 (nice-to-have / cleanup)

### P3-1: Reduce unused imports / docs accuracy

- `scripts/define_graphs.py` still imports XML parsing modules from older loader path (safe but unnecessary).
- Consider tightening `--force` help text (mentions “truncate ontology edge collections” but now uses ArangoRDF overwrite).

