## Test coverage report (Lead agent)

### What ran (REMOTE)

- Phase 1 runner: `python scripts/test_phase1.py --remote-only --install-visualizer`
  - `pytest -q`: **12 passed**
  - `pytest -q -m integration`: **7 passed, 5 deselected**
- Phase 2 runner: `python scripts/test_phase2.py --remote-only`
  - ER run + `pytest -q -m integration`: **7 passed, 5 deselected**

Evidence: `docs/phase1-validation-report.md`, `docs/phase2-validation-report.md`.

### Why “5 deselected” happens

When running `pytest -m integration`, pytest selects only tests marked with `@pytest.mark.integration`. Any test files without that marker are **intentionally deselected** (not failed/skipped). In this repo today:
- There are **12** tests total in the relevant suite window.
- **7** are marked integration, so they run.
- **5** are not integration, so they are deselected.

### What’s covered well

- **Generator invariants**: cycles, mule hub/shared device, undervalued property, no orphan addresses, deterministic edge `_key` uniqueness (`tests/test_generator_invariants.py`).
- **DB schema contract**: required collections exist after ingest (`tests/test_schema_contract.py`).
- **Fraud pattern presence on DB**: integration AQL checks (`tests/test_fraud_patterns_integration.py`).
- **ER outputs**: GoldenRecord populated and resolvedTo constraints (`tests/test_entity_resolution_integration.py`).

### Gaps / suggestions

- Add a small integration assertion that **`OntologyGraph` exists** and that `Class` has `_label/_uri` docs (to prevent regression of the `_label` vs `label` mismatch).
- Add a lightweight integration check that default canvas actions exist (counts only), if we want to lock in Visualizer behavior.

