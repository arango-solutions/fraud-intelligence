# Demo environment validation (devops-managed cluster)

This document validates that the Fraud Intelligence demo can run end-to-end against the configured **REMOTE** cluster.

## Security rules

- Do **not** paste `.env` contents here.
- Do **not** paste tokens, passwords, or Kubernetes configs.
- URLs/hosts should be treated as sensitive. Use “(redacted)” if sharing externally.

## Expected `.env` keys (required)

This repo expects the following environment variables for REMOTE runs:

- `MODE` (set to `REMOTE`)
- `ARANGO_URL`
- `ARANGO_DATABASE`
- `ARANGO_USERNAME`
- `ARANGO_PASSWORD`

## Validation steps (REMOTE)

Run these from repo root:

```bash
python scripts/test_phase1.py --remote-only --install-visualizer
python scripts/test_phase2.py --remote-only
python scripts/test_phase3.py --remote-only
```

## Results (latest run)

- Phase 1 (REMOTE): **PASS** (data + ingest + graphs/themes + smoke queries)
- Phase 2 (REMOTE): **PASS** (ER → GoldenRecord/resolvedTo + integration tests)
- Phase 3 (REMOTE): **PASS** (analytics + risk scoring + integration tests)

Generated artifacts:

- `docs/phase1-validation-report.md`
- `docs/phase2-validation-report.md`
- `docs/phase3-analytics-report.md`
- `docs/phase3-validation-report.md`

