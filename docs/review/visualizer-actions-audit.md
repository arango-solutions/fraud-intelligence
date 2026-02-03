## Visualizer actions audit (Lead agent)

### What was checked (AMP/REMOTE)

- `_canvasActions` contains a single default action per graph:
  - `OntologyGraph` → **Find 2-hop neighbors (default)**
  - `DataGraph` → **Find 2-hop neighbors (default)**
  - `KnowledgeGraph` → **Find 2-hop neighbors (default)**
- For any action using `@nodes`:
  - `bindVariables` is exactly **`{ "nodes": [] }`** (array, not string)
- Per-collection expand actions apply filters to the **selected `node`** (outer loop), not traversal `v`.

### Implementation notes

- Installer: `scripts/install_graph_themes.py`
  - Adds `WITH ...` clause for cluster execution safety.
  - Uses `check_rev=False` for idempotent replace.
  - Dedupe behavior:
    - Keeps one action per `(graphId, name)` and deletes extras.

### Known gotchas

- Visualizer queries should remain bounded (`LIMIT`) to avoid overly heavy traversals.
- If the Visualizer UI ever sends a single node as a scalar bind var, the **correct fix remains**: define `bindVariables.nodes` as an array (`[]`) in stored actions (no query-side type coercion).

