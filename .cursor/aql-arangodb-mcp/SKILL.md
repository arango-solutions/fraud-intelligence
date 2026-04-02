---
name: aql-arangodb-mcp
description: Writes and executes ArangoDB AQL using the Arango MCP server with a manual-first workflow (AQL reference + optimization), safe parameterization (bind vars), and a validate-then-scale approach. Use when the user asks for AQL, Arango queries, graph traversals, ArangoSearch queries, or wants to run queries via the Arango MCP server.
---

# AQL with Arango MCP (manual-first, optimized, safe)

This skill standardizes how to explore ArangoDB and write/execute AQL via the **Arango MCP server**.

## Non-negotiable workflow (required by the MCP server)

Before writing or executing any AQL:

1. Fetch `aql_ref` manual.
2. Fetch `optimization` manual.
3. Only then draft AQL (with bind vars) and execute.

## Default safety posture

- Prefer **read-only** queries (`FOR…FILTER…RETURN`) unless the user explicitly requests writes.
- Use **bind variables** instead of string interpolation.
- Start with a small **LIMIT** and widen after validating shape/performance.

## Quick start (what to do when asked for “an AQL query”)

1. **Identify target DB** (default is fine if unspecified).
2. **Inventory** (as needed):
   - list databases
   - list collections (document vs edge)
   - list graphs / views / analyzers (if relevant)
3. Fetch manuals (`aql_ref` then `optimization`).
4. Draft the query with:
   - bind vars
   - early FILTERs
   - explicit LIMIT (initially)
   - deterministic SORT (when returning top-N)
5. Execute; if results are wrong/slow:
   - refine query
   - consider indexes / alternative patterns from optimization manual

## Performance checklist (apply from optimization manual)

- **Filter early**: `FILTER` as close to the `FOR` as possible.
- **Avoid full scans** on large collections; rely on selective filters and indexes.
- **Prefer edge-index filtering** for graph patterns (avoid “vertex-centric” scans).
- Use **projections**: return only fields needed (`RETURN {a: doc.a, ...}`).
- Use small `LIMIT` while iterating.

## Common patterns (templates)

### 1) Basic filtered query (parameterized)

```aql
FOR d IN @@col
  FILTER d.type == @type
  SORT d.createdAt DESC
  LIMIT @limit
  RETURN d
```

Bind vars:
- `@col`: collection name
- `type`: string
- `limit`: number

### 2) Existence / counts

```aql
RETURN {
  total: LENGTH(@@col),
}
```

Prefer `COLLECT WITH COUNT INTO` or dedicated count patterns from docs when scaling.

### 3) One-hop traversal (edge collection)

```aql
FOR v, e IN 1..1 OUTBOUND @start @@edgeCol
  LIMIT @limit
  RETURN {v, e}
```

Use bind vars:
- `start`: vertex `_id` (e.g. `"RTL_Module/or1200_cpu"`)
- `@edgeCol`: edge collection name

### 4) Named graph traversal

```aql
FOR v, e, p IN 1..@maxDepth OUTBOUND @start GRAPH @graphName
  LIMIT @limit
  RETURN p
```

## Output expectations

When producing an AQL query, include:
- the AQL string
- the bind vars object
- what it returns (shape)
- any index assumptions / performance notes

## Examples

See `examples.md` for ready-to-run query snippets and “explore the DB” recipes.

