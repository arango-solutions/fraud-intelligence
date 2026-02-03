## Performance & scalability report (Lead agent)

### Bulk ingest

- Current ingest is via `python-arango` bulk import (`import_bulk`) in `scripts/ingest.py`.
- **REMOTE safe behavior**: by default, import is skipped when collections are non-empty (unless `--force`), preventing accidental destructive re-ingests on AMP.

### AQL and graph actions

- Canvas actions:
  - Traversals are bounded (`LIMIT 100` for 2-hop default, `LIMIT 20` for 1-hop expansion).
  - Include `WITH ...` clause for cluster compatibility.

### ER pipeline

- Phase 2 uses `arango-entity-resolution`:
  - Blocking → similarity scoring → similarity edge writes → WCC clustering → golden record persistence.
  - The clustering step uses `truncate_existing=True` for cluster results (expected for reruns; keeps output consistent but is destructive to that cluster collection).

### Recommendations (non-blocking)

- **Ingestion index warnings**: migrate from deprecated `add_persistent_index` helpers to `add_index({type:'persistent', ...})` to reduce log noise and ensure forward compatibility.
- **Instance typing edges**: `instanceOf` is rebuilt deterministically (currently truncates when allowed). This is OK for demo-scale, but if we scale up, consider:
  - chunked upsert with stable keys (already implemented) without truncation, or
  - rebuilding only when ontology changes.

